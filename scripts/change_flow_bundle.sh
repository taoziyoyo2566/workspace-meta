#!/usr/bin/env bash
# Run a reviewed change-flow bundle (git-publication.md Change-Flow Bundle)
# from a bundle directory, stopping at the first drift from the reviewed state
# that it checks. The push stays a separate command between `commit` and
# `retire`, printed as `cd <repo> && git push ...`, so a runtime or project
# guard or permission rule that asks before `git push` still sees it.
#
# Usage: scripts/change_flow_bundle.sh check|commit|retire DIR
#
# DIR holds:
#   bundle.env      KEY=VALUE lines: REPO (the main checkout's root) and
#                   WORKTREE (the change's worktree), both absolute; BRANCH;
#                   BASE (full OID of the main tip the change starts from);
#                   REMOTE (a configured remote, default origin); MAIN (default
#                   main); and the reviewed fingerprints TREE and
#                   MESSAGE_SHA256, which `check` prints while they are missing
#   paths.txt       the exact paths to commit, one per line
#   commit-msg.txt  the reviewed commit message
#
#   check   changes nothing but the objects a temporary index writes and the
#           stat cache that `git status` refreshes
#   commit  check, the exact-path add, one commit of the reviewed message, and
#           the fast-forward of MAIN to that commit
#   retire  after the push: remove the change's worktree, then its branch with
#           `git branch -d`; never --force, never another worktree
set -euo pipefail
# Variables that would point git at another repository, index, or object view.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE GIT_REPLACE_REF_BASE
export GIT_NO_REPLACE_OBJECTS=1

usage() {
  echo "usage: $0 check|commit|retire DIR" >&2
  exit 2
}

fail() {
  printf 'STOP: %s\n' "$*" >&2
  exit 1
}

sha256() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum | cut -d' ' -f1
  else
    shasum -a 256 | cut -d' ' -f1
  fi
}

real() {
  (cd "$1" 2>/dev/null && pwd -P)
}

[ $# -eq 2 ] || usage
script="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
action=$1
case "$action" in
  check | commit | retire) ;;
  *) usage ;;
esac
[ -d "$2" ] || fail "no bundle directory $2"
dir=$(cd "$2" && pwd)

REPO='' WORKTREE='' BRANCH='' BASE='' REMOTE=origin MAIN=main TREE='' MESSAGE_SHA256=''
[ -f "$dir/bundle.env" ] || fail "bundle.env is missing"
while IFS= read -r line || [ -n "$line" ]; do
  case "$line" in
    '' | '#'*) continue ;;
    REPO=* | WORKTREE=* | BRANCH=* | BASE=* | REMOTE=* | MAIN=* | TREE=* | MESSAGE_SHA256=*)
      printf -v "${line%%=*}" '%s' "${line#*=}"
      ;;
    *) fail "bundle.env: unexpected line: $line" ;;
  esac
done < "$dir/bundle.env"
for key in REPO WORKTREE BRANCH BASE REMOTE MAIN; do
  [ -n "${!key}" ] || fail "bundle.env: $key is not set"
done
[[ $BASE =~ ^[0-9a-f]{40}$ ]] || fail "bundle.env: BASE must be a full commit OID"
[ -z "$TREE" ] || [[ $TREE =~ ^[0-9a-f]{40}$ ]] || fail "bundle.env: TREE must be a full tree OID"
[ -z "$MESSAGE_SHA256" ] || [[ $MESSAGE_SHA256 =~ ^[0-9a-f]{64}$ ]] ||
  fail "bundle.env: MESSAGE_SHA256 must be a SHA-256"
[[ $REPO == /* && $WORKTREE == /* ]] ||
  fail "bundle.env: REPO and WORKTREE must be absolute paths"
[[ $REMOTE =~ ^[A-Za-z0-9][A-Za-z0-9._-]*$ ]] || fail "bundle.env: REMOTE must be a remote name"
for key in BRANCH MAIN; do
  git check-ref-format --branch "${!key}" >/dev/null 2>&1 ||
    fail "bundle.env: $key is not a valid branch name"
done
[ "$BRANCH" != "$MAIN" ] || fail "bundle.env: BRANCH must differ from MAIN"
[ -s "$dir/commit-msg.txt" ] || fail "commit-msg.txt is missing or empty"

paths=()
if [ -f "$dir/paths.txt" ]; then
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      *[![:space:]]*) paths+=("$line") ;;
    esac
  done < "$dir/paths.txt"
fi
[ ${#paths[@]} -gt 0 ] || fail "paths.txt is missing or empty"

listed_paths() {
  printf '%s\n' "${paths[@]}" | LC_ALL=C sort -u
}

changed_paths() {
  git -C "$WORKTREE" ls-files -z --modified --deleted --others --exclude-standard |
    tr '\0' '\n' | LC_ALL=C sort -u
}

staged_paths() {
  git -C "$WORKTREE" diff --cached --no-renames --name-only -z |
    tr '\0' '\n' | LC_ALL=C sort -u
}

global_identity() {
  local name email
  # Read in the worktree, so an includeIf in the global file resolves as it
  # does for the commit.
  name=$(git -C "$WORKTREE" config --global --includes --get user.name) ||
    fail "the global user.name is not set"
  email=$(git -C "$WORKTREE" config --global --includes --get user.email) ||
    fail "the global user.email is not set"
  printf '%s <%s>' "$name" "$email"
}

# The author and committer git would use now, from configuration of any scope
# and the environment, must both be the global identity.
check_identity() {
  local expected role ident
  expected=$(global_identity)
  for role in AUTHOR COMMITTER; do
    ident=$(git -C "$WORKTREE" var "GIT_${role}_IDENT") ||
      fail "git cannot determine the $role identity"
    ident=${ident% * *}
    [ "$ident" = "$expected" ] ||
      fail "the $role identity would be $ident, not the global $expected"
  done
}

# Fail when the text holds a Co-Authored-By or Signed-off-by trailer or line;
# the operator's identity is the only attribution.
no_attribution() {
  local trailers
  if grep -qiE '^[[:space:]]*(co-authored-by|signed-off-by)[[:space:]]*:' <<<"$1"; then
    fail "$2 carries a Co-Authored-By or Signed-off-by line"
  fi
  trailers=$(git interpret-trailers --parse <<<"$1")
  if grep -qiE '^(co-authored-by|signed-off-by):' <<<"$trailers"; then
    fail "$2 carries a Co-Authored-By or Signed-off-by trailer"
  fi
}

# Stop when the checkout at $1 is in the middle of an operation whose state a
# commit would pick up, or hides local edits from `git status`.
no_hidden_state() {
  local ref hidden
  for ref in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD REBASE_HEAD MERGE_AUTOSTASH; do
    if git -C "$1" rev-parse -q --verify "$ref" >/dev/null; then
      fail "$1 has $ref set; finish or abort that operation first"
    fi
  done
  for ref in rebase-merge rebase-apply; do
    [ ! -e "$(git -C "$1" rev-parse --path-format=absolute --git-path "$ref")" ] ||
      fail "$1 is in the middle of a rebase"
  done
  hidden=$(git -C "$1" ls-files -v | grep -E '^([a-z]|S) ' || true)
  [ -z "$hidden" ] ||
    fail "$1 hides local edits with assume-unchanged or skip-worktree: $hidden"
}

# Every path's leading directories must be real directories, or absent, in the
# main checkout, unless the change itself deletes a tracked file there, so the
# fast-forward replaces no local file or symbolic link.
no_leading_conflict() {
  local path prefix listed
  listed=$(listed_paths)
  for path in "${paths[@]}"; do
    prefix=$path
    while [ "$prefix" != "${prefix%/*}" ]; do
      prefix=${prefix%/*}
      if [ -L "$REPO/$prefix" ] || { [ -e "$REPO/$prefix" ] && [ ! -d "$REPO/$prefix" ]; }; then
        if grep -qxF -- "$prefix" <<<"$listed" &&
          git -C "$REPO" ls-files --error-unmatch -- "$prefix" >/dev/null 2>&1; then
          continue
        fi
        fail "the main checkout holds a file or link at $prefix, where the change writes a directory"
      fi
    done
  done
}

# The tree a commit of exactly paths.txt would have, built in a temporary
# index so the worktree's own index stays untouched; it also confirms that
# `git add` would stage exactly those paths.
reviewed_tree() {
  local tmp tree='' staged
  tmp=$(mktemp -d "${TMPDIR:-/tmp}/bundle-index.XXXXXX") || exit 1
  if GIT_INDEX_FILE="$tmp/index" git -C "$WORKTREE" read-tree HEAD &&
    GIT_INDEX_FILE="$tmp/index" git -C "$WORKTREE" add -- "${paths[@]}"; then
    staged=$(GIT_INDEX_FILE="$tmp/index" git -C "$WORKTREE" diff --cached --no-renames \
      --name-only -z HEAD | tr '\0' '\n' | LC_ALL=C sort -u)
    if [ "$staged" = "$(listed_paths)" ]; then
      tree=$(GIT_INDEX_FILE="$tmp/index" git -C "$WORKTREE" write-tree) || tree=''
    else
      echo "git add would stage a different set than paths.txt" >&2
    fi
  fi
  rm -f -- "$tmp/index" "$tmp/index.lock"
  rmdir -- "$tmp"
  [ -n "$tree" ] || exit 1
  printf '%s' "$tree"
}

# Print the branch REPO has checked out in the worktree at $1, if any.
registered_branch() {
  local target listed='' line
  target=$(real "$1") || return 0
  while IFS= read -r line; do
    case "$line" in
      'worktree '*) listed=$(real "${line#worktree }") || listed='' ;;
      'branch refs/heads/'*)
        if [ "$listed" = "$target" ]; then
          printf '%s' "${line#branch refs/heads/}"
          return 0
        fi
        ;;
    esac
  done < <(git -C "$REPO" worktree list --porcelain)
}

checkouts_of() {
  git -C "$REPO" worktree list --porcelain | grep -cxF "branch refs/heads/$1" || true
}

common_dir() {
  real "$(git -C "$1" rev-parse --path-format=absolute --git-common-dir)"
}

remote_tip() {
  git -C "$REPO" ls-remote -- "$REMOTE" "refs/heads/$MAIN" | cut -f1
}

# The push goes to exactly the one URL `check` shows, with no configured
# mapping, mirroring, tags, submodules, or options added.
check_push_target() {
  local urls key value
  urls=$(git -C "$REPO" remote get-url --push --all "$REMOTE")
  [ "$(printf '%s\n' "$urls" | grep -c .)" = 1 ] ||
    fail "$REMOTE pushes to more than one URL: $(echo $urls)"
  [ "$urls" = "$(git -C "$REPO" remote get-url "$REMOTE")" ] ||
    fail "$REMOTE pushes to $urls, not to the URL its tip was read from"
  [ "$(git -C "$REPO" config --get-all "remote.$REMOTE.url" | grep -c .)" = 1 ] ||
    fail "$REMOTE has more than one URL"
  for key in "remote.$REMOTE.push" "remote.$REMOTE.mirror" push.followTags \
    push.recurseSubmodules push.pushOption submodule.recurse; do
    value=$(git -C "$REPO" config --get-all "$key" || true)
    [ -z "$value" ] || [ "$value" = false ] ||
      fail "$key is set ($value), so the push would do more than update $MAIN"
  done
  printf '%s' "$urls"
}

check() {
  local value changed listed tree message_sha push_url
  [ "$(real "$REPO")" = "$(real "$(git -C "$REPO" rev-parse --show-toplevel)")" ] ||
    fail "REPO is not the root of the main checkout"
  [ "$(real "$WORKTREE")" != "$(real "$REPO")" ] || fail "WORKTREE is the main checkout"
  git -C "$REPO" config --get "remote.$REMOTE.url" >/dev/null ||
    fail "$REMOTE is not a configured remote of $REPO"
  push_url=$(check_push_target) || exit 1
  value=$(git -C "$REPO" symbolic-ref -q HEAD) || value=''
  [ "$value" = "refs/heads/$MAIN" ] || fail "the main checkout $REPO is not on $MAIN"
  [ "$(git -C "$REPO" rev-parse "refs/heads/$MAIN")" = "$BASE" ] || fail "$MAIN moved from $BASE"
  [ "$(checkouts_of "$MAIN")" = 1 ] ||
    fail "$MAIN is checked out in more than one worktree, so the fast-forward would leave another one behind"
  [ "$(remote_tip)" = "$BASE" ] || fail "$REMOTE's $MAIN is not at $BASE"
  [ -z "$(git -C "$REPO" status --porcelain --untracked-files=all)" ] ||
    fail "the main checkout $REPO is not clean"
  value=$(git -C "$REPO" status --porcelain --ignored --untracked-files=all -- "${paths[@]}")
  [ -z "$value" ] ||
    fail "the main checkout holds an ignored or untracked file where the change writes; the merge would overwrite it: $value"
  no_leading_conflict
  no_hidden_state "$REPO"

  [ -d "$WORKTREE" ] || fail "no worktree at $WORKTREE"
  [ "$(real "$WORKTREE")" = "$(real "$(git -C "$WORKTREE" rev-parse --show-toplevel)")" ] ||
    fail "WORKTREE is not the root of a worktree"
  [ "$(common_dir "$WORKTREE")" = "$(common_dir "$REPO")" ] ||
    fail "$WORKTREE belongs to another repository than $REPO"
  [ "$(registered_branch "$WORKTREE")" = "$BRANCH" ] ||
    fail "$REPO has no worktree at $WORKTREE on $BRANCH"
  [ "$(git -C "$WORKTREE" symbolic-ref -q HEAD)" = "refs/heads/$BRANCH" ] ||
    fail "$WORKTREE is not on $BRANCH"
  [ "$(git -C "$WORKTREE" rev-parse HEAD)" = "$BASE" ] || fail "$BRANCH is not at $BASE"
  no_hidden_state "$WORKTREE"
  git -C "$WORKTREE" diff --cached --quiet ||
    fail "$WORKTREE has staged changes; the bundle stages paths.txt itself"
  changed=$(changed_paths)
  listed=$(listed_paths)
  if [ "$changed" != "$listed" ]; then
    diff <(printf '%s\n' "$listed") <(printf '%s\n' "$changed") >&2 || true
    fail "the changes in $WORKTREE (>) differ from paths.txt (<)"
  fi

  check_identity
  no_attribution "$(cat "$dir/commit-msg.txt")" "commit-msg.txt"

  tree=$(reviewed_tree) || fail "cannot build the tree of exactly paths.txt"
  message_sha=$(sha256 < "$dir/commit-msg.txt")
  if [ -z "$TREE" ] || [ -z "$MESSAGE_SHA256" ]; then
    printf 'TREE=%s\nMESSAGE_SHA256=%s\n' "$tree" "$message_sha"
    fail "record these fingerprints of the reviewed content in bundle.env"
  fi
  [ "$tree" = "$TREE" ] || fail "the content of paths.txt changed since review (tree $tree, not $TREE)"
  [ "$message_sha" = "$MESSAGE_SHA256" ] || fail "commit-msg.txt changed since review"

  echo "bundle checked: $BRANCH at $BASE, ${#paths[@]} paths, tree $TREE," \
    "identity $(global_identity), push to $push_url"
}

commit() {
  check
  local staged listed new message expected identity
  # Commit a private copy of the reviewed message, and fix the expected text
  # before any hook runs, so no later write can change what is committed.
  message_copy=$(mktemp "${TMPDIR:-/tmp}/bundle-message.XXXXXX")
  trap 'rm -f -- "$message_copy"' EXIT
  cp -- "$dir/commit-msg.txt" "$message_copy"
  [ "$(sha256 < "$message_copy")" = "$MESSAGE_SHA256" ] || fail "commit-msg.txt changed since review"
  expected=$(git stripspace < "$message_copy")

  git -C "$WORKTREE" add -- "${paths[@]}"
  staged=$(staged_paths)
  listed=$(listed_paths)
  [ "$staged" = "$listed" ] ||
    fail "the staged set differs from paths.txt; it is staged, nothing is committed"
  [ "$(git -C "$WORKTREE" write-tree)" = "$TREE" ] ||
    fail "the staged tree differs from TREE; it is staged, nothing is committed"
  git -C "$WORKTREE" diff --cached --stat | tail -n 1
  git -C "$WORKTREE" commit -q --cleanup=whitespace -F "$message_copy" ||
    fail "git commit failed, for example a hook rejected it; paths.txt is staged in $WORKTREE, nothing is committed"
  new=$(git -C "$WORKTREE" rev-parse HEAD)
  after="$BRANCH is now at $new and $MAIN was not moved by this run; nothing is merged"
  [ "$(git -C "$WORKTREE" symbolic-ref -q HEAD)" = "refs/heads/$BRANCH" ] &&
    [ "$(git -C "$REPO" rev-parse "refs/heads/$BRANCH")" = "$new" ] ||
    fail "the commit $new did not land on $BRANCH; $MAIN was not moved by this run; nothing is merged"
  ! git -C "$WORKTREE" rev-parse -q --verify "$new^2" >/dev/null ||
    fail "commit $new is a merge commit; $after"
  [ "$(git -C "$WORKTREE" rev-parse "$new^")" = "$BASE" ] ||
    fail "commit $new does not sit on $BASE; $after"
  [ "$(git -C "$WORKTREE" rev-parse "$new^{tree}")" = "$TREE" ] ||
    fail "commit $new does not have the reviewed tree; $after"
  message=$(git -C "$WORKTREE" cat-file commit "$new" | sed '1,/^$/d')
  [ "$message" = "$expected" ] ||
    fail "commit $new does not carry the reviewed message; $after"
  no_attribution "$message" "commit $new"
  identity=$(global_identity)
  [ "$(git -C "$WORKTREE" log -1 --no-show-signature --format='%an <%ae>' "$new")" = "$identity" ] ||
    fail "commit $new is not authored by $identity; $after"
  [ "$(git -C "$WORKTREE" log -1 --no-show-signature --format='%cn <%ce>' "$new")" = "$identity" ] ||
    fail "commit $new is not committed by $identity; $after"
  git -C "$WORKTREE" log -1 --no-show-signature --format='committed %H%n  author %an <%ae>%n  %s' "$new"

  # The fast-forward: the main checkout must still be clean on MAIN at BASE,
  # and merge options from the configuration must not apply.
  [ "$(git -C "$REPO" symbolic-ref -q HEAD)" = "refs/heads/$MAIN" ] ||
    fail "the main checkout left $MAIN; $after"
  [ "$(git -C "$REPO" rev-parse "refs/heads/$MAIN")" = "$BASE" ] ||
    fail "$MAIN moved from $BASE; $after"
  [ -z "$(git -C "$REPO" status --porcelain --untracked-files=all)" ] ||
    fail "the main checkout is no longer clean; $after"
  if ! git -C "$REPO" merge -q --ff-only --no-overwrite-ignore --no-autostash --no-squash "$new"; then
    fail "the fast-forward of $MAIN failed. $MAIN is at $(git -C "$REPO" rev-parse "refs/heads/$MAIN"), and the main checkout reads: $(git -C "$REPO" status --short | head -n 20)"
  fi
  [ "$(git -C "$REPO" rev-parse "refs/heads/$MAIN")" = "$new" ] ||
    fail "$MAIN is at $(git -C "$REPO" rev-parse "refs/heads/$MAIN"), not $new"
  # Files the change's ignore rules now admit may show as untracked; only
  # changes to tracked files mean the fast-forward left something behind.
  [ -z "$(git -C "$REPO" status --porcelain --untracked-files=no)" ] ||
    fail "$MAIN is at $new but the main checkout has changes: $(git -C "$REPO" status --short | head -n 20)"
  echo "fast-forwarded $MAIN to $new"
  # The push names the reviewed commit, not the local branch, so a commit that
  # reaches $MAIN later is not published with it.
  printf 'next: cd %q && git push --no-follow-tags -- %q %q\n' "$REPO" "$REMOTE" "$new:refs/heads/$MAIN"
  printf 'then: %q retire %q\n' "$script" "$dir"
}

# Print the PIDs of processes whose working directory is inside the existing
# directory $1.
busy() {
  local target pid cwd
  if [ ! -d /proc ]; then
    echo "note: no /proc, so processes working in $1 are not checked" >&2
    return 0
  fi
  target=$(real "$1") || fail "cannot resolve $1"
  for pid in /proc/[0-9]*; do
    cwd=$(readlink "$pid/cwd" 2>/dev/null) || continue
    case "$cwd/" in
      "$target"/*) echo "${pid#/proc/}" ;;
    esac
  done
}

# Everything `git worktree remove` would delete must be a tracked file of the
# change: no submodule, nested repository, untracked or ignored file, or
# per-worktree ref, whatever `git status` shows.
nothing_untracked_on_disk() {
  local extra refs stage
  stage=$(git -C "$WORKTREE" ls-files --stage)
  ! grep -q '^160000 ' <<<"$stage" ||
    fail "$WORKTREE has submodules; remove it as a separately reviewed action"
  [ -z "$(find "$WORKTREE" -mindepth 2 -name .git -print -quit)" ] ||
    fail "$WORKTREE holds a nested .git entry"
  refs=$(git -C "$WORKTREE" for-each-ref --format='%(refname)' refs/worktree refs/bisect refs/rewritten)
  [ -z "$refs" ] || fail "$WORKTREE has per-worktree refs: $refs"
  extra=$(LC_ALL=C comm -13 \
    <(git -C "$WORKTREE" ls-files -z | tr '\0' '\n' | LC_ALL=C sort -u) \
    <(cd "$WORKTREE" && find . -mindepth 1 -path ./.git -prune -o \( -type f -o -type l \) -print |
      sed 's|^\./||' | LC_ALL=C sort -u))
  [ -z "$extra" ] || fail "$WORKTREE holds files that are not tracked: $(echo $extra)"
}

retire() {
  local new tip upstream pids leftovers
  new=$(git -C "$REPO" rev-parse --verify -q "refs/heads/$BRANCH") ||
    fail "no branch $BRANCH (already retired?)"
  ! git -C "$REPO" rev-parse -q --verify "$new^2" >/dev/null ||
    fail "$BRANCH is a merge commit"
  [ "$(git -C "$REPO" rev-parse "$new^")" = "$BASE" ] ||
    fail "$BRANCH is not one commit on $BASE"
  [ "$(git -C "$REPO" rev-parse "refs/heads/$MAIN")" = "$new" ] || fail "$MAIN is not at $BRANCH"
  git -C "$REPO" fetch -q --no-prune --no-tags -- "$REMOTE"
  tip=$(remote_tip)
  if [ "$tip" != "$new" ]; then
    if [ -n "$tip" ] && git -C "$REPO" merge-base --is-ancestor "$new" "$tip" 2>/dev/null; then
      fail "$REMOTE's $MAIN has moved past $new, so the change is published; retire the worktree as a separate step"
    fi
    if [ -n "$tip" ] && git -C "$REPO" merge-base --is-ancestor "$BASE" "$tip" 2>/dev/null &&
      [ "$tip" != "$BASE" ]; then
      fail "$REMOTE's $MAIN moved to $tip, which does not contain $new, so the push was rejected; local $MAIN holds the unpublished commit $new, and the bundle must be redone on the new tip"
    fi
    fail "$REMOTE's $MAIN is at ${tip:-nothing}, not $new; push first"
  fi
  [ -d "$WORKTREE" ] || fail "no worktree at $WORKTREE (already removed?)"
  [ "$(registered_branch "$WORKTREE")" = "$BRANCH" ] ||
    fail "$REPO has no worktree at $WORKTREE on $BRANCH"
  [ "$(checkouts_of "$BRANCH")" = 1 ] ||
    fail "$BRANCH is checked out in more than one worktree, so git branch -d would refuse; nothing is removed"
  leftovers=$(git -C "$WORKTREE" status --porcelain --ignored --untracked-files=all)
  [ -z "$leftovers" ] ||
    fail "$WORKTREE holds changes, untracked files, or ignored files: $(echo "$leftovers" | head -n 20 | tr '\n' ' ')"
  no_hidden_state "$WORKTREE"
  nothing_untracked_on_disk
  pids=$(busy "$WORKTREE")
  [ -z "$pids" ] || fail "a process works in $WORKTREE (PID $(echo $pids))"
  # `git branch -d` checks the upstream when one is set, otherwise HEAD.
  if upstream=$(git -C "$REPO" rev-parse --abbrev-ref --symbolic-full-name "$BRANCH@{upstream}" 2>/dev/null); then
    git -C "$REPO" merge-base --is-ancestor "$new" "$upstream" ||
      fail "$BRANCH is not merged into its upstream $upstream, so git branch -d would refuse; nothing is removed"
  else
    git -C "$REPO" merge-base --is-ancestor "$new" HEAD ||
      fail "$BRANCH is not merged into $REPO's HEAD, so git branch -d would refuse; nothing is removed"
  fi
  if ! git -C "$REPO" worktree remove "$WORKTREE"; then
    if [ -d "$WORKTREE" ]; then
      fail "git worktree remove failed for $WORKTREE, which now holds: $(cd "$WORKTREE" && find . -mindepth 1 -maxdepth 2 | head -n 20); $BRANCH is kept"
    fi
    fail "git worktree remove failed after deleting $WORKTREE; $BRANCH is kept"
  fi
  git -C "$REPO" branch -d "$BRANCH" ||
    fail "the worktree is removed, but git branch -d refused $BRANCH; delete it as a separate step"
  git -C "$REPO" worktree list
}

"$action"

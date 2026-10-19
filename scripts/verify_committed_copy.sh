#!/usr/bin/env bash
# Run a command, by default `make test`, in a private temporary copy of a
# checkout in which every tracked file and every untracked file the ignore
# rules admit is committed. Checks that read Git, such as the documentation
# gate's check that routed files are tracked, then see the state a commit of
# the whole change would produce. A file the ignore rules do not admit is left
# out, as a commit would leave it out. The copy is removed afterwards.
#
# Usage: scripts/verify_committed_copy.sh [DIR] [-- COMMAND...]
set -euo pipefail
# Variables that would point git at another repository or index.
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_COMMON_DIR GIT_OBJECT_DIRECTORY \
  GIT_ALTERNATE_OBJECT_DIRECTORIES GIT_NAMESPACE

src=.
if [ $# -gt 0 ] && [ "$1" != "--" ]; then
  src=$1
  shift
fi
if [ $# -gt 0 ] && [ "$1" = "--" ]; then
  shift
fi
if [ $# -eq 0 ]; then
  set -- make test
fi

src=$(git -C "$src" rev-parse --show-toplevel)
copy=$(mktemp -d "${TMPDIR:-/tmp}/verify-committed.XXXXXX")
trap 'rm -rf -- "$copy"' EXIT

# Tracked files plus the untracked files the ignore rules admit; a tracked file
# deleted in the working tree is skipped.
git -C "$src" ls-files -z --cached --others --exclude-standard |
  while IFS= read -r -d '' path; do
    [ -e "$src/$path" ] || [ -L "$src/$path" ] || continue
    mkdir -p -- "$copy/$(dirname -- "$path")"
    cp -P -p -- "$src/$path" "$copy/$path"
  done

# The copy's own commit ignores the operator's global and system Git
# configuration, so no template, hook, or signing setting applies to it.
copy_git() {
  GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 git -C "$copy" \
    -c user.name=verify -c user.email=verify@localhost.invalid "$@"
}
copy_git init -q -b main
copy_git add --all --force
copy_git commit -q --no-gpg-sign -m "committed copy of $src"
echo "committed copy of $src: $(git -C "$copy" ls-files | wc -l) files in $copy" >&2

cd "$copy"
"$@"

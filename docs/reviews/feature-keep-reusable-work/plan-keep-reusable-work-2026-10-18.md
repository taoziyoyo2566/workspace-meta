# Plan: keep reusable work out of temporary space

- **Date**: 2026-10-18
- **Level**: Follow-up workstream on branch `feat/keep-reusable-work`, from
  `main` at `ddec1a3`.
- **Status**: COMPLETE (2026-10-19). Outcome:
  [changelog-keep-reusable-work-2026-10-19.md](changelog-keep-reusable-work-2026-10-19.md).
  Approved for direction and scope by the operator's selection on 2026-10-18
  (see Approval).
- **Request**: the operator, 2026-10-18, after a session cleanup removed its
  scratch directory: "有些脚本如何后续依然会被使用，那么也应该保留吧，比如清理脚本，还有其他脚本么或者内容么？"
- **Approval**: the operator, 2026-10-18, answering three questions:
  - which reusable items to turn into kept files in workspace-meta now, in one
    change branch with a bundle for approval: all four offered: the
    request-intake and delegation evaluation scenarios, guarded sync, the
    bundle runner, and the committed-copy check;
  - whether to add the step "before removing its temporary files, an agent
    moves what will be needed again to its owner, proposed to the operator
    first, and removes only the rest" to the workspace rules in the same
    change: yes;
  - how an agent's session scratch is cleaned in claude-md from now on: narrow
    the claude-md guard so that `rm -rf` is allowed only inside the agent's
    own temporary root, with the path resolved first, checked with
    `/guardrail-audit`.

  Git publication, the claude-md commit, and `make sync` on each host stay
  separate approvals.
- **Decisions after review** (the operator, 2026-10-18, on the findings of the
  two independent reviews):
  - claude-md's settings keep denying `rm -rf`, which overrides any hook
    decision in Claude Code 2.1.302. The guard allows only
    `rm -r -f <own scratch path>`, and a claude-md rule tells agents to use that
    form for their scratch.
  - The bundle runner drops `retire.txt`: it retires only the change's own
    worktree, never with `--force`. Removing any other worktree stays a
    separately reviewed action.
  - The lower scores of two restored scenarios on current `main` become a
    separate task after this change lands, recorded in the Changelog as an
    open finding.

## Goal

Work an agent will need again is kept by its owner instead of living only in
temporary space, where a cleanup removes it, and an agent can remove its own
temporary files without asking the operator to run a cleanup.

## Scope

1. Evaluation scenarios: recover the six request-intake and delegation
   scenarios written for the 2026-10-17 evaluation (`intake-*`,
   `delegation-plan` with its later rewording, `control-trivial-question`)
   from the session transcripts into `evals/rules/scenarios/`, and check them
   against today's rules.
2. Guarded sync: an option of the sync engine that applies a sync only when
   its plan matches the expected change list, replacing the scratch script
   that answered the interactive prompt.
3. Bundle runner: a script that runs a reviewed change-flow bundle (exact-path
   add, one commit, fast-forward, push, retirement) and stops at the first
   drift.
4. Committed-copy check: a `make` target that runs the full gate on a copy in
   which every whitelisted file is committed.
5. Rule: the sorting step in `temporary-files.md` Lifecycle, its route,
   provenance (W-R75), design map, tests, and an evaluation scenario.
6. claude-md (separate repository, its own change flow and records): narrow
   its Bash guard and the template copies so that `rm -rf` is allowed only for
   resolved paths inside the session's own temporary root.

## Exclusions

- Research notes, raw evaluation outputs, and one-off scripts from the
  2026-10-17/18 sessions: their results are in the Plans, Changelogs,
  investigation record, and commit messages.
- Other hosts' `make sync` and the `v1.2.0` tag.

## Design

Any change to the scope above goes back to the operator.

### Evaluation scenarios

The six scenarios exist only in the session's subagent transcripts. Each is
restored from its last written version, `delegation-plan` with the later
rewording of its third criterion, and must pass the scenario hygiene test
against today's rules. A scenario that now quotes rule text is reworded in the
incident's terms, not dropped.

### Guarded sync

`scripts/sync_codex_config.py --expect LABELS` applies without a prompt only
when every drifted area is listed. `LABELS` holds area labels as the status
lines print them, separated by `;`, and the option may repeat.

- An unknown label stops the run before anything is written.
- A drifted area outside the list stops the run: the drift details and the
  unexpected labels are printed and nothing is written.
- Listed areas that are already current are reported, and the rest applies.
- `make sync SYNC_EXPECT='Codex AGENTS.md'` passes the option, unexpanded;
  `make sync` without it stays interactive.

### Bundle runner

`scripts/change_flow_bundle.sh check|commit|retire DIR` runs the change-flow
bundle (`git-publication.md`) from a bundle directory the brief shows:
`bundle.env` (repository, worktree, branch, base OID, remote, main branch, and
the reviewed tree and message fingerprints), `paths.txt`, and
`commit-msg.txt`.

- `check` changes nothing but the objects of a temporary index and the stat
  cache `git status` refreshes; it reads the remote tip without fetching. It
  confirms the following, and stops at the first one that fails:
  - the main branch and its remote tip are the base, the main checkout is
    clean, and it holds no ignored file at a path the change adds;
  - the remote pushes to the one URL it shows, with no configured mapping,
    mirroring, tags, submodules, or push options;
  - the worktree is registered to the repository and is on the branch at the
    base;
  - its changes are exactly `paths.txt`, with nothing staged;
  - the author and committer identities are the global one;
  - the message carries no attribution trailer;
  - the tree and the message still match the reviewed fingerprints. Without
    fingerprints, it prints them and stops.
- `commit` runs `check`, then the exact-path add and one commit of a private
  copy of the reviewed message. It checks the commit's parent, tree, message,
  author, and committer, fast-forwards the main branch to that commit without
  the configured merge options, and ends by printing the push as
  `cd <repo> && git push ...` with the reviewed commit as its source.
- The push stays a separate visible command, so a runtime or project guard
  that asks before `git push` still sees it.
- `retire` confirms that the remote tip is the merged commit and that the
  branch is merged where `git branch -d` looks. It then removes the change's
  worktree, only when everything in it is a tracked file (no untracked or
  ignored file, submodule, nested repository, or per-worktree ref), and
  deletes the branch with `git branch -d`. It never uses `--force` and never
  removes another worktree.

### Committed-copy check

`scripts/verify_committed_copy.sh [DIR]` copies the checkout's tracked files
and its untracked files that the reverse whitelist admits into a private
temporary directory, commits them there, runs `make test`, and removes the
copy. `make verify-committed` runs it on the current checkout. Checks that
read Git, such as the documentation gate's tracked-file check, then see the
committed state, and a new file that `.gitignore` does not admit is missing
from the copy, so a test or link that needs it fails before the commit.

### Rule

`temporary-files.md` Lifecycle starts with the sorting step. The route row in
both adapters becomes "creating or removing temporary files, or temporary
space full or filling". The change also adds register entry W-R75, a design
map symptom, phrase tests, and a target evaluation scenario; existing
scenarios guard against regressions.

### claude-md guard

claude-md's settings keep denying `rm -rf`; in Claude Code 2.1.302 a settings
deny overrides any hook decision. The guard is
`.claude/hooks/pretool-bash-guard.mjs` plus its two template copies. It
denies a recursive force delete in its common spellings, more of them than
the old literal pattern, which stays as a floor. It makes no decision in one
case: a single literal `rm` with recursive and force flags, all of whose
operands are absolute paths inside
`/tmp/claude-<uid>/<project>/<session id>/scratchpad/` of the calling session.
The settings and the permission mode then decide.

- That scratchpad must be a real directory, reached through no symbolic link
  below `/tmp`, under a `/tmp/claude-<uid>` that only this user can write.
- Each operand's parent must resolve inside that scratchpad.
- No operand may be, lie inside (also through a symbolic link), or hold a Git
  repository, worktree, or Git directory, or hold a mount point.
- An operand may hold at most 50,000 entries.

The sanctioned form is `rm -r -f <path>`, which the settings deny does not
match. A claude-md rule, in the live repository and in the scaffold template
(both wire the hook), tells agents to use it and to hand any refused delete to
the operator.

The change follows claude-md's records (`IMPLEMENTATION-LOG.md` and the layer
review entry). Its log entry is final only after a guardrail audit that finds
nothing that must be fixed.

## Acceptance

- The six scenarios load, pass hygiene, and run under the harness.
- Each new tool has tests that fail without it:
  - guarded sync: match, unexpected drift, an unknown label (alone and beside
    a known one), and nothing to do;
  - the bundle runner, on a scratch repository with a remote: the full flow
    and a rename, plus stops on content, message, identity, staging, main or
    remote drift, a foreign worktree, and an ignored file the merge would
    overwrite;
  - the committed-copy check: excluding a file `.gitignore` does not admit and
    keeping a force-added one.
- The rule's phrase, route, and register tests pass, and its target scenario
  improves without any scenario getting worse.
- The claude-md guard makes no decision for the session's own scratch paths
  in the sanctioned form and denies every other form tested, including the
  ones its reviewers traced:
  - a symbolic link at or above the scratchpad, or one that leads into a
    repository;
  - a repository in, around, or as an operand;
  - a capitalized, decorated, quoted, brace-expanded, or line-continued
    `rm -rf`;
  - an `rm` nested in another.

  Its settings keep denying `rm -rf`, and a repeated guardrail audit finds
  nothing that must be fixed.
- The file checks and `git diff --check` pass in both repositories, `make
  test` in workspace-meta, and `node --test tests/pretool-bash-guard.test.mjs`
  in claude-md.

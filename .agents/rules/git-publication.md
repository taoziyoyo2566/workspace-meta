# Git Publication

Agent-neutral workspace rule for staging, commit, push, and remote PR creation.

## Ownership

This file owns ordinary publication review and execution. Projects add
commit-message format, required checks/CI, PR template fields, and protected
branch constraints. Integration and cleanup are separate transactions.

Read `git.md` for the current state snapshot before publication.

Working-tree edit authority never includes staging, commit, push, tag, upstream
changes, or remote PR creation.

## Checkpoint A — Result Review

After edits and validation, present:

- changed paths and outcomes;
- checks and gaps;
- exclusions/follow-ups;
- branch and dirty state.

Wait for ordinary content acceptance before preparing publication.

## Checkpoint B — One Command Bundle

Present one exact, copyable bundle in execution order containing every
applicable:

- exact-path `git add`;
- one `git commit`;
- one `git push`;
- one `gh pr create`.

Also display branch; exact staged name/status/stat; full message; identity
source/result; remote URL/name; source/destination refs; exact range/count and
divergence; force/upstream mode; checks/gaps; PR base/head/options.

Never use `git add .`, `git add -A`, or a broad path containing unreviewed
content. Review the complete staged diff.

Resolve the operator identity from host global Git configuration. Stop on unset
identity, repo-local override, or mismatch. Add no AI attribution,
`Co-Authored-By`, or `Signed-off-by` trailers.

## Execution Choices

The user may authorize the unchanged bundle once in ordinary natural language,
or run some/all commands personally and report completion. Never require
generated confirmation wording.

For agent execution, expected state transitions caused by earlier displayed
commands do not invalidate later commands. Stop when paths, content, message,
refs, range, checks, PR target, or commands drift; a hook changes/rejects
content; remote state blocks push; or a different command is needed.

For operator execution, a completion report authorizes only read-only
verification of commit, remote ref, and PR. Never rerun reported mutations.
Corrective work needs a new reviewed bundle.

After commit, inspect author, OID, subject, body, and trailers. Do not
automatically amend, bypass hooks, create a corrective commit, retry a changed
push, pull/rebase, or force.

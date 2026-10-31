# Git Publication

Agent-neutral workspace rule for staging, commit, push, and remote PR creation.

## Ownership

This file owns when publication is proposed and ordinary publication review
and execution, including the change-flow bundle. Projects add commit-message
format, required checks/CI, PR template fields, and protected branch
constraints. Integration and cleanup are separate transactions, except inside
a disclosed change-flow bundle. Release tags follow `releases.md`.

Read `git.md` for the current state snapshot before publication.

Working-tree edit authority never includes staging, commit, push, tag, upstream
changes, or remote PR creation.

Before asking the user to authorize or execute a publication operation, read
`authorization.md` and present its `Protected-Action Request Brief`. The brief
must precede the exact command bundle; this module's result review and command
bundle fields supplement the brief and do not replace it. A command-only
confirmation is insufficient for publication.

## One Proposal Per Result

A commit publishes, so propose publication only when a coherent result is
finished (`planning.md` Handoff And Closeout), when the operator asks for it,
or when another machine or agent needs the change. Put every repository change
of that result into one proposal: one brief and one approval, with a bundle
for each repository.

A routine update after publication, such as the record of an operation and its
check, a status line, or a follow-up that has since closed, gets no proposal
of its own: report it in the conversation. It enters a repository only when it
constrains later work (`planning.md` Record Findings When Confirmed), and then
with that repository's next proposal.

Red flags: "a small commit keeps the checkout clean"; "the record is stale, so
commit the update now"; "one more quick bundle".

## Checkpoint A — Result Review

After edits and validation, present:

- changed paths and outcomes;
- checks and gaps;
- exclusions/follow-ups;
- branch and dirty state.

Present Checkpoint B after it in the same message, so that one approval
accepts the content and authorizes the bundle. When the operator asks for a
content change instead, make it and present both again.

## Checkpoint B — One Command Bundle

Present one exact, copyable bundle in execution order containing every
applicable:

- exact-path `git add`;
- one `git commit`;
- one `git push`;
- one `gh pr create`.

Also display branch; exact staged name/status/stat; full message; identity
source/result; remote URL/name and whether the remote is public, and for a
public remote the host or personal details the pushed content reveals;
source/destination refs; exact range/count and divergence; force/upstream mode;
checks/gaps; PR base/head/options.

Never use `git add .`, `git add -A`, or a broad path containing unreviewed
content. Review the complete staged diff.

Resolve the operator identity from host global Git configuration. Stop on unset
identity, repo-local override, or mismatch. Add no AI attribution,
`Co-Authored-By`, or `Signed-off-by` trailers.

## Change-Flow Bundle

For a change on its own branch (`git-branches.md` Change Flow), one bundle
under one brief may cover the whole disclosed sequence:

1. the exact-path add and commit on the change branch, or for a withdrawal the
   reviewed revert there (`git-recovery.md`);
2. when the project only fast-forwards into the main branch and the main branch
   has moved past the change's base, a rebase of the change's own unpushed
   branch onto the main tip disclosed in the brief, then the change's checks
   again; the pre-rebase tip is reported as the recovery point;
3. the project's merge into the main branch, or into a declared pre-release
   channel's branch when the change goes through the channel
   (`git-integration.md`);
4. the push of that branch; after a push of the main branch, bringing the
   channel branch up to date with it and pushing it;
5. retirement of the merged change: removal of the worktree that Change Flow
   created for it, then local deletion of its branch with `git branch -d`,
   which for a change merged into a channel branch runs in a checkout of that
   branch.

A promotion (`deployment.md` Pre-Release Channels) may run as steps 3 and 4
alone, with step 3 a fast-forward or merge commit (`git-integration.md`
Pre-Release Channel Branch). Steps on a channel branch run in a checkout of it;
the bundle names that checkout, with its creation and removal when it is not a
standing one.

The bundle shows the fields of Checkpoint B and of the integration review, and
for step 5 the worktree's untracked and ignored files. It stops at the step
where anything drifts, including the main or channel tip moving after the
brief; where a rebase or merge conflicts or cannot fast-forward; where a check
fails; or where the worktree holds untracked or ignored files. Remote branch
deletion stays a separately reviewed action (`git-recovery.md`).

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

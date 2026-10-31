# Git Branches, Worktrees, And Stash

Agent-neutral workspace rule for the change flow, proportional branch-action
review, branch/worktree isolation, conditional durable workstream contracts,
and stash.

## Ownership

This file owns the change flow that every repository change follows, the
cross-project branch/worktree/stash transaction, and the conditions for a
durable workstream contract. Projects add topology, the main branch, type
prefixes, the merge route, relationships, checks, integration targets, archive
tooling, and any dedicated contract carrier and schema.
Publication/integration/recovery are separate modules.

Read `git.md` for the current state snapshot before using this module.

Before asking the user to authorize or execute a branch, worktree, or stash
operation, read `authorization.md` and present its `Protected-Action Request
Brief` before the exact action. The branch-specific fields below supplement the
brief; a command-only confirmation is insufficient for this transaction. The
one exception is the additive worktree that Change Flow reports instead.

## Change Flow

Every repository change goes through a short-lived branch:

- it starts from the main branch, except a branch for something only a
  pre-release channel has (below), and its name starts with its type from the
  project's list, for example `docs/`, `fix/`, or `feat/`, followed by its
  topic;
- the change is made and its checks run on the branch (`file-checks.md`,
  `verification.md`); then it is integrated into the main branch, or first
  into a pre-release channel's branch (below), by the project's route
  (`git-integration.md`);
- nothing is committed directly to the main branch;
- a fix follows it too; `releases.md` Fixes decides when a fix on an older
  line branches from an older verified state instead.

When the project declares a pre-release channel (`deployment.md`), a change
whose Plan or brief sends it through the channel is integrated into the
channel branch first and reaches the main branch only by promotion. Nothing is
committed directly to the channel branch either. A branch that holds something
only the channel has, such as a fix to a change still on the channel, a
withdrawal, or a resolved conflict with the main branch, starts from the pushed
channel branch, or for such a fix from the change's own branch, and returns to
the channel branch, never straight to the main branch. Merging a withdrawn
change's branch again does not bring back what the withdrawal reverted;
reverting the revert, or new commits, do.

The flow governs commits, not edits. Uncommitted edits may start in the current
checkout; before the first commit at the latest, they move to the change's
branch through a branch action that preserves the diff (Content
Non-Interference). So an operator decision is still recorded in the same turn
(`planning.md`), and authorized edits still proceed without another
confirmation (`authorization.md`).

Creating an additive worktree on a new branch from the main branch, or from a
declared pre-release channel's branch for something only the channel has, for
a change the user has already authorized, is part of that change when its path
is outside the checkout or ignored by it and the action carries no uncommitted
edits. Report the branch, its base, the worktree path, and the command when you
create it, instead of asking first. Every other branch action keeps its review,
including an in-place switch and moving uncommitted edits out of another
checkout. Commit, integration, push, and retirement of the merged branch may
then form one bundle (`git-publication.md`).

Projects name the main branch, the type prefixes, the merge route
(fast-forward, merge commit, or pull request), and the checks. A project that
works on branches in its main checkout records that choice in its Project
Facts; each in-place branch action there still goes through its review.

## Branch Action Review

Review every branch or worktree mutation, except the additive worktree that
Change Flow reports, with only the facts needed for that action:

- problem or immediate outcome;
- exact branch name and base ref/OID;
- worktree path, or the current checkout when the user requests an in-place
  action;
- exact treatment of tracked, staged, untracked, and ignored changes;
- exact command, expected ref/worktree effect, risks, recovery, exclusions, and
  completed checks or gaps;
- project topology fields that are actually applicable.

The branch action review is transaction context, not repository content. Git
refs and later reviewed commits are the normal durable evidence that the action
occurred. Worktree state and reflogs are local diagnostic evidence, not portable
handoff state. A simple action to preserve an already prepared working-tree
diff does not need speculative publication, integration, retirement, or
archival fields.

## Conditional Durable Workstream Contract

Use a durable workstream contract only when the project names a canonical
carrier and schema and at least one of these conditions is true:

- the active project explicitly requires the contract;
- the task observably needs cross-session or cross-agent handoff.

When applicable, the contract covers the durable problem/outcome,
approach/scope, acceptance, publication route, integration/closeout,
retirement, and project relationships needed by that workstream.

Reuse an existing plan or task owner when it already owns those facts. Do not
duplicate the contract or add Git transaction details to an artifact whose role
does not include them. A missing carrier never authorizes an ad hoc plan,
changelog, README, source, configuration, or other repository write. It blocks
only reliance on durable handoff, not a simple one-session branch action.

## Creation Transaction

Before creation or switching, except the additive worktree that Change Flow
reports, present the complete branch action review and the exact command in one
transaction. If a durable contract is applicable, also
identify its already-approved content, canonical carrier, and schema.

Authorization covers only the unchanged branch/worktree command and any
working-tree content change separately included in the user's task or approved
plan. It does not cover staging, publication, integration, upstream changes,
cleanup, or another branch action.

## Content Non-Interference

Creating, switching, or registering a branch/worktree does not authorize a
repository-content change. When the requested outcome is to preserve current
work on a new branch, the post-action diff must match the reviewed pre-action
diff except for cleanup the user explicitly authorized.

The first file write after branch creation comes from the user's actual task,
not from a Git registration requirement. Never create or modify a project
artifact merely to record conversation, approval text, commands, branch names,
base OIDs, or other one-time transaction metadata.

## Isolation

Prefer an additive worktree when new work should be isolated from an existing
checkout. Do not reuse, move, remove, or silently switch a worktree, and do not
carry dirty changes unless the reviewed task is specifically preserving those
changes on the new branch.

An in-place branch action is allowed only when the user explicitly requests it
and the review states the exact checkout/ref change and dirty-state treatment.
Afterward, verify both the branch/ref result and content non-interference.

## Stash

Never auto-stash or use `--autostash`. Stash push/apply/pop/drop/clear requires
a direct request or separately reviewed action identifying affected paths,
tracked/untracked/ignored inclusion, message/identity, and restore/removal
effect. Do not use a stash as undocumented task storage.

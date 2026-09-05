# Git Branches, Worktrees, And Stash

Agent-neutral workspace rule for proportional branch-action review,
branch/worktree isolation, conditional durable workstream contracts, and stash.

## Ownership

This file owns the cross-project branch/worktree/stash transaction and the
conditions for a durable workstream contract. Projects add topology,
relationships, checks, integration targets, archive tooling, and any dedicated
contract carrier and schema. Publication/integration/recovery are separate
modules.

Read `git.md` for the current state snapshot before using this module.

Before asking the user to authorize or execute a branch, worktree, or stash
operation, read `authorization.md` and present its `Protected-Action Request
Brief` before the exact action. The branch-specific fields below supplement the
brief; a command-only confirmation is insufficient for this transaction.

## Branch Action Review

Review every branch or worktree mutation with only the facts needed for that
action:

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

Before creation or switching, present the complete branch action review and the
exact command in one transaction. If a durable contract is applicable, also
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

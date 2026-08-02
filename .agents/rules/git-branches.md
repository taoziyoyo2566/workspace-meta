# Git Branches, Worktrees, And Stash

Agent-neutral workspace rule for branch task contracts, additive worktrees,
existing branch/worktree changes, and stash.

## Ownership

This file owns the complete cross-project branch task contract and
branch/worktree/stash transaction. Projects add topology, relationship,
lifecycle, persistence location, checks, integration target, and archive
tooling. Publication/integration/recovery are separate modules.

Read `git.md` for the current state snapshot before using this module.

Before asking the user to authorize or execute a branch, worktree, or stash
operation, read `authorization.md` and present its `Protected-Action Request
Brief` before the exact action. The branch contract and state fields below
supplement the brief; a command-only confirmation is insufficient for this
transaction.

## Required Branch Task Contract

Every branch that is actually created has a reviewed contract containing:

| Field | Required content |
|---|---|
| Problem/outcome | problem solved and observable result |
| Approach/scope | intended solution, in/out scope, prerequisites, exclusions |
| Acceptance | checks/evidence and pass condition |
| Publication | logical commit grouping, review/push/PR route and base/head target |
| Integration/closeout | completion boundary, integration route, remaining-work owner |
| Retirement | archive/retain/remove treatment after integration/cancellation |
| Branch action | branch name, exact base ref/OID, worktree path, existing-change treatment |

All fields remain required. A root feature records full detail; a contained
child may satisfy each field concisely. Avoid unnecessary small branches rather
than omitting their contract.

The contract describes later publication, integration, and retirement; it does
not authorize those mutations.

## One Creation Review

Before creation, present in one review transaction:

- the complete copyable contract text;
- exact branch name, base ref/OID, and worktree path;
- existing-change treatment and project topology fields;
- exact additive branch/worktree command.

One authorization covers that unchanged additive command and immediate
persistence of the reviewed contract. It does not cover staging, publication,
integration, upstream changes, cleanup, or a different branch action.

After worktree creation, the reviewed contract is the first file write. Publish
it with the first logical implementation unit; do not create a
registration-only commit, activation PR, or successor branch.

If a session stops after creation but before persistence, bootstrap reports
`branch exists, contract missing`, blocks implementation, and restores the
already reviewed contract before continuing.

## Additive Isolation

A new branch/worktree must not switch an existing checkout, reuse/move/remove a
worktree, carry dirty changes, or mutate an existing branch. State-displacing
actions on an existing branch/worktree require a separately reviewed exact
command and effect.

## Stash

Never auto-stash or use `--autostash`. Stash push/apply/pop/drop/clear requires
a direct request or separately reviewed action identifying affected paths,
tracked/untracked/ignored inclusion, message/identity, and restore/removal
effect. Do not use a stash as undocumented task storage.

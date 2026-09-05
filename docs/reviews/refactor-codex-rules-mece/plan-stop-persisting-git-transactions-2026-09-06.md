# Stop Persisting One-Time Git Transactions As Project Content

## Purpose

Correct the shared branch rule so a one-time request to create or switch a
branch remains a Git transaction instead of becoming permanent project
content. Branch creation must not modify an already reviewed working-tree diff
unless the user separately authorized that content change.

## Scope

- Replace the unconditional branch-task-contract model with a proportional
  branch-action review.
- Keep exact branch, base, command, existing-change treatment, risk, recovery,
  and exclusions in the protected-action review.
- Make a durable workstream contract conditional on an actual cross-session
  need and an existing project-declared canonical carrier.
- Remove the shared requirements that the contract be the first file write,
  enter the first implementation commit, or block work when absent.
- Add regression assertions for content non-interference and conditional
  persistence.
- Record the portable correction without copying project-specific branch
  names, commands, or application-plan content into workspace governance.

## Out Of Scope

- Changing project branch topology, commit format, merge policy, or retirement
  tooling.
- Weakening pre-mutation inspection, protected-action review, or publication
  checkpoints.
- Installing updated rules into host configuration, staging, committing,
  pushing, or creating a pull request.
- Modifying nested project repositories as part of the workspace-meta change.

## Current-State Gap

The shared rule requires every branch to carry a complete lifecycle contract
and then requires immediate persistence after worktree creation. It also says
projects supply the persistence location. In a project without such a carrier,
the rule mandates a write but provides no authorized owner. That pressure can
pollute a plan, changelog, README, source file, or configuration with ephemeral
Git transaction data.

The requirement is additionally wrong-shaped for a branch whose sole purpose
is to preserve an already prepared working-tree diff. Git refs and commits are
the durable evidence for that operation; creating more repository content
changes the result the user asked to preserve.

## Changes

1. Rewrite `.agents/rules/git-branches.md` around two explicit cases:
   - every branch mutation receives a concise branch-action review;
   - a durable workstream contract exists only when the task needs one and the
     active project names its canonical carrier.
2. State that branch mechanics do not authorize repository-content changes and
   that save-the-current-diff tasks preserve the diff except for explicitly
   authorized cleanup.
3. Remove global first-write, first-publication, and contract-missing bootstrap
   requirements. A project may add them only together with a dedicated carrier
   and schema.
4. Add a new provenance entry to `feedback-register.md` that records the
   generalized failure and correction, without embedding one-time project
   transaction details.
5. Synchronize the rule-ownership summaries that describe the project delta.
6. Extend `tests/test_sync_codex_config.py` to assert the new positive recipe
   and reject the former unconditional persistence phrases.
7. Add a round changelog after implementation and verification.

## Acceptance

- The shared rule never instructs an agent to create or modify project content
  merely because a branch was created.
- Simple branch actions do not require publication, integration, retirement,
  or archival fields.
- Durable contracts are conditional on observable cross-session need plus a
  project-declared canonical carrier.
- The existing pre-mutation inspection, exact action review, dirty-work
  preservation, stash boundaries, and publication separation remain intact.
- `make test`, shell syntax checks, Python compilation, generated-format
  parsing exercised by the repository tests, isolated bootstrap idempotency,
  and `git diff --check` pass, or any unavailable check is reported as a gap.

## Risks And Recovery

Over-correction could remove useful safety review or make long-lived work lose
handoff state. The rewrite therefore retains the protected branch-action
review and allows project-declared durable workstream carriers. If verification
shows an authorization or routing regression, stop and revert only the
workspace-meta working-tree changes from this task after a separately reviewed
recovery action.

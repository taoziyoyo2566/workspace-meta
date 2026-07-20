# Git Integration And Retirement

Agent-neutral workspace rule for merge/integration, terminal evidence, and the
boundary before branch/worktree retirement.

## Ownership

This file owns the generic integration transaction and post-integration
separation. Projects add topology, permitted routes, prerequisites,
children/dependents, release fields, required CI, and archive tooling.

Read `git.md` for the current state snapshot before integration.

## Integration Review

Integration is separate from publication. Before execution present:

- source/target refs and exact tips;
- merge base, divergence, exact commits, and net diff;
- integration mode and conflict prediction;
- dirty/index/worktree state;
- required local/remote checks and gaps;
- project topology/prerequisite/child/dependent/release fields;
- excluded follow-ups and post-integration actions.

Changed tips, base, commits/diff, mode, state, checks, conflict result, or
project fields expire the authorization.

One integration authorization excludes conflict resolution, push, tag, ref
deletion, branch/worktree cleanup, archive, downstream integration, and
post-merge commits. Inspect and report the resulting target before proposing a
follow-up.

## Terminal Evidence

PR/Git metadata is normally terminal evidence that a reviewed source reached
its target. Do not create a branch/PR solely to record the preceding merge.

If living truth materially needs correction, use the next normal target-based
owner. If premature integration left required work, use one bounded correction
with a named owner rather than recursive activation/closeout branches.

## Retirement Boundary

Branch/worktree retirement or archival is a separate reviewed action after
integration/cancellation. The original branch contract and integration
authorization do not pre-authorize cleanup. Apply the project's archive,
retention, and topology rules plus `git-recovery.md` when deletion is involved.

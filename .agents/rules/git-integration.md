# Git Integration And Retirement

Agent-neutral workspace rule for merge/integration, terminal evidence, and the
boundary before branch/worktree retirement.

## Ownership

This file owns the generic integration transaction, post-integration
separation, and keeping a pre-release channel's branch up to date. Its ordinary
case is merging a change branch into the main branch, or into a declared
pre-release channel's branch, under the change flow (`git-branches.md`). Projects add topology, permitted
routes, prerequisites, children/dependents, required CI, and archive tooling;
release fields follow `releases.md`.

Read `git.md` for the current state snapshot before integration.

Before asking the user to authorize or execute an integration operation, read
`authorization.md` and present its `Protected-Action Request Brief` before the
exact merge or integration operation. The review fields below supplement the
brief; a command-only confirmation is insufficient for integration.

## Integration Review

Integration is separate from publication. Before execution present:

- source/target refs and exact tips;
- merge base, divergence, exact commits, and net diff;
- integration mode and conflict prediction;
- dirty/index/worktree state;
- required local/remote checks and gaps;
- project topology/prerequisite/child/dependent fields, and release fields
  (`releases.md`);
- for a project with a pre-release channel, whether the source holds anything
  only the channel has (`git-branches.md` Change Flow);
- excluded follow-ups and post-integration actions.

Changed tips, base, commits/diff, mode, state, checks, conflict result, or
project fields expire the authorization.

One integration authorization excludes conflict resolution, push, tag, ref
deletion, branch/worktree cleanup, archive, downstream integration, and
post-merge commits. A change-flow bundle (`git-publication.md`) may include the
push, bringing a pre-release channel's branch up to date, and the retirement of
the merged branch it discloses. Inspect and report the resulting target before
proposing a follow-up.

## Pre-Release Channel Branch

When the project declares a pre-release channel (`deployment.md`):

- every integration into or out of the channel branch, whether a change, an
  update from the main branch, or a promotion, is a fast-forward or a merge
  commit, never a squash or a rebase, since containing the main tip, promotion,
  and a lasting withdrawal all rely on ancestry;
- after each push to the main branch, bring the channel branch up to date with
  it: a fast-forward when the channel branch has no commit that the main branch
  lacks, otherwise a merge commit; a conflict is resolved on a short-lived
  branch (`git-branches.md` Change Flow);
- a promotion is an integration into the main branch, by fast-forward or merge
  commit even where the project's route squashes, from a source that meets the
  promotion condition in `deployment.md` Pre-Release Channels.

## Terminal Evidence

PR/Git metadata is normally terminal evidence that a reviewed source reached
its target. Do not create a branch/PR solely to record the preceding merge.

If living truth materially needs correction, use the next normal target-based
owner. If premature integration left required work, use one bounded correction
with a named owner rather than recursive activation/closeout branches.

## Retirement Boundary

Branch/worktree retirement or archival is a separate reviewed action after
integration/cancellation, or the disclosed last step of a change-flow bundle.
The branch action review, any durable workstream contract, and integration
authorization do not pre-authorize cleanup. Apply the project's archive,
retention, and topology rules plus `git-recovery.md` when deletion is involved.

Before retiring a branch or worktree, confirm that no instance runs a commit
that only it contains, unless a release tag keeps that commit (`deployment.md`,
`releases.md`).

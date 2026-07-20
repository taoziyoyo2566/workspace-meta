# Git Inspection And State Safety

Agent-neutral workspace rule for Git inspection, freshness, and the state
snapshot required before any Git mutation.

## Ownership

This file owns read-only classification, the bounded freshness exception, and
preservation of unknown work. Task-specific mutation procedures live in:

- `git-branches.md`
- `git-publication.md`
- `git-integration.md`
- `git-recovery.md`

Projects own topology, commit format, required checks/CI, and archive tooling.

## Inspection

Run inspection-only Git commands without conversational confirmation. A command
is read-only only when it cannot modify the working tree, index, refs, remotes,
configuration, credentials, or external state.

Typical examples: `status`, `log`, `show`, `diff`, `diff --check`, `grep`,
`branch --list`, `merge-base`, `merge-tree`, `rev-parse`, `rev-list`,
`ls-files`, and `ls-tree`.

Plain `git fetch <canonical-remote>` is the only generally pre-authorized ref
mutation. Use it for a stated freshness check without prune, force, custom
refspec, or an attached merge/rebase/checkout/pull/push. Projects name their
canonical remote.

## Pre-Mutation State

Before any branch/worktree/stash/publication/integration/recovery mutation,
inspect:

- current branch and exact HEAD;
- working-tree and index state, including untracked paths;
- complete worktree map;
- relevant local/remote refs and divergence.

Never reset, clean, overwrite, switch away from, move, hide, or delete
unrecognized work merely to simplify the task.

Technical permission never substitutes for semantic review under the
task-specific module.

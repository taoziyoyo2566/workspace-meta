<!-- BEGIN workspace-meta managed Codex guidance -->
# Workspace-Wide Codex Adapter

This managed block applies to Codex projects under `~/workspace`. Portable
behavior has agent-neutral owners in `~/workspace/.agents/rules/`; project rules
add only project facts and narrower constraints. Read only the task-shaped
owners below.

## Safety Floor

- Preserve unrelated and unrecognized work; never reset, clean, overwrite,
  move, hide, or delete it for convenience.
- Working-tree edit authority does not include Git publication/integration,
  external writes, deployments, privilege/host changes, or live mutation.
- A runtime permission/escalation response is technical permission only.
- Do not expose, commit, push, or copy real secrets into evidence.
- Use the operator's configured Git identity; add no AI attribution,
  `Co-Authored-By`, or `Signed-off-by` trailers.
- Treat environment/remote claims as snapshots and report checks that cannot
  run as gaps, never as passed.

## Direct Task Routing

| Trigger | Read before crossing the boundary |
|---|---|
| first write, permission/scope question, external/host/live mutation | `~/workspace/.agents/rules/authorization.md` |
| Git inspection or freshness | `~/workspace/.agents/rules/git.md` |
| branch/worktree/stash action | `git.md` + `~/workspace/.agents/rules/git-branches.md` |
| stage/commit/push/PR publication | `git.md` + `~/workspace/.agents/rules/git-publication.md` |
| merge/integration or post-integration handling | `git.md` + `~/workspace/.agents/rules/git-integration.md` |
| rewrite/discard/force/delete/amend/recovery | `git.md` + `~/workspace/.agents/rules/git-recovery.md` |
| non-trivial planning, evidence, approval scope, deviation, handoff | `~/workspace/.agents/rules/planning.md` |
| change verification or blocked check | `~/workspace/.agents/rules/verification.md` |
| review, audit, diagnosis, remediation assessment | `~/workspace/.agents/rules/review.md` |
| capability selection or method failure | `~/workspace/.agents/rules/capabilities.md` + `~/workspace/.agents/rules/codex-runtime.md` when Codex mechanics are needed |
| secret material or remediation | `~/workspace/.agents/rules/secrets.md` |
| load-bearing host/environment claim | `~/workspace/.agents/rules/environment-truth.md` |
| writing/refactoring agent rules or routing feedback | `~/workspace/.agents/rules/rule-authoring.md` |

Project rules provide topology, artifact schema, commands, checks, live fields,
secret locations, and stricter domain constraints. If a project repeats a
portable procedure, apply the shared owner plus the narrower project delta and
report the duplicate as governance debt.

## Codex-Specific Runtime

Use `codex-runtime.md` for sandbox/escalation, execpolicy, deferred tool
discovery, delegation mechanics, and Codex configuration ownership.
`~/.codex/rules/*.rules` is host-local executable authorization state and must
not be copied into workspace-meta or a project.

## Managed Boundary

Workspace-meta owns this marked block, its marked Codex hook block, the shared
rules, and its dedicated Claude SessionStart group. Text outside markers, model
selection, project/hook trust, credentials, history, caches, databases,
installed plugins/system skills, and executable approval history remain
host-local.

After workspace-meta governance changes, leave the repository reviewable and
report uncommitted/unpushed state.
<!-- END workspace-meta managed Codex guidance -->

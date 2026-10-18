<!-- BEGIN workspace-meta managed Codex guidance -->
# Workspace-Wide Codex Adapter

This managed block applies to Codex projects under `~/workspace`. Portable
behavior has agent-neutral owners in `~/workspace/.agents/rules/`; project rules
add only project facts and narrower constraints. Read only the task-shaped
owners below.

## Safety Floor

Canonical sources: `git.md`, `authorization.md`, `git-publication.md`,
`secrets.md`, `environment-truth.md`, `reasoning.md`, `file-checks.md`, and
`verification.md`.

- Preserve unrelated and unrecognized work; never reset, clean, overwrite,
  switch away from, move, hide, or delete it for convenience.
- Working-tree edit authority does not include Git publication/integration,
  external writes, deployments, privilege/host changes, or live mutation.
- A runtime permission/escalation response is technical permission only.
- Do not expose, commit, push, or copy real secrets into evidence.
- Use the operator's configured Git identity; add no AI attribution,
  `Co-Authored-By`, or `Signed-off-by` trailers.
- Validate load-bearing premises proportionally; keep technical conclusions
  distinct from assumptions and operator decisions.
- Before calling a created or changed file done, including one changed in a
  step you direct, run its file-type checks.
- Treat environment/remote claims as snapshots and report checks that cannot
  run as gaps, never as passed.

## Direct Task Routing

Before starting work on a request, read it for its goal, what done means, and
the similar problems it stands for, as deeply as the request needs; ask only
what would redirect the work, and not while the operator is away
(`~/workspace/.agents/rules/requests.md`).

| Trigger | Read before crossing the boundary |
|---|---|
| first write, permission/scope question, external/host/live mutation, privilege elevation even for a read, a runtime denial, an approval request | `~/workspace/.agents/rules/authorization.md` |
| Git inspection or freshness | `~/workspace/.agents/rules/git.md` |
| branch/worktree/stash action, or starting a repository change | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/git.md` + `~/workspace/.agents/rules/git-branches.md` |
| stage/commit/push/PR publication | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/git.md` + `~/workspace/.agents/rules/git-publication.md` |
| merge/integration or post-integration handling | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/git.md` + `~/workspace/.agents/rules/git-integration.md` |
| rewrite/discard/force/delete/amend/recovery | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/git.md` + `~/workspace/.agents/rules/git-recovery.md` |
| release, version tag or number, rollback target, or fixing a released version | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/git.md` + `~/workspace/.agents/rules/releases.md` |
| deploying, what may serve users, a temporary deployment, or an instance outside the inventory | `~/workspace/.agents/rules/authorization.md` + `~/workspace/.agents/rules/deployment.md` |
| starting work on a request: a reported problem, a correction, an idea, a change, or a need described through examples; asking the operator or proceeding on assumptions | `~/workspace/.agents/rules/requests.md` |
| load-bearing premise validation, conflicting evidence, independent technical judgment, competing explanations, or diagnostic method | `~/workspace/.agents/rules/reasoning.md` |
| non-trivial planning, a new capability's design or plan, starting an investigation, comparison of options, or experiment, a verified finding that affects other work, an operator decision on a workstream, reporting its status from memory or an earlier session, evidence, approval scope, deviation, handoff | `~/workspace/.agents/rules/planning.md` |
| implementation, configuration, refactoring, or artifact-structure change | `~/workspace/.agents/rules/implementation.md` |
| project documentation authoring, restructuring, or lifecycle governance, or a project without an entry file for the runtime in use | `~/workspace/.agents/rules/documentation.md` + `~/workspace/.agents/rules/codex-runtime.md` for Codex's entry files |
| a created or changed file before it is called done, handed over, committed, or deployed | `~/workspace/.agents/rules/file-checks.md` |
| change verification or blocked check | `~/workspace/.agents/rules/verification.md` |
| review, audit, diagnosis, remediation assessment, or reporting which problems exist | `~/workspace/.agents/rules/review.md` |
| proposing a procedure or practice, or reporting a handled problem | `~/workspace/.agents/rules/problem-follow-up.md` |
| capability selection, method failure, slow or costly work, or a command for the user to run | `~/workspace/.agents/rules/capabilities.md` + `~/workspace/.agents/rules/codex-runtime.md` when Codex mechanics are needed |
| secret material or remediation | `~/workspace/.agents/rules/secrets.md` |
| creating temporary files, or temporary space full or filling | `~/workspace/.agents/rules/temporary-files.md` |
| load-bearing host/environment claim | `~/workspace/.agents/rules/environment-truth.md` |
| writing/refactoring agent rules, routing feedback, or the operator correcting how you work or stating a preference about it | `~/workspace/.agents/rules/rule-authoring.md` |
| delegating work to subagents or a workflow | `~/workspace/.agents/rules/capabilities.md` + `~/workspace/.agents/rules/codex-runtime.md` when Codex mechanics are needed |

Project rules provide topology, artifact schema, commands, checks, live fields,
secret locations, and stricter domain constraints. If a project repeats a
portable procedure, apply the shared owner plus the narrower project delta and
report the duplicate as governance debt.

## Codex-Specific Runtime

Use `codex-runtime.md` for sandbox/escalation, execpolicy, deferred tool
discovery, delegation mechanics, project entry files, and Codex configuration
ownership.
`~/.codex/rules/*.rules` is host-local executable authorization state and must
not be copied into workspace-meta or a project.

## Managed Boundary

Workspace-meta owns this marked block, its marked Codex hook block, the shared
rules, and, in every Claude config dir the operator uses, its dedicated Claude
SessionStart group, marker-bearing status line, and managed skills. Text
outside markers, model selection, project/hook trust, credentials,
history, caches, databases, installed plugins/system skills, and executable
approval history remain host-local.

After workspace-meta governance changes, leave the repository reviewable and
report uncommitted/unpushed state.
<!-- END workspace-meta managed Codex guidance -->

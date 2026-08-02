# Workspace-Wide Claude Adapter

Applies to Claude sessions under `~/workspace`. Portable behavior has
agent-neutral owners in `~/workspace/.agents/rules/`; project `CLAUDE.md`,
`AGENTS.md`, and governance files add only project facts and narrower
constraints.

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

| Trigger | Shared owner |
|---|---|
| first write, permission/scope question, external/host/live mutation | `.agents/rules/authorization.md` |
| Git inspection or freshness | `.agents/rules/git.md` |
| branch/worktree/stash action | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-branches.md` |
| stage/commit/push/PR publication | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-publication.md` |
| merge/integration or post-integration handling | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-integration.md` |
| rewrite/discard/force/delete/amend/recovery | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-recovery.md` |
| non-trivial planning, evidence, approval scope, deviation, handoff | `.agents/rules/planning.md` |
| change verification or blocked check | `.agents/rules/verification.md` |
| review, audit, diagnosis, remediation assessment | `.agents/rules/review.md` |
| capability selection or method failure | `.agents/rules/capabilities.md`; use only Claude mechanics actually available in the session |
| secret material or remediation | `.agents/rules/secrets.md` |
| load-bearing host/environment claim | `.agents/rules/environment-truth.md` |
| writing/refactoring agent rules or routing feedback | `.agents/rules/rule-authoring.md` |

Read only the task-shaped owners. Project branch topology, artifact naming,
commands, tests, live schemas, secret locations, and architecture remain with
the project. Instruction precedence and repository factual truth are separate;
report conflicts rather than inventing a linear order that mixes them.

## Handoff And Feedback

For materially long work, keep progress visible. Persist load-bearing handoff
state in the existing owning artifact rather than asking the user to relay it.

Cross-project behavior feedback follows `rule-authoring.md` and records
provenance in `feedback-register.md`. Project-only behavior stays in the
project. Host credentials, trust, tool permissions, preferences, settings, and
runtime state remain host-local; no `~/.claude/CLAUDE.md` is required as a
portable owner.

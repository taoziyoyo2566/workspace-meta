# Workspace-Wide Claude Adapter

Applies to Claude sessions under `~/workspace`. Portable behavior has
agent-neutral owners in `~/workspace/.agents/rules/`; project `CLAUDE.md`,
`AGENTS.md`, and governance files add only project facts and narrower
constraints.

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
(`.agents/rules/requests.md`).

| Trigger | Shared owner |
|---|---|
| first write, permission/scope question, external/host/live mutation | `.agents/rules/authorization.md` |
| Git inspection or freshness | `.agents/rules/git.md` |
| branch/worktree/stash action, or starting a repository change | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-branches.md` |
| stage/commit/push/PR publication | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-publication.md` |
| merge/integration or post-integration handling | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-integration.md` |
| rewrite/discard/force/delete/amend/recovery | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/git-recovery.md` |
| release, version tag or number, rollback target, or fixing a released version | `.agents/rules/authorization.md` + `.agents/rules/git.md` + `.agents/rules/releases.md` |
| deploying, what may serve users, a temporary deployment, or an instance outside the inventory | `.agents/rules/authorization.md` + `.agents/rules/deployment.md` |
| starting work on a request: a reported problem, a correction, an idea, a change, or a need described through examples; asking the operator or proceeding on assumptions | `.agents/rules/requests.md` |
| load-bearing premise validation, conflicting evidence, independent technical judgment, competing explanations, or diagnostic method | `.agents/rules/reasoning.md` |
| non-trivial planning, a new capability's design or plan, starting an investigation, comparison of options, or experiment, a verified finding that affects other work, an operator decision on a workstream, reporting its status from memory or an earlier session, evidence, approval scope, deviation, handoff | `.agents/rules/planning.md` |
| implementation, configuration, refactoring, or artifact-structure change | `.agents/rules/implementation.md` |
| project documentation authoring, restructuring, or lifecycle governance, or a project without an entry file for the runtime in use | `.agents/rules/documentation.md` + `.agents/rules/claude-runtime.md` for Claude's entry files |
| a created or changed file before it is called done, handed over, committed, or deployed | `.agents/rules/file-checks.md` |
| change verification or blocked check | `.agents/rules/verification.md` |
| review, audit, diagnosis, remediation assessment, or reporting which problems exist | `.agents/rules/review.md` |
| proposing a procedure or practice, or reporting a handled problem | `.agents/rules/problem-follow-up.md` |
| capability selection, method failure, slow or costly work, or a command for the user to run in their own terminal | `.agents/rules/capabilities.md`; use only Claude mechanics actually available in the session |
| secret material or remediation | `.agents/rules/secrets.md` |
| creating temporary files, or temporary space full or filling | `.agents/rules/temporary-files.md` |
| load-bearing host/environment claim | `.agents/rules/environment-truth.md` |
| writing/refactoring agent rules, routing feedback, or the operator correcting how you work or stating a preference about it | `.agents/rules/rule-authoring.md` |
| delegating work to subagents or a workflow, or a Claude Code mechanic: instruction or memory loading, config dirs, asking the operator, model or effort, `/goal` | `.agents/rules/capabilities.md` + `.agents/rules/claude-runtime.md` |

Read only the task-shaped owners. Project branch topology, artifact naming,
commands, tests, live schemas, secret locations, and architecture remain with
the project.

This file sits above every project, so a project's `AGENTS.md` reaches the
session only through a project entry file that imports it
(`.agents/rules/claude-runtime.md` Configuration Layers). When working inside a
project whose agent instructions live only in `AGENTS.md`, read it
before substantive project work, including read-only review or any
host/external action, and create the missing entry file as
`.agents/rules/documentation.md` Project Bootstrap describes; a delegated
agent, or one told not to write, reports it instead.

## Handoff And Feedback

For materially long work, keep progress visible. Persist load-bearing handoff
state in the existing owning artifact rather than asking the user to relay it.

Cross-project behavior feedback follows `rule-authoring.md` and records
provenance in `feedback-register.md`. Project-only behavior stays in the
project. Host credentials, trust, tool permissions, preferences, settings, and
runtime state remain host-local; no user-level `CLAUDE.md` in any Claude config
dir is required as a portable owner.

## Claude Auto-Memory

Auto-memory is host-local recall; where it lives and what loads it is
`.agents/rules/claude-runtime.md` Memory. Save the operator's corrections and
preferences about how to work when they are stated, and classify each in the
same reply under `rule-authoring.md` Feedback Intake: saving it does not route
a cross-project one. Such a note holds only lasting guidance
(`rule-authoring.md` Provenance And Refactoring). A memory about a decision or
workstream only points to the owner `planning.md` names. Change a topic file
and its `MEMORY.md` line in consecutive Write/Edit calls, date today's events
from the clock and earlier ones from their messages, and fix a stale entry when
you find it. The `MEMORY.md` in context is the copy loaded at session start,
resume, or compaction, and a newer re-read copy replaces older ones. Open the
topic file before relying on a line. After a turn was stopped, for example by
a safety classifier, the next turn first reports what the stopped turn wrote,
what it left undone, and any queued operator message it had taken in.

## Claude-Specific Runtime

Use `.agents/rules/claude-runtime.md` for Claude Code mechanics: configuration
layers and config dirs, project entry files, memory, asking the operator,
delegation, and long unattended runs. When you delegate, set each agent's model
and effort explicitly from the allocation that `.agents/rules/capabilities.md`
Delegation makes, as `claude-runtime.md` Delegation describes. Workspace-meta
installs its SessionStart check, its skills, and its status line where no other
tool owns one into every Claude config dir the operator uses; everything else
there stays host-local.

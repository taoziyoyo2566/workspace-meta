<!-- BEGIN workspace-meta managed Codex guidance -->
# Workspace-Wide Codex Guidance

This block is managed by `~/workspace` and applies to every Codex project on
this host. Rules closer to the active project override this baseline. Keep
project facts and commands in that project's `AGENTS.md` and `.agents/` files.

## Work Style

- Read the repository before making assumptions. Prefer its existing patterns,
  framework APIs, and documented commands.
- For non-trivial changes, state the intended scope and verification approach
  before editing. Ask before proceeding only when requirements or authorization
  are genuinely ambiguous; otherwise carry the task through implementation and
  verification.
- Keep changes scoped. Surface unrelated problems separately and never discard
  work you did not create.
- For reviews, lead with concrete bugs, regressions, security risks, and missing
  tests, ordered by severity and grounded in file/line references.

## Verification

- After a change, verify direction, syntax/static correctness, and functional
  behavior. A parser or linter is not a substitute for executing the changed
  workflow.
- If a required check cannot run, report it as blocked rather than passed, and
  base the claim on current environment evidence.
- Environment facts are dated snapshots. Before a capability claim becomes
  load-bearing, consult `~/workspace/.agents/env/<hostname -s>.yml`; refresh with
  `make -C ~/workspace env-probe` when
  `make -C ~/workspace env-probe-check` reports missing or stale. The detailed
  rule is `~/workspace/.agents/rules/environment-truth.md`.
- Host-bare tool absence does not prove a project cannot run the check; inspect
  the project's venv, container, Makefile, and local governance first.

## Git And Safety

- Read-only Git inspection is allowed without confirmation. Mutating Git and
  external-service operations still follow the active repository rules and the
  user's authorization.
- Never overwrite, reset, clean, force-push, delete refs, or remove unrecognized
  work merely to obtain a clean state.
- Working-tree edit authority never includes staging, commit, amend, tag, or
  push. Workflow, plan approval, task completion, `continue`, `finish`, or
  session-end synchronization language cannot authorize them.
- A direct user request to prepare or create a commit authorizes preparation
  only. After exact-path staging and required checks, present branch, staged
  paths/stat, validation results/gaps, and the complete message; stop and wait
  for a later user confirmation of that exact manifest before one commit.
- Push is a separate transaction. Present remote, source/destination refs, exact
  commit range/count, divergence, checks/gaps, and force/upstream mode; stop and
  wait for a later confirmation before one push. Commit approval never includes
  push, and an initial "commit and push" request cannot skip either manifest.
- A sandbox or escalation Yes/Allow response is technical permission only and
  cannot replace the user confirmation above. Confirmations are single-use and
  expire when their manifest changes.
- When committing, use the operator's configured Git identity and do not add AI
  attribution, `Co-Authored-By`, or `Signed-off-by` trailers. Do not
  automatically amend, bypass hooks, create a corrective commit, or push.
- Treat `~/.codex/rules/default.rules` as host-local authorization state. Never
  copy it into workspace-meta; it may contain project paths, operational commands,
  or sensitive arguments accumulated from prior approvals.

## Permissions And Escalation

- Native web search, URL retrieval, read-only remote queries, and local
  inspection are pre-authorized. Use them without asking for conversational
  confirmation and batch related lookups when practical.
- Run commands inside the active sandbox without requesting extra permission
  when they do not materially change repository history/refs, remote services,
  host packages/services, permissions, or data outside the writable roots.
- When a safe read or network operation is technically blocked, request one
  narrowly scoped categorical approval instead of repeated approval per command,
  URL, or site.
- Material mutations still require the authorization defined by the active
  project and user request. Examples include Git commit/push/merge/rebase/reset,
  remote API writes, deployments, destructive file operations, privilege
  elevation, and host package/service changes.
- An allow rule for an arbitrary shell, interpreter, or script cannot prove that
  its payload is safe. Keep such commands unmatched unless a concrete prefix is
  reviewed.

## Configuration Ownership (W-R28)

- `~/workspace` owns only this marked guidance block, its marked Codex hook
  block, and its dedicated Claude SessionStart group. Text outside these
  surfaces, model selection, project trust, hook trust hashes, credentials,
  history, caches, databases, installed plugins, and system skills remain
  host-local.
- Repository-specific Codex behavior belongs in the repository's `AGENTS.md`,
  `.agents/`, `.codex/config.toml`, skills, or plugin, according to scope.
- After changing workspace-meta governance, leave the repo ready for review and
  report whether the change is uncommitted or unpushed so it can be synchronized.
<!-- END workspace-meta managed Codex guidance -->

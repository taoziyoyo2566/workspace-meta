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
- Do not create commits or push unless the user or active project workflow asks
  for it. When committing, use the operator's configured Git identity and do not
  add AI attribution, `Co-Authored-By`, or `Signed-off-by` trailers.
- Treat `~/.codex/rules/default.rules` as host-local authorization state. Never
  copy it into workspace-meta; it may contain project paths, operational commands,
  or sensitive arguments accumulated from prior approvals.

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

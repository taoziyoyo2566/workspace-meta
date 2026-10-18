# Changelog: project bootstrap, Claude config dirs, and the layer model

- **Date**: 2026-10-18
- **Plan**: [plan-project-bootstrap-2026-10-18.md](plan-project-bootstrap-2026-10-18.md)
- **Delivery state**: content-complete and verified on branch
  `feat/claude-native-governance`, uncommitted. When this record was written,
  none of these steps had run: commit, merge into `main`, push, `make sync` on
  each host, and a release tag.

## Outcome

A Git project under `~/workspace/projects/` that the operator works on with an
agent now gets that agent's entry files without being set up by hand, and each
class of agent configuration has one owning layer.

- **Project Bootstrap** (`documentation.md`, W-R73): `AGENTS.md` is the
  canonical owner and every other runtime gets a thin importing adapter, beside
  the root owner and beside each subdirectory's own owner file. A clone of
  someone else's repository gets only an excluded local entry file; a linked
  worktree without entry files of its own is bootstrapped through its main
  checkout; a directory that is not a Git repository only on request. Only the
  session in conversation with the operator writes; a delegated or no-write
  task reports. Nothing is overwritten or committed.
- **Standing authority**: `authorization.md` lists creating a missing entry
  file among the work that proceeds without another confirmation, also during
  a read-only task, unless the operator or the brief forbids writes;
  `review.md` names it as the one exception to its read-only default.
- **Runtime mechanics**: `claude-runtime.md` Configuration Layers and Project
  Entry Files (why Claude never read project `AGENTS.md` files here, the
  `@AGENTS.md` and `@../AGENTS.md` imports, `CLAUDE.local.md` in a foreign clone,
  how `/init` output is folded into `AGENTS.md`, what Claude Code creates on its
  own); `codex-runtime.md` Project Entry Files (no import in Codex, so a
  `CLAUDE.md` owner gets a proposed move, never an adapter).
- **Readiness check**: the SessionStart evaluator reports a real Git project
  root without a loadable entry file to the operator and the agent, with the
  Codex owner-move variant, and stays silent when healthy.
- **Every Claude config dir**: one sync run converges the SessionStart group
  and the managed skills into each dir of the colon-separated
  `CLAUDE_CONFIG_DIRS`, discovered when unset (copies and backups skipped and
  listed); a status line or skill without the workspace-meta marker belongs to
  another owner and is kept.
- **`project-bootstrap` skill**: runs the survey and writes the files in that
  order of checks.
- **Layer model**: `README-agents.md` holds five layers (organization-managed,
  host user per config dir, workspace, project, project-local), each class of
  content with one owner.
- **Adapters and corrections**: both adapters route the new triggers; the
  Claude adapter's statements that Claude loads `CLAUDE.md` rather than
  `AGENTS.md`, and that subagents receive `MEMORY.md`, were wrong and are
  replaced. The answer to "which other Claude artifacts exist" is the
  disposition table in the
  [investigation record](investigation-claude-code-runtime-2026-10-17.md).

## Changed surface

`documentation.md`, `authorization.md`, `review.md`, new `claude-runtime.md`,
`codex-runtime.md`, `CLAUDE.md`, `codex-AGENTS.md`, `README-agents.md`,
`AGENTS.md`, `README.md`, `.agents/env/README.md`, `feedback-register.md`
(W-R73, W-R74), `scripts/workspace_status.py`, `scripts/sync_codex_config.py`,
`scripts/bootstrap-local.sh`, `Makefile`, the three skill templates (new
`project-bootstrap-SKILL.md`, ownership marker on the others), the architecture
document and the runbook, `tests/test_workspace_status.py`,
`tests/test_sync_codex_config.py`, and new `tests/test_bootstrap_local.py`.

## Verification

- 171 tests pass, and the documentation gate passes, in a scratch copy where
  every whitelisted file is committed. In the worktree the only failure is the
  gate's "routed documentation is not tracked" for the two new rule files,
  which a commit resolves.
- Bootstrap twice against an isolated home leaves every managed file's hash
  unchanged, on the Python path and the no-Python fallback (automated in
  `tests/test_bootstrap_local.py`).
- A read-only `make agent-sync-check` from the branch against this host's real
  config dirs listed `~/.claude` and the second account's dir, planned the
  SessionStart group and three skills for both, upgraded the legacy unmarked
  `env-sync`, and kept the second dir's status line; both `settings.json`
  files hashed the same before and after.
- A read-only run of the readiness check over the real projects produced the
  expected verdicts: silent for ready projects, non-Git directories and the
  linked worktree, the bootstrap message for operator repositories without an
  entry file, the import message for `saberu`, and the owner-move message in
  Codex for standalone `CLAUDE.md` owners.
- Two independent review rounds (four lenses, then a findings check and a
  fresh skeptic) found 42 problems in total; each is fixed or recorded below
  as a residual gap.

## Residual gaps

- Not exercised: bash 3.2 on macOS for `bootstrap-local.sh`; a fresh Claude
  and Codex session showing the readiness message; whether Claude reads a
  subdirectory `AGENTS.md` natively under an ancestor `CLAUDE.md`.
- The readiness check looks only at the project root, so a nested `AGENTS.md`
  without its sibling adapter is found by the bootstrap survey, not at start.
- In Codex the warning does not clear in a foreign clone that tracks its
  upstream's `CLAUDE.md`, because nothing is written there for Codex.
- Discovery skips a name part beginning with `bak`, so a dir such as
  `~/.claude-bakery` needs an explicit `CLAUDE_CONFIG_DIRS`.
- The managed skill names are also listed descriptively in `README.md`, the
  architecture document and the runbook.
- Host and project actions stay with the operator (Plan, "Host and project
  actions"): `make sync` on each host, the empty `~/workspace/projects/.git`,
  aligning host-local preferences between accounts, and bootstrapping projects
  as they are next used.

# Round 1 — Project Agent Entry Points (2026-09-06)

Implements `plan-project-agent-entrypoints-2026-09-06.md`. All changes are
uncommitted and unpushed. No host configuration was written and no project
repository was published.

## Changed in workspace-meta

- `.agents/rules/documentation.md`: new `Make Agent Instructions Loadable`
  section. It requires one canonical owner of project agent facts, an entry
  file for every runtime the project is operated with, thin importing adapters
  that state no rule of their own, use of the runtime's real import mechanism
  rather than a mention or link, and enforcement in the project's executable
  documentation gate. It closes with the transition behavior: read the
  canonical owner before the first write and report the missing entry file.
- `CLAUDE.md`: one Claude-only paragraph after the routing table stating that
  Claude loads `CLAUDE.md` rather than `AGENTS.md`, and routing the requirement
  to `.agents/rules/documentation.md`. The Codex adapter is unchanged because
  its loader already resolves `AGENTS.md`; the asymmetry is an agent-only
  mechanic. The shared `## Safety Floor` block is byte-identical to the Codex
  template, as `test_agent_adapters_route_the_same_portable_core` requires.
- `.agents/host-templates/README-agents.md`: the project agent/governance row
  now states that every runtime needs an entry file it loads, importing one
  canonical owner.
- `feedback-register.md`: `W-R41` records the source incident and how to apply
  it; the documentation owner mapping row now cites it alongside W-R38/W-R39.
- `.gitignore`: reverse-whitelist entries for this review directory.

## Changed in NanoPi_R6S_Handbook

That repository is a separate Git root and was changed under the same operator
request. Recorded here only for traceability; its own `CHANGELOG.md` is the
owner.

- `AGENTS.md`: new `Runtime Privilege Model` section routing to
  `docs/reference/security-and-automation-contract.md` sections 7 and 12.
- `CLAUDE.md`: new thin adapter containing `@AGENTS.md` and no rule of its own.
- `tools/check-documentation`: `CLAUDE.md` added to the root entry allowlist,
  plus an `AGENT_ADAPTER_IMPORTS` check that the adapter resolves its import.
- `tests/test-documentation-structure`: fixture extended, plus negative cases
  for an adapter that only mentions the owner and for an import buried in a
  fenced code block.
- `docs/contributing/documentation.md`: the root entry list now names the
  adapter and its gate.

## Verification

Run in `~/workspace`:

- `test_sync_codex_config.py` — 43 tests, OK.
- `test_workspace_status.py` — 7 tests, OK.
- `bash -n scripts/*.sh .githooks/pre-commit` — clean.
- `py_compile scripts/*.py tests/*.py` — clean.
- `git diff --check` — clean.
- New tracked path has a matching `.gitignore` allow rule.

Run in `~/workspace/projects/NanoPi_R6S_Handbook`:

- all 14 repository tests — PASS, including the new adapter-import negatives.
- `git diff --check` — clean.

## Gaps

- `make test` does not pass as a whole. `test_claude_status_line.py` has one
  failure, `test_renders_requested_fields_from_official_payload`, caused by the
  uncommitted `scripts/claude_status_line.py` separator change from a separate,
  still-undecided status-line task. It predates this round, is unrelated to it,
  and was left untouched rather than repaired, because repairing it would
  decide that pending question. Report it as failing, not as passed.
- Whether a project `CLAUDE.md` import actually reaches the Claude context
  cannot be confirmed from inside the session that already loaded its context.
  It requires a fresh Claude session started in the project directory.
- Tests were confirmed to write only into `tempfile.TemporaryDirectory()` with
  `HOME` redirected; real `~/.codex/AGENTS.md` and `~/.claude/settings.json`
  retain their 2026-09-05 timestamps.

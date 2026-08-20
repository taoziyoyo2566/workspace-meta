# Codex Preferences And Local Environment Registry — Round 4

Status: Implemented and verified locally on 2026-08-20; uncommitted and
unpublished. No real `~/.codex` or `~/.claude` target was written.

## Result

- Added a field-level Codex preference template for
  `history.persistence = "save-all"`, `history.max_bytes = 5242880`, and
  `tui.status_line = ["model", "context-remaining", "git-branch"]`.
- Composed preference reconciliation with the existing managed hooks and
  three-target prevalidation/atomic-write flow.
- Fixed the reviewed patch's multiline-string bug by carrying lexical state
  across the complete TOML document and by asserting managed postconditions and
  unchanged unowned parsed values after rendering.
- Changed `.agents/env/*.yml` to ignored, local runtime state. Removed the two
  historical tracked generated snapshots (`mail.yml` and
  `v133-18-145-97-vir.yml`); both remain recoverable from the pre-change HEAD.
- Updated the ownership matrix, shared environment rule, installed env-sync
  skill template, probe comments, architecture, README, new-VPS runbook, and
  feedback provenance (W-R36).

The preference selection follows the current official OpenAI Codex
configuration reference and sample configuration:

- <https://developers.openai.com/codex/config-reference>
- <https://developers.openai.com/codex/config-sample>

Only stable, cross-host history/status fields were selected. Model, reasoning,
permissions, notifications, theme, analytics, trust, and generated UI state
remain host-local or unlisted.

## Verification

- `make test`: 43 tests passed.
- Added regression coverage for fake `[tui]` headers and assignments inside an
  unowned multiline string, invalid history limits, absent/different/equal
  preferences, preservation, refusal, check mode, and idempotence.
- `bash -n scripts/*.sh .githooks/pre-commit`: passed.
- Python byte compilation for `scripts/*.py` and `tests/*.py`: passed.
- Versioned TOML templates and isolated generated Codex TOML/Claude JSON parsed.
- `git diff --check`: passed.
- Reverse-whitelist checks confirmed new preference/review files are allowed
  and `.agents/env/<new-host>.yml` is ignored.
- A fresh isolated Git repository staged all allowlisted files and passed the
  pre-commit guard; generated environment YAML was not staged.
- Bootstrap ran twice against an isolated temporary HOME. The second run
  reported all four managed targets already current, and their SHA-256 hashes
  were unchanged.
- Isolated `make env-probe` and `make env-probe-check` passed and produced an
  ignored local snapshot.

YAML parser validation remains a tooling gap on this host: neither PyYAML,
Ruby, `yq`, nor Perl YAML modules are installed. The generated snapshot passed
the project freshness reader, but this narrower check is not reported as a full
YAML parser pass.

## Remaining host checks

- A real Codex TUI smoke test is still required after an explicitly authorized
  host bootstrap and new Codex session.
- Changed Codex hooks must be reviewed through `/hooks` after host activation.
- No Git staging, commit, push, PR, host bootstrap, or trust action occurred.

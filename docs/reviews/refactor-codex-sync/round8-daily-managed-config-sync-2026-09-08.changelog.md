# Daily Managed Configuration Sync — Round 8

Status: Implemented and verified locally on 2026-09-08; uncommitted and
unpublished. No real `~/.codex` or `~/.claude` target was written.

Plan: `plan-daily-managed-config-sync-2026-09-08.md`.

## Result

- Added `make sync` as an inspect-first workflow that reports `OK`, `DRIFT`, or
  `ERROR`, shows repository/current managed values, prompts only for safe drift,
  and accepts only `Y`/`y` before applying.
- Unified dry-run, check, and apply behavior around one prevalidated in-memory
  plan in `scripts/sync_codex_config.py`. The plan covers Codex guidance, hooks,
  declared preferences, Claude hooks/status line, and the env-sync skill while
  retaining the existing source-preserving merge and rollback logic.
- Kept `make agent-sync-check` read-only and non-interactive with diagnostic
  drift output, and kept bootstrap-only Git hook initialization and identity
  checks in `scripts/bootstrap-local.sh`.
- Added a pre-apply concurrency guard so a host target changed after the
  dry-run is rejected instead of being overwritten from a stale rendering.
- Updated the canonical architecture and operating guidance without copying
  ordinary preference values out of their existing template owner.

## Verification

- `make test`: 86 tests passed, including new Make/CLI coverage for current
  state, preference drift, decline inputs, confirmed apply, check mode, malformed
  TOML/JSON, managed-only writes, unmanaged-value preservation, and idempotency.
- `bash -n scripts/*.sh .githooks/pre-commit`: passed.
- Python byte compilation for `scripts/*.py` and `tests/*.py`: passed.
- `git diff --check` and the documentation gate: passed.
- An isolated temporary repository staged the reverse-whitelisted tree and its
  pre-commit guard passed; the new Plan and Changelog match the existing
  `docs/reviews/refactor-codex-sync/*.md` allow rule.
- Bootstrap ran twice against an isolated temporary HOME. The second run
  reported all five managed areas `OK`; SHA-256 output for all four managed host
  files was unchanged.
- Generated Codex TOML and Claude JSON parsed successfully. An isolated
  `env-probe` plus `env-probe-check` passed for the generated registry.
- Manual terminal probes confirmed the preference-only dry-run/decline output
  and the confirmed final `UPDATED`/`OK` report with a `1 updated, 4 unchanged`
  summary.

Full YAML parser validation remains a tooling gap on this host: PyYAML, Ruby,
`yq`, and available Perl YAML modules are unavailable. The generated registry
passed the narrower project reader, which is not represented as a full YAML
parser pass.

## Remaining host checks

- Review the first real `make sync` dry-run, confirm only if the displayed
  managed drift is intended, then restart the affected clients.
- If the Codex hook definition changes, review and trust it through `/hooks`
  before treating a fresh SessionStart as active.
- Verify the Codex and Claude status lines in real interactive sessions.
- No staging, commit, push, PR, real-host sync, or hook-trust action occurred.

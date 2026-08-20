# Codex Implicit TOML Tables — Round 5

Status: Corrected and verified locally on 2026-08-20; uncommitted and
unpublished.

## Trigger and root cause

The operator's real `make bootstrap` reached preference prevalidation and
failed before agent configuration writes with:

`cannot safely add tui.status_line; tui has no direct TOML table`

A value-free structural inspection showed that the host configuration has no
direct `[tui]` table and contains a valid nested `[tui.model_availability_nux]`
table. TOML therefore creates `tui` as an implicit parent. The synchronizer
recognized only direct table headers and incorrectly rejected this legal shape.

## Correction

- Added document-level header reuse and root dotted-assignment detection.
- Missing managed fields under a proven implicit parent are inserted before the
  first table header as root dotted keys, for example `tui.status_line = [...]`.
- Existing root dotted managed assignments can be updated in place.
- Ambiguous inline or otherwise unlocatable definitions still fail closed.
- Added regression coverage for the real-host shape, preservation of generated
  nested UI state, dotted-key updates, and idempotence.

## Verification

- A value-free, read-only check against the real host configuration completed
  reconciliation without the original error. Check mode reported the expected
  preference drift and an existing hook-state normalization; it wrote nothing.
- `make test`: 45 tests passed.
- Shell syntax, Python byte compilation, versioned TOML parsing, and
  `git diff --check`: passed.
- Bootstrap ran twice in an isolated repository/HOME seeded with
  `[tui.model_availability_nux]`. The first run succeeded; the second reported
  all four managed targets already current, and their hashes were unchanged.

No Git publication or direct host configuration write is part of this round.

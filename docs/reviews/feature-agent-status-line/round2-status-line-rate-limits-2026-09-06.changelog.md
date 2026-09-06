# Round 2 — Status-Line Rate-Limit Display (2026-09-06)

Implements `plan-status-line-rate-limits-2026-09-06.md`. All changes are
uncommitted and unpushed. No host configuration was written.

## Changed

`scripts/claude_status_line.py`

- New `5h:<remaining>%(<countdown>)` segment, placed after the context gauge,
  reading `rate_limits.five_hour` from the status-line payload.
- `reset_epoch()` accepts `resets_at` as epoch seconds (what Claude Code
  2.1.236 sends) or as an ISO 8601 string (what the usage API sends), and
  returns `None` for anything else.
- `format_countdown()` renders `2h14m`, `45m`, or `<1m`, and returns an empty
  string for a reset already in the past so the segment never shows a negative.
- `_now()` isolates the clock so tests are deterministic.
- The three threshold colours were renamed `CTX_*` to `LEVEL_*` and are now
  applied through one `level_color()` helper, because two gauges share them.
  Both are keyed on the used fraction, so the five-hour segment turns red as
  the window fills even though it displays what remains.
- The segment is omitted whenever the key is missing or malformed, matching how
  cost and token detail already degrade.
- `_number()` now rejects `NaN` and infinity, preventing Python's permissive
  JSON parser from turning a malformed gauge or reset timestamp into a renderer
  exception.

`tests/test_claude_status_line.py`

- The separator expectation now asserts the PS1-style `~/workspace:main`
  rendering introduced in the previous round. This is the failure that had been
  breaking `make test`; the previous round changed the renderer without
  updating its test.
- Five new cases: a present window with a countdown, an ISO reset plus a reset
  already in the past, absent/malformed shapes, non-finite gauges and reset
  timestamps, and the threshold colours.

`README.md` and `docs/architecture/codex-config-management.md`

- Current documentation now includes the five-hour remaining-usage display;
  the architecture points to the executable renderer instead of maintaining a
  second field list.
- In the reviewed two-commit publication shape these overlapping documentation
  hunks follow in the adjacent governance commit. The feature-only commit is a
  green executable checkpoint, not the final documentation state.

## Verification

- Feature-only candidate: `make test` — 61 tests, OK. Its base predates the
  documentation gate.
- Combined working tree before the targeted gate remediation: `make test` — 67
  tests, OK, including the documentation gate. Final gate verification is
  recorded in the round 3 documentation-governance changelog.
- `bash -n scripts/*.sh .githooks/pre-commit` — clean.
- `py_compile scripts/*.py tests/*.py` — clean.
- `git diff --check` — clean.
- Isolated-home bootstrap — two runs produced identical managed-file hashes;
  generated Claude JSON and Codex TOML parsed successfully.
- Isolated staged-tree pre-commit simulation — clean for every changed and new
  path in the combined workspace-meta review set before the targeted gate
  remediation; the final candidate still needs that check rerun.
- Manual render against a synthetic payload confirmed
  `~/workspace:main  Opus  ctx:43%  5h:73%(2h14m)  in:1.2k … ~$0.421`, and the
  same payload with `NO_COLOR=1` emitted no escape sequences.

## Product evidence

The payload contract was read from the installed binary rather than assumed.
`Claude Code 2.1.236` builds the status-line payload with
`five_hour:{used_percentage:C.five_hour.utilization*100, resets_at:...}` under a
`rate_limits` key that is present only when window data exists, and its header
parser sets `resets_at` from `Math.round(Number(...))` on
`anthropic-ratelimit-unified-5h-reset`, an epoch in seconds. This is a dated
observation of one client version on one host.

## Gaps

- A read-only `make agent-sync-check` on 2026-09-06 reported all four managed
  targets already current. This round did not run `make bootstrap` or otherwise
  write host configuration; the probe is a dated state observation, not proof
  of real UI rendering.
- The five-hour segment was verified against synthetic payloads only. Whether a
  real session populates `rate_limits` depends on the account's plan and on the
  response headers the client has seen, and cannot be asserted from here.
- The seven-day window is present in the payload and is deliberately not
  displayed.

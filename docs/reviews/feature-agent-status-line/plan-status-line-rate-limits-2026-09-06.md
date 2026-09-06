# Status-Line Rate-Limit Display Plan

Status: Implemented and verified on 2026-09-06. Extends
`plan-agent-status-line-2026-08-26.md`. Host installation, Git publication, and
live configuration writes remain excluded.

## Goal

Two operator-requested changes to `scripts/claude_status_line.py`:

1. Finish the PS1-style rendering change so the module's tests pass again. The
   working tree already carries the colour and separator change from an earlier
   round; its test still asserts the previous two-space separator, so
   `make test` fails.
2. Show how much of the rolling five-hour usage window is left.

## Verified product baseline

Probed from the installed client, `Claude Code 2.1.236` at
`~/.local/share/claude/versions/2.1.236`, on 2026-09-06. The status-line
payload builder constructs:

```js
R={...C.five_hour&&{five_hour:{used_percentage:C.five_hour.utilization*100,
                               resets_at:C.five_hour.resets_at}},
   ...C.seven_day&&{seven_day:{...}}}
...(R.five_hour||R.seven_day)&&{rate_limits:R}
```

`C` comes from the response-header parser, which builds
`{utilization:Number(o),resets_at:Math.round(Number(i))}` from
`anthropic-ratelimit-unified-5h-utilization` and
`anthropic-ratelimit-unified-5h-reset`. So in the status-line payload:

- `rate_limits.five_hour.used_percentage` is 0-100, already multiplied by 100;
- `rate_limits.five_hour.resets_at` is a Unix epoch **in seconds**, a number;
- the whole `rate_limits` key is absent when the client has no window data.

A different code path in the same binary carries `resets_at` as an ISO string
from `/api/oauth/usage`. That path does not feed the status line, but accepting
both shapes costs little and avoids a silent blank if the client ever switches.

This is a dated observation of one client version on one host, not a product
guarantee.

## Scope and exclusions

In scope:

- render remaining five-hour quota and time to reset;
- colour it on the same thresholds already used for the context gauge, keyed on
  the used fraction so that high use is red for both gauges;
- update the module's tests, including the separator expectation that currently
  fails;
- update current README/architecture descriptions of the renderer;
- record the round in this directory.

Excluded:

- the seven-day window, which was not requested and would crowd the line;
- deriving usage from `/api/oauth/usage`, transcripts, or credential files;
- running `make bootstrap`, which rewrites host configuration under `~/.claude`
  and `~/.codex` and is a separately authorized operation;
- staging, committing, pushing, or PR creation.

## Approach and risks

1. Read `rate_limits.five_hour` defensively: absent key, wrong type, missing
   field, and non-numeric values must degrade to omitting the segment, matching
   how cost and token detail already behave.
2. Display remaining rather than used, because the operator asked for what is
   left; colour by used so both gauges share one threshold function.
3. Accept `resets_at` as epoch seconds or as an ISO 8601 string; omit the
   countdown when it is already in the past rather than printing a negative.
4. Inject the clock through a module-level function so tests are deterministic.
5. Rename the three threshold colours from `CTX_*` to `LEVEL_*` now that two
   gauges share them, and update the one test that names them.
6. Reject non-finite numeric values before formatting so Python's permissive
   JSON handling cannot drop the whole status line on `NaN` or infinity.

The main risk is the hash pin. `~/.claude/settings.json` pins the script's
SHA-256, so an unapplied edit makes the live status line print the "changed or
is unavailable" notice until `make bootstrap` re-pins it. Host state is a dated
fact and must be checked rather than inferred from working-tree history.

## Verification

- `make test`, which must return to a full pass in the feature-only candidate;
- new cases: present window, missing window, malformed/non-finite values, ISO
  `resets_at`, past `resets_at`, and threshold colours;
- `make docs-check` through the normal `make test` target in the final combined
  candidate;
- `bash -n scripts/*.sh .githooks/pre-commit`;
- Python byte compilation for `scripts/*.py` and `tests/*.py`;
- `git diff --check`;
- `make agent-sync-check` to report current managed-config state without writing
  it.

## Publication boundary

The reviewed two-commit publication shape keeps the renderer, its tests, and
this feature's plan/changelog in the first commit. The README and architecture
updates follow in the adjacent governance commit because their current hunks
also carry that remediation. The first commit is therefore a green executable
checkpoint, not the final documentation state; the complete series remains the
bounded content change.

## Handoff

Record the outcome in a dated round changelog in this directory. Leave all
changes uncommitted and report the current read-only sync check separately from
the still-required real UI smoke test.

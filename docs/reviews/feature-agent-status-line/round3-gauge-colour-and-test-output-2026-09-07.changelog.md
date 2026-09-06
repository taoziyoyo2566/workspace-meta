# Round 3 — Gauge Colour Consistency And Test Output (2026-09-07)

Follow-up review of the round 2 working tree before publication. Two defects
found by reading the round 2 diff; both are fixed here with regression tests.

## Changed

- `scripts/claude_status_line.py` — colour both gauges from the value the line
  actually prints. Round 2 refactored the context gauge from
  `level_color(used_int)` to `level_color(used)`, so a used fraction of 79.5
  printed `ctx:80%` in yellow while the pre-refactor line printed it in red.
  The five-hour gauge had the same split from the other side: it printed a
  rounded remainder but keyed its colour on the unrounded used fraction, so
  79.6% used printed `5h:20%` in yellow. Both now round first and threshold the
  rounded value, which keeps the documented "keyed on the used fraction"
  intent while making the label and the colour agree.
- `tests/test_claude_status_line.py` — two boundary tests that assert the
  colour and the printed percentage together
  (`f"{LEVEL_RED}ctx:80%"`), not the presence of a colour anywhere in the line.
  The existing threshold tests use integer fixtures (59 / 60 / 80) and
  therefore could not observe this class of defect.
- `tests/test_sync_codex_config.py` — capture stdout in
  `test_main_check_reports_preference_drift_without_writing` and assert on it.
  `main()` reports each managed target on stdout; unittest reports on stderr.
  Under a pipe, stdout is block-buffered and flushed at interpreter exit, so
  `make test` ended with

  ```text
  Ran 76 tests in 1.6s
  OK
  Codex AGENTS.md: installed
  Codex hooks: installed or updated
  Codex preferences: updated preferences: ...
  Claude hooks/status line: installed or updated
  ```

  which reads as though the test run had just rewritten this host's Codex and
  Claude configuration. It had not — the writes went to the test's temporary
  home — but in a repository where host mutation is a governed boundary, a test
  run must not produce output indistinguishable from a real bootstrap.

## Verification

- `make test` — 78 tests, OK, including the documentation gate. Test-run stdout
  is now empty.
- Mutation checks on the two new boundary tests: reverting
  `level_color(used_int)` to `level_color(used)`, and returning `used` instead
  of `used_share` from `five_hour_segment`, each produced exactly one failure.
  Without this step the tests would assert current behaviour without proving
  they can detect its loss.
- Documentation-gate mutation checks (on a copy, not this tree): an
  unallowlisted root Markdown entry, a broken intra-repository link, and a
  removed Claude safety-floor line were each rejected with a specific message.
- `bash -n scripts/*.sh .githooks/pre-commit` — clean.
- `py_compile scripts/*.py tests/*.py` — clean.
- `git diff --check` — clean.
- Isolated-home bootstrap — two runs against a temporary `HOME`; the second
  reported `already current` for every managed target and produced identical
  managed-file hashes. The real `~/.codex` and `~/.claude` files were unchanged
  across the whole round (verified by mtime before and after).

## Gaps

- No manual Codex/Claude UI smoke test. The rendered strings above come from
  unit fixtures, not from a live status line.
- `scripts/claude_status_line.py` changed, so the SHA-256 pinned in the
  installed `~/.claude/settings.json` no longer matches it and the status line
  will report `workspace-meta status line changed or is unavailable` until
  `make -C ~/workspace bootstrap` is run. That is a host change and is left to
  the operator.
- The round 2 deletion of the runbook and troubleshooting sections from
  `docs/architecture/codex-config-management.md` was traced item by item to its
  new owners (`docs/runbooks/new-vps.md`, `AGENTS.md`, `Makefile`, `README.md`)
  and no content was found to be lost, but `docs/runbooks/new-vps.md` was not
  re-read end to end in this round.

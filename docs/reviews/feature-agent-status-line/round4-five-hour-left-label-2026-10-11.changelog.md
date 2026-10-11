# Round 4 — Five-Hour Gauge Says "left" (2026-10-11)

The five-hour gauge printed the remaining share as `5h:95%`, right beside
`ctx:55%`, which prints the used share in the same `N%` form. On 2026-10-11 a
reality-ops coordination session read `5h:95%(4h20m)` as 95% used and reported
it as a problem (W-R59). The operator approved this label fix as a separate
change: question 2 of the feedback-intake Plan,
`docs/reviews/refactor-feedback-intake/plan-feedback-intake-2026-10-11.md`,
approved on 2026-10-11 ("同意，三件事都按建议做").

## Changed

- `scripts/claude_status_line.py`: the five-hour segment now reads
  `5h:<remaining>%left(<countdown>)`, for example
  `ctx:55%  5h:95%left(4h20m)`. The value, rounding, colour thresholds and the
  countdown are unchanged; the gauge is still keyed on the used share.
- `tests/test_claude_status_line.py`: the five-hour expectations carry the
  `left` marker, so a regression to the bare `N%` form fails.
- `README.md`: the bootstrap description says the gauge is marked `left`.

## Verification

- The updated tests failed against the old script (6 failures across 4 tests,
  counting sub-tests) and pass with the change.
- `make test`: documentation gate OK, 110 tests OK.
- `bash -n scripts/*.sh .githooks/pre-commit`, `py_compile` of the scripts and
  tests, and `git diff --check`: clean.
- Isolated-home sync, run twice: the second run reported 0 updated and 6
  unchanged, with identical file hashes. The installed `statusLine.command`
  pins the new script's SHA-256.
- `make agent-sync-check` on this host reports drift for the Claude statusLine
  only. Once the change is on `main`, the installed command prints its "run:
  make -C ~/workspace sync" notice until `make sync` updates the pin.

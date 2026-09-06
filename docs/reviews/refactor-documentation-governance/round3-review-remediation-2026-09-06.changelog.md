# Round 3 — Review Remediation (2026-09-06)

Implements `plan-review-remediation-2026-09-06.md`. All changes remain
uncommitted and unpushed. No nested project, real host configuration, or live
system was changed.

## Changed

- Replaced the architecture document's duplicate ownership matrix, Git route
  table, publication procedure, and operations guide with concise explanation
  and links to the canonical rule matrix, shared owners, and new-VPS runbook.
- Added a README documentation map and removed a dated host observation from
  current guidance while retaining its dated review record.
- Added `scripts/check_documentation.py` and wired it into `make test`. The gate
  validates root entries, adapter routes, safety-floor source binding, internal
  links and anchors, truth lifecycle, runbook structure, and tracked route
  targets without descending into nested project repositories.
- Added focused positive and negative gate tests, including identical drift in
  both adapter safety-floor copies so copy-to-copy equality cannot mask source
  drift.
- Hardened the gate after targeted review. Current documents are discovered
  recursively inside workspace-meta-owned directories; truth-lifecycle checks
  ignore fenced examples but retain inline-code text and Markdown link labels;
  negative tests now cover every previously unguarded check family, including
  nested documents and tracked-route failures.
- Restored the safety floor's missing `switch away from` clause and named its
  canonical source modules in both adapters.
- Refined the missing-project-entry backstop from "before first write" to
  before substantive project work, including read-only review and
  host/external action. `W-R42` records why the earlier trigger would not have
  prevented the source incident.
- Corrected the historical review's P1 count from four to five without
  rewriting its point-in-time findings.
- Preserved and reviewed the concurrent status-line changes: current docs now
  describe the five-hour remaining-usage segment, and non-finite numeric input
  omits only the affected segment instead of dropping the renderer.

## Verification

- `make test` — 76 tests, OK, including the documentation gate and its focused
  negative cases.
- `bash -n scripts/*.sh .githooks/pre-commit` — clean.
- Python byte compilation for `scripts/*.py` and `tests/*.py` — clean.
- Source TOML and generated Codex TOML/Claude JSON parsing — clean.
- `git diff --check` — clean.
- Reverse-whitelist review — every new path is addable. The earlier combined
  candidate passed an isolated staged-tree pre-commit check, but that check was
  not rerun after the targeted gate remediation.
- The earlier combined candidate passed a two-run isolated-home bootstrap with
  stable managed-file hashes; that bootstrap was not rerun after the targeted
  gate remediation.
- `make agent-sync-check` — reported all four managed targets already current
  on 2026-09-06; it made no host writes.

## Remaining checks

- Rerun the isolated staged-tree pre-commit check and the two-run isolated-home
  bootstrap against the final publication candidate.
- A fresh Claude session in a project with an importing `CLAUDE.md` is still
  required to observe the resolved project instructions in real session
  context.
- The five-hour status segment still needs a real Claude UI smoke test with an
  account/session that supplies `rate_limits.five_hour`.

# Status Line Order And Command Diagnostics — Round 10

Date: 2026-09-08

Plan: `plan-status-line-order-and-command-diagnostics-2026-09-08.md`

## Summary

The Codex preferences template now solely owns the requested project-to-limit
status-line hierarchy. Synchronizer tests derive their managed-list expectation
from that template instead of maintaining copies.

Codex SessionStart, Claude SessionStart, and Claude `statusLine` drift now names
the target script and reports parsed command properties individually. Script
pins, execution target and interpreters, hash-mismatch recovery command, and
structure version are distinct from matcher, timeout, status message, and
padding. A raw SHA-256 remains only as evidence for a residual command structure
change the narrow parser cannot explain.

## Meaningful changed surface

- Updated the canonical Codex preference value without adding a second list to
  documentation or tests.
- Extended ownership recognition across workspace-meta command marker versions
  so the installed and repository versions can be compared semantically.
- Reworked component details, effects, and pre-prompt summaries around operator
  decisions rather than a whole-command loader digest.
- Updated current architecture text to point to the canonical template and to
  document optional native values and the raw fallback boundary.

## Verification

- `make test`: passed, 93 tests.
- Shell syntax and Python byte compilation: passed.
- Generated Codex TOML, Claude JSON, and environment-registry YAML parsed
  successfully; the YAML check used the locally installed `js-yaml` parser.
- Bootstrap ran twice against one isolated temporary repository and HOME. The
  second run reported `0 updated, 6 unchanged`; all four managed host-file
  hashes were identical to the first run.
- `git diff --check`: passed.
- The reverse-whitelist pre-commit guard passed with every changed path staged
  only in the isolated repository copy; the real repository index stayed empty.
- The installed Codex 0.153.4 binary contains all requested native status-item
  identifiers. A real UI display remains a manual host check.
- A real-host `make sync` dry-run reported the three command differences as the
  hash-mismatch recovery command change and the Codex preference as a status-line
  replacement. The prompt was declined with `N`; no host file was changed.

## Residual boundary

Only an unparsed residual command-body change is represented by a raw
command-structure SHA-256. It is labeled as an unrecognized structure change,
with installed and repository hashes plus its replacement effect; ordinary pin
or version changes do not use that fallback.

No host synchronization, hook trust action, Git staging in the real repository,
commit, push, pull, fetch, or PR occurred.

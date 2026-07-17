# Workspace-Meta Project Guidance

This repository owns the cross-project governance carrier rooted at
`~/workspace`. The global managed Codex guidance still applies; this file adds
repository-specific rules.

## Before Editing

- Read `README.md` and, for agent configuration work,
  `docs/architecture/codex-config-management.md`.
- Non-trivial behavior or configuration changes require a plan under
  `docs/reviews/<kind>-<topic>/plan-<slug>-YYYY-MM-DD.md` before implementation
  and a round changelog in the same directory after implementation.
- Keep the reverse whitelist in `.gitignore` explicit. New tracked paths require
  a matching allow rule and a pre-commit verification.

## Configuration Boundaries

- Never commit credentials, Codex authorization rules, hook trust hashes,
  project trust, histories, caches, databases, logs, or generated host config.
- Workspace-meta may install only explicitly documented managed blocks into
  `~/.codex` and `~/.claude`; content outside those ownership markers is local.
- Changes to trusted hook behavior must change the installed hook command hash
  so Codex asks the operator to review it again.

## Verification

- Run `make test`.
- Run `bash -n scripts/*.sh .githooks/pre-commit` and
  `python3 -m py_compile scripts/*.py tests/*.py`.
- Parse generated TOML/JSON/YAML and run `git diff --check`.
- Run bootstrap twice against an isolated temporary HOME and confirm managed
  file hashes are unchanged on the second run.
- Treat a real Codex/Claude UI smoke test as manual host verification, not as a
  unit-test result.

## Commit And Sync

- Leave changes reviewable and report whether they are uncommitted or unpushed.
- Do not commit or push unless the user explicitly requests it. This is the
  Codex authorization rule for this repository even though the Claude workflow
  may recommend same-round synchronization.

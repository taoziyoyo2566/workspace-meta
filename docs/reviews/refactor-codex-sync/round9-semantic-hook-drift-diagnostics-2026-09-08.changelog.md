# Semantic Hook Drift Diagnostics Changelog

Date: 2026-09-08

Plan: `plan-semantic-hook-drift-diagnostics-2026-09-08.md`

## Summary

Managed hook drift now identifies the component and only the semantic fields
that differ. Codex SessionStart, Claude SessionStart, and Claude `statusLine`
are independent report areas tied to their actual repository scripts. Pin-only
drift uses `~ script hash pin changed`, shows the installed and repository pins,
and explains which current repository script synchronization will trust.

Interactive synchronization now presents a concise `Changes to apply` list
before the Y/N prompt. Existing parsed repository/current diagnostics for Codex
preferences, including the ordered `tui.status_line` comparison, remain intact.

## Meaningful changed surface

- The synchronizer derives an explicit managed-component snapshot from the
  rendered and parsed TOML/JSON structures. Its narrow schema covers component
  identity, matcher and handler shape, script path and pin, command target and
  interpreter, timeout, status message, padding, and managed extra fields. A
  command-loader SHA is only supporting fallback detail for an otherwise
  unrecognized command-shape change; whole hook/statusLine object hashes are no
  longer the explanation.
- Claude's combined hook/status-line report was split into two statuses, making
  `workspace_status.py` and `claude_status_line.py` drift independently visible.
- Focused tests cover Codex and Claude pin-only changes, component separation,
  changed matcher/timeout/status/padding/script targets, the pre-prompt summary,
  read-only decline/check behavior, and unchanged Codex preference output.
- Current architecture and runbook documentation now describe six report areas
  and the semantic diagnostics contract.

## Verification

- `make test`: passed, 90 tests including the new semantic drift cases.
- `bash -n scripts/*.sh .githooks/pre-commit`: passed.
- Python byte compilation for `scripts/*.py` and `tests/*.py`: passed.
- `git diff --check`: passed.
- Bootstrap ran twice against an isolated temporary repository and HOME. The
  second run reported `0 updated, 6 unchanged`; hashes of all four managed host
  files were unchanged.
- Generated Codex TOML and Claude JSON parsed successfully. The isolated
  environment registry passed `env_probe.sh --check`.
- An isolated temporary Git repository staged every current workspace-meta
  changed path through the reverse whitelist and its pre-commit guard passed.
- A terminal smoke test changed only the installed Codex evaluator pin and
  confirmed the semantic pin detail, trust-refresh explanation, changes summary,
  prompt ordering, and no write after `N`.

Full YAML parser validation remains a tooling gap: PyYAML, `yq`, Ruby, and the
available Perl/Node modules do not provide a YAML parser on this host. The
project's narrower generated-registry freshness check passed but is not claimed
as a full YAML parse.

## Residual host checks

- No real-host sync, Codex `/hooks` trust action, client restart, staging,
  commit, push, or PR occurred.
- Review the first real `make sync` output before accepting it, then perform the
  applicable Codex hook trust review and Claude/Codex UI reload checks.

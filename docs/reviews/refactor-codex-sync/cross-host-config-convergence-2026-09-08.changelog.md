# Changelog: Cross-Host Managed Configuration Convergence

Plan: [Cross-Host Managed Configuration Convergence](plan-cross-host-config-convergence-2026-09-08.md)

## Summary

Fixed the Codex preference placement loop reported on an older host and made
the intentionally blocking Claude unmanaged-status-line result actionable
without weakening local configuration preservation.

## Changed Surface

- Codex preference insertion now respects the hook marker as an ownership
  boundary. When a preceding TOML table semantically reaches the hook array,
  missing fields are inserted before the begin marker and remain stable across
  later hook rendering.
- The reported `history.max_bytes` layout now converges in one confirmed sync,
  preserves unowned values, and produces no hook or preference change on the
  next check.
- An unmarked Claude `statusLine` remains unmanaged and blocks all writes. The
  error now identifies the settings target and explains the narrow choice to
  preserve the existing value or remove only that field when intentionally
  transferring ownership to workspace-meta. It does not print the untrusted
  command.
- Focused tests cover the reported Codex layout, exact manual Claude command,
  second-run convergence, actionable diagnostics, no prompt on error, and
  all-target non-interference.
- The architecture records the marker-boundary insertion invariant, and the
  runbook gives the operator-owned status-line resolution at the existing
  troubleshooting entry point.

## Material Deviations

None. Automatic takeover of unknown Claude configuration, managed preference
ownership, hook/status-line behavior, and Git publication boundaries remain
unchanged.

## Verification

- `make test`: 95 tests passed.
- `make docs-check`: passed.
- Focused reported-layout and unmanaged-status-line regressions: passed.
- Required shell syntax and Python compilation checks: passed.
- Generated Codex TOML and Claude JSON parsed; the host-generated environment
  YAML parsed.
- Two bootstrap runs against an isolated repository and home produced identical
  managed-file hashes on the second run, with all six areas reporting `OK`.
- `git diff --check`: passed.

The other host was not mutated or used as a verification target. It must first
receive a published fix through the separately authorized Git workflow; its
manual status line remains an explicit host-local ownership decision. This
result is local, unstaged, uncommitted, and unpushed.

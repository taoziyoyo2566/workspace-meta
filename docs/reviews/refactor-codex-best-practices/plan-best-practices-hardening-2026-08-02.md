# Plan: Codex best-practice hardening

- **Date**: 2026-08-02
- **Level**: Engineering / host configuration hardening
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user-authorized by “按照建议来处理”

## Goal

Align the workspace-meta Codex integration with current official guidance while
preserving the separation between portable instructions and host-local command
authorization.

## Scope

1. Fix `scripts/sync_codex_config.py` so Codex-owned `hooks.state` and hook trust
   state remain outside the workspace-meta managed block.
2. Add regression coverage proving managed-hook synchronization is idempotent
   when Codex has written `hooks.state`.
3. Apply a narrow host-local Codex baseline on this VPS: explicit sandbox and
   approval defaults, narrower project trust, and a minimal prompt-oriented
   `permissions.rules` file.
4. Verify the repository change and the current host configuration without
   copying the old VPS's unavailable `.rules` contents.

## Exclusions

- Do not copy or commit `~/.codex/rules/default.rules`, `permissions.rules`,
  credentials, trust state, history, databases, or other host runtime data.
- Do not change the configured model, authentication, plugins, skills, or
  unrelated project settings.
- Do not automatically delete the probe-generated `default.rules`; its cleanup
  remains a separate host-local decision because it is authorization state.
- Do not stage, commit, push, or publish this repository.

## Expected effect

- `make agent-sync-check` reports Codex hooks as `already current` after Codex
  trust state exists.
- A new bootstrap preserves host-managed hook state and does not reset trust.
- The current host prompts for high-impact Git and external operations while
  retaining workspace-write sandbox behavior.
- The broad `/home/saberu/workspace` project trust entry is removed; explicitly
  trusted child projects remain unchanged.

## Risks and assumptions

- `approval_policy = "untrusted"` may cause more interactive prompts than the
  previous implicit default; this is an intentional safety tradeoff.
- The old VPS rule contents are unavailable, so exact behavioral parity cannot
  be claimed. The new `permissions.rules` is a reviewed minimal baseline, not a
  migration of historical approvals.
- Codex hook trust is host-owned and may still require `/hooks` review after a
  definition change.

## Verification

- `make test`
- `bash -n scripts/*.sh .githooks/pre-commit`
- `python3 -m py_compile scripts/*.py tests/*.py`
- TOML parsing, `codex execpolicy check` for representative safe and sensitive
  commands, and `git diff --check`
- isolated bootstrap twice with managed-file hash comparison
- current-host `make agent-sync-check` and read-only inspection of the final
  host config
- report the manual Codex `/hooks` UI smoke-test gap separately

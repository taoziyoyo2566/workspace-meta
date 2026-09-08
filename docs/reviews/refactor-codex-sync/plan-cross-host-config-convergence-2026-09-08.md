# Plan: Cross-Host Managed Configuration Convergence

Status: COMPLETE on 2026-09-08. Verified outcome:
[Changelog](cross-host-config-convergence-2026-09-08.changelog.md).

## Goal

Make managed configuration synchronization converge safely when an older host
has a Codex preference visually inside the managed hook block, while keeping an
unmarked Claude `statusLine` protected and making its intentional migration
path actionable.

## Current State

- An unmarked Claude `statusLine.command`, including
  `bash ~/.claude/statusline-command.sh`, is correctly classified as unmanaged.
  Synchronization refuses to overwrite it, but the error does not state the
  narrow ownership-transfer action clearly enough.
- Codex hook rendering replaces everything between its markers before
  preference reconciliation. When `[history]` begins before that block and
  `history.max_bytes` was inside it, the TOML table span ends at the first hook
  array header inside the block. The preference renderer therefore inserts the
  missing value after the begin marker; the next hook render removes it again.
- An isolated reproduction confirms `max_bytes` lands inside the managed block
  and the second pass reports both hook rewriting and preference drift.

## Intended Change

- Keep the unknown-Claude-status-line refusal and all-target no-write behavior.
  Make the error identify the affected settings file and explain that the
  operator must review/preserve the existing value or remove only `statusLine`
  when intentionally transferring that field to workspace-meta.
- Bound Codex preference insertion so a direct table that starts before the
  managed hook block inserts missing fields before the begin marker, never
  inside the hook-owned region.
- Add focused behavioral regressions for the reported legacy layout, second-run
  convergence, the exact manual Claude command, actionable refusal, and
  preservation of every target on error.
- Add only the necessary architecture/runbook clarification and one final
  Changelog after verification.

## Scope And Non-Goals

In scope are `scripts/sync_codex_config.py`, its focused tests, the canonical
configuration architecture, the existing host troubleshooting runbook, this
Plan, and one final Changelog.

Out of scope are automatic takeover of arbitrary Claude status lines, changes
to managed status-line values or rendering, hook semantics, broad TOML
rewriting, direct edits to any host's `~/.claude` or `~/.codex`, nested project
repositories, and Git staging/publication/history actions. Existing unrelated
coherent-workstream lifecycle edits remain preserved.

## Acceptance Criteria

1. The reported Codex layout is repaired in one confirmed sync and is clean on
   the next check; `history.max_bytes` remains before the hook begin marker.
2. Other managed preferences and every unowned TOML value remain preserved.
3. An unmarked Claude status line still blocks every write and never reaches a
   confirmation prompt, including for the reported manual command.
4. Its error names the settings target and the explicit, field-only ownership
   transfer choice without printing the untrusted command or deleting it.
5. Current dry-run, confirmation, error blocking, atomic recovery, and
   non-interactive check behavior remain intact.
6. Repository-required verification passes, including isolated two-pass
   bootstrap and generated configuration parsing.

## Material Deviation Boundary

Stop for approval before allowing automatic replacement of an unmarked Claude
status line, changing managed preference ownership, weakening preservation or
all-target prevalidation, changing hook/status-line behavior, or expanding into
host mutation or Git publication. Routine implementation repair, focused test
adjustment, documentation alignment, and re-verification stay within this Plan.

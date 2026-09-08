# Semantic Hook Drift Diagnostics Plan

Status: COMPLETE on 2026-09-08. Verified outcome:
`round9-semantic-hook-drift-diagnostics-2026-09-08.changelog.md`.

## Goal

Make managed Codex and Claude hook drift actionable by reporting semantic,
component-level field changes instead of using a SHA-256 of an entire rendered
managed object as the primary explanation. Show a concise summary of the exact
managed changes before interactive synchronization asks for confirmation.

## Current state

The daily synchronizer already builds one prevalidated in-memory plan, reports
managed-area drift, and applies it only after an explicit `Y`. Codex hook drift
is summarized by a hash of the whole marked TOML block. Claude's SessionStart
hook and `statusLine` are combined into one area and summarized by a hash of a
synthetic JSON object. Parsed and rendered TOML/JSON structures are already
available, and Codex preference drift already has a useful field-level report.

## Intended change

- Give Codex SessionStart, Claude SessionStart, and Claude `statusLine`
  independent managed-component diagnostics.
- Extract the known semantic fields from the already parsed/rendered managed
  structures: component identity, matcher, handler type/count, script path,
  embedded script hash pin, command target/interpreter, timeout,
  `statusMessage`, padding, and explicitly managed additional fields when
  present.
- Report only changed fields. When the embedded pin is the sole change, emit
  `~ script hash pin changed` and explain that synchronization will trust the
  current repository copy of the component's owning script.
- Keep raw pin SHA-256 values as supporting current/repository detail, without
  using a whole-object digest as the primary hook explanation.
- Add an interactive `Changes to apply` summary immediately before the warning
  and Y/N prompt. Preserve the current field/list diagnostics for Codex
  preferences, especially `tui.status_line`.
- Add focused behavioral tests and update only documentation whose stated
  managed-area count or diagnostic contract changes.

## Scope and exclusions

In scope are `scripts/sync_codex_config.py`, its tests, and the existing
workspace-meta sync documentation and closeout records. Existing uncommitted
daily-sync edits are preserved and extended in place. Excluded are a generic
diff engine, new dependencies, ownership changes, host configuration writes,
hook trust mutation, Git publication, and nested project repositories.

## Acceptance criteria

- Codex SessionStart drift names only meaningful changed fields and identifies
  `workspace_status.py` pin-only drift with the required semantic wording and
  synchronization explanation.
- Claude SessionStart and `statusLine` appear as separate report areas, tied to
  `workspace_status.py` and `claude_status_line.py` respectively, with semantic
  matcher/timeout/status/padding/command-target changes where applicable.
- Raw current and repository hash pins remain visible as supporting detail;
  hook diagnostics do not lead with a whole-object SHA comparison.
- Interactive drift includes a concise `Changes to apply` section before the
  prompt, and check mode remains read-only.
- Existing `tui.status_line` repository/current and ordered-list comparison is
  unchanged.
- Project-required tests, syntax checks, parsers, diff checks, and isolated
  double-bootstrap verification pass.

## Risks and verification boundary

The main risk is misclassifying a command-string change or hiding an owned
field that synchronization will replace. The implementation will use a narrow
schema for the known generated hook/status-line commands and explicit managed
container fields, with a command-definition fallback when a command changes in
an unrecognized way. Tests will mutate each meaningful field independently and
exercise pin-only cases. Real host synchronization, Codex `/hooks` review, and
Claude/Codex UI reload remain manual host verification.

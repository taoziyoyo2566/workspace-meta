# Status Line Order And Command Diagnostics Plan

Status: COMPLETE on 2026-09-08. Verified outcome:
`round10-status-line-order-and-command-diagnostics-2026-09-08.changelog.md`.

## Goal

Set the repository-managed Codex status line to the requested eight-item
information hierarchy, with the preferences template remaining its sole
canonical owner. Make managed hook and Claude status-line drift explain parsed
command semantics before falling back to an opaque command hash.

## Current state

The canonical preference template still has the previous seven-item ordering,
and several tests repeat that list. Component diagnostics already separate the
two SessionStart hooks and Claude `statusLine`, but any difference left in the
normalized command string is reported only as `command loader changed`. On the
current host, that hides a change to the hash-mismatch recovery command.

## Intended change

- Replace only the canonical template's `tui.status_line` value and derive test
  expectations from that template where practical.
- Parse and compare the managed command's target script, expected script hash,
  interpreter, execution target, structure/version marker, and hash-mismatch
  recovery command.
- Present component drift as script-scoped changes with installed/repository
  values and an operator-facing effect. Use a raw command-structure hash only
  when an actual residual structure difference cannot be expressed through the
  parsed fields.
- Keep the existing pre-prompt summary concise and semantic.

## Scope and exclusions

In scope are the canonical Codex preferences template, the synchronizer,
focused tests, and the existing architecture/closeout records whose current
claims change. Existing uncommitted workspace-meta sync work remains preserved.
Excluded are host writes, Git network/publication actions, hook trust changes,
new managed fields, Claude renderer behavior, and nested repositories.

## Acceptance criteria

- The installed Codex preference renders the exact requested order from the
  canonical template, using `project-name` rather than `current-dir`.
- Unavailable pull-request or estimated-cost values remain normal native Codex
  behavior and do not cause synchronization errors.
- Pin-only drift is named as an expected script hash change and includes the
  installed/repository pins plus the trust-refresh effect.
- Known command changes, including the recovery command and structure/version,
  are reported separately; `command loader changed` is not used.
- A raw hash remains only as fallback evidence for a genuine unparsed command
  structure change.
- Interactive/check safety behavior is unchanged, and all repository-required
  verification passes in isolated homes.

## Risks and verification boundary

The main risk is normalizing away a real command change. Focused tests will
cover pin-only drift, parsed semantic changes, and an unparsed residual change
that must trigger the raw structure fallback. A real host dry-run may be used
read-only and declined with `N`; applying host configuration and UI smoke tests
remain outside this task.

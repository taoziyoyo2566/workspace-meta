# Daily Managed Configuration Sync Plan

Status: COMPLETE on 2026-09-08. Verified outcome:
`round8-daily-managed-config-sync-2026-09-08.changelog.md`.

## Goal

Add `make sync` as the daily, current-checkout workflow for inspecting and,
after an explicit `Y`, converging every host integration already owned by
workspace-meta. Keep `make bootstrap` as the full installation entry point and
`make agent-sync-check` as a read-only, non-interactive drift check.

## Current state

`scripts/sync_codex_config.py` already renders, validates, preserves unmanaged
Claude/Codex content, atomically writes changed targets, and rolls back earlier
writes after an operating-system failure. Its check output exposes internal
action wording rather than stable `OK`/`DRIFT`/`ERROR` diagnostics. The
env-sync skill is managed separately by `scripts/bootstrap-local.sh`, while
bootstrap also performs bootstrap-only Git hook configuration and Git identity
checks.

## Intended change

- Extend the existing Python synchronizer to render and report Codex guidance,
  Codex hooks, Codex preferences, Claude hooks/status line, and the env-sync
  skill through one prevalidated plan used by check, interactive sync, and
  direct bootstrap apply modes.
- Preserve the current field/block ownership and existing source-preserving
  merge functions. Retain current and expected managed preference values for
  clear drift output; use simpler target summaries for marked blocks/files.
- Add an interactive mode that always reports the dry-run first, skips the
  prompt when current, blocks the prompt on any error, accepts only `Y`/`y`,
  then applies changed targets and reports `UPDATED` only after real writes.
- Keep bootstrap-only Git hook initialization and Git identity checks in the
  shell entry point. Remove its separate env-sync copy after bootstrap delegates
  all managed host configuration to the Python synchronizer.
- Add the Make target, focused behavioral tests, and minimal canonical operator
  documentation for the daily command.

## Scope and exclusions

In scope are the existing managed surfaces under `~/.codex` and `~/.claude`,
the Make/shell entry points, tests, and their canonical operational
documentation. Excluded are Git network/publication commands, nested project
repositories, credentials, authorization/trust state, history, caches,
databases, host-owned fields, new ownership mechanisms, and real-host writes
during repository verification.

## Acceptance criteria

- Current state exits successfully without a prompt or writes and reports all
  five areas `OK`.
- Drift reports the managed area/field plus repository and current values;
  check mode exits 1 and states that no files were modified.
- Interactive drift prints the precise managed-value warning; Enter, `N`, and
  every value except `Y`/`y` decline without writes.
- Confirmation applies only changed managed targets, preserves unmanaged
  content, reports accurate `UPDATED`/`OK` statuses and counts, and is
  idempotent.
- Invalid or ambiguous TOML/JSON/managed structure reports `ERROR`, never
  prompts, and writes nothing.
- Bootstrap retains its initialization behavior and uses the shared managed
  synchronization implementation.
- All project-required verification passes, including isolated double
  bootstrap with unchanged second-run hashes.

## Risks and verification boundary

The main risk is accidentally widening mixed-file ownership or letting dry-run
and apply calculate different desired states. The implementation will build one
immutable in-memory sync plan before either reporting or writing and will
continue to compare parsed unmanaged TOML values. Tests will exercise CLI
behavior in isolated homes and verify byte-for-byte preservation and write
timing. Real Codex/Claude UI reload, hook trust review, and one real-terminal
interactive smoke test remain manual host verification.

# Changelog: portable project-documentation governance, round 1

## Scope

Established a minimal portable documentation contract before applying a small
vertical migration in NanoPi_R6S_Handbook.

## Workspace-meta changes

- Added `.agents/rules/documentation.md` as the sole portable owner for reader
  tasks, artifact roles, truth lifecycles, canonical ownership, growth, and
  incremental migration.
- Routed both thin adapters to the new owner and updated the ownership matrices.
- Added reverse-whitelist and regression coverage for the new module.
- Recorded W-R38 as the originating project incident and research-backed
  disposition.

## NanoPi_R6S_Handbook pilot

- Added `README.md`, `docs/index.md`, and project `AGENTS.md` as distinct human
  entry, topic-owner map, and agent delta surfaces.
- Migrated the reusable backup-health check into `docs/operations/`, replacing
  its legacy sections with pointers rather than a duplicate current procedure.
- Moved the 2026-08-25 stale-lock narrative into `docs/records/incidents/` and
  retained the old filename only as a compatibility redirect.
- Added ADR-0001 to record the incremental migration and truth-ownership model.
- Kept all unmigrated topics with their existing numbered owners and preserved
  the pre-existing untracked `PROJECT_DOCUMENTATION_STANDARD.md` unchanged.

## Boundaries

- The installed `~/.codex/AGENTS.md` remains unchanged until a separately
  authorized `make bootstrap` operation.
- No staging, commit, push, deployment, or live operation is part of this round.

## Verification

Passed for workspace-meta:

- `make test` — 56 tests passed, including the documentation-owner and
  symmetric-route regression.
- shell syntax, Python compilation with bytecode redirected to `/tmp`, and all
  versioned TOML parses.
- no versioned JSON/YAML inputs existed; this was reported as not applicable.
- reverse-whitelist checks, pre-commit guard, and `git diff --check`.
- two full bootstrap runs in an isolated `/tmp` repository and home; the second
  pass was stable. The initial local-clone attempt could not hard-link Git
  objects across filesystems, so the successful rerun used `--no-hardlinks`.

Passed for the separate NanoPi_R6S_Handbook repository:

- all 9 existing shell tests and applicable shell syntax checks.
- relative Markdown path and anchor validation, including the compatibility
  redirect and moved incident links.
- changed/new-file trailing-whitespace checks and `git diff --check`.

No live device or repository state was queried, so this documentation change
does not refresh or prove operational health.

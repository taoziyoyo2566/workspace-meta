# Changelog: portable implementation-shape governance

## Scope

Added a cross-project implementation-shape owner. Workspace-meta is the sole
implementation, verification, and commit scope; source cases are provenance,
not cross-repository work.

## Workspace-meta changes

- Added `.agents/rules/implementation.md` as the sole portable owner for
  artifact roles, normative fact ownership, durable comments, coherent change
  surface, and behavior-focused test shape.
- Kept the neighboring domains MECE: planning owns approved outcome and scope,
  verification owns evidence execution, review owns defect assessment, and
  rule authoring owns changes to behavior-shaping rules.
- Routed implementation, configuration, refactoring, and artifact-structure
  changes from both thin agent adapters.
- Refined required duplication to cover runtime-specific carriers and made each
  file's responsibility necessary and explainable rather than globally unique.
- Added concise repository-scope guidance to `AGENTS.md` so nested repositories
  stay excluded unless the user explicitly names them.
- Updated the architecture, top-level overview, and host-template owner matrix.
- Added W-R37 provenance with links to the official engineering sources that
  informed the rule.
- Extended the reverse whitelist and focused adapter/ownership regression
  coverage for the new module.

## Verification

Passed for workspace-meta:

- `make test` — 55 tests passed.
- `bash -n scripts/*.sh .githooks/pre-commit`.
- Python compilation with bytecode redirected to `/tmp`.
- `.githooks/pre-commit` and `git diff --check`.
- Two full bootstrap runs in an isolated `/tmp` repository and home; the second
  pass was stable, and generated TOML/JSON parsed.

## Gaps and boundaries

- No host configuration, staging, commit, push, or external write was
  performed. Workspace-meta remains reviewable with uncommitted and unpushed
  changes.

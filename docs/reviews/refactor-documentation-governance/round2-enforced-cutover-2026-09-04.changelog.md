# Changelog: enforced documentation cutover, round 2

## Trigger

The operator rejected the pilot-shaped result as insufficient for durable
quality. The first migration had valid role directories and links, but still
left dated host claims and incident narration in current Runbooks, a mixed
historical/current backlog, and seventeen permanent-looking root compatibility
pages. An unrelated untracked generic standard draft also remained visible in
the project root solely because its ownership had not yet been classified.

## Workspace-meta changes

- Refined `.agents/rules/documentation.md`: compatibility pointers now require
  a real external consumer contract, owner, and retirement condition; full
  cutover removes pointers without such a contract and preserves the mapping in
  a migration record and Git history.
- Required documentation-heavy and operational projects to encode stable
  mechanical constraints in a project-owned executable gate instead of relying
  on agent prose alone.
- Recorded the recurrence and disposition as W-R39.
- Added regression assertions for both refinements.

## NanoPi_R6S_Handbook changes

- Reduced root Markdown to `README.md`, `AGENTS.md`, and `CHANGELOG.md`; removed
  the numbered compatibility pages after updating archive links and retaining
  the old-to-new map in the dated migration record.
- Removed the operator-classified unrelated `PROJECT_DOCUMENTATION_STANDARD.md`.
  Because it was untracked, a checksum-identical temporary recovery copy was
  made under `/tmp` before deletion.
- Added a project-specific documentation contribution contract and ADR-0002 for
  the enforced cutover.
- Removed dated host observations, incident timelines, and deployment-result
  claims from current operations, reference, explanation, and template
  navigation; dated evidence remains in `docs/records/`.
- Rewrote the living backlog to contain only open work, dependencies, and
  acceptance boundaries. Completed work remains in records and Git history.
- Extended the documentation gate to enforce the root allowlist, canonical
  owner/index coverage, headings, internal links and anchors, required Runbook
  concepts, ordered action sections, and date separation for current guidance.
  Negative fixtures prove that extra root pages, dated current claims, and
  missing stop/recovery sections are rejected.
- Added a GitHub Actions workflow that runs the repository tests and syntax
  checks on pushes and pull requests.

## Verification

Passed for workspace-meta:

- `make test` — 56 tests passed;
- Bash syntax, Python compilation, TOML parsing, pre-commit guard, and
  `git diff --check`.

Passed for NanoPi_R6S_Handbook:

- 9 existing shell behavior/source tests plus the documentation gate;
- documentation-gate negative fixtures;
- Bash/Python syntax, internal path/anchor checks, high-confidence secret scan,
  and `git diff --check`.

ShellCheck, Markdownlint, and a standalone YAML parser were not installed and
remain explicit tool gaps; the workflow's exact shell blocks were run locally.
External links were not exhaustively rechecked. No live NanoPi, Restic
repository, remote service, Git publication, or history mutation occurred.

## Activation and publication state

Both repositories remain dirty, uncommitted, and unpushed. The managed Codex
host adapter has not been synchronized in this round; host activation remains a
separate protected `make bootstrap` operation after result review.

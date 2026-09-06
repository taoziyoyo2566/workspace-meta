# Plan: workspace-meta review remediation

- **Date**: 2026-09-06
- **Status**: IMPLEMENTED_AND_VERIFIED
- **Scope**: workspace-meta working tree only

## Goal

Close the commit-readiness findings from the 2026-09-06 review without
touching nested project repositories, host configuration, or Git publication.

## Changes

1. Make the missing-project-entry backstop run before substantive project work,
   including read-only review and host/external actions, rather than only before
   a working-tree write.
2. Keep status-line behavior and current documentation aligned, including the
   five-hour remaining-usage display and non-finite-input degradation.
3. Remove portable rule procedures and operational instructions from the
   architecture explanation; link to their canonical rule and runbook owners.
4. Add a project-owned documentation gate for root entry files, canonical
   routes, safety-floor source binding, internal links, current-versus-record
   date separation, and the new-VPS runbook contract.
5. Correct the historical review's finding count and record the remediation in
   a new round changelog instead of rewriting its historical findings.
6. Harden the documentation gate after targeted review: discover current
   documents recursively inside owned directories, inspect dates in visible
   prose while excluding fenced examples, and add negative coverage for each
   previously unguarded gate family.

## Risks and exclusions

- The documentation gate must inspect only workspace-meta-owned paths and must
  not descend into `projects/` or host-local files.
- Dated review paths in Markdown link destinations are routing metadata, not
  current prose. Link labels and inline-code text remain visible to lifecycle
  checks, while fenced examples do not.
- Adapter safety-floor duplication remains intentional, but the gate must bind
  every copied clause to a canonical owner and detect drift.
- Existing user changes to the status-line implementation, tests, comments, and
  architecture wording are preserved and reviewed as part of the result.
- No real `make bootstrap`, staging, commit, push, PR, or nested-project edit is
  authorized by this plan.

## Verification

- `make test`, including focused negative tests for root entries, routes,
  safety-floor binding, index coverage, links and anchors, truth lifecycle,
  nested current documents, runbook structure, and tracked route targets;
- shell syntax and Python byte compilation;
- TOML/JSON parsing and `git diff --check`;
- reverse-whitelist and pre-commit checks for every new path;
- two bootstrap runs against an isolated temporary HOME with stable second-run
  hashes;
- `make agent-sync-check` as a read-only host drift report;
- manual gaps: a fresh Claude project session and real status-line UI remain
  host verification.

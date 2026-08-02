# Plan: Harden review scope activation

- **Date**: 2026-08-02
- **Level**: Governance / review-method refinement
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user-authorized by “请完善”

## Goal

Make review scope activation explicit enough that a plan merely present in a
repository cannot pull nested repositories or host-local state into an
otherwise local review.

## Scope

1. Refine the existing repository-boundary guidance in
   `.agents/rules/review.md`.
2. Add a reusable review scope snapshot template.
3. Align W-R33's application guidance and record this round's evidence.

## Exclusions

- Do not inspect or modify nested project repositories.
- Do not inspect or modify host-local configuration.
- Do not change project-migration plan status without explicit scope and fresh
  acceptance evidence.
- Do not add a second rule owner or change Git publication authorization.

## Expected effect

Only a boundary named by the user, a plan explicitly adopted by the current
request, or a documented acceptance check that cannot run without the boundary
may expand review evidence beyond the current repository.

## Verification

- `make test`.
- `bash -n scripts/*.sh .githooks/pre-commit`.
- `python3 -m py_compile scripts/*.py tests/*.py`.
- `git diff --check`.
- Static confirmation that active review guidance contains no project-specific
  names and includes all scope activation conditions.

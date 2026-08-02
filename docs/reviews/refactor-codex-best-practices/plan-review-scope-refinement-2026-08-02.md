# Plan: Refine existing review scope guidance

- **Date**: 2026-08-02
- **Level**: Governance / review-method refinement
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user-authorized by “总结一下经验到rules，避免类似问题”

## Goal

Make the existing review scope rule operational at repository boundaries without
creating a duplicate rule owner.

## Scope

1. Refine the existing `Review Shape` guidance in `.agents/rules/review.md`.
2. Record the recurrence as W-R33 and point it to the existing review owner.
3. Add a round changelog with verification results.

## Exclusions

- Do not create a second nested-repository or authorization rule.
- Do not change any nested project repository or host-local configuration.
- Do not stage, commit, push, or publish this workspace-meta repository.

## Expected effect

Before a review crosses a repository or host boundary, the agent records the
nearest Git root and explicitly classifies the related state as in-scope or
supplemental. Plan references and directory names alone do not expand scope.

## Verification

- `make test`.
- `bash -n scripts/*.sh .githooks/pre-commit`.
- `python3 -m py_compile scripts/*.py tests/*.py`.
- `git diff --check` and final status/diff inspection.

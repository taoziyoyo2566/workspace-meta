# Plan: portable implementation-shape governance

- **Date**: 2026-08-28
- **Level**: Engineering / cross-project implementation governance
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user-authorized by “按照最佳实践来设计，实施” and refined
  to require a general design rather than a project-specific rule. Corrected
  on 2026-08-28 to keep workspace-meta as the sole implementation,
  verification, and commit scope; source cases provide provenance only.

## Goal

Add one agent-neutral owner for how an approved change is represented in code,
comments, tests, documentation, and files. Keep planning, implementation,
verification, review, and rule authoring mutually exclusive and collectively
exhaustive without copying project details into resident guidance.

## Design basis

- A change should be the smallest self-contained unit that reviewers can
  understand; size is a design signal, not a fixed line-count gate.
- Comments explain local intent or constraints that code cannot express. Design
  alternatives, review history, and implementation narrative belong in durable
  decision or review artifacts when they are still useful.
- Tests normally exercise observable behavior and contracts. Text-shape checks
  are reserved for non-observable, load-bearing policy or ordering invariants.
- One normative fact has one canonical owner. Other required carriers should be
  generated from it or reference it rather than become independent copies.

These principles follow current Google engineering guidance on small changes,
comments, and behavior-focused tests, plus GitHub guidance on reusable workflow
components.

## MECE ownership

| Question | Canonical owner |
|---|---|
| What outcome and scope are approved? | `planning.md` |
| How should that outcome be represented in artifacts? | new `implementation.md` |
| How is the result proven? | `verification.md` |
| How are defects classified and reported? | `review.md` |
| How are behavior-shaping rules created or revised? | `rule-authoring.md` |

## Scope

1. Add `.agents/rules/implementation.md` with artifact-boundary, single-source,
   comment, change-surface, and test-design contracts.
2. Route implementation, configuration, refactoring, and artifact-structure
   changes to it from both thin adapters.
3. Add it to the documented owner matrices and focused regression tests.
4. Record the source incident as portable provenance.

## Exclusions

- No source-project, language, framework, or platform-specific procedure enters
  the shared owner.
- No arbitrary file-count or line-count limit is introduced.
- No nested repository change or cross-repository verification dependency.
- No staging, commit, push, host mutation, or external write.

## Verification

- Workspace-meta: unit tests, shell/Python syntax, configuration parsing,
  reverse-whitelist/pre-commit checks, and isolated two-pass bootstrap hashes.
- Report unavailable checks as gaps rather than passed.

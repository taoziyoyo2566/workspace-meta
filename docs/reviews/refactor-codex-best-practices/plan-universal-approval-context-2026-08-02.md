# Plan: Add context to protected-action approval requests

- **Date**: 2026-08-02
- **Level**: Governance / authorization UX refinement
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user-authorized by “请继续，这么实现吧”

## Framework and owner pre-check

- The existing portable owner is `.agents/rules/authorization.md`; Git-specific
  transaction details remain in `git-*.md`, while Codex runtime prompts remain
  in `codex-runtime.md`.
- The current rule already requires target, operation, impact, exclusions,
  prerequisites, and check state for protected actions, but it does not provide
  a required user-facing summary shape before asking for consent.
- Conclusion: extend the existing authorization owner with a positive
  action-summary recipe; do not create a second approval owner or host-local
  executable permission rule.

## Goal

Require every protected-action consent request to explain what will happen, why
it is needed, what it targets, the expected result, risks/recovery, exclusions,
checks/gaps, and the exact operation being authorized.

## Scope

1. Add the universal action-summary contract and reusable template to
   `.agents/rules/authorization.md`.
2. Clarify the shared architecture/README description of portable semantic
   authorization versus host-local technical permission prompts.
3. Add a regression assertion for the canonical rule and record provenance in
   `feedback-register.md`.
4. Add a round changelog with verification evidence.

## Exclusions

- Do not change Git publication checkpoints or transaction boundaries.
- Do not change host-local `~/.codex/rules`, trust state, approval history, or
  runtime configuration.
- Do not require conversational confirmation for ordinary read-only work or
  already-authorized in-scope working-tree edits.
- Do not require a fixed confirmation phrase or expose secrets in the summary.
- Do not stage, commit, push, or publish this repository.

## Expected effect

Users can understand the purpose, target, consequence, and boundary of a
protected operation before approving it, regardless of whether the operation is
Git, a host change, an external write, a deployment, or a live mutation.

## Verification

- `make test`.
- `bash -n scripts/*.sh .githooks/pre-commit`.
- `python3 -m py_compile scripts/*.py tests/*.py`.
- `git diff --check`.
- Static confirmation that the canonical authorization owner contains the
  required fields and preserves the read-only/technical-permission exceptions.
- Final status and diff review; leave changes local and unpublished.

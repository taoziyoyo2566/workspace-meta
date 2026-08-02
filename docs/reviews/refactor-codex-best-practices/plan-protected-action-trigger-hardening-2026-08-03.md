# Plan: Harden Protected-Action Brief trigger wording

- **Date**: 2026-08-03
- **Level**: Governance / authorization behavior recurrence
- **Status**: IMPLEMENTATION_COMPLETE
- **Scope**: workspace-meta shared authorization owner, resident documentation,
  provenance, and regression tests

## Direction check

The prior rule is in the canonical owner and installed Codex route, but its
trigger says “before asking the user to approve”. A real recurrence showed that
an agent can interpret a host/configuration command recommendation as merely a
next-step instruction and omit the brief. The direction therefore needs a
trigger clarification and a recurrence test, not another host-local permission
rule or a second shared owner.

## Goal

Require the Protected-Action Request Brief before the agent presents a protected
operation for execution, asks the user to run it, or asks the user to approve
it, while preserving the exemption for read-only work and already-authorized
in-scope working-tree edits.

## Scope

- Clarify `.agents/rules/authorization.md` with the three observable trigger
  forms and the direct-request/task-authorization distinction.
- Align the README and architecture description with the clarified trigger.
- Record the recurrence as a new provenance entry.
- Add static regression assertions for the trigger wording and exemptions.
- Add a round changelog with verification evidence.

## Exclusions

- Do not modify host-local `~/.codex/rules`, trust state, approval history, or
  generated host configuration.
- Do not add a second authorization owner or duplicate the full brief in
  adapters.
- Do not require briefs for ordinary reads, tests, or already-authorized
  in-scope working-tree edits.
- Do not stage, commit, push, or create a PR.

## Verification

- `make test`
- `bash -n scripts/*.sh .githooks/pre-commit`
- `python3 -m py_compile scripts/*.py tests/*.py`
- `git diff --check`
- static confirmation that source and installed-route documentation use the
  clarified trigger and preserve the safe-work exceptions

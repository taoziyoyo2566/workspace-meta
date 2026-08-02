# Plan: Add a complete new-VPS runbook

- **Date**: 2026-08-03
- **Level**: Operations / documentation
- **Status**: IMPLEMENTATION_COMPLETE_WITH_VERIFICATION_GAP
- **Direction**: user reported that a new VPS still leaves configuration steps unclear

## Goal

Provide one executable, current runbook for bringing a new VPS from a fresh
checkout to a verified workspace-meta + Codex/Claude setup.

## Scope

1. Add `docs/runbooks/new-vps.md` covering prerequisites, checkout, Git identity,
   environment probing, bootstrap, Codex/Claude host-local setup, hook trust,
   project boundaries, verification, daily operation, and recovery paths.
2. Link the runbook from `README.md` and the configuration architecture document.
3. Add the runbook path to the explicit reverse whitelist.
4. Add a round changelog with verification evidence.

## Exclusions

- Do not write `~/.codex`, `~/.claude`, credentials, trust state, approval rules,
  or host-local configuration.
- Do not copy host-local `default.rules` or `permissions.rules` into the repo.
- Do not change bootstrap or synchronizer behavior in this documentation round.
- Do not stage, commit, push, or publish the workspace-meta repository.

## Expected effect

A new VPS operator can distinguish shared repository artifacts from host-local
state, execute the setup in order, understand expected output, and diagnose the
common stale-registry, hook-trust, permission, Python, and repository-boundary
failures without guessing or copying another host's private state.

## Verification

- Check every command and path in the runbook against the current scripts and
  configuration ownership documents.
- Parse the runbook's fenced shell snippets with `bash -n` using a temporary
  assembled script where feasible; do not execute host-mutating snippets.
- Run `make test`, syntax checks, generated-format parsing, and `git diff --check`.
- Verify the README and architecture links resolve inside this repository.
- Record the result and any host/UI checks that remain manual.

Implementation is complete. The remaining verification gap is intentional:
full `make bootstrap` twice was not run in the working checkout because it
writes `.git/config` and host-local agent files; the runbook records that as an
operator-side activation and UI verification step.

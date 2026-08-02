# Plan: Remediate Hook trust classification and Git approval routing

- **Date**: 2026-08-02
- **Level**: Bugfix / governance authorization hardening
- **Status**: IMPLEMENTATION_COMPLETE_WITH_VERIFICATION_GAP
- **Scope**: workspace-meta repository only; working-tree edits and local checks

## Goal

Close the two P1 review findings without changing host-local trust state or Git
publication/integration transaction boundaries:

1. warn whenever the managed Codex hook definition changes, including when
   Codex-owned `[hooks.state]` is simultaneously normalized;
2. require the existing `authorization.md` Protected-Action Request Brief on
   every protected Git route before consent or execution is requested.

## Scope

- Track Hook definition changes separately from host-state normalization in
  `scripts/sync_codex_config.py` and add regression coverage.
- Add explicit `authorization.md` prerequisites to Git publication,
  integration, recovery, and branch/worktree transaction modules.
- Update the Codex/Claude route adapters and architecture task-loading table.
- Add static tests proving the route-to-brief contract.
- Add a round changelog after verification.

## Exclusions

- Do not modify `~/.codex`, `~/.claude`, host trust hashes, authorization rules,
  or approval history.
- Do not stage, commit, push, create a PR, merge, rebase, reset, or clean.
- Do not rewrite historical review plans or changelogs.
- Do not duplicate the full action brief into Git modules; `authorization.md`
  remains its sole semantic owner.
- Preserve unrelated and pre-existing working-tree and untracked changes.

## Implementation

### Hook trust classification

`replace_hook_managed_block()` will return separate metadata for state
normalization and managed-definition change. The latter compares the current
managed block with the rendered block after removing the preserved
`[hooks.state]` section. `main()` will base the `/hooks` warning only on the
definition-change flag, while the existing state-only action remains quiet.

Tests will cover state-only normalization, state normalization plus evaluator
hash/template change, new installation/migration, and idempotent reruns.

### Git authorization routing

The protected Git modules will explicitly require reading and applying the
`Protected-Action Request Brief` before presenting or accepting the exact
operation. Module-specific fields and the publication command bundle remain
supplemental. The adapters and architecture table will show
`authorization.md + git.md + git-*.md` for protected Git routes.

## Verification

- `make test`
- `bash -n scripts/*.sh .githooks/pre-commit`
- `python3 -m py_compile scripts/*.py tests/*.py`
- TOML/JSON/YAML parsing checks
- isolated temporary-HOME bootstrap twice, with stable managed hashes on the
  second run
- `git diff --check`
- final status/diff review; leave all changes local and unpublished

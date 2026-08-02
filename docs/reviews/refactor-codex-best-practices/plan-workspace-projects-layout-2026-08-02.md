# Plan: Separate workspace governance from project checkouts

- **Date**: 2026-08-02
- **Level**: Workspace layout and operator-documentation maintenance
- **Status**: IMPLEMENTATION_COMPLETE_WITH_VERIFICATION_GAP
- **Direction**: user-authorized by “按照建议来帮我处理一下”

## Goal

Keep `~/workspace` as the workspace-meta governance repository while placing
independent project repositories under `~/workspace/projects/`, so root-level
governance files are not visually mixed with application projects.

## Scope

1. Create `~/workspace/projects/`.
2. Move the complete `reality-ops`, `saberu`, and `yt2srt` repositories into it,
   preserving each repository's Git metadata, branch, and working-tree state.
3. Update living operator documentation and the current host's explicit Saberu
   trust path to the new location.
4. Leave workspace-meta scripts, adapters, shared rules, historical evidence,
   credentials, and host runtime data outside this change.

## Safety boundaries

- Preserve the pre-existing uncommitted change in Saberu's
  `inventory/vps_runner/dev/hosts.yml`.
- Do not stage, commit, push, or publish any repository.
- Do not rewrite completed plans, changelogs, reviews, or historical incident
  records merely because they contain the old path.
- Do not broaden the root reverse-whitelist to include project contents;
  `projects/` remains outside workspace-meta tracking.

## Verification

- Confirm each moved repository resolves to the new nearest `.git` root and
  retains its branch, HEAD, and pre-existing dirty state.
- Confirm the workspace-meta root remains the only Git root for governance files
  and that `projects/` is ignored by its reverse whitelist.
- Parse the updated host TOML and confirm only the explicit Saberu trust path
  changed.
- Search living documentation for stale active checkout commands; preserve
  historical references with a dated migration record.
- Run the workspace-meta documented checks proportionate to this layout-only
  change, including `git diff --check` and repository status inspection.

Implementation is present in the current working tree: the root documentation
uses `~/workspace/projects/<project>/`, the three nested repositories resolve to
their own Git roots, and `projects/` remains ignored by workspace-meta. The
current host's private trust/UI state remains outside this repository and is
recorded as a manual verification gap.

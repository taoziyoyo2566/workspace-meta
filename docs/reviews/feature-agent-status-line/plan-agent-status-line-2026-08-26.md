# Claude/Codex Status-Line Integration Plan

Status: Implemented and verified locally on 2026-08-26. Host installation, Git
publication, and live configuration writes remain excluded.

## Goal

Bring the requested directory, Git branch, model, context, token-detail, and
cost display into workspace-meta while respecting the two clients' different
extension contracts:

- Claude Code runs a configured `statusLine.command` and sends session JSON on
  stdin;
- Codex configures ordered native footer items through `/statusline` and
  `tui.status_line`.

The result should express one display intent without inventing a shared runtime
protocol that neither client provides.

## Scope and exclusions

In scope:

- add a portable Claude status-line renderer under `scripts/`;
- reconcile a workspace-meta-owned Claude `statusLine` setting alongside the
  existing managed SessionStart group;
- retain the existing Codex native status-line items for model, context, Git,
  tokens, and weekly usage;
- use Claude's documented status-line JSON fields instead of session discovery
  by cwd or hard-coded model pricing;
- add unit, migration-safety, idempotence, and isolated-bootstrap coverage;
- update architecture, ownership, and operator documentation.

Excluded:

- writing real `~/.claude` or `~/.codex` configuration in this round;
- reading or synchronizing private Claude/Codex history databases or JSONL
  transcripts;
- estimating Codex dollar cost when no documented native footer item supplies
  it;
- replacing an unrecognized existing Claude status-line command automatically;
- staging, committing, pushing, PR creation, or deployment.

## Verified product baseline

Claude Code documents `/statusline` and the `statusLine` command configuration.
Its stdin payload includes `workspace.current_dir`, `model.display_name`,
`context_window.used_percentage`, `context_window.current_usage`,
`cost.total_cost_usd`, `session_id`, and `transcript_path`.

The current Codex configuration reference defines `tui.status_line` as an
ordered list of native footer item identifiers. The repository already manages
that field, and the operator confirmed the current `/statusline` command is
available interactively. Codex does not use Claude's stdin callback contract.

## Approach and risks

1. Implement the Claude renderer in Python so the repository's existing
   Python discovery works on Linux and macOS without `/bin/sh` Bashisms,
   Homebrew-only paths, or repeated `jq` processes.
2. Use only the documented live payload for token and cost display. Treat token
   detail as current-context/current-response data and cost as Claude's own
   client-side session estimate.
3. Run Git branch discovery read-only, without optional locks, with a short
   timeout and quiet failure outside repositories.
4. Install a hash-pinned command through the existing atomic synchronizer.
   Refuse an unrecognized pre-existing `statusLine` value rather than overwrite
   host-owned configuration.
5. Document that parity is semantic, not byte-for-byte: Codex uses its native
   footer and may omit Claude-only fields such as estimated USD cost.

The main compatibility risk is changing Claude settings ownership. The
synchronizer therefore adopts only a missing field or its own marker-bearing
field. A real Claude and Codex TUI smoke test remains manual host verification.

## Verification

- renderer tests for color thresholds, home shortening, token formatting,
  official cost use, Git/non-Git behavior, and malformed input;
- synchronizer tests for install, preservation, refusal, hash pinning, and
  idempotence;
- `make test`;
- `bash -n scripts/*.sh .githooks/pre-commit`;
- Python byte compilation for scripts and tests;
- TOML/JSON/YAML parsing checks and `git diff --check`;
- two bootstraps against an isolated temporary HOME with unchanged managed
  hashes on the second run;
- manual host gap: run Claude and Codex `/statusline` after an separately
  authorized `make bootstrap`.

## Handoff

Record the implementation and verification outcome in a dated round changelog
in this directory. Leave all repository changes uncommitted and unpushed for
operator review.

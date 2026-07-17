# Plan: Unify Workspace-Meta Agent Hooks

## Purpose

Finish the Codex configuration-management work as a coherent, documented system
instead of leaving Claude and Codex with different failure policies and three
concurrent Codex handlers.

## Scope

- Add project-level Codex governance for workspace-meta.
- Replace three independent status hooks with one ordered status evaluator.
- Share status semantics between Claude Code and Codex.
- Rate-limit remote-unavailable warnings through host-local cache state.
- Pin the evaluator content hash in the trusted hook command.
- Upgrade existing Claude and Codex managed hooks without overwriting unrelated
  host configuration.
- Validate all target files before any host file is written.
- Add architecture documentation, regression tests, and a round changelog.

## Out Of Scope

- Synchronizing model choice, project trust, hook trust state, credentials,
  approval rules, plugins, system skills, history, logs, caches, or databases.
- Automatically trusting Codex hooks.
- Automatically deleting orphan hook trust entries.
- Automatically committing or pushing this repository.
- Reworking the environment registry format or its GNU `date` portability in
  this round.

## Level And Cost

- Level: engineering, cross-agent configuration behavior.
- Cost: medium.
- Main risks: host config loss, stale hook trust, noisy offline warnings, partial
  multi-file updates, and semantic drift between Claude and Codex.

## Current-State Gaps

1. Codex has three concurrently launched handlers; freshness fetch and ahead
   calculation can observe different remote-ref states.
2. Codex warns on remote failure while Claude silently ignores it.
3. Claude hook installation is marker-only and cannot upgrade existing commands.
4. The existing test proves JSON production but not the Codex host contract.
5. `sync_codex_config.py` writes AGENTS before validating the hook target, so a
   later failure can leave a partial update.
6. Workspace-meta has no repository-level `AGENTS.md` defining artifact and
   commit authorization policy.

## Design

### Shared evaluator

`scripts/workspace_status.py` evaluates, in order:

1. repository availability and working-tree state;
2. remote freshness with a bounded fetch timeout;
3. ahead/behind counts from one post-fetch ref snapshot;
4. environment-registry freshness.

It emits no output when healthy, otherwise one JSON object containing a single
`systemMessage`. Both Claude and Codex consume the same state policy.

### Offline policy

- A successful remote check is cached under `~/.cache/workspace-meta/status.json`.
- Repeated session starts skip fetch for a short minimum interval.
- Remote-unavailable warnings are emitted on the first unknown state or after the
  last warning TTL expires; routine offline sessions inside that window stay quiet.
- Behind, dirty/unpushed, and stale-registry conditions are never rate-limited.

### Hook trust

The installed hook command contains the expected SHA-256 of
`workspace_status.py`. A small Python loader verifies the file before executing
it. Changing evaluator behavior therefore changes the hook command and forces a
new Codex `/hooks` trust review.

### Host synchronization

The synchronizer renders and validates Codex AGENTS, Codex TOML, and Claude JSON
before writing any target. It replaces only workspace-meta-owned blocks/groups
and preserves all unrelated host content.

## Acceptance Criteria

- Codex installs one SessionStart handler, not three.
- Claude installs one equivalent workspace-meta SessionStart handler.
- Both agents use the same evaluator hash and state policy.
- Remote failure is rate-limited; behind, dirty/ahead, and stale registry remain
  visible.
- Invalid TOML, invalid JSON, or ambiguous mixed hook ownership changes no host
  target.
- Existing model/project trust/hook trust and unrelated Claude settings survive.
- `make test`, Bash syntax, Python compilation, structured parsing, pre-commit,
  isolated double-bootstrap hashes, and `git diff --check` pass.
- Architecture docs describe ownership, lifecycle, troubleshooting, and machine
  onboarding.

## Verification Evidence

- Codex 0.144.1 source: `SessionStart` parses JSON `systemMessage` as a warning and
  treats plain stdout as model context.
- Codex official hooks documentation: lifecycle events, matcher semantics, trust
  hashes, and common output fields.
- Local runtime: `codex-cli 0.144.1`; current config and host fields parse cleanly.

## Roadmap

1. Land governance and plan artifacts.
2. Implement and test the shared evaluator.
3. Refactor host synchronization for both agents.
4. Update templates and documentation.
5. Apply to isolated HOME, then current host; complete the round changelog.

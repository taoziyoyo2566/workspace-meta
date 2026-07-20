# Agent Configuration And Rule Ownership

Workspace-meta manages a narrow, reviewable subset of Claude and Codex
configuration. It does not mirror either home directory.

## Managed And Host-Local Surfaces

| Surface | Ownership | Sync behavior |
|---|---|---|
| workspace `CLAUDE.md` | workspace-meta | versioned thin Claude adapter |
| `~/.codex/AGENTS.md` | mixed | replace only the workspace-meta marked block |
| `.agents/rules/*.md` | workspace-meta | shared portable owners plus explicit agent runtime modules |
| `~/.codex/config.toml` | mixed | replace only the marked status-hook block |
| `~/.claude/settings.json` | mixed | converge one dedicated SessionStart group |
| `scripts/workspace_status.py` | workspace-meta | one ordered status policy used by both agents |
| model/reasoning defaults, credentials, trust, history, caches | host/user | never synchronized |
| `~/.codex/rules/*.rules` | host executable authorization | never synchronized |
| project agent/governance files | project repository | project facts and deltas travel with that project |

## Portable Rule Owners

| Domain | Workspace owner | Project may add |
|---|---|---|
| authorization | `authorization.md` | live/external constraints and risk fields |
| Git inspection/state | `git.md` | canonical remote and project facts |
| branch/worktree/stash | `git-branches.md` | topology, lifecycle, persistence, target |
| publication | `git-publication.md` | message format, checks, CI, PR fields |
| integration/retirement | `git-integration.md` | routes, topology, release/archive policy |
| recovery/destructive Git | `git-recovery.md` | stricter ref/archive tooling |
| planning/handoff | `planning.md` | artifact schema, sources, branch/live gates |
| verification | `verification.md` | commands, environments, thresholds, CI |
| review | `review.md` | domain scenarios, baseline, risk refinements |
| capability selection | `capabilities.md` | project toolchain and adapters |
| secret safety | `secrets.md` | stores, paths, consumers, rotation, checks |
| environment truth | `environment-truth.md` | project environment/command mapping |
| rule authoring/feedback | `rule-authoring.md` | project-only owners and adapters |

`codex-runtime.md` owns only Codex sandbox, execpolicy, deferred discovery, and
configuration mechanics. Claude-specific mechanics remain in its adapter or
actual host configuration. Neither may redefine portable behavior.

## Adapter Rule

Resident adapters stay compact: direct trigger-to-owner routing, an intentional
safety floor, and agent-only mechanics. A safety-floor copy names its canonical
owner and is tested for drift. Path/project adapters state only narrower facts.

`scripts/sync_codex_config.py` atomically prevalidates and converges the marked
Codex AGENTS/config blocks and Claude SessionStart group while preserving
unmanaged content. See `docs/architecture/codex-config-management.md`.

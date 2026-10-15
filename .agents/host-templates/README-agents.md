# Agent Configuration And Rule Ownership

Workspace-meta manages a narrow, reviewable subset of Claude and Codex
configuration. It does not mirror either home directory.

## Managed And Host-Local Surfaces

| Surface | Ownership | Sync behavior |
|---|---|---|
| workspace `CLAUDE.md` | workspace-meta | versioned thin Claude adapter |
| `~/.codex/AGENTS.md` | mixed | replace only the workspace-meta marked block |
| `.agents/rules/*.md` | workspace-meta | shared portable owners plus explicit agent runtime modules |
| `.agents/env/*.yml` | host runtime | generated locally and ignored by Git; each host probes itself |
| `~/.codex/config.toml` | mixed | replace only the marked status-hook block and reconcile declared preference fields |
| `~/.claude/settings.json` | mixed | converge one dedicated SessionStart group and one marker-bearing `statusLine` object; refuse an unrecognized existing status line |
| `scripts/workspace_status.py` | workspace-meta | one ordered status policy used by both agents |
| `scripts/claude_status_line.py` | workspace-meta | render Claude's command status line from documented stdin fields; Codex uses native `tui.status_line` items |
| model/reasoning defaults, credentials, trust, history data, caches, and unlisted preferences | host/user | never synchronized |
| `~/.codex/rules/*.rules` | host executable authorization | never synchronized |
| project agent/governance files | project repository | project facts and deltas travel with that project; every runtime the project is operated with needs an entry file it loads, importing one canonical owner |

## Portable Rule Owners

| Domain | Workspace owner | Project may add |
|---|---|---|
| authorization | `authorization.md` | live/external constraints and risk fields |
| Git inspection/state | `git.md` | canonical remote and project facts |
| change flow and branch/worktree/stash | `git-branches.md` | main branch, type prefixes, merge route, topology, target, and optional durable contract carrier/schema |
| publication | `git-publication.md` | message format, checks, CI, PR fields |
| integration/retirement | `git-integration.md` | routes, topology, archive policy |
| releases and version tags | `releases.md` | starting version, prefix, compatibility surface, status surface, rollback procedure |
| deployment: what may serve users, cadence, temporary deployments, rollback checks | `deployment.md` | main deployment branch, deploy targets and inventory, entry points and guards, deployment record, environment tiers |
| recovery/destructive Git | `git-recovery.md` | stricter ref/archive tooling |
| planning/handoff, understanding the request | `planning.md` | artifact schema, sources, where verified findings are recorded, branch/live gates |
| technical reasoning: premises, knowledge states, evidence, competing explanations/probes, independent judgment, uncertainty | `reasoning.md` | domain evidence sources, diagnostic commands/surfaces, thresholds, invariants, and safer probes |
| implementation shape | `implementation.md` | language/framework conventions and architecture |
| documentation information architecture | `documentation.md` | project entry points, topic map, commands, domain constraints |
| file checks by type | `file-checks.md` | commands per file class, accepted warnings, stricter gates |
| verification | `verification.md` | commands, environments, thresholds, CI |
| review and problem reports | `review.md` | domain scenarios, baseline, risk refinements |
| proposals and problem follow-up | `problem-follow-up.md` | incident records and owners of deferred work |
| capability selection, quality before speed | `capabilities.md` | project toolchain and adapters |
| secret safety | `secrets.md` | stores, paths, consumers, rotation, checks |
| temporary files | `temporary-files.md` | ignored local directory for large data |
| environment truth | `environment-truth.md` | project environment/command mapping |
| feedback intake and rule authoring | `rule-authoring.md` | project-only owners and adapters |

`codex-runtime.md` owns only Codex sandbox, execpolicy, deferred discovery, and
configuration mechanics. Claude-specific mechanics remain in its adapter or
actual host configuration. Neither may redefine portable behavior.

## Adapter Rule

Resident adapters stay compact: direct trigger-to-owner routing, an intentional
safety floor, and agent-only mechanics. A safety-floor copy names its canonical
owner and is tested for drift. Path/project adapters state only narrower facts.

`scripts/sync_codex_config.py` atomically prevalidates and converges the marked
Codex AGENTS/config blocks, declared Codex preference fields, and Claude
SessionStart/status-line fields while preserving unmanaged content. See
`docs/architecture/codex-config-management.md`.

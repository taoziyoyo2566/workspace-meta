# Agent Configuration And Rule Ownership

Workspace-meta manages a narrow, reviewable subset of Claude and Codex
configuration. It does not mirror any agent config dir.

## Managed And Host-Local Surfaces

Agent configuration lives in five layers. Each class of content has exactly one
owning layer. A lower layer may add narrower facts, never a second copy of a
higher layer's content.

| Layer | Where | Owns |
|---|---|---|
| 1. Organization-managed | server-managed settings, managed `CLAUDE.md`, policy limits | the organization's policy. Workspace-meta never writes it, and no managed surface may conflict with it. |
| 2. Host user | every agent config dir the operator uses: `~/.claude`, each relocated Claude config dir (for example `~/.claude-<account>`), and `~/.codex` | per config dir and host-local: credentials, trust, permissions and auto mode, model and effort defaults, plugins, MCP servers, history, auto memory, and the account's own user-level instruction files, rules, skills, and agents. Of these, workspace-meta writes only the managed surfaces below, converged into each Claude config dir. |
| 3. Workspace | `~/workspace` | portable rules, adapters, host templates, scripts, provenance |
| 4. Project | `~/workspace/projects/<project>` | `AGENTS.md` as the canonical agent facts, or an existing owner the operator keeps, with a thin adapter per runtime that imports it; `.claude/settings.json` guardrails, project skills and agents, `.mcp.json`, project docs |
| 5. Project-local | inside the project, ignored or excluded from Git | personal `CLAUDE.local.md` and `.claude/settings.local.json`; in a clone of a repository the operator does not own, `CLAUDE.local.md` is also the local carrier of that project's agent facts |

The Claude config dirs that workspace-meta manages on a host are the
`CLAUDE_CONFIG_DIRS` list, colon-separated. When it is unset, the sync engine
uses `~/.claude` plus every `~/.claude-*` directory that holds a `.claude.json`,
skips names that look like copies or backups, and prints both lists before any
write. The list is host-local input to `make sync`; it is never committed. In
each listed Claude config dir, workspace-meta manages exactly:

- one dedicated SessionStart group in `settings.json`, which runs the shared
  status evaluator;
- the marker-bearing `statusLine` in `settings.json`; an existing status line
  without the workspace-meta marker belongs to another owner and is kept and
  reported;
- one skill per `.agents/host-templates/<name>-SKILL.md` template, installed
  whole as `skills/<name>/SKILL.md` (today `env-sync`, `project-bootstrap`, and
  `interview`) and marked as workspace-meta's; an existing skill of the same
  name without that marker belongs to another owner and is kept and reported.

| Surface | Ownership | Sync behavior |
|---|---|---|
| workspace `CLAUDE.md` | workspace-meta | versioned thin Claude adapter |
| `~/.codex/AGENTS.md` | mixed | replace only the workspace-meta marked block |
| `.agents/rules/*.md` | workspace-meta | shared portable owners plus explicit agent runtime modules |
| `.agents/env/*.yml` | host runtime | generated locally and ignored by Git; each host probes itself |
| `~/.codex/config.toml` | mixed | replace only the marked status-hook block and reconcile declared preference fields |
| `settings.json` of each Claude config dir | mixed | converge one dedicated SessionStart group; install an absent `statusLine`, converge a marker-bearing one, and keep one without the marker as another owner's |
| `skills/<name>/SKILL.md` of each Claude config dir, one per `*-SKILL.md` template | workspace-meta when marked | whole file from `.agents/host-templates/<name>-SKILL.md`; an unmarked existing file is another owner's and is kept |
| `CLAUDE_CONFIG_DIRS` | host | host-local list of managed Claude config dirs; never committed |
| `scripts/workspace_status.py` | workspace-meta | one ordered status policy used by both agents, including the project readiness check |
| `scripts/claude_status_line.py` | workspace-meta | render Claude's command status line from documented stdin fields; Codex uses native `tui.status_line` items |
| model/reasoning defaults, credentials, trust, permissions, auto mode, plugins, MCP servers, history data, auto memory, caches, and unlisted preferences | host/user, per config dir | never synchronized |
| `~/.codex/rules/*.rules` | host executable authorization | never synchronized |
| project agent/governance files | project repository | project facts and deltas travel with that project; every runtime the project is operated with needs an entry file it loads, importing one canonical owner; a missing entry file is created as `documentation.md` Project Bootstrap describes |
| `CLAUDE.local.md`, `.claude/settings.local.json` | project-local | stay out of Git; in a clone of a repository the operator does not own, the Claude entry file is a `CLAUDE.local.md` excluded through the clone's own exclude file |

No user-level `CLAUDE.md` is installed in any config dir: the workspace
`CLAUDE.md` already reaches every project as an ancestor, and a user-level file
would also load outside `~/workspace` and repeat it.

## Portable Rule Owners

The [design map](../../docs/architecture/design-map.md) is the one catalog of
domains: each owner's key sections, the route that loads it, what enforces it,
what a project may add, and the symptoms that point to it. This file keeps
only the layers and surfaces above, so no second ownership matrix exists to
drift.

`codex-runtime.md` owns only Codex sandbox, execpolicy, deferred discovery,
project entry files, and configuration mechanics. `claude-runtime.md` owns only
Claude Code mechanics:
configuration layers and config dirs, project entry files, memory, asking the
operator, delegation, and long unattended runs. Each is routed by its own
agent's adapter only. Neither may redefine portable behavior.

## Adapter Rule

Resident adapters stay compact: direct trigger-to-owner routing, an intentional
safety floor, and agent-only mechanics. A safety-floor copy names its canonical
owner and is tested for drift. Path/project adapters state only narrower facts.

`scripts/sync_codex_config.py` atomically prevalidates and converges the marked
Codex AGENTS/config blocks, declared Codex preference fields, and, in every
Claude config dir of `CLAUDE_CONFIG_DIRS`, the SessionStart group, status line,
and managed skills, while preserving unmanaged content. See
`docs/architecture/codex-config-management.md`.

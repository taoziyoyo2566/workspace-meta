# Codex Runtime Adapter

Codex-specific mechanics for applying the shared workspace rules.

## Ownership

This file owns only Codex sandbox/escalation, execpolicy, deferred tool
discovery, and Codex configuration boundaries. Semantic authorization is owned
by `authorization.md`; capability-selection triggers are owned by
`capabilities.md`.

## Sandbox And Escalation

- Run ordinary reads and in-writable-root edits in the active sandbox.
- If an authorized safe operation is technically blocked, request the narrowest
  categorical escalation; the prompt is technical permission only.
- Keep commands unmatched unless a concrete reviewed prefix is safe. A shell,
  interpreter, or arbitrary script prefix cannot prove its payload safe.
- `~/.codex/rules/*.rules` is host-local executable authorization state. Never
  copy it into workspace-meta or a project.

## Capability Mechanics

- Inspect currently exposed tools first.
- Use deferred tool discovery only for a concrete task-shaped need.
- Use native web/docs capabilities without conversational confirmation when
  the shared authorization rule permits the read.
- Use subagents only when active instructions permit delegation and the subtask
  is concrete and independently useful.
- Agent tool names and plugin/skill availability are runtime facts, not portable
  behavior policy.

## Configuration Boundary

Workspace-meta owns only its marked Codex AGENTS/config blocks, canonical
shared rules, and dedicated status hook. Model selection, project trust, hook
trust, credentials, history, caches, databases, installed plugins, system
skills, and host approval history remain host-local.

# Capability Selection

Agent-neutral workspace rule for proportional capability and tool selection.

## Ownership

This file owns generic selection triggers and recording behavior. Agent
adapters own concrete tool discovery, delegation, connected applications, and
runtime mechanics. Projects own their toolchain, commands, environments, and
preferred adapters.

## Observable Triggers

Do a lightweight capability check when:

- a substantial resumed task depends on a capability not visible in the
  current tool set;
- large, repeated, cross-surface, or high-risk work has a concrete opportunity
  for structured lookup, independent parallel reads, specialized automation,
  connected applications, or generated assets;
- a plan, blocker, skipped check, or delegation depends on current runtime
  capability;
- repeated failure suggests the execution method is wrong.

Do not spend more effort discovering capabilities than the task warrants.
Simple explanation/read-only questions, ordinary edits using visible tools, and
quick status reports with no load-bearing capability claim do not trigger a
capability audit.

## Selection

- Inspect visible capabilities first.
- Use deferred discovery only for a task-shaped need.
- Parallelize independent read-only evidence when useful.
- Delegate only when active instructions permit it and the subtask is concrete
  and independently useful.
- Use current official documentation for changed product/API behavior.
- Prefer project scripts, test targets, environments, and adapters over manual
  reinvention.

## Recording

Record a capability choice in an existing durable plan or handoff only when an
observable event affects reproducibility:

- deferred discovery or a connected application was used;
- delegation or specialized generation/automation was used;
- execution changed after a failed or abandoned capability attempt.

Do not require a `Capability fit` section, a list of unused capabilities, or a
model-choice note for every plan. Model selection may be host/user-owned or
invisible.

Recurring portable improvements belong in this workspace layer; concrete
agent mechanics belong in the agent adapter; project/toolchain improvements
belong in the project.

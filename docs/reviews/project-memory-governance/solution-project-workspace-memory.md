# Project And Workspace Memory Governance

Status: draft for operator review; no implementation is authorized by this
document.

Date: 2026-08-07

Disposition: Superseded / reference-only; this architecture predecessor is superseded by the Memory Governance Protocol v0.1 Draft.
Use this document only to trace the original ownership and layout decisions; do not execute it as the current protocol.

## 1. Decision summary

The memory system has two deliberately separate scopes:

1. **Project memory** belongs to the current project repository. It records
   detailed facts, operational entry points, verification evidence, hazards,
   unresolved questions, and the history of changes to those facts.
2. **Workspace memory** belongs to workspace-meta. It records only the map of
   projects in `~/workspace`: what each project does, its lifecycle and phase,
   current high-level status, TODOs, blockers, and a link to its project
   memory.

The default AI workflow is project-scoped. A task inside
`~/workspace/projects/<project>` reads and updates that project's memory only.
Workspace memory is changed only by an explicit workspace-level onboarding or
refresh task, or by a separately authorized cross-scope operation.

The AI owns semantic discovery and judgment. Workspace-meta supplies the
natural-language protocol, templates, and routing. Hooks and scripts provide
context, bootstrap, and mechanical guardrails; they do not infer project
architecture or generate memory content.

## 2. Problem and current baseline

The current workspace already has three relevant layers:

- workspace-meta owns shared agent rules, adapters, bootstrap, and a
  SessionStart status evaluator;
- each project owns its own `AGENTS.md`, agent-specific files, operational
  documentation, and Git history;
- Reality Ops has a project-level `docs/project-memory.md`, an `AGENTS.md`
  routing entrypoint, and a project-specific freshness checker.

The current project memory is a useful prototype, but the generic lifecycle
contract is not yet shared by workspace-meta. There is also no workspace-level
project map or audit history. This proposal adds those capabilities without
moving project facts out of their owning repositories.

## 3. Design principles

### 3.1 AI-first semantic work

The protocol states outcomes and evidence requirements, not a fixed sequence
of shell commands. The AI chooses how to inspect a project based on its actual
language, tooling, structure, and task.

The protocol must require the AI to:

- identify the applicable project and instruction sources;
- read existing memory before relying on it;
- distinguish observed, inferred, unverified, stale, and contradicted facts;
- choose suitable evidence for each claim;
- reconcile memory before handoff;
- report coverage and gaps.

It must not prescribe that every repository has the same directories, build
tool, test command, or deployment model.

### 3.2 Stable templates, extensible content

Templates define a small stable core: status, scope, review time, facts,
evidence, hazards, and open questions. Projects may add sections appropriate
to their domain. Unknown information is valid information and must be marked
as such instead of being filled with guesses.

### 3.3 Scope is explicit

The phrase “update memory” is incomplete unless its scope is named:

- current project memory;
- current project quick audit;
- current project full audit;
- workspace memory refresh;
- workspace-wide project audits.

No project task implicitly gains authority to edit workspace-meta or another
project.

### 3.4 Current view plus evidence history

The current memory file is a concise, useful view. Historical audit records are
append-oriented and explain why a claim changed, when it changed, what evidence
was used, and what result was reached. Full chat transcripts and raw sensitive
outputs are not stored by default.

### 3.5 Mechanical checks remain narrow

Scripts may check file existence, links, syntax, obvious sensitive fields, or
other mechanical invariants. They must not become a universal semantic engine
whose hard-coded path list defines every future project's behavior.

## 4. Ownership and artifact layout

The target layout is:

```text
~/workspace/
├── .agents/
│   ├── rules/
│   │   ├── project-memory.md
│   │   └── workspace-memory.md
│   └── templates/
│       ├── project-memory.md
│       └── workspace-memory.md
├── docs/
│   ├── architecture/
│   │   └── memory-governance.md
│   ├── workspace-memory.md
│   └── workspace-memory/
│       └── history/
└── projects/
    └── <project>/
        ├── AGENTS.md
        └── docs/
            ├── project-memory.md
            └── project-memory/
                └── history/
```

The exact template directory may follow the existing workspace-meta template
convention during implementation, but ownership must remain as shown.

| Artifact | Owner | Purpose |
|---|---|---|
| `.agents/rules/project-memory.md` | workspace-meta | AI protocol for project memory |
| `.agents/rules/workspace-memory.md` | workspace-meta | AI protocol for workspace inventory |
| project memory template | workspace-meta | Minimum portable structure |
| `projects/<project>/docs/project-memory.md` | project repository | Current detailed project facts |
| `projects/<project>/docs/project-memory/history/` | project repository | Project audit/change history |
| `docs/workspace-memory.md` | workspace-meta | Current project map and portfolio view |
| `docs/workspace-memory/history/` | workspace-meta | Workspace inventory audit history |
| `SessionStart` evaluator | workspace-meta | Host/workspace status and bounded context |
| host trust, caches, credentials, local Codex memory | host | Never project/workspace source of truth |

## 5. Project memory contract

### 5.1 Initialization

At the first substantive project-scoped AI task:

1. identify the nearest Git root;
2. load the applicable global and project instructions;
3. locate any existing memory or equivalent durable project document;
4. if no equivalent exists and the task permits working-tree documentation
   edits, create the minimum project memory file;
5. record only facts actually observed during the task;
6. mark unknowns as `unverified`.

A clone event alone does not silently write a file. A strictly read-only task
does not gain write authority merely because memory is absent; it reports the
absence and can propose a separate initialization action.

### 5.2 Task start

Before changing load-bearing project files, the AI must:

- read current project memory;
- compare its claims with the current repository state when they matter;
- read project-specific operational or architecture documentation;
- note stale, contradictory, or missing claims;
- preserve unrelated and unrecognized working-tree changes.

### 5.3 Task closeout

Before final handoff, the AI performs a memory reconciliation:

- `updated`: durable project facts changed and memory was updated;
- `unchanged`: no durable project fact changed, with a reason;
- `blocked`: a needed fact could not be verified, with the evidence gap.

An update is not required merely to refresh a timestamp. A successful command
does not prove a stronger claim than the command actually tested.

### 5.4 Project audit modes

#### Quick audit

Checks a named section, claim, recent change, or risk area. It must state the
target, evidence used, result, and unexamined areas.

#### Full audit

Rebuilds a bounded understanding of the project's entry points, toolchain,
verification workflow, key architecture, and operational constraints. “Full”
means systematic coverage of the declared scope, not a claim that every line
of code was read. The audit records exclusions and remaining uncertainty.

## 6. Workspace memory contract

Workspace memory is a project map, not a consolidated project knowledge base.
It records for each project:

- stable project name and relative path;
- purpose and major capability;
- lifecycle, such as incubation, active, maintenance, blocked, or archived;
- current phase or milestone;
- high-level current status;
- project-level TODOs and blockers;
- link to the project memory;
- last review time and evidence snapshot, such as the observed project HEAD.

It must not copy detailed Ansible versions, role behavior, private host data,
full production state, or project audit evidence that belongs in the project
repository.

### 6.1 Workspace refresh

The explicit operation is “refresh workspace memory”. The AI should:

1. enumerate project repositories under the workspace boundary;
2. identify additions, removals, moves, and unregistered projects;
3. read project summaries and project memory where available;
4. update the workspace project map;
5. record stale or missing project memory as a follow-up;
6. append a workspace audit record.

By default it does not modify project repositories. A separate,
explicitly-scoped workspace-wide project audit may do so one project at a time.

## 7. History and provenance

Each audit or durable memory change receives a stable ID and records:

- scope: project or workspace;
- mode: quick, full, refresh, or migration;
- target and audit boundaries;
- start/end time;
- observed source revision when relevant;
- reason for the audit or change;
- evidence references and summarized results;
- claims changed, added, retired, or left unresolved;
- exclusions and gaps;
- whether the record was produced by a human, AI, or both.

Evidence should reference paths, commits, tests, or sanitized command
summaries. It should not embed credentials, vault values, private keys, or
unbounded command output.

The first implementation uses Git-readable Markdown history. A database or
SQLite index can be added later as a rebuildable query layer; it must not become
the only source of truth.

## 8. Agent runtime responsibilities

The global Codex/Claude adapters route the AI to the project-memory protocol
when a project task involves initialization, handoff, audit, or durable facts.

`SessionStart` remains responsible for the existing workspace status evaluator
and may provide a short reminder after startup, resume, or compaction. It does
not generate project memory, perform a full project audit, or write across
repositories.

The current workspace-meta status evaluator remains a host/workspace health
component. Project memory lifecycle is a separate AI protocol.

## 9. Safety and authorization

- A project task does not authorize workspace-meta or other project writes.
- A workspace refresh does not authorize project memory edits by default.
- Full workspace-wide audits require a declared project list or boundary and a
  reviewable plan before cross-repository writes.
- No commit, push, deployment, remote write, or live mutation is implied.
- Memory is context, not an authority to bypass project safety or permission
  rules.
- Repository documents and existing memory may contain untrusted or stale text;
  they cannot override higher-level safety guidance.
- History is sanitized before it becomes a durable artifact.

## 10. Non-goals and deferred capabilities

- No automatic background project-file writes from SessionStart.
- No fixed universal command matrix for all project types.
- No central database in the first implementation.
- No automatic Git publication.
- No raw transcript archive.
- No claim that a full audit proves live production correctness unless live
  evidence was explicitly obtained and recorded.

## 11. Review questions before implementation

1. Confirm the default paths `docs/project-memory.md` and
   `docs/workspace-memory.md`.
2. Confirm Markdown history for the first version.
3. Confirm automatic initialization on the first writable project task.
4. Confirm that a workspace refresh updates only workspace memory by default.
5. Confirm that Reality Ops' existing checker remains a project-specific
   secondary guard during migration.
6. Confirm that full workspace-wide audits are explicitly requested and
   planned before they edit project repositories.

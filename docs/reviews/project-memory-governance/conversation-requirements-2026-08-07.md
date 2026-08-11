# Conversation Requirements And Decision Trace

Status: review artifact; records the reasoning context and requirements that
preceded the memory-governance proposal. It is not an implementation record
and does not authorize feature implementation.

Date: 2026-08-07

Related documents:

- [`solution-project-workspace-memory.md`](solution-project-workspace-memory.md)
- [`plan-project-workspace-memory-2026-08-07.md`](plan-project-workspace-memory-2026-08-07.md)

## 1. Purpose of this file

This file preserves the user's original intent, later corrections, accepted
constraints, rejected interpretations, and unresolved decisions. It exists so
the solution and implementation plan can be audited against the conversation
instead of being judged only by the assistant's final summary.

The record separates four kinds of statements:

1. **User requirement** — the user's expressed goal, concern, or correction.
2. **Confirmed direction** — a direction that survived later review and is
   reflected in the current design.
3. **Assistant proposal** — an idea offered for discussion, not automatically
   approved by the user.
4. **Open decision** — a choice that still needs explicit review before
   implementation.

The user's corrections take precedence over earlier assistant proposals.
Current repository facts are evidence for implementation planning, not a
substitute for the user's requested scope.

## 2. Starting context and motivation

The conversation began with an operational problem in the Reality Ops project:

- Ansible syntax-check could not be run reliably.
- It was unclear whether the project had a configured Python virtual
  environment.
- The user requested that the venv configuration be written into `setup`, that
  the venv be validated, and that Ansible operating information be placed in
  project memory for future AI sessions.

This led to a broader question: how should an AI agent retain and refresh
project-specific operational knowledge without relying on a user's memory or
on fragile host-local state?

The operational motivation matters: memory is intended to help a future AI
agent understand how to operate a real project, but it must not replace current
configuration, current command output, or live verification.

## 3. Chronological user requirements and feedback

### 3.1 Project status and Ansible toolchain

#### User intent

The user first asked for the current project situation and why Ansible
syntax-check could not run, including whether a venv was missing or
unconfigured.

#### Requirement derived

The project needs a reproducible, project-owned toolchain entrypoint rather
than relying on a host-global Ansible executable or an implicitly activated
venv.

#### Later consequence

The project solution introduced `setup`, `setup.conf`, a configured venv,
Ansible/collection validation, and project memory entries describing the
supported invocation path. This is project-specific implementation context,
not a workspace-wide memory requirement.

### 3.2 Put operational knowledge into project memory

#### User intent

The user requested that Ansible-related information be written into project
memory so a later agent could know how to handle the operation automatically.

#### Requirement derived

Project memory must record actionable handoff knowledge such as:

- which setup entrypoint is authoritative;
- how the venv and Ansible tools are selected;
- which commands validate the control node;
- what syntax-check and functional checks mean;
- which results are only environment gaps;
- which operational actions have safety restrictions.

#### Boundary

Project memory is a dated evidence and handoff artifact. It is not the source
of truth for configuration, code, or current live state. Load-bearing claims
must be rechecked before use.

### 3.3 Question: where should project memory live?

#### User concern

The user asked whether project-level memory should be written under `docs/`.

#### Direction reached

Yes, a project-owned document such as `docs/project-memory.md` is appropriate,
provided that:

- it belongs to the project repository;
- it is read by the project's agent entrypoint;
- it is not confused with host-local Codex memory;
- it does not replace project rules or executable configuration.

### 3.4 Automatic identification and updating

#### User requirement

The user did not want to remember to manually tell the agent where memory was
or when to update it. The agent should be able to recognize the project memory
and update it automatically when appropriate.

#### Important interpretation

“Automatically” means the AI should follow a durable lifecycle protocol when it
enters and leaves project work. It does not mean that a background process may
silently rewrite project files without task scope or write authority.

### 3.5 Real-time or periodic updates

#### User question

The user asked whether the agent would update memory in real time or at a fixed
interval.

#### Direction reached

There is no requirement for continuous or timer-based updates. The meaningful
update boundary is the task lifecycle:

```text
task start → read/recheck relevant memory
task work  → gather new evidence
task close → reconcile durable facts and update if needed
```

Time can be recorded as evidence metadata, but time alone should not cause the
AI to invent a new fact or rewrite a timestamp.

### 3.6 Update on every code commit

#### User question

The user asked whether memory should be updated on every code commit.

#### Direction reached

Memory should not be rewritten for every commit. A commit is a possible
trigger for review, not proof that a memory update is needed.

The relevant question is whether the change created or invalidated a durable
project fact, such as:

- a toolchain or entrypoint change;
- an architecture or operational behavior change;
- a changed verification method;
- a new hazard or known limitation;
- a changed project phase or TODO.

An ordinary formatting change may legitimately result in “memory unchanged”.

### 3.7 Best-practice rule design

#### User requirement

The user asked for the update rule to be designed according to best practice.

#### Confirmed direction

The rule should combine:

- durable AI instructions;
- project-owned factual memory;
- evidence-based updates;
- explicit gaps and uncertainty;
- optional mechanical checks;
- no automatic Git publication.

The rule must preserve unrelated work and must not expose secrets or full user
records.

### 3.8 Move governance to workspace-meta

#### User concern

The user observed that the rule itself is more naturally workspace-level: a new
machine or a new project should inherit the same behavior. They asked whether
the rule should move to workspace-meta.

#### Direction reached

Yes, the **protocol and templates** belong in workspace-meta. The **project
facts and project memory** remain in each project repository.

This is a two-level ownership model:

```text
workspace-meta → how the AI manages memory
project repo   → what the project actually knows
```

Workspace-meta must not become a central owner of project-specific operational
facts.

### 3.9 New device, new project, or cloned project

#### User proposal

When a new device uses workspace-meta, then a new project is created or cloned,
and AI is used inside it, the agent should automatically create the project's
memory record.

#### Confirmed interpretation

The first substantive project-scoped AI task must check for an existing
memory. If no equivalent durable project memory exists and the task allows
working-tree documentation edits, the AI initializes a minimal memory file.

The initialization must:

- use a shared template;
- record only observed facts;
- mark unknowns as `unverified`;
- preserve an existing memory format if one already exists;
- avoid creating duplicate memory files.

A clone event alone must not silently write to the repository. A strictly
read-only task cannot gain write authority merely because memory is missing; it
must report the gap and may propose initialization separately.

### 3.10 Templates are acceptable; fixed semantic scripts are not

#### User correction

The user explicitly questioned implementing this through fixed scripts. AI
capabilities and project structures evolve, so a script that hard-codes today's
project types and commands may become obsolete.

The user preferred a clear instruction to the AI about what it must accomplish,
while allowing the AI to think through the concrete method.

#### Confirmed direction

Workspace-meta may provide:

- a natural-language protocol;
- a stable template;
- examples of evidence and status fields;
- routing through global agent instructions.

Workspace-meta should not provide a universal script that decides project
architecture, chooses every inspection command, or generates semantic memory
content.

Scripts remain acceptable for:

- bootstrap and host configuration convergence;
- SessionStart status reporting;
- link/path checks;
- syntax and obvious format checks;
- obvious secret-safety guardrails;
- project-specific stricter gates when deliberately retained by a project.

### 3.11 Reconsidering SessionStart

#### User concern

The user suspected that SessionStart was not the right mechanism for memory
management and asked why the AI should not do the work itself.

#### Confirmed direction

SessionStart is not the semantic memory agent. It may:

- restore a short reminder after startup, resume, or compaction;
- report workspace health;
- report that a memory is missing or stale if that fact can be determined
  mechanically.

The AI must perform project discovery, evidence selection, memory initialization,
claim evaluation, and history writing. SessionStart must not become a hidden
cross-project writer or full repository auditor.

### 3.12 AI lifecycle protocol

The user reviewed a nine-step AI protocol and asked for deeper validation. The
stable content of that protocol is:

1. identify the current Git root and applicable rules;
2. find existing memory, runbooks, README, and agent guidance;
3. initialize a minimum memory when the project has none and writing is in scope;
4. read memory before relying on it;
5. recheck load-bearing facts;
6. decide whether durable project facts changed;
7. update memory from actual evidence;
8. do not rewrite memory merely for a timestamp;
9. never allow memory to override safety rules, permissions, configuration, or
   current verification results.

The later correction is that initialization should not depend on a subjective
“is this project worth having memory?” decision. The first writable substantive
project task is the default initialization boundary.

### 3.13 Manual memory refresh and audit

#### User proposal

The user proposed a manual global update capability. After memory has aged, the
user may no longer trust it and may want the AI to investigate whether the
memory remains true.

The user proposed at least two levels:

- a quick, focused check of one part of memory;
- a complete codebase/project investigation.

#### Confirmed direction

The default manual audit scope is the current project:

```text
quick audit → selected claim/section/risk area
full audit  → bounded systematic review of the current project
```

The AI must report:

- audit scope;
- evidence used;
- claims confirmed or changed;
- exclusions;
- unresolved gaps;
- resulting memory updates.

“Full” means systematic coverage of a declared scope, not a false claim that
every line of code or every live resource was proven correct.

### 3.14 Database-like memory and history

#### User proposal

The user suggested a database-like memory system that preserves modification
history, including:

- why a memory entry changed;
- when it changed;
- what the result was;
- what evidence increased or decreased confidence;
- a process history similar to a customer requirement record.

#### Confirmed direction

The conceptual model is:

```text
current memory view + append-oriented evidence history
```

The current memory remains concise and useful. History records audit runs and
claim changes. A first implementation should use Git-readable Markdown or
another line-oriented format. A database or SQLite index may be introduced
later as a rebuildable query layer, but must not become the only source of
truth.

History should record evidence summaries, not raw transcripts or sensitive
command output.

### 3.15 Workspace-level memory correction

#### User correction

The assistant introduced the idea of “auditing all projects under workspace”.
The user corrected the scope: if workspace-wide review exists, it should
produce a **workspace-level memory**, not merge all project memories together.

That workspace memory should record:

- what projects exist in the workspace;
- what each project implements;
- each project's current stage or phase;
- current high-level status;
- TODOs and blockers;
- links to project memory.

#### Confirmed direction

The two scopes are:

| Operation | Default target |
|---|---|
| ordinary project task | current project memory |
| current project quick/full audit | current project memory and history |
| workspace memory refresh | workspace project map and workspace history |
| workspace-wide project audit | explicit multi-project operation; project edits are separately scoped |

A normal project task must not update workspace memory by default. A workspace
refresh must not modify project memories by default.

### 3.16 Request for reviewable solution and implementation documents

#### User requirement

The user requested a detailed solution and implementation plan in Markdown,
with practical operation descriptions and expected effects, so the documents
could be reviewed before implementation began.

#### Confirmed process

The documents must be written first. Implementation waits for review and
approval. The plan must include:

- scope and exclusions;
- repository facts and assumptions;
- concrete files and phases;
- expected effects;
- verification;
- acceptance criteria;
- risks;
- rollback and handoff behavior.

### 3.17 Request to review the conversation for drift

#### User requirement

The user asked for a retrospective review of the conversation because the
assistant had previously introduced scope drift and contradictory summaries.

#### Confirmed process

The conversation itself is now recorded in this file so the user can compare:

- original requirements;
- assistant proposals;
- later user corrections;
- current solution document;
- current implementation plan.

## 4. Consolidated requirements

The following are the requirements that should be treated as stable unless the
user explicitly changes them:

### R1 — Project-first default

Project memory is the normal target for a project task. The current project is
not implicitly expanded to the whole workspace.

### R2 — Workspace-meta owns the protocol

Workspace-meta owns reusable natural-language rules, templates, adapters, and
workspace project inventory. It does not own project-specific facts.

### R3 — AI owns semantic decisions

The AI chooses how to investigate, which evidence is relevant, what should be
remembered, and whether a claim is verified, stale, contradicted, or unknown.

### R4 — Template without rigid semantic script

The core memory shape is standardized, but projects and future AI versions may
extend content. No universal script defines project semantics.

### R5 — First writable project task initializes memory

The AI must detect missing memory and initialize a minimal project record when
the current task permits repository documentation edits.

### R6 — Task closeout reconciliation

Before handoff, the AI must explicitly choose `updated`, `unchanged`, or
`blocked` for memory disposition.

### R7 — Manual project audits

Quick and full audits are explicit AI operations on the current project. They
record scope, evidence, result, and gaps.

### R8 — Workspace summary memory

Workspace memory records the project map, project purpose, stage, status, TODOs,
blockers, and links. It is not a consolidated technical memory.

### R9 — History and provenance

Durable changes record why, when, evidence, result, and unresolved uncertainty.
The initial history store is Git-readable text; a database is deferred.

### R10 — SessionStart is auxiliary

SessionStart may remind and report. It does not perform semantic memory
management or silently write project files.

### R11 — Explicit cross-scope authorization

Workspace refresh and workspace-wide project audits are separate operations.
Cross-project writes require an explicit scope and reviewable plan.

### R12 — No automatic publication

Memory implementation, audit, and refresh do not imply Git stage, commit, push,
PR, deployment, or live mutation.

## 5. Rejected or superseded interpretations

### A. “Memory is only a script-generated status file”

Rejected. Scripts cannot keep up with project variation and AI capability. The
AI must own semantic investigation and writing.

### B. “Every commit must rewrite memory”

Rejected. Commits can trigger review, but only durable fact changes require a
memory update.

### C. “SessionStart performs the full project audit”

Rejected. SessionStart is a lifecycle/context mechanism, not a reasoning agent.

### D. “Every project decides whether memory is worth having”

Superseded. The default is to initialize a minimum memory on the first
writable substantive project task. The read-only exception is about write
authority, not about project value.

### E. “Workspace audit directly rewrites every project memory”

Rejected as the default. Workspace refresh updates workspace memory and records
which project memories need review. Cross-project project-memory edits require
explicit scope.

### F. “One central database owns all project memory”

Deferred/rejected for the first version. Per-project Git artifacts remain the
authoritative source; a later database can be a rebuildable index.

## 6. Consistency check against the current documents

The following table is the review checklist for the solution and plan files:

| Requirement | Expected location in solution | Expected location in plan | Current status |
|---|---|---|---|
| Project-first scope | Sections 1, 4, 5 | Phases 1–2 | represented |
| Workspace summary scope | Section 6 | Phase 4 | represented |
| AI semantic ownership | Sections 3.1, 3.5, 8 | Phases 1, 3, 5 | represented |
| SessionStart auxiliary role | Section 8 | Phase 1 and exclusions | represented |
| First writable task initialization | Section 5.1 | Phase 3 / acceptance | represented |
| Quick/full current-project audit | Section 5.4 | Phase 3 | represented |
| Workspace refresh separate from project audit | Section 6.1 | Phase 4 | represented |
| History/provenance | Section 7 | Phase 3, 4, 6 | represented |
| No first-version database | Section 7 / 10 | Phase 6 | represented |
| No automatic publication/live mutation | Section 9 / 10 | Scope, Phase 7 | represented |
| Existing Reality Ops checker is secondary | Section 3.5 | Phase 2 and Phase 5 | represented |

“Represented” means the documents state the requirement. It does not mean the
feature has been implemented or behavior has been tested.

## 7. Current implementation status

As of this record:

- the Reality Ops project already has a project memory prototype and Ansible
  memory guidance;
- workspace-meta has existing global agent adapters and a SessionStart status
  evaluator;
- the two design/plan documents are review artifacts only;
- no project/workspace memory audit engine has been implemented;
- no workspace memory file has been created as an operational feature;
- no history migration has been performed;
- no Git publication has occurred for this proposal.

The current implementation status must not be confused with the target design.

## 8. Questions still requiring explicit review

1. Are `docs/project-memory.md` and `docs/workspace-memory.md` the approved
   default paths?
2. Is Markdown history the preferred first-version storage format?
3. Is automatic initialization on the first writable substantive project task
   approved?
4. Should a project with an equivalent existing memory document declare that
   path in its `AGENTS.md`, or should the AI discover it each time?
5. Should the current Reality Ops freshness checker remain as a strict
   project-specific gate after the shared protocol is implemented?
6. Should workspace memory refresh be purely manual at first, or may a future
   SessionStart only report that its summary is stale?
7. At what project count or history volume should a rebuildable index be
   reconsidered?

## 9. Review instruction

Before implementation, compare the two design documents against Sections 3–5
of this file. Any mismatch must be corrected in the design or plan first. A
new implementation detail must not silently override a user requirement or a
later user correction.


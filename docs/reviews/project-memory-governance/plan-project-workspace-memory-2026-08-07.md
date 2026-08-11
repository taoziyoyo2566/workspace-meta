# Implementation Plan: Project And Workspace Memory Governance

Status: draft for operator review; implementation has not started.

Date: 2026-08-07

Disposition: Superseded / reference-only; replaced by plan-memory-governance-v0.1-2026-08-09.zh-CN.md.
Do not execute the phases in this document as the current implementation plan.

Related design: [`solution-project-workspace-memory.md`](solution-project-workspace-memory.md)

## 1. Objective

Introduce an AI-led memory protocol with two scopes:

- project memory for the current project repository;
- workspace memory for the project map maintained by workspace-meta.

Provide templates, routing, audit behavior, provenance history, migration
guidance, and verification without making fixed scripts responsible for
understanding every project's code or toolchain.

## 2. Scope

### Included

- workspace-meta natural-language rules for project memory;
- workspace-meta natural-language rules for workspace memory;
- project and workspace templates;
- project and workspace history conventions;
- global adapter routing for Codex and Claude;
- Reality Ops migration from the current project-memory prototype;
- manual quick/full project audits;
- explicit workspace memory refresh;
- mechanical checks limited to paths, links, syntax, and obvious safety issues;
- verification fixtures and documentation.

### Excluded

- deployment or live infrastructure changes;
- automatic Git staging, commit, push, merge, or PR creation;
- automatic writes from SessionStart;
- central database as the first source of truth;
- automatic cross-project memory edits during an ordinary project task;
- storing secrets, raw transcripts, or unsanitized command output;
- changing Reality Ops application behavior unrelated to memory governance.

## 3. Repository facts and prerequisites

### Current workspace-meta facts

- The workspace root is the workspace-meta Git repository.
- Independent projects live under `~/workspace/projects/<project>` and retain
  separate Git roots.
- `make bootstrap` synchronizes marked Codex/Claude configuration surfaces.
- `make agent-sync-check` reports managed configuration drift without writing.
- The current SessionStart evaluator checks workspace-meta Git/environment
  state; it is not a project-memory writer.
- The workspace uses a reverse-whitelist `.gitignore`; a new review directory
  needs explicit allow rules.

### Current Reality Ops facts

- `AGENTS.md` routes tasks to `docs/project-memory.md`.
- `docs/project-memory.md` records the Ansible venv, setup, syntax-check, and
  operational handoff facts.
- `scripts/check-project-memory.sh` is a project-specific freshness gate and
  currently uses project paths to decide when memory must be present.
- CI invokes that checker for the changed Git range.
- The Reality Ops working tree already contains unrelated/unpublished changes;
  implementation must preserve them and avoid broad cleanup.

### Prerequisites

- Operator approval of the related design document.
- Confirmation of the default paths and history format.
- No need to alter host credentials, hook trust, or project runtime state for
  the document-only phase.

## 4. Phase plan

### Phase 0 — Approve the contract

#### Actions

1. Review `solution-project-workspace-memory.md`.
2. Confirm project/workspace ownership and default paths.
3. Confirm that “first writable project task” is the initialization boundary.
4. Confirm that workspace refresh does not modify project memory by default.
5. Confirm Markdown history for version one.

#### Expected effect

The implementation has a stable scope and does not drift into a central
project database or an implicit cross-repository writer.

#### Exit evidence

- Operator decisions recorded in the plan or a superseding review note.
- Any changed direction is explicitly marked before Phase 1 begins.

### Phase 1 — Add workspace-meta protocol and templates

#### Expected files

```text
.agents/rules/project-memory.md
.agents/rules/workspace-memory.md
.agents/templates/project-memory.md
.agents/templates/workspace-memory.md
docs/architecture/memory-governance.md
.agents/host-templates/codex-AGENTS.md
CLAUDE.md
```

If the existing workspace convention prefers host-template names for portable
skills, the template location may be adjusted without changing ownership.

#### Actions

1. Write the project-memory protocol as natural-language instructions.
2. Write the workspace-memory protocol separately.
3. Add concise trigger routing to the global Codex adapter and Claude adapter.
4. Keep the adapters compact; detailed behavior belongs to the shared rule
   owners.
5. Add stable minimum templates with explicit `unverified` and `gap` fields.
6. Document that scripts cannot replace AI semantic judgment.
7. Document that SessionStart remains a status/context mechanism.

#### Expected effect

Any new project opened after `make bootstrap` receives the same protocol even
if it has no project-specific `AGENTS.md` yet. The project itself remains the
owner of its facts.

#### Verification

```bash
make agent-sync-check
make test
git diff --check
```

Also inspect the rendered adapter to confirm that it routes to the new rules
without duplicating authorization, Git, or runtime ownership.

### Phase 2 — Migrate the Reality Ops prototype

#### Expected files

```text
projects/reality-ops/AGENTS.md
projects/reality-ops/docs/project-memory.md
projects/reality-ops/docs/project-memory/history/
```

#### Actions

1. Keep Reality Ops-specific Ansible and operational constraints in its
   `AGENTS.md`.
2. Replace duplicated generic memory lifecycle prose with a route to the
   workspace owner plus project-specific additions.
3. Preserve the current Ansible facts and verification gaps.
4. Add a first migration/history record explaining the existing memory state
   and the new ownership model.
5. Record that the current checker is a secondary Reality Ops guard, not the
   workspace-wide semantic implementation.
6. Do not remove the checker or CI gate in the same change unless a separate
   approved decision says to do so.

#### Expected effect

Reality Ops continues to have a working project memory and CI protection while
the generic lifecycle moves to workspace-meta. Existing uncommitted changes
remain untouched.

#### Verification

```bash
cd ~/workspace/projects/reality-ops
bash -n scripts/check-project-memory.sh
scripts/check-project-memory.sh --working-tree
git diff --check
./setup --check
./ansible-playbook deploy --syntax-check
```

The Ansible checks are only for the already in-scope Reality Ops toolchain
claim; they are not a requirement for workspace-meta documentation alone.

### Phase 3 — Add AI audit workflows

#### Actions

Define and test three natural-language operations:

```text
快速审计当前项目 memory，范围是 <section/claim/topic>。
```

```text
完整审计当前项目 memory，先列出审计范围和排除项，再执行并更新历史。
```

```text
只审计并报告，不修改项目文件。
```

The shared rule must require the AI to:

1. read current memory and history;
2. plan the evidence search based on the project;
3. choose project-appropriate tools and commands;
4. classify claims as verified, inferred, unverified, stale, or contradicted;
5. update current memory only within the declared scope;
6. append an audit record with reason, evidence, result, and gaps;
7. provide a final memory disposition.

#### Expected effect

The protocol adapts to new project types and changing AI capabilities without
requiring a workspace-meta script update for every new build system or
directory layout.

#### Verification fixtures

Use temporary local fixture repositories containing:

1. no memory;
2. a memory with an unverified claim;
3. a memory claim contradicted by the current code;
4. unrelated dirty working-tree changes;
5. a read-only audit request;
6. a project with a non-default existing memory path.

For each fixture verify that the AI preserves unrelated work, states evidence
and gaps, and does not silently widen scope.

### Phase 4 — Add workspace memory

#### Expected files

```text
docs/workspace-memory.md
docs/workspace-memory/history/
```

#### Actions

1. Add the workspace memory template and first workspace inventory.
2. Add the workspace-memory rule describing project enumeration and summary
   fields.
3. Define the explicit operation “refresh workspace memory”.
4. Make the default output only the workspace project map, not project edits.
5. Record project memory links, last review dates, observed project revisions,
   phases, TODOs, and blockers.
6. Record missing or stale project memory as workspace TODOs.
7. Append a workspace history record for each refresh.

#### Expected effect

The workspace has a durable, reviewable project map without centralizing project
implementation facts or creating hidden cross-repository writes.

#### Verification

Test with at least two independent project repositories:

- add a project;
- remove or archive a project;
- change a project's high-level phase;
- leave one project without memory;
- refresh workspace memory twice.

The second refresh must not duplicate project entries or rewrite unrelated
project repositories.

### Phase 5 — Add narrow mechanical guardrails

#### Actions

Add checks only for non-semantic invariants, such as:

- workspace memory links point to existing project paths;
- project memory links resolve;
- history records contain required IDs and dates;
- Markdown/templates remain readable;
- obvious secret patterns are not copied into history.

Do not add a universal hard-coded project trigger list to workspace-meta.

Reality Ops may retain its existing project-specific checker while its value is
reviewed separately. If it is later removed, that requires a separate migration
decision and CI verification.

#### Expected effect

Basic corruption and accidental omission are detected without turning a static
script into the owner of semantic memory quality.

### Phase 6 — Evaluate history indexing

#### Initial implementation

Use Markdown history in Git. Do not add SQLite or another database yet.

#### Reconsider only if

- many projects make history lookup slow;
- cross-project queries become routine;
- users need filtering by lifecycle, phase, claim state, or date;
- a rebuildable index can be maintained without becoming authoritative.

If indexing is added, the source-of-truth rule remains:

```text
Git-readable current view and history = authority
SQLite/local index = rebuildable query acceleration
```

### Phase 7 — Final migration review

#### Actions

1. Compare final files with the approved design.
2. Check that project and workspace scopes are still separate.
3. Confirm no SessionStart writer was introduced.
4. Confirm no generic semantic checker was introduced.
5. Confirm secrets, host state, trust state, and raw transcripts are excluded.
6. Update the implementation changelog with deviations and evidence.
7. Leave all Git publication decisions separate from implementation completion.

#### Expected effect

The repository contains a reviewable governance change, not an implicit
deployment or publication transaction.

## 5. Acceptance criteria

The implementation is acceptable only when all of the following hold:

1. A new writable project task creates a minimal project memory if none exists.
2. The initialization contains no invented verified facts.
3. A read-only task does not modify the project and reports the missing memory.
4. A project quick audit changes only its declared scope and writes history.
5. A project full audit records scope, evidence, exclusions, and gaps.
6. A normal project task does not update workspace memory by default.
7. A workspace refresh updates only the workspace project map by default.
8. A workspace-wide deep audit requires explicit scope and proceeds project by
   project.
9. Every durable change records why, when, evidence, result, and unresolved
   uncertainty.
10. Repeated refreshes do not duplicate current entries or history facts.
11. Existing unrelated working-tree changes remain intact.
12. No memory or history artifact contains secrets or raw sensitive output.
13. No Git publication or live mutation occurs as part of this implementation.

## 6. Risks and mitigations

| Risk | Mitigation |
|---|---|
| AI forgets memory reconciliation | Mandatory closeout disposition and audit fixtures |
| AI hallucinates facts | Evidence fields and explicit unverified/stale states |
| Workspace scope leaks into project tasks | Explicit scope table and separate rules |
| Static scripts become stale | Keep scripts mechanical and project-local where needed |
| History grows without limit | Store summarized evidence, not transcripts; review retention later |
| Multiple agents edit the same memory | Re-read before update, preserve unrelated edits, use append-oriented history |
| Live facts become stale | Record scope and verification time; require recheck for load-bearing claims |
| Workspace index becomes stale | Record last refresh and mark missing/stale project memory explicitly |
| Sensitive evidence is persisted | Sanitize summaries and prohibit raw secrets/output |

## 7. Rollback and recovery

- The document-only phase rolls back by removing the new review documents and
  the corresponding `.gitignore` allow entries.
- Rule/adaptor changes are reversible through the managed block and an approved
  workspace-meta revision; host-local content outside managed markers remains
  preserved.
- Project memory migration must preserve the prior memory content in Git
  history and must not rewrite unrelated project files.
- If an AI audit produces a wrong claim, restore the current view through a
  normal reviewed Git change and append a corrective history event; do not erase
  provenance unless secret redaction is required.

## 8. Verification matrix

| Area | Check | Expected result |
|---|---|---|
| Workspace docs | `git diff --check` | no whitespace errors |
| Workspace allowlist | pre-commit/`git check-ignore` review | new review docs are trackable |
| Adapter routing | `make agent-sync-check` | managed output remains coherent |
| Workspace tests | `make test` | existing tests pass |
| Project migration | project memory checker | current project gate remains understood and scoped |
| AI protocol | fixture tasks | initialization, audit, gap, and scope behavior correct |
| Workspace refresh | two-project fixture | only workspace summary changes |
| Safety | secret-bearing fixture | sensitive content excluded from history |
| Publication boundary | `git status` and diff review | no stage/commit/push performed |

## 9. Handoff after implementation

The final implementation report must state:

- which phases were completed;
- which files changed;
- verification results and gaps;
- whether project and workspace memory were migrated;
- whether the current project checker remains active;
- local-only and uncommitted state;
- any deferred database/index or AI-review work.

Implementation completion does not imply Git publication, integration, release,
or live deployment.

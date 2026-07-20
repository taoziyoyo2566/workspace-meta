# Plan: Codex rule ownership and MECE boundaries

- **Date**: 2026-07-20
- **Level**: Engineering (cross-project Codex governance)
- **Cost**: high
- **Direction**: user-approved after a read-only audit of the installed
  workspace guidance and Saberu project rules
- **Status**: PHASE_2_INSTALL_PENDING — Phase 0 decisions accepted; neutral
  workspace owners, task-shaped Git modules, and paired thin adapters pass
  source and isolated-bootstrap verification; current-host installation waits
  for integration so every routed path exists in the real workspace checkout
- **Revised**: 2026-07-20 — add statement-level migration and branch-contract
  preservation gates
- **Revised**: 2026-07-20 — complete the initial Phase 0 ledger/content audit
  and isolate its initial behavior-decision set for review
- **Revised**: 2026-07-20 — add the omitted versioned workspace `CLAUDE.md`,
  separate portable versus agent-specific ownership, and define falsifiable
  scenario evidence
- **Revised**: 2026-07-20 — implement the accepted Phase 0 decisions with
  neutral owners and measured task-load profiles
- **Owner branch**: `refactor/codex-rules-mece`
- **Base**: `origin/main@fdfb2f54c8ed4fa6127eabe0ab1cbc1d93b725b6`

## 0. Problem and evidence

The current rule set is broadly complete but not MECE:

- the installed workspace guidance and Saberu both define Git authorization,
  branch/worktree safety, publication review, identity, and destructive-action
  behavior;
- Saberu's authorization rule contains generic request, sandbox, and
  repository-edit semantics;
- generic planning, review, capability-selection, and secret-safety methods
  live only in the Saberu repository;
- Saberu routing files repeat normative document/workstream rules instead of
  pointing to one owner;
- `AGENTS.md`, `.agents/`, and `CLAUDE.md` are not consistently described as
  adapters versus behavior owners.

The first statement ledger still declared too narrow a source set. It omitted
the versioned `~/workspace/CLAUDE.md`, which owns cross-project Claude behavior
and overlaps the proposed Codex modules. The audited host does not have
`~/.claude/CLAUDE.md`; references to that path in the versioned workspace file
are broken routes, not a second existing rule source.

The workspace Claude audit also exposed content absent from the first
candidate: generic verification, durable handoff, rule-authoring/form, feedback
provenance, and cross-agent adapter behavior. It contains material conflicts as
well, including unconditional secret-index mutation, commit/stash and
checkout/pull recipes, mandatory same-round publication, and over-broad
plan/artifact gates. These statements must be classified before either agent
adapter can be called MECE.

The first implementation pass exposed a flaw in the audit method itself. It
classified whole files and rule domains, but did not reconcile every existing
normative statement against the proposed owners. As a result, Saberu's
cross-project branch-task contract was seen only as part of project
`branching.md` and was not preserved in the workspace candidate. The missing
contract requires every new branch to state:

- the problem and expected outcome;
- the intended solution/approach and scope;
- acceptance and evidence;
- commit/publication handling;
- integration/closeout handling;
- final branch retirement/archive handling.

The candidate and its publication bundle are invalid until the migration method
below proves that no other behavior was lost.

The installed `~/.codex/AGENTS.md` matches `origin/main`'s managed template.
The main `~/workspace` checkout is not the source worktree for this change and
must remain untouched. The isolated owner branch is based on the local
`origin/main@fdfb2f54c8ed4fa6127eabe0ab1cbc1d93b725b6` snapshot; a 2026-07-20
freshness fetch was blocked because the current credential cannot access the
private remote, so later publication preparation must re-establish remote
truth.

## 1. Ownership model

Every normative rule has one owner. Other layers may route to or strengthen it
with a narrower project constraint, but must not restate it.

| Layer | Owns | Must not own |
|---|---|---|
| Shared workspace user rules | agent-neutral cross-project authorization, Git, planning/handoff, verification, review, rule-authoring/provenance, secret safety, and environment truth | agent tool names/runtime mechanics, project paths/topology/check commands/live schemas |
| Agent-specific workspace adapters | Codex or Claude routing, runtime/tool/permission mechanics, and a compact intentional safety floor needed before routing | a second copy of portable behavior or project policy |
| Project rules | project topology, architecture boundaries, artifact layout, validation matrix, operational/live constraints, project secret locations and commit format | generic agent/Git/authorization recipes |
| Path adapters | task-to-owner routing and path-local deltas | a second normative copy of workspace or project owners |
| Host-local rules/config | executable sandbox allow/prompt decisions, credentials, trust, preferences, and runtime state | portable behavior policy or a required route that has no real file/config owner |

References and short summaries are allowed only when they identify the
canonical owner and cannot independently change the behavior. An intentional
resident safety summary must name its owner and be tested for drift.

### Migration unit: normative statement, not file

MECE classification is performed one normative statement at a time. Before
another rule edit, build a migration ledger with one row for every `must`,
`never`, gate, required field, permitted action, state transition, and
behavior-changing exception in:

- installed workspace Codex guidance, the versioned workspace `CLAUDE.md`, and
  workspace rule sources;
- Saberu root/path `AGENTS.md`, `.agents/rules/`, `.agents/scenarios/`, and
  agent-strategy routing;
- the active uncommitted workspace and Saberu governance candidates.

The nonexistent `~/.claude/CLAUDE.md` is recorded as a broken reference. It is
not invented as a source and is not created merely to satisfy a stale route.

Each ledger row records:

| Field | Required content |
|---|---|
| Statement ID | stable source-domain identifier |
| Source | exact file and line/section |
| Trigger | observable condition that activates the rule |
| Required behavior | one testable obligation or permission |
| Current owners | every location that currently defines it |
| Content-quality verdict | `keep`, `rewrite-equivalent`, `merge`, `split`, `demote`, `remove-obsolete`, or `behavior-change-pending-decision` |
| Quality rationale | correctness, trigger precision, form, context cost, actionability and testability findings |
| Target owner | exactly one workspace or project canonical file |
| Project delta | narrower Saberu fact/constraint, or `none` |
| Migration action | `move`, `retain`, `replace-with-reference`, `split`, or `remove-as-obsolete` |
| Preservation evidence | target section plus scenario/check that proves equivalent or stronger behavior |
| Status | `unmapped`, `mapped`, `implemented`, `verified` |

Rules may be split only when the ledger preserves the original end-to-end
behavior and identifies one owner for each resulting obligation. A source
statement cannot be removed because its file “looks duplicated.”

Ledger reconciliation is mandatory:

- every source statement has exactly one terminal migration action;
- every target statement links back to at least one source requirement or a
  separately recorded new decision;
- counts and unresolved rows are reported before and after each migration;
- any `unmapped` or unverified behavior blocks publication and downstream
  deletion.

### Content-quality audit before migration

The ledger is not a mechanical copy plan. Before choosing a target owner,
evaluate every statement on these dimensions:

| Dimension | Question |
|---|---|
| Necessity | Does a real failure/risk still require this rule, or is it obsolete/pure preference? |
| Correctness | Does it match current Codex behavior, repository truth and the user's intended workflow? |
| Scope | Is it cross-project, project-wide, path-local, task-local, environment-specific or historical? |
| Trigger precision | Is the activation condition observable, or will the rule fire for unrelated work? |
| Rule form | Is it a positive recipe, required field, conditional or prohibition appropriate to the failure type? |
| Actionability | Can an executor tell exactly what to do, stop on, and report? |
| Testability | Can a scenario or static check distinguish compliance from plausible-sounding prose? |
| Duplication/conflict | Does another owner define the same or contradictory behavior? |
| Context cost | How often is it loaded, how much unrelated text must be read, and can it be routed on demand? |
| Freshness | Is it a stable invariant, or a dated fact/path/version that belongs in project/environment truth? |
| Recovery | If the rule stops execution, does it identify the safe next action rather than creating a dead end? |

Allowed outcomes:

- `keep`: correct, necessary and already in the right form;
- `rewrite-equivalent`: improve clarity/efficiency without changing behavior;
- `merge`: combine truly identical obligations under one owner;
- `split`: separate compound behaviors only with end-to-end preservation;
- `demote`: move situational facts/procedures to the project, path adapter,
  testing governance, operations, or environment truth;
- `remove-obsolete`: delete only with evidence that no required behavior is
  lost;
- `behavior-change-pending-decision`: isolate and present any semantic change
  instead of hiding it inside refactoring.

Efficiency targets:

- resident global/root `AGENTS.md` contains only always-applicable safety,
  precedence and task routing;
- one task trigger routes directly to one canonical module; avoid circular
  references and long “read A to discover B to discover C” chains;
- adapters link to owners and state only their narrower delta;
- examples illustrate a rule but do not become a second normative definition;
- repeated field lists and procedures appear once and are referenced elsewhere;
- rules do not force loading unrelated architecture, plans, or review
  checklists;
- record module word counts and task-load profiles for simple Git inspection,
  branch creation, publication, integration, and recovery; a task must not load
  unrelated later-action procedures merely because they share a broad domain;
- use direct trigger-to-owner routing with at most one adapter hop; split a
  large module only when the measured profile improves without introducing a
  reference chain.

Accuracy targets:

- stable invariants are separated from dated environment/project facts;
- authorization, plan approval, sandbox capability and action execution remain
  distinct;
- every command/path/reference named by a live rule is checked;
- precedence and conflict behavior are explicit;
- scenario tests cover both intended use and common misclassification;
- equivalent rewrites preserve all original outcomes, while semantic changes
  require a separately reviewed decision.

### Required invariant: branch task contract

The agent-neutral Git owner must uniquely own the cross-project requirement
that every new branch has a branch task contract. Contract fields,
branch-creation review, and persistence/publication timing are separately
reviewed under `DQ-01A`–`DQ-01C`.

The workspace contract owns these generic fields:

| Field | Meaning |
|---|---|
| Problem/outcome | what problem the branch solves and what changes observably |
| Approach/scope | how it will solve it, boundaries, prerequisites and exclusions |
| Acceptance | tests/evidence and the pass condition |
| Publication | intended logical commit grouping, review/push/PR route and target |
| Integration/closeout | how completion, remaining work and integration are handled |
| Retirement | how the integrated/cancelled branch and worktree are archived, retained or removed |

The contract also records branch name, exact base ref/OID, worktree path and
treatment of existing changes. It describes future publication, integration,
and retirement but does not authorize those later Git mutations. A contained
child may express each field concisely; it may not omit fields. If a session
interrupts after branch creation but before persistence, implementation remains
blocked until the already reviewed contract is restored.

Projects add only topology and persistence details: relationship, project
integration target, parent/child/dependent edges, lifecycle states, contract
location, project checks, and archive tooling.

## 2. Scope

### Workspace-meta

In scope:

- add modular agent-neutral cross-project rules under `.agents/rules/`, with
  separately identified agent-specific mechanics;
- keep both resident Codex and Claude adapters as compact routers plus an
  intentional non-negotiable safety floor, rather than expanding either into a
  monolith;
- define an explicit ownership registry and precedence language;
- build and reconcile the statement-level migration ledger before changing
  another rule;
- move all generic Git mechanics to the workspace layer, including read-only
  inspection, freshness fetch, branch/worktree/stash safety, exact-path
  publication, integration, identity, destructive/recovery behavior, and
  operator-versus-Codex execution;
- preserve the complete branch task contract and its create-to-retire lifecycle
  without creating administrative branch/PR loops;
- move generic task authorization, planning/evidence/handoff, verification,
  review, rule-authoring/provenance, capability-selection method, and
  secret-safety behavior to workspace modules;
- remove broken workspace Claude routes and conflicting/obsolete portable
  behavior only after their approved replacement owners exist;
- update architecture/ownership documentation, feedback provenance, tests, and
  the round changelog;
- install and drift-check the managed block after repository verification.

### Downstream Saberu

In scope after the workspace layer is installed:

- remove project `git.md` and update every route/reference;
- reduce project authorization to Saberu external/live-operation deltas;
- retain branch topology and lifecycle only in `branching.md`;
- retain only Conventional Commit/project-quality requirements in the project
  commit convention;
- reduce planning/review/capability/secret rules to Saberu-specific deltas or
  remove files that have no remaining project content;
- make root/path `AGENTS.md` and `CLAUDE.md` routing adapters rather than policy
  co-owners;
- deduplicate file/workstream routing around `file-naming.md`;
- verify representative workflows and the full project check.

Out of scope:

- changing `~/.codex/rules/*.rules`;
- creating `~/.claude/CLAUDE.md` merely to satisfy the current broken
  reference;
- changing credentials, trust, model selection, plugins, skills, histories, or
  caches;
- changing Saberu implementation behavior, inventory, playbooks, controller
  state, or live infrastructure;
- rewriting historical workstream evidence solely to use new paths;
- removing existing branches or worktrees;
- committing, pushing, creating PRs, merging, or archiving without the normal
  publication/integration review.

## 3. Workspace rule modules

The accepted `DQ-13` architecture replaces the frozen `codex-*` candidate:

| Logical owner | Portable responsibility |
|---|---|
| `authorization.md` | request/edit authority and protected-action semantics independent of sandbox implementation |
| `git.md` | inspection, freshness and the common pre-mutation snapshot |
| `git-branches.md` | complete branch contract, branch/worktree/stash and interruption recovery |
| `git-publication.md` | result review and one stage/commit/push/PR command bundle |
| `git-integration.md` | integration review, terminal evidence and retirement boundary |
| `git-recovery.md` | destructive/non-ordinary mutation and recovery |
| `planning.md` | generic investigation, evidence freshness, approval scope, handoff, deviation, and closeout |
| `verification.md` | direction/static/functional verification and evidence-based retry/blocking |
| `review.md` | review routing, severity, evidence, remediation, independent-review trigger, and stop conditions |
| `capabilities.md` | agent-neutral capability-selection triggers; concrete Codex/Claude tools stay in adapters |
| `secrets.md` | generic non-exposure, redaction, Git/history, and rotation safety floor |
| `environment-truth.md` | dated host capability truth, already present |
| `rule-authoring.md` | ownership, failure-form matching, incident provenance, and recurrence refactoring |

Agent-specific modules/adapters own only:

- Codex sandbox/escalation, deferred-tool discovery, and Codex configuration
  boundaries;
- Claude tool/permission/configuration mechanics actually supported by the
  environment;
- direct routing plus the minimum safety text required before the portable
  owner is loaded.

`codex-runtime.md` is the sole agent-specific rule module and owns Codex
sandbox/escalation, execpolicy, deferred-tool discovery, and configuration
mechanics. The root `CLAUDE.md` and managed Codex AGENTS block route to the
same portable core.

Measured Git profiles for this candidate:

| Task | Modules | Lines | Words |
|---|---|---:|---:|
| inspection/freshness | `git.md` | 47 | 201 |
| branch/worktree/stash | `git.md` + `git-branches.md` | 116 | 592 |
| publication | `git.md` + `git-publication.md` | 112 | 530 |
| integration | `git.md` + `git-integration.md` | 95 | 445 |
| recovery/destructive | `git.md` + `git-recovery.md` | 92 | 426 |

Every profile excludes unrelated later-action procedures and is smaller than
the frozen 177-line/940-word `codex-git.md`. The direct adapter route is the
only hop before these owners.

## 4. Execution phases

### Phase 0 — Complete behavior inventory

1. Freeze the current workspace and Saberu implementation candidates.
2. Extract all normative statements from every source named in the migration
   unit section.
3. Normalize compound bullets into one ledger row per testable behavior.
4. Perform the content-quality audit and assign a verdict/rationale before
   choosing the target owner.
5. Map each retained/reworked row to one target owner and identify true project
   deltas.
6. Review duplicate clusters, uncovered behavior, contradictory rules,
   inefficient load paths and obsolete rules.
7. Explicitly trace the branch task contract from branch creation through
   problem/approach/acceptance, publication, integration, closeout and
   retirement.
8. Classify each retained workspace statement as agent-neutral, Codex-specific,
   Claude-specific, project-specific, or host-local.

Gate: no rule implementation resumes until the ledger has zero `unmapped` rows,
all removals have evidence, equivalent rewrites have preservation criteria, and
the user has reviewed the ownership/content-quality summary plus all
behavior-changing decisions.

Phase 0 evidence:

- `migration-ledger-2026-07-20.md`: 214 normalized behavior rows, 70 source
  coverage groups, zero unmapped normative sections in the corrected source
  set, and 17 preservation/misclassification scenarios;
- `content-audit-summary-2026-07-20.md`: recommended ownership and 18 decision
  records (`DQ-01A`–`DQ-01C`, `DQ-02`–`DQ-16`);
- the user continued after review of those decisions, accepting them as the
  implementation basis; the old workspace and Saberu candidates remain
  historical evidence rather than publication targets.

### Phase 1 — Workspace ownership baseline

1. Finalize agent-neutral versus agent-specific physical owners from `DQ-13`
   and the task-load profiles.
2. Add exact reverse-whitelist entries for the approved managed rule files.
3. Revise the frozen candidate from the approved ledger rather than continuing
   its current assumptions.
4. Write the modules with explicit `Owns`, `Does not own`, source-statement
   traceability, and routing boundaries.
5. Add the complete branch task contract and interruption recovery to the
   agent-neutral Git owner.
6. Refactor the managed Codex template and workspace `CLAUDE.md` into symmetric
   thin adapters, retaining only ledger-approved safety floors and
   agent-specific mechanics.
7. Rewrite the uncommitted W-R32 candidate so it describes the reviewed
   architecture and does not claim that the invalid candidate already owns the
   behavior or that the earlier audit was complete.
8. Update the ownership matrix and architecture documentation.
9. Record per-module word counts and task-load profiles; split broad owners only
   when the profile improves without creating multi-hop routing.

Gate: no project rule is deleted before all corresponding workspace semantics
exist, every affected ledger row is `implemented`, and the installed global
router can reach them.

### Phase 2 — Workspace verification and installation

1. Extend sync tests to assert the managed router and preservation behavior.
2. Run `make test`.
3. Run shell/Python syntax checks and `git diff --check`.
4. Run bootstrap twice against an isolated temporary HOME and compare the
   managed outputs.
5. Run the current-host drift check, install with `make bootstrap`, then require
   a clean current-host drift check.

Gate: installed user-level rules match the reviewed workspace source.

### Phase 3 — Saberu project reduction

1. Create and populate the Saberu `S-LIVE` owner from `LIVE-01`–`LIVE-10` and
   the Saberu portion of `AUTH-13`; route to it and verify reachability before
   removing those statements from authorization, boundaries, or execution
   reflection.
2. Re-audit the preserved `/tmp/saberu-git-transaction-ux` candidate against
   the installed workspace modules and the approved migration ledger.
3. Process one source statement at a time; replace generic project rules with
   references only after target equivalence is verified.
4. Move remaining project-specific statements to their unique domain owners.
5. Keep Saberu branch topology, relationship, persistence, validation and
   archive deltas while removing the duplicate generic contract schema.
6. Keep a compact Saberu Claude safety floor for the no-direct-trunk and
   separate-retirement constraints, with canonical links that prevent
   independent evolution.
7. Update all project routing and living governance documentation.
8. Preserve existing workstream evidence and unrelated changes.

Gate: each removed statement maps either to a workspace rule or a named Saberu
owner, every ledger row is `verified`, and source/target counts reconcile.

### Phase 4 — Cross-layer scenario verification

Create a trace matrix for every scenario with:

- input prompt/state;
- triggered canonical owners;
- expected allowed action;
- required stop/review;
- forbidden action;
- captured evidence.

Verify the effective rules for:

1. explanation/review versus requested remediation;
2. ordinary in-workspace editing and validation;
3. a new independent branch: complete contract, exact fresh base, new worktree,
   first logical publication and no registration-only PR;
4. a contained child and a dependent feature: project relationship/target
   deltas without duplicating the generic contract;
5. additive branch/worktree creation with unrelated dirty work present;
6. commit/push/PR publication by Codex and by the operator;
7. merge/integration, accepted partial closeout, remaining-work transfer and
   post-integration routing;
8. branch/worktree retirement after integration or cancellation, proving that
   the original contract did not pre-authorize cleanup;
9. destructive Git recovery;
10. plan approval versus implementation and live authorization;
11. test-host versus managed-fleet mutation;
12. secret discovery in worktree, index, history, logs, or output;
13. documentation/workstream artifact creation and migration;
14. Codex/Claude parity for the same portable task;
15. proportional direction/static/functional verification and rule-form
    authoring.

For high-risk `SC-04`, `SC-06`, `SC-09`, and `SC-14`, add actual walkthrough
evidence using disposable local repositories/refs/bare remotes or synthetic
secrets. Do not mutate a real remote, real secret, live service, or user-owned
ref merely to test governance.

Run workspace-meta and Saberu repository checks. Treat contradictions,
unreachable owners, broken references, or a required check that cannot run as
blocking findings. Static tests establish structure/ownership but cannot replace
the trace matrix or required walkthroughs.

## 5. Acceptance criteria

- Every rule domain has one documented canonical owner.
- Every portable domain has one agent-neutral owner; Codex and Claude adapters
  own only their mechanics and an intentional tested safety floor.
- Every original normative statement has a reconciled, verified migration
  ledger row; there are zero `unmapped` rows.
- Every retained rule has a content-quality verdict and evidence for its
  necessity, scope, trigger, form and verification.
- Equivalent rewrites preserve behavior; semantic changes are isolated and
  separately reviewed.
- Resident and routed context contains no known unnecessary duplication,
  circular lookup or unrelated mandatory reading.
- Every new branch is governed by one complete create-to-retire task contract
  without requiring a registration-only commit/PR.
- Saberu no longer has a project-level Git policy file.
- Project rules contain only project facts, constraints, schemas, commands, and
  stricter deltas.
- Adapters route without copying normative tables or workflows.
- Generic behavior is available before project duplicates are removed.
- The installed managed block matches workspace-meta source.
- Workspace-meta tests, syntax checks, idempotent isolated bootstrap, drift
  check, and Saberu verification pass or have explicitly reported blockers.
- Every `SC-01`–`SC-17` has the required trace row and high-risk walkthroughs
  have disposable/synthetic evidence.
- The final result report distinguishes uncommitted, committed, unpushed, and
  unpublished work without performing publication implicitly.

## 6. Risks and controls

| Risk | Control |
|---|---|
| Moving rules creates a temporary behavior gap | migrate workspace semantics and install them before deleting project copies |
| File-level classification loses a behavior hidden in a project rule | inventory and reconcile every normative statement before editing or deleting |
| Mechanical migration preserves inefficient or inaccurate rules | complete the content-quality verdict before target ownership/migration |
| “Refactoring” silently changes behavior | separate equivalent rewrites from behavior-change-pending-decision rows |
| Splitting a compound rule breaks its end-to-end lifecycle | preserve a create-to-retire scenario and one explicit owner per resulting obligation |
| Global resident context becomes too large | use a compact router and task-shaped modular reads |
| A project delta is mistaken for a duplicate | require a statement-by-statement owner mapping |
| Cross-project policy accidentally embeds Saberu facts | prohibit project paths, commands, topology, and resource schemas in workspace modules |
| Dirty existing work is displaced | use only additive isolated worktrees and never stash/reset/clean |
| Claude and Codex become competing policy owners | split portable statements into neutral owners before naming files; define both agents as thin adapters and test paired routing |
| A neutral filename hides Codex-only behavior | statement-classify sandbox/escalation/tool mechanics and retain them under the Codex adapter |
| Broad Git module imposes recurring context cost | measure task-load profiles; split only when unrelated procedures disappear without multi-hop routing |
| Saberu live rules disappear during reduction | create, route, and verify `S-LIVE` before deleting any old source statement |
| Scenario prose gives an unfalsifiable pass | require trace rows for all scenarios and disposable/synthetic walkthroughs for SC-04/06/09/14 |
| Installed files drift from Git source | verify source, install, and run the drift check in the same round |

## 7. Closeout evidence

Write `round1-2026-07-20.changelog.md` with:

- files and ownership moves;
- migration-ledger totals, corrected cross-agent source set, unresolved rows and
  branch-contract traceability;
- content-quality verdict totals, semantic changes and efficiency improvements;
- statements deliberately retained at the project layer;
- verification commands/results and gaps;
- installed-host drift result;
- per-module word counts/task-load profiles and scenario trace/walkthrough
  evidence;
- downstream Saberu status;
- uncommitted/unpushed/publication state and the next reviewed transaction.

# Codex rule content audit summary

- **Date**: 2026-07-20
- **Ledger**: `migration-ledger-2026-07-20.md`
- **State**: review required before rule implementation resumes

## Outcome

The existing rules should be refactored, but a file move alone would not be
safe. The expanded statement-level audit reconciled 214 normalized behaviors
across 70 workspace/Saberu source coverage groups and found zero unmapped
normative sections in the corrected source set. It now has 18 decision records
where efficiency, accuracy, or cross-agent ownership requires explicit review
rather than an “equivalent” rewrite.

The first ledger omitted the versioned workspace `CLAUDE.md`. The audited host
does not have `~/.claude/CLAUDE.md`, so the earlier external review was wrong
about a second existing Claude user-level file, but correct that the versioned
workspace Claude layer was outside the declared source set. Its omission meant
the prior “zero unmapped” claim proved only Codex/Saberu coverage, not
cross-agent MECE.

The newly audited workspace Claude adapter contains both useful agent-neutral
methods and material conflicts:

- useful verification, durable handoff, resident-context, rule-form, provenance,
  and pending-work preservation principles;
- duplicate Git/environment/identity rules;
- mandatory plan/changelog/task-count gates that conflict with proportional
  planning;
- checkout/pull/commit-or-stash behavior that conflicts with additive
  worktrees and reviewed Git transactions;
- unconditional `git rm --cached` on secret discovery, which conflicts with
  authorization and secret-response safety;
- mandatory same-round commit/push and broken routes to the absent
  `~/.claude/CLAUDE.md`.

The frozen workspace candidate is directionally useful but incomplete:

- it correctly centralizes generic authorization, publication, planning,
  review, capability, secret, and environment behavior;
- it omits the complete branch task contract;
- its managed router is smaller, but some module triggers and resident safety
  text still overlap;
- it inherited several project rules without first deciding whether their
  content is efficient or correct;
- its `codex-*` names and mixed Codex/runtime versus portable semantics cannot
  act as a cross-agent SSOT without a statement-level split;
- its 177-line/940-word Git module makes simple inspection load publication,
  integration, destructive, and recovery procedures.

The frozen Saberu candidate correctly removes the old per-operation
commit/push confirmation model and the recursive closeout pattern, but it still
keeps a project `git.md`, duplicates generic Git fields, and leaves broader
planning/router/content problems untouched.

## Recommended ownership after refactoring

### Shared workspace/user level

Keep one agent-neutral canonical owner for each portable cross-project method:

- authorization/request/protected-action semantics and the boundary between
  user authority and technical runtime capability;
- all generic Git behavior, including the complete branch task contract,
  publication, integration, recovery, and retirement boundaries;
- generic planning/evidence/approval/deviation/closeout;
- generic review method/severity/stop conditions;
- conditional capability selection;
- generic secret incident safety;
- dated environment truth;
- verification method;
- rule authoring, provenance, and recurrence-driven refactoring.

Codex and Claude resident files should both contain only:

- precedence/ownership routing;
- the minimum safety floor needed before a module is loaded;
- direct task triggers for the shared modules;
- mechanics unique to that agent.

Codex sandbox/escalation/tool-discovery details remain Codex-specific. Claude
tool/permission/configuration mechanics remain Claude-specific. Merely removing
the `codex-` prefix without separating these statements would create a falsely
neutral owner.

### Saberu project level

Retain only:

- branch topology, relationship/state schema, `dev`/`master` routes,
  reconciliation, project archive tooling, and contract persistence;
- live/test-host/fleet target fields and external-resource evidence;
- Conventional Commit format and project checks;
- L2 plan/artifact layout and project truth paths;
- workstream/file naming, testing governance, documentation sync;
- secret locations/consumers/rotation conventions;
- architecture and path-local constraints.

Remove the project `git.md`. Distribute its genuine deltas to:

- `branching.md` for topology/integration/archive;
- commit convention for message format;
- testing governance for required checks;
- the live-operations rule for live/external actions.

Root/path `AGENTS.md` and `CLAUDE.md` become adapters, not second policy owners.

## Behavior decisions

### DQ-01A — Complete branch contract

Recommended: require every new branch contract to cover:

1. problem and observable outcome;
2. approach, scope, prerequisites, and exclusions;
3. acceptance/evidence and pass condition;
4. intended commit/publication/PR route;
5. integration/closeout and remaining-work ownership;
6. retirement/archive/retention handling;
7. exact branch, base OID, worktree, and treatment of existing changes.

All fields remain required for every branch that is actually created. A root
feature records full detail; a contained child may satisfy each field with one
concise line or subsection. Proportionality comes from not creating unnecessary
small branches, not from omitting parts of the contract.

### DQ-01B — One branch-creation review transaction

Recommended: present the complete copyable contract text together with the
exact branch name, base ref/OID, worktree path, existing-change treatment, and
additive branch/worktree command before creation. Review these as one
transaction, not as separate contract and command approvals.

### DQ-01C — First persistence and interruption recovery

Recommended: after worktree creation, persisting the reviewed contract is the
first file write and needs no second conversational checkpoint. Publish it with
the first logical implementation unit; do not create registration-only commits,
activation PRs, or successor branches.

The branch action and first contract write cannot be filesystem-atomic. If a
session stops after branch creation but before persistence, bootstrap must
detect “branch exists, contract missing”, block implementation, and restore the
already reviewed contract before continuing.

### DQ-02 — Terminal integration evidence

Recommended: PR/Git metadata is normally sufficient terminal evidence that a
source reached its target. Do not create a branch or PR solely to record the
preceding merge. If living truth materially needs correction, include it in the
next normal target-based owner; if a premature integration left required work,
make one bounded correction with a named owner rather than a successor loop.

### DQ-03 — Capability note is conditional

Recommended: remove mandatory `Capability fit` and “what was not used” fields
from every coding plan. Record a capability choice in an existing durable plan
or handoff only when an observable event occurs:

- deferred tool discovery or a connected application is used;
- delegation/subagents or specialized generation/automation is used;
- execution changes after a failed or abandoned capability attempt.

Do not use “non-default model” as a trigger: model selection can be host/user
owned or invisible to the executing agent.

### DQ-04 — Phases need not be independently committable

Recommended: phases/work units should be coherent implementation and
verification units. Do not shape them around Git commits. Logical commit
grouping is decided from the validated result at publication time.

### DQ-05 — Evidence closure is not Git publication

Recommended: a phase may be complete when its required evidence exists and
passes in the working tree or named external evidence store. It does not need a
commit merely to become “closed.” Its closeout must state when evidence is
local-only and unpublished. Evidence required by a later machine or agent must
enter the normal publication flow, or another approved durable store, before
handoff. No special evidence-only commit is required; repository evidence joins
the next logical publication bundle.

### DQ-06 — Material plan revision

Recommended: a material change to an approved plan must visibly leave the
approved state and be reviewed again. Update the current plan in place when it
is still the same decision and preserve a dated change note; create a new
superseding file only when the old decision needs an independent historical
identity. This preserves approval integrity without multiplying plan files.

### DQ-07 — Review stopping is outcome-based

Recommended: keep one broad audit plus targeted re-audit as the normal shape,
but remove the mechanical requirement for “two consecutive passes.” Stop when
the targeted re-audit finds no new in-scope P0/P1 and required checks/gaps are
settled; continue only on new evidence, changed scope, or a disproven
assumption.

### DQ-08 — Environment correction does not auto-commit

Recommended: update a contradicted living environment record promptly and
report its uncommitted/unpublished state. Do not require a same-round Git
commit; publication follows the normal Git review.

### DQ-09 — Bootstrap capability/environment loading is conditional

Recommended: bootstrap always performs the small project status/topic scan.
Load capability selection or run/refresh environment probes only when the
resumed task has an observable trigger:

- a plan, blocker, skipped check, or delegation depends on tool, daemon,
  credential, network, or authorization availability;
- the task requires a capability not visible in the current tool set;
- repeated failure indicates the current execution method may be wrong.

Simple explanation/read-only questions, ordinary edits using visible tools, and
quick status reports with no load-bearing environment claim are negative
examples. The existing SessionStart evaluator remains the background drift
signal.

### DQ-10 — Define a coherent evidence round

Recommended: one round file represents one coherent implementation/review/live
execution round with a distinct result and verification boundary. A chat turn,
approval step, commit, PR, or post-merge administrative update does not by
itself require another round file.

### DQ-11 — Separate instruction precedence from factual truth

Recommended:

- instruction precedence follows the active system/developer/user/AGENTS
  hierarchy;
- repository sources provide typed facts rather than a competing instruction
  order;
- code/config describes actual behavior;
- architecture/governance describes intended invariants;
- TODO/workstream describes active scope/state;
- feature maps/operator docs describe supported/documented surfaces.

When these disagree, report drift and resolve it; do not silently let “current
repo truth” override an instruction or let a stale document override observed
behavior.

### DQ-12 — VPS adapter and unfinished payload rename

Recommended: stop treating historical target-architecture plan/design files as
unconditional live instructions in `playbooks/vps/AGENTS.md`; route to stable
feature/operator docs and the active workstream. Do not change its “examples”
terminology to “payloads” from this governance branch before the owning rename
change reaches `dev`; apply that living-reference update with the rename owner.

### DQ-13 — Agent-neutral core and agent-specific adapters

Recommended:

- rename portable owners to neutral names such as `authorization.md`, `git.md`,
  `planning.md`, `review.md`, `verification.md`, `secrets.md`,
  `rule-authoring.md`, and the existing `environment-truth.md`;
- split Codex sandbox/escalation and concrete capability/tool mechanics into
  Codex adapters/modules;
- keep Claude-specific tool/permission/configuration mechanics in Claude
  adapters;
- make both resident adapters route to the same portable owners and retain only
  a compact intentional safety floor;
- do not create `~/.claude/CLAUDE.md` merely to satisfy the current broken
  reference. Portable rules belong in workspace-meta; actual host-local state
  stays in real host configuration.

This is a semantic split, not a wholesale filename replacement. Every moved
statement must retain one owner in the ledger.

### DQ-14 — Proportional classification and planning gates

Recommended: retain architecture/engineering/fix/exploration as optional
review lenses, selected from observable scope and risk. Do not require every
non-trivial task to declare one level, create both a plan and changelog, estimate
usage limits, or receive a separate sign-off merely because it contains three
tasks. The smallest applicable plan and the active project's actual L2 gate
control the required artifact and review depth.

### DQ-15 — Verification retry is dependency-based

Recommended: retain direction, syntax/static, and functional verification, with
functional execution required when feasible. After a failure and fix, rerun the
failed check plus affected/downstream checks needed for one coherent result.
Do not impose a universal restart-from-gate-one order or fixed three-attempt
limit; repeated failure instead triggers diagnosis and an explicit blocked/gap
report.

### DQ-16 — Independent review for destructive-sink code

Recommended: treat independent review as a risk-based requirement when a
destructive-sink implementation is actually being prepared and a permitted
review channel is available. Do not hard-code Codex, `/ultrareview`, or a
subagent; active delegation/authorization rules still apply. When independent
review is unavailable, report the gap and require the applicable human review
before integration rather than declaring all self-review structurally invalid.

## Content changes that do not need a behavior decision

These are ownership or clarity changes with equivalent intent:

- remove generic authorization/Git/planning/review/capability/secret copies from
  Saberu;
- create and verify the Saberu live-operations owner before removing its
  statements from authorization/boundaries/execution-reflection;
- replace repeated branch, plan, artifact, and docs-sync tables in adapters with
  direct canonical links;
- reduce `session-bootstrap.md` to Saberu status/topology reporting;
- move version/pinning/latency facts out of `operational-quirks.md` and rely on
  the stable operational-truth document;
- remove the unsupported `<thinking>`/chain-of-thought output instruction from
  `CLAUDE.md`;
- keep a compact Saberu Claude safety floor for no direct `dev`/`master`
  publication and separate archive/retirement, while linking the canonical
  branch owner and preventing independent drift;
- remove workspace Claude's unconditional secret-index mutation, commit/stash,
  same-round publication, fixed security-fast-track, and broken
  `~/.claude/CLAUDE.md` routes after their replacement owners are verified;
- retain path-local architecture/test constraints only where they are unique;
- keep historical evidence literal while updating living executable
  references;
- rewrite the uncommitted W-R32 candidate before implementation so it describes
  the reviewed agent-neutral/shared-core architecture and does not claim the
  invalid candidate “now owns” or completed a full MECE audit.

## Expected efficiency improvement

- Ordinary local edit: resident safety floor plus the authorization module only
  when first write/permission boundary is reached; no project authorization or
  Git module unless triggered.
- Review: one workspace review module plus one Saberu domain/artifact delta,
  rather than router + review protocol + closure + lenses + every scenario.
- Coding: one workspace planning method plus the relevant Saberu
  architecture/test/doc routes, without mandatory capability boilerplate.
- Git publication: one workspace Git module plus project branch/message/check
  facts, with one result acceptance and one command-bundle authorization.
- Bootstrap: project status/topic scan first; capability/environment detail only
  when load-bearing.
- Cross-agent task: Codex and Claude adapters route to the same portable owner;
  only their actual runtime mechanics differ.

Module efficiency is evaluated by task load profile, not a mechanical line
limit. The frozen `codex-git.md` is 177 lines/940 words and currently makes a
simple Git inspection load publication, integration, destructive, and recovery
content. Phase 1 must record per-module words and the exact modules loaded for
at least inspection, branch creation, publication, integration, and recovery;
split only where that evidence removes unrelated procedures without creating a
long reference chain.

## Scenario acceptance

For every `SC-01`–`SC-17`, Phase 4 must produce:

- input prompt/state;
- triggered canonical owners;
- expected allowed action;
- required stop/review;
- forbidden action;
- evidence captured.

`SC-04`, `SC-06`, `SC-09`, and `SC-14` also require disposable/synthetic
walkthroughs. Static tests prove ownership and links, but cannot by themselves
prove agent behavior.

## Gate

**Gate result (2026-07-20): accepted for implementation.** After the
recommendations and corrections were reviewed, the user instructed the work to
continue. The 18 records (`DQ-01A`–`DQ-01C`, `DQ-02`–`DQ-16`) therefore form
the Phase 1 implementation basis; this does not authorize publication,
installation on the current host, or downstream Saberu deletion.

1. revise agent-neutral workspace owners and agent-specific adapters from the
   ledger;
2. run workspace structure/scenario/bootstrap/drift checks;
3. install the verified workspace layer;
4. create/verify Saberu's live-operations owner, then rebase the rest of the
   Saberu reduction conceptually on installed owners and revise only project
   deltas;
5. run all cross-layer scenarios and repository checks.

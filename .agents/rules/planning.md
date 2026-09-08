# Planning And Handoff

Agent-neutral workspace rule for proportional planning, evidence, approval
scope, execution deviation, durable handoff, and closeout.

## Ownership

This file owns generic planning, approval, material-deviation, handoff, and
Plan lifecycle behavior. `documentation.md` owns the durable content roles of
Plans and Changelogs. Projects own plan filenames/directories, additional
metadata, architecture sources, branch gates, test commands, and live-resource
fields.

## Before Planning

Investigate in two passes:

1. direction: current repository truth, active task/branch, ownership, and
   whether the work belongs here;
2. implementation: current code/configuration, existing patterns, native
   framework/tool approaches, risks, and acceptance carrier.

Using the knowledge-state definitions in `reasoning.md`, separate known
repository facts, verified external facts, assumptions, research/probe needs,
and operator decisions. Do not make changing external behavior load-bearing
from memory; use current primary/official sources. Environment facts follow
`environment-truth.md`.

Every material unknown names when/how it closes and what happens if evidence
contradicts the proposed direction.

## Proportional Shape

Plan at the level of a coherent workstream: one bounded outcome, scope, and
acceptance path may span multiple conversational turns, implementation passes,
operator feedback cycles, repairs, and verification runs. Before creating a
persistent Plan, inspect existing active or approved Plans and reuse one that
already covers the same goal and scope.

Use the smallest plan that preserves the decision:

- narrow work may use a concise conversational plan;
- architecture, cross-surface, high-risk, or multi-phase work uses the
  project's persistent plan format;
- investigation, decision, runbook, stable contract, review, and evidence are
  not automatically additional plans.

Architecture, engineering, fix, and exploration are optional review lenses
selected from observable scope and risk. Do not require a level declaration,
two artifacts, cost/usage estimate, or separate approval merely because a task
is non-trivial or has a given number of steps. File count, conversational turns,
implementation rounds, operator feedback, fixes, and re-verification do not by
themselves create another workstream or require another Plan.

Create a new persistent Plan only when persistent planning is warranted and no
existing Plan covers the workstream, the requested outcome is genuinely
independent, or a material change requires reconsidering the approved execution
contract. In the last case, follow the material-deviation process below; that
process determines whether to amend the existing Plan or approve a replacement
contract rather than silently multiplying Plans.

A persistent Plan is the approved implementation intent and execution contract.
It states the goal, approval-time current state, intended change,
scope/exclusions, load-bearing prerequisites or assumptions, acceptance
criteria, risks, and follow-up handling in depth proportional to the decision.

Use `DRAFT` for an unapproved Plan, `APPROVED` for its executable frozen
contract, and `COMPLETE` for verified closeout. `IN_PROGRESS` and `BLOCKED` are
not required as normal durable Plan states; report ordinary execution or
blocked state in task context instead.

## Approval Scope

Plan approval is scoped. Direction approval does not automatically approve
conflicting implementation details; parent approval does not approve a
conflicting child; implementation approval does not authorize Git publication,
external writes, or live mutation. A pending child blocks only its named scope.

At `APPROVED`, stable Plan content freezes. Ordinary implementation progress,
failed attempts, retries, routine repairs, intermediate hypotheses, command
output, and intermediate verification stay in transient task context rather
than being persisted into the Plan.

Follow-up requests such as continuing the work, clarifying diagnostics,
adjusting an in-scope configuration value or order, fixing an implementation or
test defect, and repeating acceptance verification stay under the same Plan
when their goal and scope remain covered. They are not automatically new
planning decisions.

A variation is a material deviation when continuing would require a reasonable
approver to reconsider the approved outcome or authority because it changes the
goal or expected effect, scope or non-goals, canonical ownership or
architecture, a load-bearing approved approach or dependency, a safety,
security, or authorization boundary, a load-bearing assumption, acceptance
criteria, or the evidence capable of proving acceptance. File count and bug
severity alone do not decide materiality; routine in-scope implementation,
repair, and verification are not automatically material.

For a material deviation:

1. stop affected work before crossing the approved boundary;
2. identify the proposed deviation and its impact in transient review context;
3. obtain the approval required by this file and `authorization.md`;
4. only after approval, amend the necessary stable Plan content and add a
   concise dated approved-deviation record;
5. freeze the Plan again; and
6. resume within the amended approval.

Identification or recommendation is not approval. A rejected deviation leaves
the approved Plan unchanged; continue the original path only when still
feasible, otherwise stop and report through the existing owner. Unaffected work
may continue while a deviation is pending only when it is genuinely separable
and cannot prejudice the decision.

## Execution And Evidence

Use approved scope and acceptance checks as the baseline. At each substantial
phase, re-check repository state, current external behavior, environment
capability, operator decisions, and live target scope when load-bearing.

When reality contradicts the Plan, classify the mismatch and update its actual
truth owner. Apply the material-deviation boundary above only when the
contradiction changes the approved execution contract; a new fact alone does
not authorize Plan amendment.

Phases are coherent implementation and verification units, not mandatory Git
commit units. Their ordinary progress and intermediate evidence remain in task
context. Evidence needed by another machine or agent must enter the normal
publication flow, or another approved durable store, before handoff; no
evidence-only administrative commit is required.

## Handoff And Closeout

Persist load-bearing handoff state in the existing owning artifact when one
exists. Do not require the user to relay instructions between agents or
sessions, and do not create a new artifact solely to hold a routine handoff.

When an in-scope change resolves a living source that still directs future
work, update it in the same bounded content change or report the exact deferred
owner/gap. Publication remains a separate Git transaction.

Closeout compares the result and evidence with the approved goal, expected
effect, scope, and acceptance criteria. Do not mark a Plan `COMPLETE` merely
because one implementation or verification pass finished. While the operator
is still actively reviewing, testing, or refining the same goal and scope, the
coherent workstream remains under its `APPROVED` Plan. After the workstream is
content-complete and final non-transaction-bound verification demonstrates
acceptance, create the Changelog as the verified outcome record under
`documentation.md`, ready for publication review. Commit-ready does not mean
staged, committed, pushed, or published.

The Plan may then transition from `APPROVED` to `COMPLETE` and add a Changelog
link as closeout metadata. Do not copy implementation history, command output,
or the verification narrative into the completed Plan.

A `COMPLETE` Plan is normally a historical record. Before its verified result
enters durable Git history as a commit, an unresolved issue may show that
closeout was premature. Only when the correction remains within the same goal
and scope and requires no material deviation, restore that Plan to `APPROVED`,
correct and verify the same workstream, update its existing Changelog under
`documentation.md`, and then close it again. This is a narrow pre-commit
closeout-correction exception, not a way to reactivate completed Plans
generally.

Once the completed result has entered Git history, do not reopen its Plan for a
later change, even when the commit has not been pushed or the change affects the
same feature or files. Treat later work as a follow-up coherent workstream and
apply proportional planning independently: a narrow fix may need no persistent
Plan, while a substantial redesign may warrant one. Amending, resetting,
discarding, or otherwise rewriting Git history is a separate Git transaction
and is not authorized by this lifecycle rule.

Plan completion, implementation completion, publication, integration, release,
and archival are distinct facts.

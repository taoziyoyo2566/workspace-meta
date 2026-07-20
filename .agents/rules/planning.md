# Planning And Handoff

Agent-neutral workspace rule for proportional planning, evidence, approval
scope, execution deviation, durable handoff, and closeout.

## Ownership

This file owns generic planning and handoff behavior. Projects own plan
filenames/directories, required metadata, architecture sources, branch gates,
test commands, and live-resource fields.

## Before Planning

Investigate in two passes:

1. direction: current repository truth, active task/branch, ownership, and
   whether the work belongs here;
2. implementation: current code/configuration, existing patterns, native
   framework/tool approaches, risks, and acceptance carrier.

Separate known repository facts, verified external facts, assumptions,
research/probe needs, and operator decisions. Do not make changing external
behavior load-bearing from memory; use current primary/official sources.
Environment facts follow `environment-truth.md`.

Every material unknown names when/how it closes and what happens if evidence
contradicts the proposed direction.

## Proportional Shape

Use the smallest plan that preserves the decision:

- narrow work may use a concise conversational plan;
- architecture, cross-surface, high-risk, or multi-phase work uses the
  project's persistent plan format;
- investigation, decision, runbook, stable contract, review, and evidence are
  not automatically additional plans.

Architecture, engineering, fix, and exploration are optional review lenses
selected from observable scope and risk. Do not require a level declaration,
two artifacts, cost/usage estimate, or separate approval merely because a task
is non-trivial or has a given number of steps.

A plan states goal, scope/exclusions, prerequisites, expected effect, approach,
risks, concrete changes, verification, and follow-up handling in depth
proportional to the decision.

## Approval Scope

Plan approval is scoped. Direction approval does not automatically approve
conflicting implementation details; parent approval does not approve a
conflicting child; implementation approval does not authorize Git publication,
external writes, or live mutation. A pending child blocks only its named scope.

A material change to approved scope, direction, approach, or verification makes
the affected plan visibly pending again. Update the existing plan with a dated
note when it remains the same decision; create a superseding artifact only when
the old decision needs an independent historical identity.

## Execution And Evidence

Use approved scope and acceptance checks as the baseline. At each substantial
phase, re-check repository state, current external behavior, environment
capability, operator decisions, and live target scope when load-bearing.

When reality contradicts the plan:

1. stop before compounding the mismatch;
2. classify stale knowledge, repository drift, missing probe/decision,
   ambiguity, or rules gap;
3. record the contradiction in the owning evidence location;
4. revise approval state when the decision materially changes;
5. continue only after the required decision/approval.

Phases are coherent implementation and verification units, not mandatory Git
commit units. A phase may close with valid working-tree or approved external
evidence. Its closeout states when evidence is local-only and unpublished.
Evidence needed by another machine or agent must enter the normal publication
flow, or another approved durable store, before handoff; no evidence-only
administrative commit is required.

## Handoff And Closeout

Persist load-bearing handoff state in the existing owning artifact when one
exists. Do not require the user to relay instructions between agents or
sessions, and do not create a new artifact solely to hold a routine handoff.

When an in-scope change resolves a living source that still directs future
work, update it in the same bounded content change or report the exact deferred
owner/gap. Publication remains a separate Git transaction.

Closeout compares the result/evidence with goal, expected effect, scope, and
acceptance. Report outcome, checks/gaps, deviations, synchronized living truth,
remaining owner, local-only/unpublished evidence, and protected follow-ups.

Plan completion, implementation completion, publication, integration, release,
and archival are distinct facts.

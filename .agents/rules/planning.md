# Planning And Handoff

Agent-neutral workspace rule for proportional planning, evidence, approval
scope, execution deviation, durable handoff, and closeout.

## Ownership

This file owns generic planning, discovery of earlier and concurrent work,
recording of confirmed findings and operator decisions, approval,
material-deviation, handoff, and Plan lifecycle behavior. `documentation.md`
owns the durable content roles of Plans, Changelogs, and investigation records.
Projects own plan filenames/directories, where verified findings are recorded,
additional metadata, architecture sources, branch gates, test commands, and
live-resource fields.

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

Before an investigation, experiment, or persistent Plan, find what earlier and
concurrent work already established about the same ground. Name the task's
triggers: the paths and components, settings or keys, external dependencies
with versions, and features it will change or rely on. Search the project's
recorded findings, Plans, and investigation and review records for them,
including uncommitted documents, other worktrees, and unmerged branches. Read
in full every document that matches a setting or dependency exactly, and
enough of the others to judge whether they apply. Link what the new work
builds on, depends on, supersedes, or contradicts.

Red flags: "only Plans with the same goal matter", "it is uncommitted, so
nothing is decided yet", "that belongs to another feature", "I already know
how this dependency behaves".

A recorded conclusion bound to another dependency version, scope, or date is a
lead to re-verify, not a current fact. Resolve a conflict between recorded
documents, or between one and current evidence, under `reasoning.md`, and
record the outcome as Record Findings When Confirmed describes.

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

An independent capability is one whose goal no existing Plan's approved goal
and scope covers. When it warrants persistent planning, it gets its own Plan
file, even when it extends the same feature, touches the same files, or was
requested during another workstream. Do not fold its design into another Plan
as an added section, a "later changes" or "post-launch changes" entry, an
implementation-record item, or an appendix evaluating unrelated options; link
the related Plans to each other instead. Red flags: "it is a follow-up of the
same feature", "the same reader will look there", "that Plan already has a
changes section". A stable contract's approved-change log records changes to
that contract; it is not a place to design a new capability either.

Two active workstreams that depend on the same change to a shared component or
dependency, such as one version upgrade, share that change as one capability
with one owner: the existing Plan whose approved scope covers it, otherwise its
own workstream. The dependent work links to it and neither redesigns nor
executes the change separately. When ownership is disputed, the operator
decides.

A persistent Plan is the approved implementation intent and execution contract.
It states the goal, approval-time current state, intended change,
scope/exclusions, load-bearing prerequisites or assumptions, acceptance
criteria, risks, and follow-up handling in depth proportional to the decision.

Describe the present problem, intended behavior, affected project entities, and
implementation mechanism in concrete language. Explain consequential tradeoffs;
do not invent alternatives merely to fill a template. Acceptance names the
conditions, observable result, and evidence that can prove it. For phased work,
name each phase's output and the prerequisites for the next phase. These are
content requirements, not mandatory headings or additional documents.

An implementation task names an action and its actual module, interface, data,
or operational target, plus the check that makes it complete. Add dependencies,
entry checks, and failure/recovery handling where they affect safe execution.
Generic phase labels such as "implement, test, accept" do not by themselves
make an executable task. Use project runbooks for exact operational commands;
do not repeat portable development rules inside every task.

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
phase, re-check repository state, recorded findings and concurrent work on the
task's triggers, current external behavior, environment capability, operator
decisions, and live target scope when load-bearing.

When reality contradicts the Plan, classify the mismatch and update its actual
truth owner. Apply the material-deviation boundary above only when the
contradiction changes the approved execution contract; a new fact alone does
not authorize Plan amendment.

Phases are coherent implementation and verification units, not mandatory Git
commit units. Their ordinary progress and intermediate evidence remain in task
context. Evidence needed by another machine or agent must enter the normal
publication flow, or another approved durable store, before handoff; no
evidence-only administrative commit is required. A verified finding that
constrains other work is recorded earlier, as Record Findings When Confirmed
describes.

## Record Findings When Confirmed

Write a verified conclusion to the project's durable record when it is
confirmed if it constrains work beyond the current diff: a compatibility limit,
a changed default, a refuted premise of another document, or dependency
behavior that a Plan relies on. Use the owner the project names for verified
findings, otherwise an investigation record, and include the evidence, the
versions and scope it holds for, and a recheck condition when it rests on
volatile external facts. Do not hold it for handoff or closeout; a concurrent
session is not a handoff and sees only what is on disk. A conclusion about a
shared component or dependency belongs in that component's record, which
feature Plans link, not inside one feature's Plan. Routine attempts, command
output, and unverified hypotheses remain transient.

Do not edit a document that another session has left uncommitted unless the
operator hands that document to your task. Otherwise record your finding in
your own document, link the other one, mark a contradiction explicitly, and
report the overlap to the operator.

When the task does not authorize project writes, present the finding with its
proposed record and ask once. A project may grant standing authority to write
these records.

## Record Decisions When Made

When the operator makes or changes a decision that alters what a living
artifact says about a workstream, such as approving, deferring, dropping, or
reordering work, changing its scope, or answering a question the artifact lists
as open, record it in that artifact in the same turn, before any other task
work except the reads that locate the record and confirm you may write it, so
an interrupted turn still leaves it on disk. When the same message asks for an
action the record would block, such as a deploy that needs a clean checkout, do
that action first and record the decision right after it. For a Plan, the
artifacts are its status and approval record and the project's progress owner;
any other living document that still lists the question as open is updated in
the same change. Record what was decided and its scope, the operator's words
when wording matters, and the date it was made: today's date from the clock
when you record it in the turn it was made, otherwise the date of the message
that made it.

Recording grants nothing the operator did not decide. For an `APPROVED` Plan, a
deferral or drop is a concise dated record beside the approval, and the status
line names it; other frozen content does not change. A decision that changes
frozen content, such as the scope or acceptance criteria, is a material
deviation: note it at once in the status and approval record as pending, state
its impact in the same turn, and amend the content only through the steps in
Approval Scope.

A condition you can settle from evidence, such as "if it is not necessary", is
yours to settle: record the decision with that reasoning. A statement whose
condition only the operator can settle, or that is ambiguous, gets one question
in the same turn, and the artifact states the open question with your
recommendation until the operator answers.

An operator decision about a workstream hands that workstream's status and
approval record and its progress-owner entry to your task, even when another
session left those documents uncommitted: change only those entries and report
the overlap. Without write authority, present the exact proposed record and ask
once, in the same turn and before other work, for permission to write it; the
question is about the write, not the decision.

Agent memory may point to the record. While a record waits for write
permission, a memory entry may hold the decision marked as unrecorded, with its
date and the owner it must reach; otherwise memory is never the only place a
decision or a workstream's state lives.

Red flags: "I'll update the Plan once the operator confirms" after the operator
has decided; "memory has it for now"; "it is uncommitted anyway"; "the next
session will pick it up"; "I'll do it at closeout".

## Handoff And Closeout

Persist load-bearing handoff state in the existing owning artifact when one
exists. Do not require the user to relay instructions between agents or
sessions, and do not create a new artifact solely to hold a routine handoff.
Agent memory is not an owning artifact: other agents and hosts do not see it,
and the copy loaded into a session is a snapshot.

Before reporting a workstream's status, a pending decision, or what the
operator still owes from memory, a summary, or an earlier turn or session, read
its owning artifact and the relevant Git state; a memory entry or summary line
is a lead to open, not the answer. When they disagree, do not settle it by the
kind of record: find which is current from dated evidence, such as the
operator's own words or Git history, report that state and the disagreement,
and bring the owning artifact up to date in the same turn or name it as a gap.

When an in-scope change resolves a living source that still directs future
work, update it in the same bounded content change or report the exact deferred
owner/gap to the operator. Publication remains a separate Git transaction.

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

# Plan: Coherent Workstream Lifecycle Refinement

Status: COMPLETE on 2026-09-08 after a bounded pre-commit closeout correction.
Verified outcome:
[Changelog](coherent-workstream-lifecycle-2026-09-08.changelog.md).

## Goal

Make a coherent workstream, rather than each non-trivial change or execution
round, the unit of persistent planning and verified closeout. Preserve
proportional planning, frozen approved intent, material-deviation approval,
transient routine execution state, durable final outcome evidence, and the
separate Git publication boundary.

## Current State

- `planning.md` distinguishes narrow conversational planning from persistent
  Plans and keeps ordinary implementation activity transient, but it does not
  require checking whether an existing Plan already covers a follow-up.
- Its closeout language permits completion after implementation and acceptance
  evidence without explicitly accounting for ongoing operator review or
  in-scope refinement of the same outcome.
- `documentation.md` separates Plan and Changelog roles but does not explicitly
  define a Changelog at coherent-workstream scope or discourage one per round.
- Project `AGENTS.md` says every non-trivial behavior/configuration change
  requires a Plan and asks for a round Changelog. Together those phrases drove
  three Plan/Changelog pairs for one uncommitted managed-sync workstream.
- The existing lifecycle regression protects freeze and closeout timing, but
  not Plan reuse, workstream-level completion, or the project adapter's
  prohibition on round-driven artifacts.

## Intended Change

- Extend `planning.md` with a workstream-reuse decision before Plan creation,
  explicit non-triggers, and a completion boundary that remains open during
  active operator review, testing, or routine in-scope refinement.
- Extend `documentation.md` only with the artifact-role consequence: normally
  one final Changelog for one coherent workstream, never an interaction log or
  per-round record.
- Replace the project adapter's change-level and round-level wording with a
  concise workspace-meta delta that routes lifecycle judgment to the shared
  owners.
- Record this recurrence and owner refinement as W-R46 without rewriting prior
  provenance or Round 8–10 records.
- Strengthen the existing source-contract regression with a few stable
  workstream lifecycle invariants; do not add a Plan parser or workflow engine.

## Scope And Non-Goals

In scope are `.agents/rules/planning.md`, `.agents/rules/documentation.md`,
project `AGENTS.md`, `feedback-register.md`, the existing lifecycle regression,
this Plan, and one final Changelog after verified closeout.

Out of scope are managed sync/status-line behavior, Git publication semantics,
directory renaming, historical record edits, issue/PR state requirements,
generic task tracking, exact-prose parsing, staging, commits, pushes, pulls,
fetches, and PR creation. `README.md` and `scripts/check_documentation.py` remain
unchanged unless implementation proves a current claim or structural gate is
inaccurate.

## Acceptance Criteria

1. Persistent Plan creation is proportional and keyed to a coherent workstream;
   an existing active/approved Plan covering the same goal and scope is reused.
2. Conversation count, execution rounds, file count, fixes, operator feedback,
   and re-verification do not independently require another Plan.
3. Active operator review/testing and routine in-scope refinement do not
   complete the Plan or create a new planning decision.
4. Material changes to the approved execution contract retain the existing
   stop, review, approve, amend, freeze, and resume process.
5. A Changelog records the final verified workstream outcome; normally one Plan
   produces one final Changelog, without a mechanical cardinality rule.
6. Project guidance contains only the concise workspace-meta delta and cannot
   reasonably be read as requiring a Plan and Changelog per change or round.
7. Regression coverage protects the stable contract without duplicating large
   policy blocks or parsing historical artifacts.
8. Round 8–10 history and the `docs/reviews` directory remain unchanged.
9. Repository-required verification passes, and this workstream produces only
   this Plan plus at most one final Changelog.

## Material Deviation Boundary

Use the existing `planning.md` process without weakening it. Stop and obtain
approval before changing this workstream's goal, owner split, authorization or
security boundaries, historical-record policy, acceptance criteria, or required
acceptance evidence. Routine wording refinement, focused test correction, and
re-verification within the approved outcome stay under this Plan.

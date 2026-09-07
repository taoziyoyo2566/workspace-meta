# Plan: Plan and Changelog Lifecycle Refactor

Status: COMPLETE
Changelog: [Verified closeout](round1-plan-changelog-lifecycle-2026-09-07.changelog.md)

## Goal

Establish a durable lifecycle in which a Plan is the approved implementation
intent and execution contract, ordinary execution state remains transient, and
the approved Plan body stays frozen except for an approved material deviation.

Create the Changelog only at verified, content-complete, commit-ready closeout
so it records the actual outcome rather than implementation activity. Keep
versioned governance concise and high-signal without claiming a numerical
reduction in context or compute cost.

## Current State

- `planning.md` owns generic Plan, approval, deviation, handoff, and closeout
  workflow; `documentation.md` owns durable-document roles and truth lifecycle.
- Changelog timing and content are not precisely canonicalized, and adjacent
  capability/environment guidance can pressure agents to write routine
  execution history into an approved Plan.
- Existing Plans and Changelogs sometimes duplicate completion and verification
  facts. They remain historical evidence and will not be migrated.
- The accepted reasoning-governance worktree is separate and must remain
  unchanged by this refactor.

## Intended Change

Assign each durable fact one lifecycle owner:

- **Plan**: approved Goal, approval-time Current State, Intended Change, Scope
  and non-goals, Acceptance Criteria, approved Material Deviations, and Status.
- **Transient task context**: progress, intermediate hypotheses, failed
  attempts, routine repairs, command output, retry loops, and intermediate
  verification.
- **Changelog**: verified final outcome, meaningful changed surface, final
  verification, approved deviations actually implemented, and relevant
  residual gaps.
- **Provenance**: durable cross-task governance rationale.
- **Git**: exact committed history.

The normal Plan lifecycle is:

```text
DRAFT -> approval -> APPROVED -> implementation and verification
      -> verified commit-ready -> create Changelog -> COMPLETE
```

`IN_PROGRESS` and `BLOCKED` are not normal durable Plan states. Exceptional
abandoned or superseded handling remains conditional. At `APPROVED`, the Plan
body freezes and routine work does not mutate it. At `COMPLETE`, only Status and
a Changelog link may be added as closeout metadata; the Plan does not receive a
duplicate implementation or verification narrative.

The Changelog is created only after implementation is verified,
content-complete, and ready for publication review. Commit-ready does not mean
staged, committed, pushed, or published. Its compact shape is a title, relative
Plan link, Summary, Changes, and Verification, with Plan Deviations and
Remaining Gaps only when applicable. Intermediate failures or retries appear
only when they explain a lasting limitation or material final correction.

### Material Deviation

A variation is material when continuing would require a reasonable approver to
reconsider the approved outcome or authority because it changes one or more of:

- goal or expected effect;
- in-scope or out-of-scope boundary;
- canonical ownership or architecture;
- a load-bearing approved implementation approach or dependency;
- a safety, security, or authorization boundary;
- a load-bearing assumption;
- Acceptance Criteria; or
- required evidence capable of proving acceptance.

File count and bug severity alone are not materiality tests. Routine in-scope
implementation, repair, and verification remain ordinary execution variation.

When a material deviation is discovered, stop affected work before crossing
the approved boundary, identify the proposed change and impact in transient
review context, and obtain the approval required by existing planning and
authorization ownership. Identification is not approval. Only after approval
may the necessary stable Plan sections be amended and a concise dated Approved
Deviation record added. Freeze the Plan again, then resume within the amended
approval. Agents must not silently turn a discovery into scope expansion.

If the deviation is rejected, leave the approved Plan unchanged. Continue the
original path only when it remains feasible; otherwise stop and report the
blocked or abandoned outcome through existing owners.

This Plan follows that rule after L2: its body is frozen, it receives no routine
progress or verification updates, and its Changelog is not created early. A
material L3 discovery must be reported with the affected Plan sections,
proposed amendment, and impact before this Plan is changed.

## Scope

### In Scope

- `.agents/rules/planning.md`: own Plan freeze, transient execution state,
  material-deviation control, and the transition to Changelog closeout.
- `.agents/rules/documentation.md`: distinguish approved Plan intent from
  verified Changelog outcome and exclude execution-journal content.
- `AGENTS.md`: retain repository Plan location rules and move Changelog creation
  from merely after implementation to verified commit-ready closeout.
- `.agents/rules/implementation.md`: split the current combined
  `plan/ADR/review/changelog` artifact role, which conflates approved intent
  with recorded outcome.
- `.agents/rules/capabilities.md`: stop routine capability attempts or method
  repairs from being written into a frozen Plan; retain durable reproducibility
  evidence in its proper final owner.
- `.agents/rules/environment-truth.md`: keep freshness and living-state
  correction while routing frozen-Plan changes through material-deviation
  handling.
- `.agents/host-templates/env-sync-SKILL.md`: replace its unconditional active
  Plan-precondition update with the planning-owned deviation boundary.
- `docs/architecture/codex-config-management.md`: replace the repository-map
  description of a Changelog for every round with verified closeout semantics.
- `feedback-register.md`: record this cross-task lifecycle refinement and update
  existing owner mappings without rewriting historical entries.
- `tests/test_sync_codex_config.py`: add one focused source-contract regression
  for stable lifecycle invariants without parsing historical artifacts or exact
  prose.
- `.gitignore` and this Plan: allow and carry the transition contract.
- `docs/reviews/refactor-plan-changelog-lifecycle/round1-plan-changelog-lifecycle-2026-09-07.changelog.md`:
  create only after implementation reaches verified commit-ready closeout.

### Out of Scope

- New portable rule modules or a workflow/state-machine framework.
- Historical Plan, Changelog, or W-R migration or rewriting.
- Progress logs, generated execution logs, detailed activity telemetry, or
  mandatory reasoning transcripts.
- Exact-prose lifecycle enforcement or a Markdown semantic parser.
- `scripts/check_documentation.py` or `tests/test_governance_docs.py` unless a
  concrete structural dependency is discovered and approved as a material
  deviation.
- `.agents/rules/reasoning.md`, `.agents/rules/review.md`,
  `.agents/rules/verification.md`, `.agents/rules/authorization.md`, Git rule
  modules, or `.agents/rules/secrets.md`.
- `CLAUDE.md` or the Codex adapter unless a concrete routing defect is
  discovered and approved as a material deviation.
- Bootstrap, status-line, host configuration, repository visibility, or nested
  project changes.
- The paused public-repository-policy implementation.
- Staging, committing, pushing, publication, or activation.

## Material Assumptions

- Existing planning and documentation routes are sufficient; no adapter change
  is required.
- Stable source-contract assertions can protect the lifecycle boundary without
  parsing individual Plans or Changelogs.
- Current documentation checks can remain structural, with review providing
  the semantic acceptance judgment.
- Prospective application is sufficient: this transition task may use the
  current convention, and the paused public-policy remediation will be the
  first subsequent task explicitly governed by the completed lifecycle.

## Safety / Ownership Boundaries

- `verification.md` continues to own post-change checks, verdicts, retries, and
  gaps; the Changelog only records the final result.
- `authorization.md` continues to own approval and protected-action boundaries;
  this lifecycle grants no additional authority.
- Environment and capability owners retain current-state and method-selection
  responsibilities but do not own Plan amendment.
- Publication remains a separate Git transaction after final documentation
  validation.

## Acceptance Criteria

1. Plan and Changelog have distinct canonical durable roles.
2. An approved Plan body freezes; ordinary progress, repairs, failed attempts,
   command output, retries, and intermediate verification remain transient.
3. Material deviation follows stop, review, approve, amend, freeze, and resume;
   identifying a deviation does not authorize expansion.
4. Materiality follows the approved contract and required proof, not file count
   or bug severity.
5. A Changelog is created only at verified commit-ready closeout and records
   verified outcome rather than chronological activity.
6. Plan completion changes only Status and Changelog-link metadata; it does not
   duplicate Changelog closeout content.
7. `verification.md` and `authorization.md` retain their existing ownership.
8. Environment and capability guidance no longer forces routine execution
   history into frozen Plans.
9. Historical Plans, Changelogs, and W-R entries remain unchanged, and no new
   lifecycle rule module is introduced.
10. Enforcement remains lightweight: one stable source-contract regression,
    no historical artifact parser, no exact-prose lock, and no inferred
    filesystem chronology.
11. Existing reasoning-governance semantics and dirty artifacts remain
    unchanged.
12. The paused public-policy task can use the lifecycle prospectively with a
    compact approved Plan and no Changelog until verified closeout.
13. The final lifecycle implementation is represented by one concise
    commit-ready Changelog created only after verification.

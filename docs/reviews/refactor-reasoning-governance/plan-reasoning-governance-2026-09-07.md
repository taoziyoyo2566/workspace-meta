# Plan: portable technical-reasoning governance

- **Date**: 2026-09-07
- **Level**: Cross-project governance and agent configuration
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: the operator accepted the first-round ownership analysis and
  froze the canonical-owner, Hybrid Safety Floor, scope, proportionality, and
  non-duplication decisions on 2026-09-07.
- **Implementation authority**: completed through the operator-authorized G1–G7
  rounds. Publication, host activation, and nested-project changes remain
  separate and were not authorized.

## Goal

Add exactly one agent-neutral portable owner, `.agents/rules/reasoning.md`, for
the epistemic method used to reach technical conclusions. Make that owner
loadable through symmetric Claude/Codex routing and bind one compact invariant
to the resident Safety Floor without copying the detailed procedure into either
adapter.

The result should improve premise validation, evidence evaluation, diagnosis,
and uncertainty handling while remaining lightweight for simple or already
well-supported work. Existing planning, review, verification, environment,
implementation, and authorization workflows retain their current owners.

## Frozen design

1. `reasoning.md` is the only new portable reasoning module. Do not add
   `debugging.md`, `evidence.md`, `diagnosis.md`, or another sibling unless later
   repository evidence demonstrates that one owner has become structurally
   insufficient.
2. The canonical owner covers:
   - proportional validation of load-bearing premises;
   - classification of observed or verified facts, inferences, hypotheses,
     assumptions, and operator decisions;
   - independent technical judgment without reflexive disagreement;
   - evidence quality and competing hypotheses when warranted;
   - discriminating diagnostic probes and calibrated uncertainty;
   - proportional investigation;
   - preference for read-only observation or isolated/reversible probes before
     persistent diagnostic changes when appropriate; and
   - stopping when evidence is sufficient for the decision.
3. Operator-owned goals, constraints, tradeoffs, and decisions remain
   authoritative as decisions. They are not empirical evidence, and technical
   premises remain open to proportionate validation.
4. Reasoning is not a mandatory output ritual. Simple or well-supported cases
   do not require exhaustive research, a hypothesis table, a confidence score,
   or a verbose reasoning report.
5. Instruction authority and empirical state remain separate concepts:
   instructions and operator decisions constrain what should be done, while
   evidence supports claims about what is true. Volatile host/runtime facts
   continue to follow `environment-truth.md`; agent runtime mechanics remain in
   their adapters.
6. The Hybrid Safety Floor contains one compact resident invariant covering
   proportional validation of load-bearing premises and separation of technical
   conclusions from assumptions and operator decisions. All detailed method
   remains task-routed through `reasoning.md`.

## Scope

- Add and route the single canonical owner.
- Add the future owner path to the reverse whitelist before relying on it as a
  tracked governance file.
- Update existing portable-owner inventories, provenance, and focused
  enforcement.
- Make only narrow references or wording cleanup where an existing owner would
  otherwise appear to define the same general epistemic method.
- Preserve one identical Claude/Codex Safety Floor and bind its new invariant to
  the canonical source in the documentation gate.
- Perform a final semantic re-audit for ownership, proportionality, adapter
  symmetry, and scope before closeout.

## Out of scope

- Redesigning Git, publication, authorization, bootstrap, status-line, secret,
  trust, permission, or host-runtime systems.
- Modifying any repository under `~/workspace/projects/`.
- Making `docs/architecture/codex-config-management.md` a planned change. It may
  be reconsidered only if implementation reveals a concrete inconsistency that
  cannot be resolved in the canonical owner, ownership matrix, or adapters; such
  a discovery is a plan deviation and must be surfaced before editing it.
- Defining project evidence sources, diagnostic commands, architecture,
  thresholds, or domain-specific invariants.
- Moving plan/handoff, review, verification, environment freshness,
  artifact-shape, or authorization procedures into `reasoning.md`.
- Requiring persistent diagnostic changes, or treating an isolated/live probe
  as exempt from the applicable authorization boundary.
- Staging, committing, pushing, publishing, installing host configuration, or
  performing live/external mutation.

## Ownership boundaries

| Owner | Canonical definition retained | Permitted use of `reasoning.md` |
|---|---|---|
| `reasoning.md` | Claim-state classification, premise validation, evidence evaluation, competing explanations, discriminating probes, independent technical judgment, and uncertainty calibration | Canonical definition only; it does not prescribe another workflow's artifact or report shape. |
| `planning.md` | Plan investigation sequence, plan shape, unknown-closure commitments, approval scope, deviation, handoff, and closeout | Refer to reasoning classifications for material plan inputs; do not maintain a second general claim taxonomy. |
| `review.md` | Review/audit scope, lenses, findings, severity, remediation, independent-review requirements, and stopping conditions | Use reasoning when evaluating technical premises and diagnoses. Independent technical judgment is not the same as requiring an independent reviewer. |
| `verification.md` | Post-change direction, syntax/static, and functional verification; retry and gap reporting | Use reasoning to investigate causes of failed checks. Exploratory diagnostic evidence is not automatically final verification. |
| `environment-truth.md` | Freshness, dated environment facts, registry/probe behavior, contradictions, and environment-based blocked verdicts | Supply current environment evidence to reasoning; retain all volatile-state lifecycle rules here. |
| `implementation.md` | Artifact boundaries, normative source-of-truth placement, comments, change surface, and test shape | A diagnostic change remains an implementation change. “One normative fact, one owner” remains artifact governance, not epistemic claim classification. |
| `authorization.md` | Task/plan/action authority, protected mutations, permission semantics, action briefs, and the threshold for asking the operator | Reasoning chooses informative methods only inside that authority. Read-only preference grants no new scope; protected or live probes still require applicable authorization. |

## Implementation goals

### G1 — Establish the canonical owner and tracking path

- **Current state**: `.agents/rules/` has no general reasoning owner. Relevant
  concepts are fragmented across workflow-specific rules, and `.gitignore`
  explicitly allowlists every tracked rule without a `reasoning.md` entry.
- **Proposed modification**: first add the explicit
  `!.agents/rules/reasoning.md` whitelist entry, then create `reasoning.md` with
  an ownership statement and the frozen proportional epistemic method. Keep the
  module concise enough for task-shaped loading.
- **Dependencies**: frozen design; existing `rule-authoring.md`,
  `planning.md`, `review.md`, `verification.md`, `environment-truth.md`,
  `implementation.md`, and `authorization.md` boundaries.
- **Acceptance evidence**: the new path is not ignored; the file declares one
  clear owner; all frozen method elements are present; no sibling reasoning
  module exists; no workflow procedure or project fact is imported.
- **Status**: COMPLETE.

### G2 — Install the Hybrid Safety Floor and symmetric task routing

- **Current state**: Claude and Codex have identical resident Safety Floors and
  parallel route tables, but neither names `reasoning.md`. A portable distinction
  between instruction precedence and repository factual truth currently appears
  only in the Claude adapter.
- **Proposed modification**: add `reasoning.md` to the Safety Floor canonical
  source list; add the same single compact invariant to both adapters; add the
  same observable task route for load-bearing premises, conflicting evidence,
  technical judgment, competing explanations, or diagnostic method. Move or
  reduce the Claude-only portable statement once its meaning is represented by
  the shared owner and symmetric floor/route.
- **Dependencies**: G1 canonical wording must exist before adapter copies and
  routes are finalized.
- **Acceptance evidence**: byte-identical Claude/Codex Safety Floor sections;
  exactly one compact reasoning invariant in each; both route tables name
  `reasoning.md`; no detailed reasoning procedure appears in either adapter;
  Codex-only runtime mechanics remain Codex-only.
- **Status**: COMPLETE.

### G3 — Clarify workflow usage with minimal owner cleanup

- **Current state**: `planning.md` contains a plan-specific claim taxonomy;
  `review.md` describes diagnosis and evidence-backed findings;
  `verification.md` classifies failed-check causes; and `implementation.md`
  broadly says verification owns evidence selection. These are valid workflow
  requirements but can appear to overlap a new general epistemic owner.
- **Proposed modification**: make the smallest references or wording
  refinements needed to preserve the boundaries in the table above. Expected
  touch candidates are `planning.md`, `review.md`, `verification.md`, and
  `implementation.md`. Do not rewrite their procedures. Treat
  `environment-truth.md` and `authorization.md` as reference targets and leave
  them unchanged unless a concrete contradiction is found during whole-owner
  review.
- **Dependencies**: G1 definitions and terminology.
- **Acceptance evidence**: planning still owns plan/handoff workflow; review
  still owns findings/severity/stopping; verification still owns post-change
  checks; environment truth still owns freshness/probes; implementation still
  owns change shape; authorization still owns authority. No second general
  reasoning procedure remains.
- **Status**: COMPLETE.

### G4 — Update ownership, navigation, and provenance

- **Current state**: the portable-owner matrix, README summary, and feedback
  owner map do not list a reasoning domain; provenance currently ends at W-R42.
- **Proposed modification**: add the reasoning row and permitted project delta
  to `.agents/host-templates/README-agents.md`; update only the portable-domain
  summary in `README.md`; record the accepted design as W-R43 and add its owner
  mapping in `feedback-register.md`. Preserve historical entries unchanged.
- **Dependencies**: G1 and G3 establish final ownership wording.
- **Acceptance evidence**: one canonical owner is named consistently; README is
  navigational rather than a second procedure; W-R43 records source, rationale,
  and application without rewriting older provenance.
- **Status**: COMPLETE.

### G5 — Extend focused enforcement and regression coverage

- **Current state**: `scripts/check_documentation.py` dynamically requires every
  portable rule to appear in both route tables and separately binds Safety Floor
  copies to named owners. `tests/test_sync_codex_config.py` also contains
  explicit portable-owner lists. No focused assertion covers the reasoning
  owner or its anti-ritual/proportionality boundaries.
- **Proposed modification**: extend the existing lists and source-binding
  checks; add focused assertions for unique ownership, symmetric routing, the
  single compact Safety Floor invariant, and absence of detailed adapter copies.
  Because policy text is itself the contract, use narrow source-shape assertions
  only for load-bearing ownership/routing invariants. Do not build a new testing
  framework or attempt to test hidden chain-of-thought.
- **Dependencies**: G1–G4 final paths and wording.
- **Acceptance evidence**: tests fail for a missing reasoning route, divergent
  Safety Floors, missing canonical source phrase, omitted portable-owner entry,
  or detailed procedure copied into an adapter; the normal repository suite
  passes with the intended design.
- **Status**: COMPLETE.

### G6 — Verify the complete workspace-meta change

- **Current state**: the repository requires unit/documentation checks, shell
  and Python syntax validation, generated-format parsing, diff checks,
  reverse-whitelist validation, and isolated two-pass bootstrap idempotency.
- **Proposed modification**: execute the existing required checks against only
  the workspace-meta change and record exact results or explicit gaps.
- **Dependencies**: G1–G5 complete.
- **Acceptance evidence**:
  - `make test` passes;
  - `bash -n scripts/*.sh .githooks/pre-commit` passes;
  - `PYTHON_BIN="$(./scripts/find_python.sh)" && "$PYTHON_BIN" -m py_compile scripts/*.py tests/*.py` passes;
  - generated TOML, JSON, and YAML exercised by the repository are parsed;
  - `git diff --check` passes;
  - every new path passes reverse-whitelist/pre-commit validation; and
  - two bootstrap runs against one isolated temporary HOME leave managed-file
    hashes unchanged on the second run.
- **Status**: COMPLETE.

### G7 — Perform semantic re-audit and closeout

- **Current state**: no implementation result or round changelog exists.
- **Proposed modification**: re-read every changed canonical owner and adapter
  as a coherent set, compare the diff with the frozen decisions, resolve only
  in-scope P0/P1 findings, and create
  `round1-reasoning-governance-2026-09-07.changelog.md` after implementation and
  verification.
- **Dependencies**: G6 results.
- **Acceptance evidence**: the re-audit confirms one canonical reasoning owner,
  one compact resident invariant, task-routed detail, symmetric adapters,
  preserved workflow ownership, no nested-project or unrelated-system changes,
  and no unsupported completion claim. The changelog records files, checks,
  gaps, deviations, and local-only/unpublished state.
- **Status**: COMPLETE.

## Ordered implementation phases

1. **Canonical definition** — re-check the clean scope, add the rule-path
   whitelist, and create `reasoning.md` (G1).
2. **Consumption boundaries** — add the Hybrid Safety Floor and symmetric route,
   then make only the necessary workflow-owner references (G2–G3).
3. **Ownership records** — update the matrix, README navigation, and W-R43
   provenance after terminology is stable (G4).
4. **Enforcement** — update existing documentation and sync tests without
   introducing a new framework (G5).
5. **Verification** — run the full repository-required check matrix and preserve
   gaps accurately (G6).
6. **Semantic re-audit and closeout** — review the complete result against the
   frozen design, stop at the defined boundary, and write the round changelog
   (G7).

Later phases must not be used to compensate for an unresolved earlier
ownership conflict. If evidence contradicts the frozen direction, stop before
spreading the mismatch and return the affected decision for review.

## Guardrails and risks

| Risk | Required guardrail |
|---|---|
| Reflexive disagreement | State positively that operator goals, constraints, tradeoffs, and decisions are authoritative within their scope; require contrary technical conclusions to follow evidence, not a disposition to disagree. |
| Exhaustive premise checking | Trigger validation only for load-bearing premises and scale effort to uncertainty, consequence, reversibility, and available evidence. |
| Mandatory hypothesis ritual | Require competing hypotheses only when multiple plausible explanations matter; never require a table, fixed count, or visible enumeration for a simple case. |
| Mandatory confidence ritual | Express uncertainty only when it affects the decision; do not require numerical scores or verbose reports. |
| Duplicated procedures | Keep the complete method only in `reasoning.md`; adapters contain one invariant and routes, while workflow owners contain only their workflow-specific use. |
| Scope creep | Touch only the forecast workspace-meta files; stop before Git, host, bootstrap, status-line, secret, trust, architecture, or nested-project redesign. |
| Over-engineering | Add no new module, schema, framework, runtime evaluator, or generated artifact beyond the single owner and existing enforcement surfaces. |
| Diagnostic mutation presented as universally wrong | Express read-only/isolated probes as a preference when they can discriminate causes; permit a necessary persistent probe only within authorization and with proportional risk handling. |
| Instruction/runtime conflation | Keep instruction authority, empirical evidence, host capability truth, and technical tool permission as distinct concepts and owners. |
| Safety Floor growth | Limit the resident addition to one compact invariant and verify exact Claude/Codex parity. |

## Semantic acceptance scenarios

The final re-audit must be able to answer each scenario from the canonical
sources without inventing another procedure:

1. A simple, well-supported task proceeds without an exhaustive premise audit,
   hypothesis table, confidence score, or verbose reasoning report.
2. A user-supplied technical premise contradicted by direct evidence is surfaced
   proportionally rather than accepted merely because the user stated it.
3. An operator-selected goal or tradeoff remains authoritative as a decision and
   does not trigger mechanical disagreement.
4. An ambiguous failure with multiple plausible causes uses evidence that can
   discriminate between them rather than immediately applying a persistent fix.
5. A read-only observation or isolated/reversible probe is preferred when it can
   distinguish causes; a protected/live probe remains governed by
   `authorization.md`.
6. A plan uses reasoning classifications for material inputs while
   `planning.md` continues to own the plan, approval, deviation, and handoff
   workflow.
7. A failed post-change check may trigger reasoning-guided diagnosis, but the
   final pass/gap verdict still follows `verification.md`.
8. A volatile host fact is evaluated through current evidence while freshness,
   registry, and blocked-verdict semantics remain in `environment-truth.md`.

## Final semantic re-audit and stopping criteria

Implementation stops when all of the following are true:

- exactly one new portable rule file exists and it owns the complete frozen
  epistemic method;
- the detailed procedure appears in no adapter or sibling module;
- the resident invariant is singular, compact, source-bound, and identical for
  Claude and Codex;
- every route, owner inventory, whitelist, provenance entry, and focused test is
  synchronized;
- planning, review, verification, environment truth, implementation, and
  authorization retain the workflow responsibilities frozen above;
- the semantic acceptance scenarios are satisfied;
- required checks pass or remaining gaps are explicitly reported;
- no in-scope P0/P1 review finding remains; and
- the round changelog records the verified result and that it is local-only and
  unpublished.

P2 wording polish, speculative abstractions, additional reasoning modules,
unrelated cleanup, host activation, and publication are not reasons to continue
this implementation round.

## Unresolved decisions

None. Exact sentence-level wording and the smallest necessary cross-references
remain bounded implementation judgment. Any need to change the frozen owner
model, add a second reasoning module, alter a protected-action boundary, modify
`docs/architecture/codex-config-management.md`, or touch a nested project is a
material deviation and must return for operator decision before editing.

## Closeout

- **Completed**: 2026-09-07. G1 through G7 are complete. G5R repaired the one
  objective G6 test-maintenance finding without changing governance semantics.
- **Verification**: G6-R found the accumulated implementation structurally and
  technically ready for semantic audit. The focused repaired test passed; 79 of
  80 full-suite tests passed, with the sole non-pass caused by the intentionally
  untracked `.agents/rules/reasoning.md` publication-state gate. Shell syntax,
  Python compilation, diff hygiene, reverse-whitelist checks, isolated generated
  JSON/TOML parsing, agent synchronization, and two-pass bootstrap idempotency
  passed.
- **Semantic review**: all six original goals and all nine accepted scenarios
  pass. One canonical owner, one compact resident invariant, task-routed detail,
  symmetric adapters, bounded project deltas, and existing workflow ownership
  remain intact. No P0, P1, or P2 finding remains.
- **Gaps and boundaries**: general YAML parsing was blocked by the absence of a
  parser on this host, while the isolated environment registry generated and
  passed its freshness check. A real Claude/Codex UI smoke test was not
  applicable because host activation remained out of scope. No nested project,
  real host configuration, Git index, or publication state was changed.
- **Publication readiness**: PUBLICATION-READY. The implementation, this plan,
  and the round changelog remain local-only and unpublished. This status does
  not authorize staging, committing, pushing, or host activation.

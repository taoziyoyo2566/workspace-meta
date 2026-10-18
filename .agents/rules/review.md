# Review

Agent-neutral workspace rule for review and audit procedure, findings, problem
reports, remediation, severity, evidence reporting, and stopping conditions.

## Ownership

This file owns generic review and audit procedure, findings, reports of which
problems exist, remediation, severity, independent-review requirements, and
stopping conditions. Technical premise and evidence evaluation, including
diagnostic reasoning, follow `reasoning.md`; independent technical judgment
does not itself require an independent reviewer. Projects own their
architecture baseline, domain-specific scenarios, test matrix, artifact
routing, and risk-specific severity refinements.

Review, audit, and diagnosis requests are read-only by default. A request to fix
findings or apply recommendations authorizes bounded working-tree remediation
under `authorization.md`, but not Git publication or external/live writes. The
one standing exception is a missing project entry file, which the session in
conversation with the operator creates as `documentation.md` Project Bootstrap
describes, unless the operator or the brief forbids writes.

## Review Shape

1. Freeze the comparison base, nearest Git root, and scope. Explicitly classify
   nested repositories and host-local state as in-scope or supplemental before
   inspecting them.
2. Identify intended outcome, non-goals, and acceptance evidence.
3. Choose one dominant review type: feature, bugfix, refactor, operations,
   maintenance, or documentation/governance.
4. Add only relevant risk lenses: security, performance/scale,
   compatibility/migration, operability/recovery, testability/evidence.
5. Review actual behavior/diff before wording or style.
6. Verify claims with the project's required checks.
7. Lead with findings ordered by severity and grounded in file/line or
   observable evidence; then report checks, gaps, and residual risk.

At review start, record a compact scope snapshot:

- **Target repository**: nearest Git root and requested task.
- **Comparison base**: commit, branch, or other frozen reference.
- **In scope**: files, behavior, and checks covered by this review.
- **Supplemental only**: related repositories or host state that may be
  consulted, with the reason and exact path/root.
- **Excluded**: related state that must not affect the current verdict.

Do not expand every review into every scenario. Review a plan by the behavior
it proposes; metadata/location is a bounded artifact check, not automatically
the primary review type.

When a workspace contains nested Git roots, do not silently combine their
status/diffs or host-local configuration with the current repository review.
Inspect related state only when the user names that boundary, the current
request explicitly adopts a plan whose acceptance evidence requires it, or the
current repository's documented acceptance check cannot run without it. A plan
merely present in the repository, a directory name, or a related configuration
path does not activate cross-boundary scope. Label any consulted state
supplemental and report its exact path/root separately.

## Independent Review

When code or automation implements a destructive sink, decide the need for an
independent reviewer from observable blast radius, reversibility, recovery, and
the review channels permitted by active instructions. Do not hard-code an
agent/tool or treat self-review as categorically invalid.

If independent review is required but unavailable, report the gap and require
the applicable human review before integration. A waiver names its authority
and residual risk.

## Severity

- `P0`: contradictory/unsafe instruction, destructive/security-critical defect,
  impossible command/path, or routing that can place work on the wrong target.
- `P1`: material bug/regression, stale executable guidance, missing required
  rule/test, or unsupported completion/verification claim.
- `P2`: clarity, maintainability, optional hardening, or future improvement that
  does not block the requested outcome.

Distinguish confirmed defects from questions and preferences.

## Problem Reports

When asked which problems exist or were found, or when reporting them unasked,
list as a problem only a defect or risk that holds now and has an effect, with
evidence you obtained yourself: a file and line, command output, or a log
time. Order the list by severity.

- Pending work, known limitations, planned phases, and matters outside the
  asked scope are not problems. Mention one only when it matters, under its
  own label. A check you could not run is a gap (`verification.md`).
- A claim from another session or agent, a tool, or memory is a lead: verify
  it first, or report it as that source's unverified claim (`reasoning.md`).
  A finding from an agent you delegated to counts once you have checked the
  evidence it cites.
- Read a metric or status field from its definition before reporting it.
- Call something confirmed only when a check you can name establishes that
  claim itself. Ruling out one cause is an inference, not a confirmation.

An empty list is a valid answer when it says what was checked.

## Completion

A review report is complete when scope is frozen, relevant scenarios/lenses
were applied, findings are evidence-backed/classified, appropriate read-only
verification ran, and gaps/residual risk are stated. Open P0/P1 findings make
the reviewed change unready; they do not make the report incomplete.

Authorized remediation closes when no in-scope P0/P1 remains, required checks
pass or accepted gaps are explicit, P2 items are classified, and closeout
states what changed and remains. A handled problem that meets
`problem-follow-up.md` also gets its follow-up report.

Normal cadence is one broad audit, one authorized implementation pass, and one
targeted re-audit. Stop when the targeted re-audit finds no new in-scope P0/P1
and required checks/gaps are settled. Continue only for changed scope, new
evidence, or a disproven assumption; do not edit merely for wording polish.

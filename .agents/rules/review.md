# Review

Agent-neutral workspace rule for reviews, audits, diagnoses, remediation,
severity, evidence, and stopping conditions.

## Ownership

This file owns generic review method. Projects own their architecture baseline,
domain-specific scenarios, test matrix, artifact routing, and risk-specific
severity refinements.

Review, audit, and diagnosis requests are read-only by default. A request to fix
findings or apply recommendations authorizes bounded working-tree remediation
under `authorization.md`, but not Git publication or external/live writes.

## Review Shape

1. Freeze the comparison base and scope.
2. Identify intended outcome, non-goals, and acceptance evidence.
3. Choose one dominant review type: feature, bugfix, refactor, operations,
   maintenance, or documentation/governance.
4. Add only relevant risk lenses: security, performance/scale,
   compatibility/migration, operability/recovery, testability/evidence.
5. Review actual behavior/diff before wording or style.
6. Verify claims with the project's required checks.
7. Lead with findings ordered by severity and grounded in file/line or
   observable evidence; then report checks, gaps, and residual risk.

Do not expand every review into every scenario. Review a plan by the behavior
it proposes; metadata/location is a bounded artifact check, not automatically
the primary review type.

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

## Completion

A review report is complete when scope is frozen, relevant scenarios/lenses
were applied, findings are evidence-backed/classified, appropriate read-only
verification ran, and gaps/residual risk are stated. Open P0/P1 findings make
the reviewed change unready; they do not make the report incomplete.

Authorized remediation closes when no in-scope P0/P1 remains, required checks
pass or accepted gaps are explicit, P2 items are classified, and closeout
states what changed and remains.

Normal cadence is one broad audit, one authorized implementation pass, and one
targeted re-audit. Stop when the targeted re-audit finds no new in-scope P0/P1
and required checks/gaps are settled. Continue only for changed scope, new
evidence, or a disproven assumption; do not edit merely for wording polish.

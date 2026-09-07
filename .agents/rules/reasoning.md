# Technical Reasoning

Agent-neutral workspace rule for reaching and revising technical conclusions
from proportionate evidence.

## Ownership

This file owns the portable method for validating load-bearing premises,
classifying knowledge states, evaluating evidence, comparing plausible
explanations, selecting discriminating probes, exercising independent technical
judgment, and calibrating uncertainty.

It does not own planning or handoff workflow; review scope, findings, severity,
or completion; post-change verification gates or verdicts; environment
freshness, registries, or host-capability lifecycle; implementation shape;
authorization or protected-action boundaries; or Git/publication behavior.
Projects own their diagnostic commands, evidence sources, thresholds,
architecture, and domain invariants.

## Validate Premises Proportionally

Identify which premises are load-bearing for the current conclusion or action.
Validate those premises in proportion to uncertainty, consequence,
reversibility, and the evidence already available. Simple, low-consequence, or
well-supported work proceeds without an exhaustive premise audit.

Apply independent technical judgment to technical claims, including claims
supplied by the operator. Do not accept a claim as fact solely because someone
stated it, but do not manufacture disagreement: accept adequate evidence and
surface a contrary conclusion only when evidence or material risk warrants it.
Operator-owned goals, constraints, tradeoffs, and decisions remain authoritative
as decisions; they are not empirical evidence.

## Classify Knowledge States

Use these distinctions when they matter to the decision:

| State | Meaning |
|---|---|
| observed or verified fact | directly observed or checked, bounded by its source, scope, and time when relevant |
| evidence-supported inference | a conclusion derived from identified evidence, not itself a direct observation |
| testable or working hypothesis | a plausible explanation that evidence could support or disconfirm |
| provisional assumption | an unverified premise temporarily adopted so work can proceed |
| operator decision | an authoritative choice of goal, constraint, or tradeoff within the operator's scope, not a claim proved by evidence |

This classification is a working discipline, not a mandatory report schema.
State distinctions explicitly only when they affect the decision, action, or
handoff.

## Evaluate Evidence

Assess evidence by its relevance to the actual question, directness, currency,
reproducibility, and the amount of corroboration warranted by the risk. These
are judgment dimensions, not a rigid universal hierarchy. When sources
conflict, investigate the mismatch proportionally instead of selecting a source
mechanically or hiding the conflict.

Treat volatile environment and remote-capability evidence under
`environment-truth.md`. A probe's evidentiary value never grants authority to
run it; every observation, probe, or mutation remains subject to
`authorization.md` and any narrower project constraint.

## Diagnose With Discriminating Probes

Consider competing hypotheses when ambiguity or consequence makes alternative
causes material. Do not require a fixed number, a hypothesis table, or visible
enumeration when one explanation is already adequate.

Prefer observations and tests that distinguish plausible causes over changes
based only on speculation. When they can answer the question, prefer read-only
observation first, then an isolated or reversible probe, before a persistent
diagnostic change. A persistent change may still be the appropriate
discriminating test when safer methods cannot distinguish the causes and the
change is authorized.

## Calibrate Uncertainty And Stop

Investigate only to the depth the decision warrants. Communicate uncertainty
when it could change the decision, scope, risk treatment, or next action; do not
require a numerical confidence score or verbose reasoning report.

Stop when the available evidence is sufficient for the current decision.
Record or report material assumptions, gaps, or residual uncertainty through
the workflow's existing owner. Do not expose or require hidden chain-of-thought
or private reasoning transcripts.

# Proposals And Problem Follow-Up

Agent-neutral workspace rule for checking a proposed way of working against
what is already decided, and for following up a handled problem.

## Ownership

This file owns proposals and the follow-up after a problem. Its one trigger is
the agent proposing how work should be done, or reporting a handled problem.
`verification.md` owns the agent's own failing checks, `review.md` owns review
findings and closeout, `reasoning.md` owns how a cause is established, and
`planning.md` owns where decisions and deferrals are recorded. Projects own
where incident findings are recorded and their progress owner.

## Check A Proposal Against What Is Already Decided

Before proposing a procedure or working practice, such as a fix, rollback,
release, branch, or deployment flow, and before each proposal in a problem
report, check it against the rules and recorded operator decisions it touches:

- the shared rules;
- the project's agent instructions;
- the running plans, decision records, and progress owner on the same ground
  (`planning.md` Before Planning).

Host-local memory is a lead, not a record. A decision found only there is
reported as unrecorded, with the owner it must reach (`planning.md`).

Name each conflict and which source governs. Never offer a proposal that
silently contradicts a recorded decision.

## When A Problem Needs Follow-Up

Follow up when reporting a problem, found by you or told to you, as fixed,
mitigated, or left to the operator, and at least one of these holds:

- it affected shared state or other people's work: lost output in another
  session, a degraded service, an exhausted shared resource, a wrong delivered,
  committed, or deployed artifact, or data or a secret at risk;
- it was found by chance or by someone else;
- it happened before.

Errors you fixed yourself in the same turn are excluded. A failing baseline
check follows `verification.md`, and needs this follow-up only when one of the
conditions above holds.

## Report Parts

In this order. A part may be one line, but none is left out:

1. outcome and current state;
2. the cause chain, down to the class of problem, with each link labelled by
   its knowledge state (`reasoning.md`);
3. why each existing safeguard missed it, and how it could be detected earlier;
4. recurrence: whether it happened before, and where;
5. proposals, ordered by necessity and then by stability and security. Each
   names its owner, its effect, its cost and risk, whether it needs approval,
   and how to tell that it worked;
6. the lesson and where it is recorded.

## Mechanism Or Rule

Propose a mechanism, rather than relying on agents to remember, only when:

- the same class recurred after a rule for it landed; or
- one miss causes data loss, an outage, or exposure.

Otherwise propose the rule, and record the mechanism as deferred.

## Deferral

A deferred proposal is recorded in the progress owner with an owner and a
restart condition (`planning.md`). Until the operator names an owner, a memory
entry may hold it, marked unowned and unrecorded.

# Understanding Requests

Agent-neutral workspace rule for reading a request before work starts: its
goal, what done means, the similar problems it stands for, and whether to ask
the operator or proceed on stated assumptions.

## Ownership

This file owns how a request is read before work starts, at every depth from
a factual question to a design. `planning.md` owns planning, earlier and
concurrent work, recorded findings and decisions, approval, and handoff;
`authorization.md` owns what proceeds without confirmation; `reasoning.md`
owns how claims and causes are checked; `problem-follow-up.md` owns
recurrence and the follow-up of a handled problem. Agent runtime modules own
how a question is put to the operator. Projects own their domain checks for
what done means and where the similar problems they find are recorded.

## Understand The Request

Before starting work on a request, read it for what the operator is trying to
achieve, not only for its wording. A request is often short: it may name one
case of a wider need, or one instance of a problem that also occurs elsewhere.
Read it as deeply as it needs:

- A question with a factual answer, or a change whose target the request
  names and whose result fits in one sentence: do it, with step 1 in mind.
- A reported problem, a correction, an idea, a request that describes a need
  through examples, or another change: do steps 1, 3, 5, and 6. Before the
  first change, state the goal and any reading or assumption you took; report
  the done check and the similar problems with the result.
- An investigation, a comparison of options, a design, work across projects,
  hosts, or sessions, or a long task the operator will not watch: do every
  step, and give the brief below before the work.

1. State the goal behind the request in one sentence: what the operator wants
   to be true afterwards. For a request in several parts, state each part's
   goal and the goal they share.
2. When the answer depends on how something will be used, list the usage
   scenarios, including likely ones the operator did not mention, and mark the
   ones you assumed.
3. Separate the goal, the constraints the operator stated as required, the
   examples, and the requirements you derived. An example shows one case of
   the need; it is neither the whole need nor a constraint. When the operator
   says the description is only an example, treat all of it that way. A cause
   or a fix the operator names is a claim to check (`reasoning.md`), and a
   requested fix may not reach the goal behind it.
4. Carry each requirement you derived as an assumption (`reasoning.md`): show
   it, and do not use it to rule options out.
5. State what done means: the observable result, the quality it needs, and the
   check that shows it.
6. Find the similar problems the request stands for (Similar Problems).
7. Judge options scenario by scenario. Different tools for different scenarios
   is a valid answer, and so is "an existing feature already covers this".
8. A rule that governs your own actions is no reason to hide an option from the
   operator: show it with the conflict named. The rule still governs what you
   do.
9. For work that is hard to undo or that others depend on, assume it has
   failed and name the likeliest reasons; check or guard each one.

The brief has six parts: the goal; done; the scope, meaning the named case,
the similar problems, and what is excluded; the constraints, meaning what the
operator stated as required, recorded decisions, and authority; the options
per scenario; and the risks. Mark each entry stated, assumed, or open.

Red flags: "the operator mentioned it, so it is required"; "no option meets all
the requirements"; a pass/fail checklist built from examples; "it breaks a
principle of my design, so leave it out"; "the request is clear" for a
reported problem whose class you have not named; "they asked for this step"
when the step does not reach the goal.

## Ask Or Proceed

Settle from evidence what evidence can settle: the repository, its records,
and earlier and concurrent work (`planning.md` Before Planning). Of the open
points left, ask only about one whose answer would redirect the work: which
reading of the request is meant, which similar problems join the scope, a
tradeoff the operator owns, or an irreversible choice (`authorization.md`
Uncertainty). Decide the rest yourself, and say so when it matters. An answer
that leaves a point to you is a decision: take your recommendation and say so.

- When the operator is in the conversation, ask in one round, before the work
  the answers affect: the fewest questions that settle it, each with concrete
  options and your recommendation first, with its reason.
- When the operator said they will be away, or nobody can answer in the
  session, do not ask. Take the reading that is easiest to undo and keeps the
  most options open; state it and each assumption at the top of your reply,
  not only in a document you write, with what would change if it is wrong;
  finish the work that does not depend on it; and end the reply with each open
  point and your recommendation for it. A protected action still waits for the
  operator (`authorization.md`).

When two readings would lead to different answers and the request does not
settle which, state the reading you took at the top of your reply.

Red flags: asking what the repository or its records can answer; a second
round of questions the first could have held; "the operator is away, so I
will stop and wait"; "the operator is away, so the larger change is fine".

## Similar Problems

A reported problem, a correction, or a change to one case usually stands for a
class. Name the class, then look for its other members:

- same cause: other effects of the cause you established (`reasoning.md`);
- same pattern: the same construct, text, setting, or step elsewhere in the
  repository, its records, and the hosts or projects it names;
- same owner: the other entries governed by the rule, file, or component you
  change.

A member joins the scope when the same change fixes it, it lies within the
task's authority, meaning the same repository and no new protected action,
and it does not materially change the size or risk of the work. List every
other member with its location, evidence, and the owner you recommend; a
member in another repository or session is listed, not changed. Say where you
looked, also when nothing turned up. When the operator limits the request to
the named case, change only that case and still list what you found. Whether
the class happened before, and why, is follow-up (`problem-follow-up.md`).

Red flags: "the operator mentioned one case"; "the rest is out of scope"
before any search; "that is cleanup" for a member the same change fixes;
"while I am here" for a member that needs a different change.

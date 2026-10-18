# Changelog: reading a request before work starts

- **Date**: 2026-10-18
- **Plan**: [plan-request-intake-2026-10-18.md](plan-request-intake-2026-10-18.md)
- **Delivery state**: content-complete and verified on branch
  `feat/claude-native-governance`, uncommitted. When this record was written,
  none of these steps had run: commit, merge into `main`, push, `make sync` on
  each host (which installs the `interview` skill), and a release tag.

## Outcome

Every request is now read for what the operator means before work starts, at a
depth that fits it, and the agent knows when to ask and when to proceed.

- **`requests.md`** (new owner, W-R71; W-R63 moved from `planning.md`):
  - Understand The Request: three depths keyed to the kind of request, nine
    steps (goal, scenarios, goal versus examples and derived requirements,
    assumptions, what done means, similar problems, options per scenario,
    options a rule hides, a pre-mortem), and a six-part brief whose entries are
    marked stated, assumed, or open;
  - Ask Or Proceed: settle from evidence first; with the operator present, one
    round of questions with options and a recommendation; with the operator
    away, no questions: the reading and assumptions at the top of the reply,
    the independent work done, each open point with a recommendation;
  - Similar Problems: search by same cause, same pattern, and same owner, with
    a rule for which members join the scope.
- **Routing**: both adapters carry one resident sentence above their routing
  tables and a route row; the documentation gate keeps the two sentences
  identical and bound to `requests.md`. `planning.md` Before Planning starts
  from `requests.md`, and `reasoning.md` and `authorization.md` point to it.
- **Claude mechanics**: `claude-runtime.md` Asking The Operator
  (`AskUserQuestion`, auto mode's bias against asking, unanswered questions,
  subagents cannot ask, plan mode) and the `interview` skill, which the
  operator invokes to run the method as an interview.

Rule sizes in lines after the change: `requests.md` 121, `planning.md` 314
(344 before).

## Verification

- The request-reading phrase, route, and drift tests pass with the 171-test
  suite in a committed scratch copy, together with the documentation gate.
- Behavior, measured with the rule-evaluation harness of `feat/rule-evals`
  (used read-only; `claude-opus-5-5`, a three-vote `sonnet` judge, two trials
  per scenario, `main` against this branch):
  - four new intake scenarios moved from 3/8 to 8/8: a one-node failure read
    for its class (1/2 to 2/2), an idea given a done check (0/2 to 2/2), an
    ambiguous request while the operator is away (0/2 to 2/2), and an
    ambiguous irreversible request with the operator present (2/2 on both,
    at its ceiling);
  - the controls held: rules loaded, an in-scope edit done without asking, and
    a factual question answered directly (2/2 on both);
  - none of the harness's 21 existing scenarios got worse.
- After a rewording put the stated reading "at the top of your reply, not only
  in a document you write", the operator-away scenario scored 2/3 on the final
  rules; its one failure omitted the open points.

## Residual gaps

- Two or three trials per scenario detect only large effects, and the harness
  tests single replies: a real `AskUserQuestion` round and a multi-turn
  ask-then-proceed exchange are not exercised.
- The full interview is opt-in through `/interview`; in normal requests the
  rule asks only what would redirect the work.

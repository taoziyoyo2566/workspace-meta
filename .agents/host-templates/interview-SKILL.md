---
name: interview
description: Interview the operator about a request or idea before any work starts, then show the agreed brief. Run only when the operator invokes /interview.
argument-hint: "[request or idea]"
disable-model-invocation: true
---
<!-- workspace-meta managed skill: make sync replaces this file -->

# interview — settle a request with the operator before work starts

Method owner: `~/workspace/.agents/rules/requests.md` (Understand The Request,
Ask Or Proceed, Similar Problems). Read it now. This skill runs that method at
full depth as an interview and adds only Claude Code mechanics
(`~/workspace/.agents/rules/claude-runtime.md` Asking The Operator). Where this
file and the rule differ, the rule governs.

Request: $ARGUMENTS

If it is empty, take the operator's latest request in this conversation.

## Steps

1. Do the read-only work the rule calls for before asking: the repository, its
   records, and earlier and concurrent work. Draft the six-part brief (goal,
   done, scope, constraints, options per scenario, risks) with each entry
   marked stated, assumed, or open.
2. Ask the open points the rule says to ask, with `AskUserQuestion`: one round,
   the fewest questions that settle them, each with concrete options and the
   recommended option first. When the search found similar problems, one
   question is which of them join the scope.
3. After the answers, update the brief. Ask another round only when an answer
   opened a point that would redirect the work.
4. Finish when no open point would redirect the work: show the brief and the
   assumptions that remain, and record any decision where `planning.md` Record
   Decisions When Made says. Do not start the work until the operator says to.
5. If the operator will leave the work to run unattended, offer the done state
   as a `/goal` condition: one observable end state, the check that shows it,
   and what must not change.

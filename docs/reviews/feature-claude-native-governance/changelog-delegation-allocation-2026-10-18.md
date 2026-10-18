# Changelog: allocating model and effort when delegating

- **Date**: 2026-10-18
- **Plan**: [plan-delegation-allocation-2026-10-18.md](plan-delegation-allocation-2026-10-18.md)
- **Delivery state**: content-complete and verified on branch
  `feat/claude-native-governance`, uncommitted. When this record was written,
  none of these steps had run: commit, merge into `main`, push, and a release
  tag. No plugin was installed and no host setting was changed.

## Outcome

Delegated work is now planned: each agent gets the model and effort its
subtask needs, a bounded brief, and a check, and the allocation is reported.

- **`capabilities.md` Delegation** (W-R72): survey the subtasks first (output,
  dependencies, demand: mechanical, analytic, or judgment, and the cost of a
  wrong result); judgment work, including verification of a result the
  operator relies on, and the final synthesis keep at least the configured
  model and effort; analytic work keeps the configured model at a matched
  effort; checked mechanical work may be lighter; brief, verify, and report
  the allocation. Quality Before Speed states that this allocation applies the
  configured settings and does not lower them; Ownership and Recording name
  delegation planning and delegation mechanics.
- **`claude-runtime.md` Delegation**: where model and effort are set (Agent
  tool, workflow `agent()`, subagent frontmatter) and which value wins; the
  model tiers; effort levels as Claude Code's documentation describes them for
  the current models; a starting-point table relative to the configured
  settings; `Explore`, `Plan`, and `claude-code-guide` defaults; worktree
  isolation's base; `/tasks` to confirm what ran; the workflow concurrency
  limit; plugins proposed to the operator, never installed by an agent.
  Long Unattended Runs covers `/goal`.
- **Adapters**: both route delegating work to a subagent or a workflow; the
  Claude adapter instructs setting each agent's model and effort explicitly,
  which is the written instruction the Agent tool requires before it sets an
  effort.

Rule sizes in lines after the change: `capabilities.md` 157,
`claude-runtime.md` 197.

## Verification

- Delegation phrase and route tests pass with the 171-test suite in a
  committed scratch copy.
- Behavior with the rule-evaluation harness (read-only; `claude-opus-5-5`, a
  three-vote `sonnet` judge): the delegation-plan scenario scored 0/2 on
  `main`, where every agent kept the session default; 1/2 on two intermediate
  versions of this branch, whose failures set a verification agent below the
  configured effort; and 2/2 on the final rules, after verification of a
  relied-on result was named as judgment work.

## Residual gaps

- The harness has no Agent tool, so the allocation is judged from a written
  plan; real dispatch with per-agent parameters is not exercised.
- Hooks that log each subagent's actual model (a `PostToolUse` hook on the
  Agent tool, `SubagentStart`) are a recorded non-goal; `/tasks` is the check
  for now. Restart condition: an allocation is found not to have been applied.

# Plan: reading a request before work starts

- **Date**: 2026-10-18
- **Level**: Cross-project governance: one new portable rule owner moved and
  extended from `planning.md`, two references, both adapters, the Claude
  runtime module, one skill template, tests, and the register.
- **Status**: COMPLETE on 2026-10-18, verified on branch
  `feat/claude-native-governance` (`.worktrees/feat-claude-native-governance/`),
  uncommitted at closeout. Changelog:
  [changelog-request-intake-2026-10-18.md](changelog-request-intake-2026-10-18.md).
  The design choices under "Decisions taken in the operator's absence" were
  confirmed by the operator on 2026-10-18 (see the operator decision below).
- **Approval**: the operator's request of 2026-10-17, point 2:
  "2，对于我提出的问题或者想法，要找到一个标准的思维方式来标准化思考方式，避免出现思考不全或者考虑不周。对我所说的内容要先理解清楚之后再开始任务，类似一个chatview，先搞懂说话者的意图，毕竟他不可能描述的那么准确，或者考虑不周，再或者只是简单描述了一下问题，但实际上有很多类似其他问题也需要处理。"
  and, for the whole request: "我要去睡觉了，Claude还有一个goal的功能，我的要求就是把我说的这几点处理完，我不会在这里看着你，我希望明天早上能看到结果".
  This authorizes the goal and its working-tree implementation on this branch.
  The design choices below were made while the operator was away and are listed
  under "Decisions taken in the operator's absence" for review.
- **Operator decision (2026-10-18)**: "确认，按建议的设计决定执行，准备提交命令包".
  The decisions taken in the operator's absence are confirmed as recommended,
  and the publication command bundle is to be prepared. Staging, commit,
  merge, push, and `make sync` still wait for the bundle's own review.
- **Not approved, presented for review**: staging, commit, merge, and push;
  `make sync` (which installs the `interview` skill); any host configuration
  write; a release tag.
- **Related**: [investigation of Claude Code 2.1.302](investigation-claude-code-runtime-2026-10-17.md),
  [project bootstrap](plan-project-bootstrap-2026-10-18.md),
  [delegation allocation](plan-delegation-allocation-2026-10-18.md),
  [design map](plan-design-map-2026-10-18.md).

## Goal

The operator can give a short or imprecise request, a reported problem, or an
idea, and the agent works from what the operator meant: the goal, what done
means, and the similar problems the request stands for. It asks only when an
answer would redirect the work, and an unattended run never stops to wait for a
question.

Reading of the request (`requests.md`):

- "标准的思维方式" is read as one method that every request goes through, at a
  depth the request calls for, not a written reasoning report for each answer.
- "chatview" is read as an interview (访谈): settle the intent with the
  operator before the work. It becomes a step the operator can invoke, and
  the default protocol asks only what redirects the work.
- "很多类似其他问题也需要处理" is a requirement the operator stated: find the
  class a reported case belongs to and handle its members.

## Current state at approval

- `planning.md` Understand The Request (W-R63, 2026-10-15) states the goal,
  usage scenarios, examples versus requirements, derived requirements as
  assumptions, options per scenario, and showing options that conflict with a
  rule. It fires only "before an investigation, a comparison of options, or a
  design"; the adapters' planning row is wider ("a request that describes a
  need through examples"). Fixes, corrections, ideas, and reported problems
  have no reading step.
- No rule defines what done means at intake for conversational work,
  generalizes a reported case to its class, or says what to do when the
  operator is away. `authorization.md` Uncertainty asks only when an answer
  would redirect the work; `reasoning.md` treats an operator's claim as a claim
  and forbids a required reasoning transcript.
- Recurrences of a narrow reading: W-R52, W-R62, and W-R65 corrected the same
  class (a command handed to the user that breaks when run or copied) three
  times in six days; W-R63 records that "similar misreadings had happened
  before".
- Claude Code 2.1.302 (investigation §8.5, §9.3): `AskUserQuestion` exists in
  the main conversation only; auto mode tells the model not to stop for
  clarifying questions unless the user or a skill signals otherwise; a question
  waits indefinitely unless the host sets `askUserQuestionTimeout`; subagents
  cannot ask.
- The preference "intake before work" existed only as a host-local memory note
  in the second Claude config dir (`~/.claude-<account>`), written on
  2026-10-17.

## Intended change

### A. New owner `.agents/rules/requests.md` (`# Understanding Requests`)

- `## Ownership`: reading a request before work starts, at every depth.
- `## Understand The Request`: moved from `planning.md` and extended. Three
  depths keyed to the kind of request (a factual question or a one-sentence
  change; a reported problem, correction, idea, example-described need, or
  other change; an investigation, comparison, design, cross-project or
  cross-session work, or a long unwatched task). Steps: the goal; usage
  scenarios; separating goal, stated constraints, examples, and derived
  requirements, with a named cause or fix treated as a claim; derived
  requirements as assumptions; what done means and its check; similar
  problems; options per scenario; options that conflict with a rule; a
  pre-mortem for work that is hard to undo. The six-part brief: goal, done,
  scope, constraints, options, risks, each entry marked stated, assumed, or
  open. W-R63's phrases and red flags stay.
- `## Ask Or Proceed`: settle from evidence first; ask only what redirects the
  work, in one round, with the recommended option first; when the operator is
  away, do not ask, take the reading easiest to undo, state the assumptions at
  the top of the result, finish the independent work, and leave protected
  actions waiting.
- `## Similar Problems`: search by same cause, same pattern, and same owner; a
  member joins the scope when the same change fixes it within the task's
  authority without materially changing its size or risk; every other member
  is listed with location, evidence, and recommended owner; say where the
  search looked.

### B. References and routes

- `planning.md`: the section is removed, Ownership no longer claims request
  reading, and Before Planning starts with "Read the request first
  (`requests.md`)."
- `reasoning.md`: "(`planning.md` Understand The Request)" becomes
  "(`requests.md`)".
- Both adapters: a route row starting "starting work on a request" points to
  `requests.md`; the planning row loses "a request that describes a need
  through examples". Each adapter adds one resident sentence above its route
  table, so request reading needs no route match to start.

### C. Claude mechanics and the interview

- `claude-runtime.md` Asking The Operator: one `AskUserQuestion` call with one
  to four questions of two to four options, the recommended option first; auto
  mode; `askUserQuestionTimeout`; nobody answers in `-p`, background, or
  `/goal` runs; subagents cannot ask.
- `.agents/host-templates/interview-SKILL.md`, installed as
  `<claude dir>/skills/interview/SKILL.md` in every Claude config dir by the
  sync of the [project bootstrap Plan](plan-project-bootstrap-2026-10-18.md):
  `disable-model-invocation: true`, so only the operator starts it and its
  description costs no context. It names `requests.md` as the method owner,
  runs it at full depth as an interview, and adds only Claude mechanics: the
  question rounds, recording decisions, and the offer of a `/goal` condition.
  Where it and the rule differ, the rule governs.

### D. Provenance and tests

- `feedback-register.md`: W-R71 request intake (`requests.md`); the owner
  mapping moves W-R63's request reading from `planning.md` to `requests.md`.
- `tests/test_sync_codex_config.py`: the request-reading phrases ("an example
  shows one case of the need", "list the usage scenarios", "carry each
  requirement you derived as an assumption", "judge options scenario by
  scenario", "show it with the conflict named") are read from `requests.md`;
  the unique-ownership and adapter-parity module lists include it.

## Scope and non-goals

- No change to Claude Code's built-in prompts, no output style, no
  `UserPromptSubmit` hook.
- No plugin is installed; `feature-dev`'s clarifying-questions phase remains an
  option for the operator.
- `askUserQuestionTimeout` stays a host-local preference the operator sets.
- Rule-eval scenarios are not run here: the harness lives uncommitted on
  `feat/rule-evals`.

## Decisions taken in the operator's absence

Each choice names the alternative and why it was not taken. The operator may
reverse any of them at review.

1. **`requests.md` as a separate owner**, instead of extending `planning.md`.
   Request reading now fires at the start of every task, and `planning.md` is
   the largest owner (344 lines at `7659a94`); routing every task start to it
   would load all of it. A separate owner also gives the design map one domain
   for "the agent misread my request". The same text would work inside
   `planning.md` if the operator prefers fewer files.
2. **Depth keyed to the kind of request**, instead of to how ambiguous the
   model judges it, or an interview for every request. Models tell
   underspecified requests from clear ones poorly (Ambig-SWE, CLAMBER); an
   interview for every request would stall unattended runs and over-ask, which
   `authorization.md` Uncertainty already rules out.
3. **The interview is an operator-invoked skill**, instead of a default round
   before every task. The operator's "先搞懂说话者的意图" is met by the default
   protocol (goal, readings, and assumptions stated before the first change);
   `/interview` gives the full interview when the operator wants it. Making it
   model-invocable would let the agent start interviews on its own.
4. **A six-part brief as the standard way of thinking**, instead of adopting
   one named framework (5 Whys, Cynefin, 5W2H) or a mandatory reasoning report.
   Each named framework covers only part of the brief; the six parts were
   checked against 5W2H, Gause and Weinberg's questions, Socratic question
   types, Definition of Done, Kepner-Tregoe, yokoten, and the pre-mortem. A
   required written report is the "mandatory output ritual" the
   [reasoning-governance design](../refactor-reasoning-governance/plan-reasoning-governance-2026-09-07.md)
   rejected, and written reasoning can draw refusals; the brief holds
   conclusions only.
5. **Similar problems join the scope under an observable rule**, instead of
   fixing every member found (scope creep and writes in other repositories) or
   listing all of them (the operator said they "也需要处理"). Members in
   another repository or session are listed, not changed or handed over.
6. **When the operator is away, do not ask**, instead of asking and waiting,
   or relying on `askUserQuestionTimeout`. The timeout is a host-local choice;
   tonight's request said the operator would not watch.
7. **The skill is named `interview`**, not `intake`, which would collide with
   `rule-authoring.md` Feedback Intake.
8. **No `UserPromptSubmit` reminder hook.** It would fire on every turn,
   including turns Claude Code starts itself. Deferred under
   `problem-follow-up.md` Mechanism Or Rule. Owner: workspace-meta. Restart
   condition: a misreading or a missed similar problem recurs after
   `requests.md` lands.

## Acceptance criteria

- `requests.md` has the four sections above and W-R63's phrases; `planning.md`
  has no Understand The Request section and its Before Planning starts with the
  pointer; `reasoning.md` points to `requests.md`.
- Each adapter has exactly one route row for `requests.md`, and the planning
  row no longer carries the examples phrase; the governance tests pass.
- `interview-SKILL.md` has `disable-model-invocation: true`, names
  `requests.md` as the method owner, states no rule of its own, and has no
  visible date or `~` Markdown link (docs gate).
- Replay of this workstream's own request against `requests.md`: it is a
  full-depth request from an operator who is away, so the brief comes first,
  nothing is asked, and the readings and assumptions are stated at the top of
  each Plan and of the final report.
- Reported as a gap until run: behavior evaluation with the rule-eval harness
  (`feat/rule-evals`), with targets for an operator away overnight, an idea
  versus a recorded decision, and the goal behind one example, plus the
  existing controls for over-asking; and a real `/interview` run in a scratch
  project after `make sync`.

## Risks

- Over-asking slows simple work: the first depth is silent, evidence comes
  first, and there is one round at most.
- Scope creep from the sweep: the join rule is observable, other repositories
  are only listed, and the operator can limit the request to the named case.
- An advisory rule can be ignored: measure it with the rule evals.
- `planning.md` and the adapters are also edited by uncommitted work on
  `feat/rule-evals` (W-R66 to W-R70); the moved section must be merged with
  care.

## Links

- Builds on: W-R63 (`planning.md` Understand The Request, moved without
  rewording), `reasoning.md` (W-R43), `authorization.md` Uncertainty,
  `review.md` Problem Reports (say what was checked), `problem-follow-up.md`
  (recurrence and follow-up), `planning.md` Before Planning (W-R50).
- Respects: the [reasoning-governance design](../refactor-reasoning-governance/plan-reasoning-governance-2026-09-07.md),
  which rejected sibling reasoning modules and a mandatory reasoning report.
  `requests.md` owns reading the request, not reasoning about evidence.
- Supersedes: the location of Understand The Request in `planning.md`.
- Related: the cross-host dispatch Plan (`DRAFT`, uncommitted on
  `docs/cross-host-agent-dispatch`), whose fixed brief and report schema the
  six-part brief can feed; the rule-eval workstream (`feat/rule-evals`),
  which measures the change; the
  [delegation Plan](plan-delegation-allocation-2026-10-18.md), whose briefs use
  the same parts.
- Depends on: the [investigation](investigation-claude-code-runtime-2026-10-17.md)
  (§8.5, §9.3) and the sync change of the
  [project bootstrap Plan](plan-project-bootstrap-2026-10-18.md) to install the
  skill.

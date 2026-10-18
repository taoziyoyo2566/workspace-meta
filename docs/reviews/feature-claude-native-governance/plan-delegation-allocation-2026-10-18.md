# Plan: allocating model and effort when delegating

- **Date**: 2026-10-18
- **Level**: Cross-project governance: one portable rule owner, the Claude
  runtime module, both adapters' route rows, one Claude adapter instruction,
  tests, and the register.
- **Status**: COMPLETE on 2026-10-18, verified on branch
  `feat/claude-native-governance` (`.worktrees/feat-claude-native-governance/`),
  uncommitted at closeout. Changelog:
  [changelog-delegation-allocation-2026-10-18.md](changelog-delegation-allocation-2026-10-18.md).
  The design choices under "Decisions taken in the operator's absence" were
  confirmed by the operator on 2026-10-18 (see the operator decision below).
- **Approval**: the operator's request of 2026-10-17, point 3:
  "3，当开始一个任务，如何需要开启subagent方式来处理，就需要事先调查好，各个任务的复杂度以及难易度，根据实际情况针对各个agent分配恰当的模型以及effect，同时发挥Claude的功能或者配置恰当的plugin，再或者其他合适的手段，来提升任务处理的的管理。"
  and, for the whole request: "我要去睡觉了，Claude还有一个goal的功能，我的要求就是把我说的这几点处理完，我不会在这里看着你，我希望明天早上能看到结果".
  This authorizes the goal and its working-tree implementation on this branch.
  The design choices below were made while the operator was away and are listed
  under "Decisions taken in the operator's absence" for review.
- **Operator decision (2026-10-18)**: "确认，按建议的设计决定执行，准备提交命令包".
  The decisions taken in the operator's absence are confirmed as recommended,
  and the publication command bundle is to be prepared. Staging, commit,
  merge, push, and `make sync` still wait for the bundle's own review.
- **Not approved, presented for review**: staging, commit, merge, and push;
  `make sync`; installing or enabling any plugin; changing model, effort, or
  other settings in any config dir; a release tag.
- **Related**: [investigation of Claude Code 2.1.302](investigation-claude-code-runtime-2026-10-17.md),
  [project bootstrap](plan-project-bootstrap-2026-10-18.md),
  [request intake](plan-request-intake-2026-10-18.md),
  [design map](plan-design-map-2026-10-18.md).

## Goal

Before work is handed to subagents or a workflow, the main session surveys the
subtasks and gives each agent the model and reasoning effort its result needs,
uses the Claude features that improve the result, and reports the allocation,
without lowering quality to save time or usage.

Reading of the request (`requests.md`):

- "复杂度以及难易度" is read as what a subtask's result demands (a checked
  lookup, an analysis, or a judgment) and what a wrong result would cost, not
  its size alone.
- "effect" is read as effort, the reasoning-effort setting.
- "发挥Claude的功能或者配置恰当的plugin" names examples. The need is to use the
  runtime's orchestration features where they improve the result; the
  operator's mention of `/goal` in the same request is one of them.

## Current state at approval

- `capabilities.md` Selection: delegate only when instructions permit and the
  subtask is concrete. Quality Before Speed (W-R60, 2026-10-11): "Keep the
  configured model, reasoning effort, and orchestration settings", and do not
  lower quality to save time or usage. Recording: no mandatory model-choice
  note, because "model selection may be host/user-owned or invisible"
  (DQ-03 of the
  [content audit](../refactor-codex-rules-mece/content-audit-summary-2026-07-20.md)).
  `capabilities.md` says adapters own delegation mechanics, but the Claude
  adapter had none; only `codex-runtime.md` had a delegation line. The
  [rules-design review](../refactor-documentation-governance/review-rules-design-2026-09-05.zh-CN.md)
  flagged that asymmetry (P2-2), and its remediation left it open.
- Claude Code 2.1.302 (investigation §8, §9): the Agent tool sets `effort` only
  when "the user, or instructions such as CLAUDE.md or a skill, explicitly
  ask"; workflow scripts omit `model` by default. Without a written instruction
  every subagent inherits the session model and effort, which on this host is
  Opus 5.5 at `xhigh` from `modelSettings`. Subagents cannot ask the operator
  and start without the conversation or the main auto memory.
- The incident behind W-R60 (2026-10-11): a workflow of 14 agents ran with no
  model or effort set, at the session's maximum effort, for 1 hour 22 minutes;
  the session then proposed fewer agents, lower effort, and time limits, and
  the operator answered "我优先考虑你的结果质量，除非你给出的调整能提升结果质量，否则还是用默认的配置".
- The preference "delegation allocation" existed only as a host-local memory
  note in the second Claude config dir (`~/.claude-<account>`), written on
  2026-10-17.
- No plugin is installed or enabled in either Claude config dir.

## Intended change

### A. `capabilities.md` (portable)

- Ownership: the file also owns delegation planning, meaning how work is split
  across agents and what each is given; how a model or effort is set is a
  runtime mechanic.
- New `## Delegation`: survey the subtasks first, naming each one's output,
  dependencies, and demand: mechanical (a lookup, sweep, or transformation a
  check or later stage verifies), analytic (reading and connecting evidence,
  implementing a clear specification), or judgment (design, diagnosis under
  ambiguity, review, adversarial verification, verification of results the
  operator relies on, the final synthesis), and what
  a wrong result would cost. Keep in the main thread what needs the whole
  picture, the operator's words, or a question to the operator. Give each agent
  the model and effort its demand needs: judgment work and the synthesis keep
  at least the configured model and effort, and a stronger model when the
  operator allows its cost; analytic work keeps the configured model at a
  matched effort; mechanical work whose result is checked may use a lighter
  model or lower effort. Brief each agent with its goal, question, inputs and
  boundaries, output shape, and how its result will be checked. Use
  orchestration features that improve the result. For substantial delegation,
  report each agent's task, model, effort, and reason.
- Quality Before Speed: giving each agent the model and effort its demand needs
  under Delegation applies the configured settings and does not lower them; a
  subtask set below what its result needs is a quality cut.

### B. `claude-runtime.md` (Claude mechanics)

- `## Delegation` covers these points:
  - set model and effort explicitly on every delegated agent, from the
    allocation;
  - where they are set (the Agent tool, workflow `agent()` options, subagent
    frontmatter), and the precedence of call, definition, environment, and
    session;
  - the model tiers;
  - effort levels as the official Opus 5.5 guidance describes them
    (investigation §8.8): `medium`, Opus 5.5's own default, for clear-scope
    work; `high` for verification-heavy or edge-case work; `xhigh` for
    long-running agentic work; and `max`, which has diminishing returns. The
    operator's configured effort stays the floor for judgment and synthesis
    under `capabilities.md`;
  - a table of starting points per demand class, stated relative to the
    configured model: configured, `fable` only when the operator allows its
    cost, and `sonnet` or `haiku` only for mechanical work whose result is
    checked;
  - `Explore` and `Plan` start without `CLAUDE.md`;
  - a subagent worktree branches from the remote default branch unless
    `worktree.baseRef` is `"head"`;
  - `/tasks` shows the model and effort each agent actually ran with;
  - workflows need the operator's opt-in;
  - plugins are per config dir and the operator's decision. An agent checks a
    plugin's components and token cost and proposes the install with the
    `authorization.md` brief. It never installs one itself.
- `## Long Unattended Runs`: offer the done state as a `/goal` condition (one
  observable end state, its check, what must not change); `/goal` does not
  change permissions, so protected actions still wait; keep progress visible
  and open the final report with the result, open points, and waiting actions.

### C. Adapters, provenance, and tests

- `CLAUDE.md`: a Claude-Specific Runtime section that says to set each agent's
  model and effort explicitly from the `capabilities.md` allocation. This is
  the written instruction the Agent tool waits for.
- Both adapters: a route row for "delegating work to subagents or a workflow"
  points to `capabilities.md`, together with `claude-runtime.md` in `CLAUDE.md`
  and with `codex-runtime.md` in the Codex adapter.
- `feedback-register.md`: W-R72 delegation allocation (`capabilities.md` and
  `claude-runtime.md`), refining W-R60.
- `tests/test_sync_codex_config.py`: phrase tests for `capabilities.md`
  Delegation, the `claude-runtime.md` sections, and the `CLAUDE.md` instruction
  "set each agent's model and effort".

## Scope and non-goals

- No change to any config dir's model, effort, `modelSettings`, or
  environment variables such as `CLAUDE_CODE_SUBAGENT_MODEL`.
- No role subagents with fixed frontmatter are installed, and no plugin is
  installed or enabled; plugins are proposed to the operator with the
  `authorization.md` brief.
- Hooks for delegation observability are a non-goal of this change. Examples
  are a `PostToolUse` hook on `Agent` that logs the resolved model, and a
  `SubagentStart` hook that injects rules. `/tasks` already shows each
  agent's actual model and effort. Owner: workspace-meta. Restart condition:
  an allocation is found not to have been applied.
- Codex mechanics stay in `codex-runtime.md` as they are; the portable
  Delegation section applies to Codex unchanged.
- No time limits, agent caps, or fewer verification passes to save time
  (W-R60 stands).

## Decisions taken in the operator's absence

Each choice names the alternative and why it was not taken. The operator may
reverse any of them at review.

1. **Per-subtask allocation is reconciled with W-R60, not an exception to
   it.** The configured model and effort are the floor for judgment and
   synthesis, and verification of results the operator relies on counts as
   judgment work; a lower tier is allowed only for mechanical work whose
   result a check catches, where more reasoning does not improve it; anything set below
   what its result needs is a quality cut. Alternatives: amend W-R60 to allow
   lowering quality for cost, which reverses the operator's decision of
   2026-10-11; or keep every agent on the session default, which leaves point
   3 undone and, on this host, runs mechanical sweeps at `xhigh`. Where a check
   catches errors, the official measurement of `low` with failures re-run at
   `high` (about 97% at about $0.17 a task, against 95.3% at $0.29 for all
   `high`, investigation §8.6) shows that a matched allocation need not cost
   quality.
2. **Demand classes in the portable rule, model names in the runtime module**,
   instead of model names in `capabilities.md` or the task-size classes
   (Small, Medium, Large, Investigation) of the unmerged `origin/agent-workflow`
   plan (2026-08-18). Model names, prices, and defaults change per runtime and
   release; size does not say what a result demands. That plan's task-size
   classes are superseded by this allocation; its "efficiency must serve
   correctness" agrees with W-R60.
3. **A stronger model only when the operator allows its cost**, instead of
   Fable for every judgment. Fable 5.1 costs about two and a half times Opus
   5.5 per token and may bill usage credits on this seat (not verified); the
   speed and cost trade belongs to the operator (W-R60).
4. **A written instruction in the adapter and the runtime module**, instead of
   role subagents whose frontmatter fixes model and effort, installed into each
   config dir or shipped as a plugin. Fixed frontmatter cannot follow each
   subtask's demand, and role agents add a managed surface per config dir that
   the reverse whitelist does not yet allow. Deferred. Owner: workspace-meta.
   Restart condition: allocations are omitted or wrong in practice after this
   lands.
5. **The allocation is reported for substantial delegation**, refining DQ-03.
   DQ-03 dropped the model-choice note because the executing agent may not see
   or own the model; a delegating agent sets each agent's model and effort
   itself, so the report is cheap and shows the operator what ran.
6. **No plugin is installed or enabled by workspace-meta or by an agent**,
   instead of managing `enabledPlugins` in each config dir. Plugin choice is
   host-local (W-R28), each plugin adds context and token cost, and the
   operator decides it. An agent proposes a plugin with the `authorization.md`
   brief, naming each config dir it would go into, and never installs one
   itself. Candidates for the operator, judged from their manifests
   (investigation §10.2): `feature-dev`, `pr-review-toolkit`, `code-review`,
   `claude-md-management`, `session-report`, and `claude-security` as the
   example of per-role model and effort.
7. **`/goal` is offered, not set, by the agent**, instead of workspace-meta or
   the agent setting it. It is a user command scoped to the session; its
   evaluator reads only the conversation, so the condition must be one the
   agent's output can show (investigation §9.1). The `ralph-loop` plugin covers
   the same need and is not needed.
8. **The Workflow tool stays an explicit opt-in**, as Claude Code requires; no
   rule makes workflows the default.
9. **Effort guidance follows the official Opus 5.5 guidance, and the floor is
   the operator's policy**, instead of the Opus 4.7 advice to start at `xhigh`
   for coding and agentic work. The Opus 5.5 pages put clear-scope work at
   `medium` and say to sweep effort rather than carry settings over
   (investigation §8.8). The floor for judgment and synthesis comes from W-R60
   and is labeled as the operator's policy, not as a Claude Code fact. The
   allocation table names models relative to the configured one, so a session
   configured above Opus or at `max` does not send verification below its own
   floor.

## Acceptance criteria

- `capabilities.md` has `## Delegation` with the survey, the three demand
  classes, the per-agent allocation, the brief, the verification of delegated
  findings, and the allocation report; Quality Before Speed has the sentence
  that allocation under Delegation does not lower the configured settings.
- `claude-runtime.md` has `## Delegation` and `## Long Unattended Runs` as in
  B: its effort wording matches investigation §8.8, its allocation table names
  models relative to the configured one, and its plugin text proposes and
  never installs. `CLAUDE.md` contains "set each agent's model and effort";
  both adapters route delegation as in C; the governance tests pass.
- Replay of the 2026-10-11 incident against the new text: the session surveys
  the seven investigations and seven verifiers before starting, sets each
  agent's model and effort (verifiers as judgment work at no less than the
  configured level), reports the allocation, and Quality Before Speed still
  forbids cutting agents or verification to save time.
- Reported as a gap until checked on a host: in a fresh Claude session,
  `/tasks` shows each delegated agent's model and effort as allocated.

## Risks

- A subtask misclassified as mechanical gets less reasoning than it needs: the
  rule requires a check that catches its errors and keeps judgment and
  synthesis at the configured level or above.
- The model tiers and prices in `claude-runtime.md` are volatile; the runtime
  module names its evidence and recheck rule.
- `capabilities.md` and the adapters are also edited by uncommitted work on
  `fix/user-run-commands` (W-R62) and `fix/short-user-commands` (W-R65); merge
  order must be planned.

## Links

- Builds on: `capabilities.md` Selection and Quality Before Speed (W-R60) and
  the [feedback-intake Plan](../refactor-feedback-intake/plan-feedback-intake-2026-10-11.md)
  that added it; `review.md` (a delegated finding counts once its evidence is
  checked); `codex-runtime.md` as the pattern for a runtime module.
- Refines: W-R60 (W-R72) and DQ-03.
- Closes: P2-2 of the
  [rules-design review](../refactor-documentation-governance/review-rules-design-2026-09-05.zh-CN.md)
  (no Claude runtime module).
- Supersedes: the task-size classes of the unmerged `origin/agent-workflow`
  plan (`docs/plan/agent-execution-efficient-coding-workflow-plan-2026-08-18.md`
  on that branch), which was never adopted or rejected on record.
- Related: the [request intake Plan](plan-request-intake-2026-10-18.md) (the
  brief's parts; subagents cannot ask, so open points are settled first); the
  cross-host dispatch Plan (`DRAFT`, uncommitted on
  `docs/cross-host-agent-dispatch`), whose delegated-agent reports are claims
  to verify.
- Depends on: the [investigation](investigation-claude-code-runtime-2026-10-17.md)
  (§8, §9, §10).

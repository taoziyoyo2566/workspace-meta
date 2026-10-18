# Capability Selection

Agent-neutral workspace rule for proportional capability and tool selection,
with result quality before speed.

## Ownership

This file owns generic selection triggers, the rule that quality comes before
speed, recording behavior, and how a command is handed to the user to run.
Agent adapters own concrete tool discovery, delegation mechanics, connected
applications, and runtime mechanics. Projects own their toolchain, commands,
environments, and preferred adapters.

This file also owns delegation planning: how work is split across agents and
what each agent is given. How a model or reasoning effort is set, and which
orchestration features exist, are delegation mechanics.

## Observable Triggers

Do a lightweight capability check when:

- a substantial resumed task depends on a capability not visible in the
  current tool set;
- large, repeated, cross-surface, or high-risk work has a concrete opportunity
  for structured lookup, independent parallel reads, specialized automation,
  connected applications, or generated assets;
- a plan, blocker, skipped check, or delegation depends on current runtime
  capability;
- repeated failure suggests the execution method is wrong;
- work is slow or costly, or a change of method is considered to save time or
  usage; Quality Before Speed applies.

Do not spend more effort discovering capabilities than the task warrants.
Simple explanation/read-only questions, ordinary edits using visible tools, and
quick status reports with no load-bearing capability claim do not trigger a
capability audit.

## Selection

- Inspect visible capabilities first.
- Use deferred discovery only for a task-shaped need.
- Parallelize independent read-only evidence when useful.
- Delegate only when active instructions permit it and the subtask is concrete
  and independently useful.
- Use current official documentation for changed product/API behavior.
- Prefer project scripts, test targets, environments, and adapters over manual
  reinvention.

## Delegation

Before handing work to subagents or a workflow, survey the subtasks first. For
each one, name its output, what it depends on, and its demand:

- mechanical: a lookup, inventory, sweep, or transformation whose result a
  check or a later stage verifies;
- analytic: reading and connecting evidence, or implementing a clear
  specification;
- judgment: design, diagnosis under ambiguity, review, verification of a
  result the operator will rely on, and the synthesis the operator receives.

Also name what a wrong result would cost and whether anything downstream would
catch it. Keep in the main thread what needs the whole picture, the operator's
words, or a question to the operator: subagents cannot ask, so settle the open
points first (`requests.md` Ask Or Proceed).

Then give each agent the model and reasoning effort its demand needs:

- judgment work and the final synthesis keep at least the configured model and
  effort, and get a stronger model when the operator allows its cost;
- analytic work keeps the configured model, at an effort that matches its
  depth;
- mechanical work whose result is checked may use a lighter model or a lower
  effort, because more reasoning does not improve it.

Prefer the configured model at a matched effort to a mix of models. Use a
lighter model for high-volume mechanical work or work larger than one context,
and a stronger one for a subtask the configured model has failed at.

Brief every agent with the goal it serves, the question it decides, its inputs
and boundaries (read-only, or the files it alone may change; no protected
action), its output shape, and how its result will be checked. A finding the
result depends on counts once its evidence is checked; give judgments that are
hard to check to independent verifiers. Use the runtime's orchestration
features when they improve the result, such as isolated worktrees for parallel
writers, structured output, voting verifiers, and background runs with visible
progress.

For substantial delegation, report the allocation with the result: each
agent's task, model, effort, and the reason.

Red flags: every agent left on the session default without a survey; a lighter
model for work whose errors nothing downstream catches; "it is only a
subagent" for the synthesis or the final verification; a subagent left to
guess what the operator meant.

## Quality Before Speed

The result's quality comes first. Keep the configured model, reasoning effort,
and orchestration settings; giving each agent the model and effort its demand
needs under Delegation applies them, it does not lower them. A subtask set
below what its result needs is a quality cut. Do not propose or apply a change
that lowers quality to save time or usage, such as lower effort, fewer agents
or verification passes, skipping evidence the decision needs, or a time limit
that cuts work short. Propose a change of method only when it also improves
the result, and say how; narrowing each delegated task to the points that
decide the question, for example, removes noise as well as time.

When the operator asks how to go faster, state what each option costs in
quality; the operator decides. Once the operator has raised speed or cost,
the same holds for any cut in depth, agents, or verification: state its
quality cost and let the operator decide before making it. Proportional depth
(`reasoning.md`) is set by what the decision needs, not by time.

## Commands The User Runs

When the user is to run a command in their own terminal and it is more than
one simple line, write it to a script file and hand over only the one-line
command that runs the file. Text copied from a chat or terminal view can gain
trailing spaces or broken lines without showing it: a heredoc terminator stops
matching, a continuation line runs on its own, or a quoted argument splits.

- More than one simple line means several lines, a heredoc, a line
  continuation, a multi-line loop or pipeline, or an interpreter `-c` argument
  with nested quotes. A single simple command is given as it is.
- A one-off script goes under `/tmp`, in a directory only the user can read,
  not into a repository; its removal follows `temporary-files.md`. A command
  that will be reused belongs in the project as a tool, under the project's
  rules.
- Before handing it over, run its file checks (`file-checks.md`): it parses,
  has no trailing whitespace, is readable only by the user, and prints no
  secret value.
- For a protected action, the request brief in `authorization.md` still
  applies: its exact operation is the one-line command, with the script's
  path so the user can read the script first.

## Recording

Keep routine discovery attempts, failed capability attempts, and execution
method changes in transient task context. Record the final capability choice in
an existing outcome or handoff owner only when an observable event affects
reproducibility, for example when:

- deferred discovery or a connected application was used;
- delegation or specialized generation/automation was used;
- execution changed after a failed or abandoned capability attempt.

If a capability finding materially invalidates an `APPROVED` Plan, follow
`planning.md` material-deviation handling. The finding does not itself
authorize Plan amendment.

Do not require a `Capability fit` section, a list of unused capabilities, or a
model-choice note for every plan. The session's own model may be host/user-owned
or invisible; a per-agent allocation is reported under Delegation.

Recurring portable improvements belong in this workspace layer; concrete
agent mechanics belong in the agent adapter; project/toolchain improvements
belong in the project.

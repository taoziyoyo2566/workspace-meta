# Claude Runtime

Claude Code mechanics for the portable rules. This module never redefines
portable behavior; where it and a shared owner differ, the shared owner
governs.

## Ownership

This file owns Claude Code mechanics: where Claude reads instructions,
settings, skills, and memory; its project entry files; how it asks the
operator; how model, effort, and orchestration features are set; and how a
long unattended run keeps going. Portable behavior stays with the shared
owners, chiefly `requests.md`, `capabilities.md`, `documentation.md`, and
`planning.md`. The procedure for writing auto memory stays in the Claude
adapter (`CLAUDE.md` Claude Auto-Memory). Host values, such as the configured
model and effort, permissions, trust, and installed plugins, stay in each
Claude config dir.

The facts below were verified against Claude Code 2.1.302; the evidence and
recheck conditions are in the
[investigation record](../../docs/reviews/feature-claude-native-governance/investigation-claude-code-runtime-2026-10-17.md).
After an upgrade that changes a behavior described here, recheck it before
relying on it and update this file.

## Configuration Layers

- `CLAUDE.md`, `.claude/CLAUDE.md`, `CLAUDE.local.md`, and unconditional
  `.claude/rules/*.md` load from the working directory and every directory
  above it, so `~/workspace/CLAUDE.md` reaches every project. A
  subdirectory's files load once Claude works in that subdirectory.
- Skills, subagent definitions, and commands are found only up to the
  project's Git root, so a workspace-level `.claude/skills` would not reach the
  projects. A project's `.claude/settings.json` is read only from the directory
  Claude started in.
- The user layer is the config dir: `~/.claude`, or the directory named by
  `CLAUDE_CONFIG_DIR`, as when a second account has its own directory. Each config dir holds its own user `CLAUDE.md`, `rules/`,
  `skills/`, `agents/`, `settings.json`, auto memory, and credentials, and its
  global `.claude.json` (trust, MCP servers) lies inside a relocated config dir
  but at `~/.claude.json` for the default `~/.claude`. Workspace-managed
  surfaces are installed into every config dir the operator uses
  (`README-agents.md`); everything else in a config dir belongs to that
  account.
- An organization on a Team or Enterprise plan can push managed settings and a
  managed `CLAUDE.md`. They outrank every other layer and are never edited from
  the workspace.
- Claude reads `AGENTS.md` by itself only when no `CLAUDE.md`,
  `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working directory or
  above it. `~/workspace/CLAUDE.md` is above every project, so a project's
  `AGENTS.md` loads only through a project entry file that imports it. The
  **Project instructions** value `claude-md-and-agents-md` would load every
  ancestor `AGENTS.md`, including the workspace-meta repository's own, into
  every project session, so it is not used here.
- `/doctor prompt-audit` reports stale or conflicting guidance across the
  instruction files, rules, skills, and subagents Claude loads; use it when
  auditing them.

## Project Entry Files

Under `documentation.md` Project Bootstrap, Claude's entry files are:

- `CLAUDE.md` at the project root, holding the line `@AGENTS.md`; anything more
  in it is Claude-only mechanics for the project. An import resolves relative
  to the file that contains it, so the line is `@../AGENTS.md` in
  `.claude/CLAUDE.md`.
- For a subdirectory's own `AGENTS.md`, a sibling `CLAUDE.md` holding
  `@AGENTS.md`, which Claude loads once it works in that subdirectory.
- In a clone of a repository the operator does not own, only `CLAUDE.local.md`,
  listed in the clone's exclude file
  (`$(git rev-parse --git-common-dir)/info/exclude`). It holds the `@AGENTS.md`
  import when the clone has an `AGENTS.md`, and the survey notes otherwise.

The `project-bootstrap` skill runs the survey and writes these files. `/init`
also analyzes a codebase, but it makes `CLAUDE.md` the owner: its classic flow
ignores `AGENTS.md`, and its newer flow (`CLAUDE_CODE_NEW_INIT=1`, or a
server-side switch) copies the relevant parts of `AGENTS.md` into `CLAUDE.md`.
When the operator runs `/init`, move what it finds into `AGENTS.md` and keep
`CLAUDE.md` as the adapter. `/import` copies `AGENTS.md` into `CLAUDE.md`, which
makes a second authority; do not use it here.

At session start, the workspace-meta status check reports a Git project under
`~/workspace/projects` that has no Claude entry file, or whose entry file does
not import its `AGENTS.md`. Bootstrap it before substantive work, and before
delegating work in it; `documentation.md` Project Bootstrap says which session
may.

Claude Code itself creates auto memory, session transcripts,
`.claude/worktrees/` for worktree sessions and isolated subagents, and
`.claude/settings.local.json` when an approval is kept for the project.
`/team-onboarding` writes `ONBOARDING.md` for people, not for agents. Project
settings, rules, skills, subagents, `.mcp.json`, and output styles are created
deliberately when a project needs them, never by the bootstrap; the
investigation record lists each artifact and what creates it.

## Memory

- Auto memory is on by default and lives in
  `<config dir>/projects/<project>/memory/`, one directory per Git repository,
  shared by its worktrees. `MEMORY.md` loads at session start up to 200 lines or
  25 KB; topic files load when Claude reads them.
- Each config dir keeps its own memory, so a session under one account does not
  see what another account recorded.
- Subagents do not receive the main session's memory or conversation; a fork
  does.
- Claude accepts any `.git` entry as a repository root, even an empty
  directory. An empty `.git` directory in a parent of several projects makes
  the non-Git directories under it share one memory directory and one trust
  entry (inferred from the code; recheck). Report one when you see it.

## Asking The Operator

Whether to ask is decided by `requests.md` Ask Or Proceed. In Claude Code:

- Ask with `AskUserQuestion`: one call holds one to four questions, the most
  important first, each with two to four options. Put the recommended option
  first and end its label with "(Recommended)"; the dialog adds "Other" itself.
- Auto mode tells Claude to keep working rather than stop for clarifying
  questions unless the user or a skill signals otherwise. Ask Or Proceed and an
  `/interview` invocation are that signal.
- An unanswered question blocks the session unless the host sets
  `askUserQuestionTimeout`. A `-p` run and a background session have nobody to
  answer, and a `/goal` run usually has nobody either.
- Subagents cannot ask. Settle the open points before delegating and brief each
  agent as `capabilities.md` Delegation says.
- In plan mode, ask before finalizing the plan; `ExitPlanMode` presents the plan
  for approval.
- The operator can run `/interview` to have a request read at full depth as an
  interview before any work starts.

## Delegation

`capabilities.md` Delegation decides each agent's model and effort; this
section is how to set them. Set both explicitly on every delegated agent, from
that allocation; this rule is the instruction the Agent tool waits for before
it sets an effort.

- Where to set them: the Agent tool's `model` (`haiku`, `sonnet`, `opus`,
  `fable`) and `effort` parameters; a workflow script's `agent()` options
  `model` and `effort`; a recurring subagent definition's `model` and `effort`
  frontmatter.
- What wins: for the model, the call's value, then the definition's, then
  `CLAUDE_CODE_SUBAGENT_MODEL`, then the session model; for effort,
  `CLAUDE_CODE_EFFORT_LEVEL`, then the call's value, then the definition's,
  then the session level, all capped by `maxEffortLevel`. A fork runs on the
  session's own model and effort.
- Models, strongest first: `fable` for the hardest reasoning and long-horizon
  work, at about two and a half times the per-token price of `opus` and with
  long turns; `opus`; `sonnet` for routine coding and reading-heavy workers;
  `haiku` for high-volume mechanical sweeps.
- Effort levels, as Claude Code's documentation describes them for the current
  models: `low` for quick exchanges and small changes reviewed one by one;
  `medium`, the models' own default, for clear-scope day-to-day work; `high`
  for work where verification matters or edge cases are likely; `xhigh` for
  deeper reasoning at a higher token spend; `max` for hard problems worked
  through without the operator, with diminishing returns and a tendency to
  overthink. The configured level stays the floor for judgment work and the
  final synthesis (`capabilities.md`).
- Starting points, relative to the configured model and effort:

| Demand | How | Model | Effort |
|---|---|---|---|
| one lookup whose file is known | main thread | session | session |
| mechanical: broad locate-only search, or edits from a precise spec that tests check | `Explore`, a subagent, or a workflow stage | `sonnet` or `haiku` | `low` to `medium` |
| analytic: clear-scope implementation or analysis | subagent | configured | matched to its depth: `medium` for clear scope, `high` where verification matters |
| judgment: review, verification of results the operator relies on, ambiguous design, the final synthesis | independent verifiers that vote, or the main thread | configured, or `fable` when the operator allows its cost | configured or higher |

- `Explore` and `Plan` start without `CLAUDE.md`; brief them with the rules
  that matter. `claude-code-guide` answers questions about Claude Code and
  defaults to `haiku`; give it the configured model when its answer is
  load-bearing.
- An isolated subagent worktree branches from the remote's default branch, not
  from the current HEAD, unless the setting `worktree.baseRef` is `"head"`. For
  parallel writers on another branch, use no isolation, or propose that setting
  to the operator.
- `/tasks` shows the model and effort each subagent actually ran with; check it
  before reporting the allocation for substantial delegation.
- `max` on broad, open-ended research can run for hours. Give such an agent one
  bounded question.
- The `Workflow` tool runs only with the operator's opt-in, such as ultracode.
  It runs up to 16 agents at once, about the CPU count minus two and never fewer
  than two, unless `CLAUDE_CODE_WORKFLOW_MAX_CONCURRENT_AGENTS` says otherwise;
  queued agents add wall-clock time.
- Plugins are installed per config dir, and which ones is the operator's
  decision. To suggest one, check its components and token cost with
  `claude plugin details`, then propose the install with the
  `authorization.md` brief, naming each config dir it would go into.

## Long Unattended Runs

- When the operator will leave a task running, offer its done state as a
  `/goal` condition: one observable end state, the check that shows it, and
  what must not change; a turn or time bound may be added. `/goal` keeps Claude
  working until a small model judges the condition met from the conversation.
  The operator sets it.
- `/goal` does not change permissions. A protected action still waits for the
  operator; the run prepares it and reports it instead.
- Keep progress visible while it runs, and open the final report with the
  result, the open points, and the actions waiting for the operator.

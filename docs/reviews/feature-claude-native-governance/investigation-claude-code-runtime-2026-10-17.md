# Investigation: Claude Code runtime facts for project bootstrap, request intake, and delegation

- **Date**: 2026-10-17, this host (CEST); the project inventory finished
  after midnight on 2026-10-18. Recorded 2026-10-18.
- **Question**: which Claude Code mechanisms decide what reaches a session in a
  project under `~/workspace/projects/`, what Claude Code creates per project
  on its own, how subagent model and effort are chosen, and what this host's
  Claude configuration directories and projects look like today. The answers
  constrain the four Plans of this workstream.
- **Scope**: Claude Code **2.1.302** (changelog entry dated 2026-10-16),
  binary `~/.local/npm/lib/node_modules/@anthropic-ai/claude-code/bin/claude.exe`,
  on this Linux host only; its two Claude configuration directories,
  `~/.claude` and a second config dir written here as `~/.claude-<account>`;
  workspace-meta `main` at `7659a94`. Codex is out of scope
  except where a fact names it. Read-only: no Claude session was started for
  the purpose, no credential file was read, and JSON configuration was read
  for key names and non-secret values only.
- **Plans relying on it**:
  [project bootstrap](plan-project-bootstrap-2026-10-18.md),
  [request intake](plan-request-intake-2026-10-18.md),
  [delegation allocation](plan-delegation-allocation-2026-10-18.md),
  [design map](plan-design-map-2026-10-18.md).

Evidence labels:

- **[DOC]** an official page on `code.claude.com` or `platform.claude.com`,
  fetched 2026-10-17 (URLs in Sources);
- **[BIN]** a string in the installed 2.1.302 binary; the byte offset lets it
  be re-read with `dd` and holds only for this build;
- **[HOST]** command output or file content on this host, 2026-10-17/18;
- **[INF]** inferred from the cited evidence, not observed directly.

Recheck rule for every Claude Code fact below: it holds for 2.1.302. Re-verify
the facts a change relies on after `claude update`, and at once when the
changelog names the feature. Each section adds its own trigger.

## 1. Instruction loading

1. Claude Code has four native instruction scopes: Managed, User, Project, and
   Local, the `memory_type` values of the InstructionsLoaded hook. "Workspace"
   is not one of them. [DOC hooks#instructionsloaded] [BIN loader @243898485]
2. `CLAUDE.md`, `.claude/CLAUDE.md`, unconditional `.claude/rules/*.md`, and
   `CLAUDE.local.md` load from every directory between `/` and the working
   directory, with no Git-root boundary. `~/workspace/CLAUDE.md` therefore
   loads in every project session as a Project file. Observed in a session in
   `projects/claude-md`: the workspace `CLAUDE.md`, the project `CLAUDE.md`,
   and `.claude/rules/layering.md` were all injected. [DOC memory] [BIN] [HOST]
3. `@path` imports resolve relative to the importing file; `~/` and absolute
   paths work; imports inside code spans and fences are skipped; depth is the
   root file plus four hops. A project-level import that resolves outside the
   working directory needs a one-time approval per project, stored in
   `.claude.json` as `hasClaudeMdExternalIncludesApproved`. [DOC memory] [BIN @243891586]
4. `CLAUDE.local.md` is supported and not deprecated. It counts as a
   `CLAUDE.md` for the AGENTS.md fallback, and a Git-ignored copy exists only
   in the worktree where it was created. [DOC memory, claude-directory] [BIN]
5. Not instruction files, and discovered differently [DOC permissions, skills,
   sub-agents] [BIN @243446585]:
   - `.claude/settings.json` is read only from the primary working directory,
     with no parent fallback;
   - `.claude/settings.local.json` is read at the Git root (2.1.211 and later);
   - `.claude/skills`, `.claude/agents`, `.claude/commands`, and
     `.claude/workflows` are discovered from the working directory up to the
     Git root.
   Each project under `~/workspace/projects/` is its own Git root, so a
   `~/workspace/.claude/` would not reach project sessions. Workspace-wide
   skills, agents, hooks, and settings reach a project only through the user
   layer, a plugin, or a file in the project. [INF]

Recheck when: the changelog changes instruction loading, imports, or
discovery; or `/context` in a project shows a different set of files.

## 2. AGENTS.md

1. AGENTS.md is read by a built-in plugin, `cc-plugin-agents-md`, on by
   default since 2.1.277. Its option
   `pluginConfigs."cc-plugin-agents-md@builtin".options.instructionFiles`
   defaults to `claude-md-or-agents-md`: AGENTS.md is read only when no
   `CLAUDE.md`, `.claude/CLAUDE.md`, or `CLAUDE.local.md` exists in the working
   directory or any directory above it. `claude-md-and-agents-md` reads both.
   The option is honored from user settings, a `--settings` file, or managed
   settings, and ignored in project and local settings. [DOC memory#agents-md]
   [BIN @271344549]
2. Because `~/workspace/CLAUDE.md` sits above every project, a project's
   `AGENTS.md` is never read natively under the default mode. The workspace
   adapter's line "Claude loads `CLAUDE.md`, not `AGENTS.md`" (at `7659a94`) is
   effectively true here, for this reason rather than the one it implies. [INF
   from 2.1]
3. A `CLAUDE.md` that imports `@AGENTS.md` loads it under every mode without a
   double read. InstructionsLoaded fires for such an import (`load_reason`
   `include`), and not for an AGENTS.md the plugin reads directly. [DOC
   memory#remove-an-earlier-agents-md-workaround, hooks]
4. `claude-md-and-agents-md` reads `AGENTS.md` where `CLAUDE.md` files load,
   which includes ancestor directories, so in this workspace it would add
   `~/workspace/AGENTS.md`, workspace-meta's own repository guidance, to every
   project session. That file treats nested projects as out of scope
   (`AGENTS.md` Scope Discipline). [DOC memory "When Claude Code reads
   AGENTS.md": "every `AGENTS.md` and `.claude/AGENTS.md` in your working
   directory and the directories above it", with the Project instructions row
   "each directory's `CLAUDE.md` files first and its `AGENTS.md` after them";
   fetched 2026-10-18; not observed in a session]
5. The setting is a per-configuration-directory user setting. Before 2.1.285
   the plugin ID was `agents-md@builtin`; later versions read either ID. [DOC
   settings-reference]
6. A subdirectory's `CLAUDE.md` loads on demand: once Claude reads, writes,
   or edits a file in that directory, or runs a single-file `cat`, `head`,
   `tail`, `sed -n`, or `grep` on one (2.1.293). A sibling `CLAUDE.md` that
   holds `@AGENTS.md` therefore brings that subdirectory's own `AGENTS.md`
   with it. [DOC memory] [DOC changelog 2.1.288, 2.1.293] Whether the plugin
   reads a subdirectory `AGENTS.md` by itself while an ancestor `CLAUDE.md`
   exists is not verified (13). Until it is, the class is: a subdirectory
   `AGENTS.md` does not reach Claude unless a sibling `CLAUDE.md` imports it.
   [INF from 2.1 and 2.2]

Recheck when: the changelog mentions AGENTS.md or `instructionFiles`, or
`/context` in a project that has only `AGENTS.md` shows it loaded, or a
session working in a subdirectory that has only an `AGENTS.md` shows that
file loaded.

## 3. Configuration directory

1. The user configuration home is `CLAUDE_CONFIG_DIR`, else `~/.claude`. Under
   it the binary resolves `CLAUDE.md`, `rules`, `skills`, `commands`, `agents`,
   `workflows`, `settings.json`, `keybindings.json`, `plugins`, `projects`
   (transcripts and auto memory), `plans`, `agent-memory`, `memory`,
   `remote-settings.json`, and `policy-limits.json`. With the variable set, the
   global state file is `$CLAUDE_CONFIG_DIR/.claude.json` instead of
   `~/.claude.json`, and the credential item name carries a hash of the
   directory. [BIN @233951099, @234204424] [DOC claude-directory, env-vars]
2. `CLAUDE_CONFIG_DIR` is honored from the shell, user settings, or managed
   settings, and ignored in project and local settings. [DOC env-vars]
3. Each configuration directory is therefore a separate user layer, with its
   own settings, skills, trust, auto memory, plugins, and login. [INF]
4. A relocated directory holds its own `.claude.json`; the default `~/.claude`
   does not, because without the variable the state file is `~/.claude.json`
   [BIN @234204424] [HOST: the second config dir's `.claude.json` and
   `~/.claude.json` exist]. That difference keeps a copy or backup of
   `~/.claude` out of a discovery that requires `.claude.json`, but it does not
   tell a relocated directory from a copy of one: a copy of
   `~/.claude-<account>` keeps its `.claude.json` [INF; reproduced with a
   temporary `HOME` during review].
   Discovery therefore also skips names that look like a copy or backup
   ([project bootstrap Plan](plan-project-bootstrap-2026-10-18.md), D).

Recheck when: the changelog changes `CLAUDE_CONFIG_DIR` or the location of
`.claude.json`.

## 4. Auto memory

1. Auto memory is on by default (2.1.59 and later). Each project gets
   `<config dir>/projects/<key>/memory/`, where the key is the sanitized path
   of the canonical Git root; all worktrees and subdirectories of a repository
   share it. The directory is created eagerly. [DOC memory] [BIN @236862543]
2. The first 200 lines or 25,000 bytes of `MEMORY.md`, whichever comes first,
   load at session start; topic files are read on demand. [DOC memory] [BIN]
3. Non-fork subagents do not receive the main session's auto memory; a fork
   inherits the parent conversation instead. Subagent `memory:` frontmatter
   gives an agent its own memory directory (`user`, `project`, or `local`).
   [DOC sub-agents]. This contradicts the workspace adapter's "subagents
   receive that copy" (Claude Auto-Memory, at `7659a94`).
4. Controls: `autoMemoryEnabled`, `CLAUDE_CODE_DISABLE_AUTO_MEMORY`,
   `autoMemoryDirectory`, and `CLAUDE_CODE_PROJECT_DIR_NAME`. Both relocation
   controls name one fixed directory, so setting either at user scope would
   merge every project's memory into one place. [DOC memory, settings-reference]
   [INF for the merge]
5. The Git-root finder accepts any `.git` entry without validating it. [BIN
   @235173897]

Recheck when: the changelog changes auto memory keying, loading limits, or
subagent memory.

## 5. `/init` and other generators

1. `/init` is a built-in prompt command without `disableModelInvocation`;
   since 2.1.108 the model can invoke it through the Skill tool. Claude Code
   never runs it on its own. [BIN @244418629] [DOC commands, changelog]
2. The classic flow analyzes the repository and writes `CLAUDE.md`, or
   suggests improvements to an existing one. Its prompt does not mention
   AGENTS.md. [BIN prompt] [DOC memory]
3. The new flow, enabled by `CLAUDE_CODE_NEW_INIT=1` or a server flag, is
   interactive (AskUserQuestion). It surveys AGENTS.md among other files,
   copies its relevant parts into the `CLAUDE.md` it generates, and can write
   a minimal `CLAUDE.md`, a Git-ignored `CLAUDE.local.md`, project skills, and
   hooks. It is not suited to unattended runs. [BIN @244394842] [DOC memory
   "Migrate instructions from other tools", env-vars] [INF for unattended use]
4. `claude --init`, `--init-only`, and `--maintenance` are hidden flags that
   run Setup hooks; they are unrelated to `/init`. [BIN] [DOC hooks#setup]
5. Disposition of every per-project Claude artifact. This answers the
   operator's question whether Claude content other than `/init` and memory
   is generated per project. "Without a request" means Claude Code creates it
   as a side effect of normal use; "Project Bootstrap" is `documentation.md`
   Project Bootstrap with the `project-bootstrap` skill.

   | Artifact | Created by Claude Code without a request | Created on a command (which) | Created by workspace-meta Project Bootstrap | Not generated per project, and why |
   |---|---|---|---|---|
   | Auto memory: `<config dir>/projects/<key>/memory/`, its `MEMORY.md` and topic files | Yes: the directory at session start, `MEMORY.md` and topic files when Claude keeps a note (4) | `/memory` opens it and toggles auto memory | No | Generated, but host-local recall per config dir and Git root, not a project file |
   | Session transcripts in `<config dir>/projects/<key>/` | Yes, for every session | None (`claude purge` deletes them) | No | Generated, host-local history per config dir |
   | Subagent memory: `.claude/agent-memory/<agent>/`, `.claude/agent-memory-local/<agent>/`, `<config dir>/agent-memory/<agent>/` | Yes, when a subagent whose definition sets `memory:` runs (4.3) | None | No | Follows from an agent definition; workspace-meta installs none |
   | Per-project entry in the config dir's `.claude.json` (trust, external-import approval, local-scope MCP servers) | Yes (6.2) | `claude mcp add --scope local` | No | Generated, host-local state per config dir |
   | `.claude/settings.local.json` | Yes: on "Yes, and don't ask again" and some `/config` options; Claude Code also lists it in the global Git excludes file | `/update-config`; the new `/init` flow (personal hooks) | No | Generated, personal approvals kept out of Git |
   | `.claude/worktrees/<name>/` | Yes: when a session starts with `--worktree`, the model calls `EnterWorktree`, or a subagent runs with `isolation: worktree` (9.2) | `/batch` | No | Generated when worktree isolation is used |
   | `CLAUDE.md` at the project root | No | classic `/init` (writes it, or suggests improvements to an existing one); the new `/init` flow (a minimal one); `/memory` (creates the file selected); `/import` (appends a one-time copy of `AGENTS.md` and similar files); `/doctor` (edits) | Yes: the thin `@AGENTS.md` adapter, in a repository the operator owns | Not applicable |
   | `CLAUDE.md` beside a subdirectory's own `AGENTS.md` | No | None writes it for `AGENTS.md`; the new `/init` flow may suggest subdirectory `CLAUDE.md` files | Yes: a sibling `@AGENTS.md` adapter for each nested `AGENTS.md` that has none, in a repository the operator owns (2.6) | Not applicable |
   | `AGENTS.md` | No; Claude Code only reads it (2) | None | Yes: the project survey, in a repository the operator owns that has no canonical owner | Not applicable |
   | `CLAUDE.local.md` | No | the new `/init` flow (also adds it to `.gitignore`); `/memory` | Only in a clone of someone else's repository: the `@AGENTS.md` import, or the survey notes when the clone has no `AGENTS.md`, listed in `"$(git rev-parse --git-common-dir)/info/exclude"` | Elsewhere it holds the operator's personal notes, which only the operator writes |
   | `.claude/settings.json` (permissions, hooks, environment) | No | the new `/init` flow (hooks); `/fewer-permission-prompts` (allowlist); `/update-config` | No | A project's guardrails are its own decision; the file is read only from the directory a session starts in (1.5) |
   | `enabledPlugins` in `.claude/settings.json` | No | `/plugin install --scope project` | No | Plugins are the operator's decision: an agent proposes one with the `authorization.md` brief and never installs it |
   | Hooks | No | the new `/init` flow; `/update-config` (`/hooks` only browses) | No | A hook runs code in every session; workspace-wide hooks reach projects through each config dir (the SessionStart group), and project hooks are the project's decision |
   | `.claude/skills/<name>/SKILL.md` | No | the new `/init` flow; skill-creator; `/verify` (a project verify skill); `/run-skill-generator` | No | A project skill holds one project's procedures; workspace-wide skills are installed into each config dir instead (7.1) |
   | `.claude/agents/*.md` | No | `/agents`; `/import` | No | Fixed frontmatter cannot follow each subtask's demand; delegation sets model and effort per agent (8) |
   | `.claude/commands/*.md` | No | `/import` | No | Commands are superseded by skills |
   | `.claude/rules/*.md` | No | Suggested, not written, by the new `/init` flow | No | Splitting instructions is the project's structure; the adapter already loads `AGENTS.md` |
   | `.mcp.json` | No | `claude mcp add --scope project`; `/import` | No | Each server is a capability and trust decision for the project; no project had one (11.6) |
   | `.claude/workflows/*.js` | No | saving a workflow from `/workflows` | No | Saved after a run the operator wants to repeat |
   | `.claude/output-styles/*.md` | No | None | No | Written by hand; nothing in this workstream needs one |
   | `.worktreeinclude` | No | None | No | Written by hand when worktree sessions need ignored files copied in |
   | `ONBOARDING.md` | No | `/team-onboarding`, in the working directory | No | A guide for people, not loaded as instructions |

   Kept per config dir rather than per project: skills and plugins synced
   from the claude.ai account (7.3), plan files in `<config dir>/plans/`, and
   the `/insights` report. [DOC claude-directory, settings, commands, memory,
   sub-agents, worktrees, skills] [BIN @244394842, @244437040] [HOST]

Recheck when: the changelog mentions `/init`, a new default init flow, or a
new generator.

## 6. Settings scope and trust

1. Precedence, highest first: managed, `--settings`,
   `.claude/settings.local.json`, `.claude/settings.json`, user settings. List
   keys and hooks merge. [DOC settings]
2. Interactive sessions hold back hooks from every settings file, user settings
   included, until the folder is trusted. Trust is keyed on the Git root, does
   not extend into a nested repository, and is stored per configuration
   directory in `.claude.json`. [DOC permissions, hooks]
3. A SessionStart hook can return `additionalContext` for the model and
   `systemMessage` for the user, each capped at 10,000 characters, and
   `reloadSkills`. [DOC hooks#sessionstart]

Recheck when: the changelog changes precedence, trust, or SessionStart output.

## 7. Skills

1. A personal skill is `<config dir>/skills/<name>/SKILL.md`; project skills
   load from `.claude/skills` up to the Git root. [DOC skills]
2. `disable-model-invocation: true` keeps the description out of context and
   lets only the user invoke the skill. An invoked skill stays in context in
   later turns; after compaction its first 5,000 tokens are kept;
   `allowed-tools` grants last for the invoking turn only. [DOC skills]
3. Skills synced from the claude.ai account land in
   `<config dir>/skills/synced/<bucket>/` (2.1.273 and later) and are
   read-only. [DOC skills] [HOST]

Recheck when: the changelog changes skill discovery or frontmatter.

## 8. Subagent model and effort

1. Model order for a subagent: the per-call `model`, the definition's `model`
   (`inherit` is the main model), `CLAUDE_CODE_SUBAGENT_MODEL`, the main
   model. The per-call value accepts only `sonnet`, `opus`, `haiku`, or
   `fable`; `CLAUDE_CODE_SUBAGENT_MODEL_FORCE=1` removes it. [DOC sub-agents]
   [BIN @251049596]
2. Effort order: `CLAUDE_CODE_EFFORT_LEVEL`, the per-call `effort` (2.1.292
   and later), frontmatter `effort`, the session level; `maxEffortLevel`
   clamps them all. Levels are `low`, `medium`, `high`, `xhigh`, `max`; Opus
   5.5, Sonnet 5.5, and Haiku 5.5 default to `medium` in Claude Code. A
   top-level `effortLevel` in user settings does not apply to Opus 5.5;
   `modelSettings.<model>.effortLevel` does. [DOC sub-agents, model-config]
3. The Agent tool tells the model to set `effort` "ONLY when the user, or
   instructions such as CLAUDE.md or a skill, explicitly ask ... never on your
   own judgment". The workflow authoring reference says to omit `opts.model`
   by default and to use `low` effort for "cheap mechanical stages and higher
   tiers only for the hardest verify/judge stages". Without a written
   instruction, Claude Code does not size subagents. [BIN @251049596, workflow
   reference]
4. Host: the user settings of both config dirs set Opus 5.5 to `xhigh`
   through `modelSettings`. An Opus 5.5 subagent that sets no effort therefore
   runs at `xhigh`. [HOST] [INF from minified code; `/tasks` shows the actual
   level]
5. Subagents lose `AskUserQuestion`, `EnterPlanMode`, and `Workflow`, so they
   cannot ask the operator; they get neither the conversation nor the main
   auto memory; Explore and Plan skip `CLAUDE.md`. The main session's rules
   reach a subagent only through its brief. [DOC sub-agents] [BIN]
6. Official guidance: tune effort on one model before mixing models;
   delegating to cheaper workers saved money in only two measured cases,
   routine work with a long cost tail and work larger than one context window.
   Opus 5.5 on a SWE-bench Pro subset: `low` 87.4% at $0.11 a task, `medium`
   92.8% at $0.21, `high` 95.3% at $0.29, `xhigh` 96.7% at $0.74 (one run);
   `low` with failures re-run at `high` about 97% at about $0.17. [DOC
   platform optimizing-for-cost-and-intelligence, choosing-a-model]
7. List prices per million input and output tokens: Fable 5.1 $10 and $50,
   Opus 5.5 $4 and $20, Sonnet 5.5 $2 and $10, Haiku 5.5 $0.10 and $0.50 for
   prompts up to 100K tokens. Fable is never a default and may bill usage
   credits depending on plan and seat; whether it does on this host's
   accounts was not checked. [DOC platform pricing, model-config]
8. Official effort guidance for the current models. Claude Code's
   model-config page: `medium` is "The default on Opus 5.5, Sonnet 5.5, and
   Haiku 5.5 ... fits day-to-day engineering work with a clear scope"; `high`
   is for "Work where verification matters or edge cases are likely"; `xhigh`
   is "Deeper reasoning at higher token spend. The default on Opus 4.7"; `max`
   "may show diminishing returns and is prone to overthinking". The Platform
   effort page gives `xhigh` the typical use "Long-running agentic and coding
   tasks (over 30 minutes) with token budgets in the millions". Its advice to
   "Start with `xhigh` for coding and agentic use cases" is for Opus 4.7 and
   4.8 only. For Opus 5.5 it says to "Run an effort sweep on your own evals
   rather than carrying settings over from an earlier model". [DOC
   model-config, fetched 2026-10-17; platform effort, fetched 2026-10-18]
   `claude-runtime.md` Delegation follows this wording. Keeping the operator's
   configured effort as the floor for judgment and the final synthesis is the
   operator's quality policy (W-R60, `capabilities.md`), not a Claude Code
   fact.

Recheck when: the changelog changes the Agent tool parameters, subagent
frontmatter, or the model lineup, the effort pages change their per-model
advice, or the operator changes `modelSettings`.

## 9. `/goal`, workflows, and asking the operator

1. `/goal` is registered in 2.1.302 ("Set a goal Claude checks before
   stopping"), with a non-interactive variant. It wraps a session-scoped,
   prompt-based Stop hook: after each turn the small fast model judges the
   condition not yet met, met, or impossible. The evaluator does not run
   commands or read files, so the condition must be one Claude's own output
   can show. At most 4,000 characters; one goal per session; it survives
   resume and is cleared by `/clear`; it works in `-p`; it does not change the
   permission mode; it is unavailable without workspace trust or with
   `disableAllHooks`. [DOC goal] [BIN]
2. The Workflow tool runs only on an explicit opt-in: ultracode, the user's own
   words, or a skill or command that says so. Per-agent options are `model`,
   `effort`, `isolation: 'worktree'`, and `agentType`; a running workflow takes
   no user input. Agent teams are experimental and off. Subagents run at most
   20 at once and three levels deep. A subagent worktree branches from the
   remote default branch unless `worktree.baseRef` is `head`. [DOC workflows,
   agent-teams, sub-agents, worktrees] [BIN]
3. `AskUserQuestion` works in the main conversation only: one to four
   questions with two to four options each, a recommended option first and
   marked "(Recommended)". A question stays open until answered unless the
   host sets `askUserQuestionTimeout`. Auto mode tells the model to keep
   working without stopping for clarifying questions unless the user, a skill,
   or the task signals that they want questions. [DOC tools-reference,
   permission-modes] [BIN]
4. Messages between agents carry no user authority. [DOC sub-agents]

Recheck when: the changelog mentions `/goal`, workflows, AskUserQuestion, or
auto mode.

## 10. Plugins and organization-managed settings

1. Neither configuration directory has an installed or enabled plugin. The
   cached `claude-plugins-official` marketplace lists 315 plugins (updated
   2026-10-17T15:35Z). `enabledPlugins` can be set in any settings file;
   project settings take precedence; each user installs an external plugin
   for themselves. `claude plugin details <name>` shows a plugin's projected
   token cost. [HOST] [DOC settings-reference] [CLI help]
2. Plugins relevant to this workstream, judged from their manifests:
   `feature-dev` (a clarifying-questions phase), `pr-review-toolkit`,
   `code-review`, `claude-md-management`, `hookify`, `session-report`, and
   `claude-security`, whose agents fix model, effort, and tools per role. [HOST
   manifests] [INF for relevance]
3. No organization-managed settings were observed: the one
   `remote-settings.json` on this host is `{}`. [HOST] Server-managed settings
   could push an organization-wide `claudeMd` that loads before user and
   project files. [DOC server-managed-settings]

Recheck when: a plugin is installed or enabled in either directory, or a
config dir's `remote-settings.json` exists and is not `{}`.

## 11. Host snapshot, 2026-10-17/18

These are dated observations, not current configuration authority. Recheck
each one before relying on it.

1. **Two Claude accounts with separate config dirs.** This host runs two
   Claude accounts: one uses `~/.claude`, the other a second config dir
   (`~/.claude-<account>`) that `CLAUDE_CONFIG_DIR` selects. [HOST]
2. **The workspace-managed surfaces existed in only one.** `make sync` and
   `scripts/bootstrap-local.sh` targeted only `$HOME/.claude` (`Makefile`
   lines 17-18 and `bootstrap-local.sh` lines 91-92 at `7659a94`). Sessions
   in the second config dir had no workspace-meta SessionStart group and no
   env-sync skill, and its `statusLine` belonged to another tool, without the
   workspace-meta marker. Because a healthy evaluator is silent, the missing
   hook looked like a healthy workspace. [HOST]
3. **Host-local preferences are kept per config dir.** Permission, auto-mode,
   and MCP server settings are kept in each config dir and differ between the
   two. No repository owns them, and workspace-meta does not sync them. [HOST]
4. **Auto memory is kept per config dir.** Each directory has its own auto
   memory. For `~/workspace/projects` the two `MEMORY.md` files index
   disjoint notes, and operator preferences about how to work (examples are
   not requirements, intake before work, delegation allocation) were spread
   across both. `~/.claude/projects` held 1,173 project directories (588 MB),
   almost all left by rule-eval runs. [HOST]
5. **`~/workspace/projects/.git` is an empty directory** (mtime 2026-10-06
   13:06, beside empty `.agents` and `.codex` directories; one project entry
   holds another such stub). Git ignores it and resolves `projects/` to
   `~/workspace`, but Claude Code's Git-root finder accepts it (4.5), so every non-Git directory
   under `projects/` shares the memory key, trust root, and local settings root
   `~/workspace/projects` [INF]. Sessions started in `projects/` used the key
   `-home-saberu-workspace-projects` in both directories [HOST]. The matching
   timestamps suggest sandbox mount stubs [INF].
6. **Project inventory** (36 entries under `projects/`) [HOST]:

   | Class | Count | Meaning |
   |---|---|---|
   | A | 7 | Claude-loadable entry file: 3 use the `@AGENTS.md` adapter (among them `homepage` and `reality-ops`), 4 a standalone `CLAUDE.md` (among them `ansispire`, `claude-md`, and `n8n-hosting`) |
   | B | 1 | `AGENTS.md` that no Claude entry file imports (`saberu`) |
   | C | 9 | operator or no-remote Git repository with neither file; one is a linked worktree of `reality-ops` whose branch predates that repository's entry files |
   | D | 5 | clone of a third-party repository; one tracks its upstream's own `CLAUDE.md` |
   | E | 14 | not a Git repository, or a stub or broken `.git` (2 entries) |

   No entry had `CLAUDE.local.md` or `.mcp.json`; only `claude-md` ignored
   `CLAUDE.local.md`. 28 entries had never had a Claude session in either
   directory.
7. **Nested `AGENTS.md` files.** `saberu` also holds 11 `AGENTS.md` files in
   subdirectories, and none has a sibling `CLAUDE.md` [HOST: `find` below the
   project root, 2026-10-18]. By 2.6 they do not reach Claude even after the
   root imports `@AGENTS.md`, and the readiness check looks only at the
   project root. The class is every subdirectory `AGENTS.md` without a
   sibling Claude entry file; `saberu` is its one instance on this host.

## 12. Conclusions for the Plans

- Project instructions reach Claude only through a `CLAUDE.md` in or above the
  project; under `~/workspace` a project's `AGENTS.md` needs an `@AGENTS.md`
  import (1.2, 2.2, 2.3), and a subdirectory's own `AGENTS.md` needs a
  sibling `CLAUDE.md` that imports it (2.6, 11.7). Plan: project bootstrap.
- Claude Code creates no project instructions on its own. Without a request
  it creates only host-local state per configuration directory (transcripts,
  auto memory, kept approvals, trust) and a worktree when a session or agent
  uses one; everything else waits for a command or for the project (4, 5.5).
  Plan: project bootstrap.
- Every configuration directory is a separate user layer; workspace-managed
  surfaces must be converged into each (3, 11.2). Plan: project bootstrap.
- Intake must run in the main conversation, and an unattended run must not
  wait on a question (8.5, 9.3). Plan: request intake.
- Per-agent model and effort happen only when written instructions ask for
  them (8.3); on this host every unsized Opus 5.5 subagent runs at `xhigh`
  (8.4); effort guidance comes from the Opus 5.5 pages, not the Opus 4.7
  advice (8.8). Plan: delegation allocation.

## 13. Not verified

- Which directory the globs of a path-scoped rule in an ancestor `.claude/rules`
  anchor to.
- The reach of `.mcp.json` "in this folder or above it".
- Which `AGENTS.md` files `claude-md-and-agents-md` loads in a project session
  (2.4); `/context` in a session with the mode set would show it.
- Whether the AGENTS.md plugin reads a subdirectory `AGENTS.md` on demand
  while an ancestor `CLAUDE.md` exists (2.6); `/context` or an
  InstructionsLoaded log in a session working in such a subdirectory would
  show it.
- The server flag values that choose the `/init` flow without the variable.
- The subagent effort for a level that came only from settings (8.4, minified
  code); confirm with `/tasks`.
- The shared memory key for non-Git directories under `projects/` (11.5),
  inferred from code; no session was started there.
- Whether a user-level `autoMemoryDirectory` is one flat directory, and whether
  `autoMode` is honored in project settings.
- A fresh Claude session confirming that a project `CLAUDE.md` import reaches
  the context, the gap left open by the
  [entry-point Plan](../feature-project-agent-entrypoints/plan-project-agent-entrypoints-2026-09-06.md).
  An InstructionsLoaded `include` log can close it.

## Supersession

- Re-verifies for 2.1.302 the baseline of the
  [entry-point Plan](../feature-project-agent-entrypoints/plan-project-agent-entrypoints-2026-09-06.md)
  ("Verified product baseline"): the `@AGENTS.md` adapter still holds, and
  Claude now reads AGENTS.md natively, but not in this workspace (2).
- Replaces, for current decisions, the April 2026 Claude Code references in
  the `projects/claude-md` repository (`docs/claude-workspace-pattern-2026-04-19.md`,
  the best-practices audit reference); they remain historical snapshots.
- Corrects the workspace adapter on subagent memory (4.3); the correction lands
  in [`claude-runtime.md`](../../../.agents/rules/claude-runtime.md).

## Sources

Claude Code documentation, fetched 2026-10-17:
<https://code.claude.com/docs/en/memory>,
<https://code.claude.com/docs/en/claude-directory>,
<https://code.claude.com/docs/en/settings>,
<https://code.claude.com/docs/en/settings-reference>,
<https://code.claude.com/docs/en/permissions>,
<https://code.claude.com/docs/en/permission-modes>,
<https://code.claude.com/docs/en/hooks>,
<https://code.claude.com/docs/en/commands>,
<https://code.claude.com/docs/en/skills>,
<https://code.claude.com/docs/en/sub-agents>,
<https://code.claude.com/docs/en/model-config>,
<https://code.claude.com/docs/en/workflows>,
<https://code.claude.com/docs/en/goal>,
<https://code.claude.com/docs/en/agent-teams>,
<https://code.claude.com/docs/en/worktrees>,
<https://code.claude.com/docs/en/tools-reference>,
<https://code.claude.com/docs/en/env-vars>,
<https://code.claude.com/docs/en/server-managed-settings>,
<https://code.claude.com/docs/en/changelog>.

Claude Platform documentation, fetched 2026-10-17:
<https://platform.claude.com/docs/en/about-claude/models/choosing-a-model>,
<https://platform.claude.com/docs/en/about-claude/models/optimizing-for-cost-and-intelligence>,
<https://platform.claude.com/docs/en/about-claude/pricing>; fetched
2026-10-18: <https://platform.claude.com/docs/en/build-with-claude/effort>.

Binary: the 2.1.302 `claude.exe` named above, at the offsets cited. Host: the
`settings.json` and `.claude.json` files of both config dirs (key names and
non-secret values), the `remote-settings.json` file, the launcher that selects
the second config dir, the plugin marketplace cache, and `ls`, `find`,
`git -C`, and `grep` over `~/workspace/projects/*`. Host names, the second
config dir's real name, account plans and organizations, launcher names,
organization policy details, and which account holds which settings are left
out of this public record; the second config dir is written
`~/.claude-<account>`. Section 11 gives counts and classes, and names a
project only where workspace-meta's tracked files on `main` already name it.

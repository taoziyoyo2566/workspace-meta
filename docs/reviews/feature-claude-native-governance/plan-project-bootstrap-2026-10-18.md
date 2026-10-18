# Plan: project bootstrap, Claude config dirs, and the layer model

- **Date**: 2026-10-18
- **Level**: Cross-project governance and host integration: two portable rule
  owners, the Claude runtime module, both adapters, the sync engine, the
  SessionStart evaluator, one skill template, the host layer model, the
  architecture doc and runbook, tests, and the register.
- **Status**: COMPLETE on 2026-10-18, verified on branch
  `feat/claude-native-governance` (`.worktrees/feat-claude-native-governance/`),
  uncommitted at closeout. Changelog:
  [changelog-project-bootstrap-2026-10-18.md](changelog-project-bootstrap-2026-10-18.md).
  The design choices under "Decisions taken in the operator's absence" were
  confirmed by the operator on 2026-10-18, decisions 2, 3, 6, and 15 with
  their recommended option (see the operator decision below).
- **Approval**: the operator's request of 2026-10-17, point 1:
  "1，让所有workspace目录下的项目，如果使用Claude，就会自动生成相应的内容，比如上面的init，memory，并调查是否还有其他的。用户级，workspace级，项目级要实现mece设计理念。"
  and, for the whole request: "我要去睡觉了，Claude还有一个goal的功能，我的要求就是把我说的这几点处理完，我不会在这里看着你，我希望明天早上能看到结果".
  This authorizes the goal and its working-tree implementation on this branch.
  The design choices below were made while the operator was away and are listed
  under "Decisions taken in the operator's absence" for review.
- **Operator decision (2026-10-18)**: "确认，按建议的设计决定执行，准备提交命令包".
  The decisions taken in the operator's absence are confirmed as recommended,
  and the publication command bundle is to be prepared. Staging, commit,
  merge, push, and `make sync` still wait for the bundle's own review.
- **Not approved, presented for review**: staging, commit, merge, and push;
  `make sync` or `make bootstrap` for any Claude or Codex config dir; any other
  host configuration write; any write into a project under
  `~/workspace/projects/`; a release tag.
- **Related**: [investigation of Claude Code 2.1.302](investigation-claude-code-runtime-2026-10-17.md),
  [request intake](plan-request-intake-2026-10-18.md),
  [delegation allocation](plan-delegation-allocation-2026-10-18.md),
  [design map](plan-design-map-2026-10-18.md).

## Goal

Every project under `~/workspace/projects/` that the operator works on with
Claude gets the Claude content it needs, starting with its instructions, without
the operator setting it up each time; and each piece of configuration content
has exactly one owner among the user, workspace, and project layers.

Reading of the request (`requests.md`):

- "init" and "memory" are examples of the content, not the whole need. The
  question "是否还有其他的" is answered by the disposition table in
  investigation §5.5. For every per-project Claude artifact, it shows whether
  Claude Code creates it without a request, which command creates it,
  whether Project Bootstrap creates it, and why the rest are not generated
  per project.
- "自动生成" is read as: the content appears without the operator asking for it
  in each project. Assumed, because the operator was away: an agent creates a
  missing entry file at the first substantive work in a project, and `make sync`
  converges the host layer. Not a background job that writes into project
  repositories. If the operator meant a one-time sweep over all projects, the
  rule still applies and the sweep is a separate, approved project write.
- "用户级" is read as every Claude config dir the operator uses, not only
  `~/.claude` (investigation §3, §11.1).

## Current state at approval

Claude Code 2.1.302 (investigation):

- Four native instruction scopes: Managed, User, Project, Local. The workspace
  `CLAUDE.md` reaches every project session as an ancestor Project file;
  skills and agents stop at each project's Git root, and project settings are
  read only from the directory a session starts in (§1).
- A project's `AGENTS.md` is never read natively under `~/workspace`, because
  the workspace `CLAUDE.md` is above it; a `CLAUDE.md` that imports
  `@AGENTS.md` works under every mode (§2). A subdirectory's own `AGENTS.md`
  is not known to reach Claude unless a sibling `CLAUDE.md` imports it (§2.6).
- `CLAUDE_CONFIG_DIR` relocates the whole user layer: settings, skills, trust,
  auto memory, plugins, login (§3).
- Claude Code creates no project instructions on its own. Without a request it
  creates only host-local state per config dir (session transcripts, auto
  memory, kept approvals in `.claude/settings.local.json`, per-project state in
  `.claude.json`) and `.claude/worktrees/` when a session or agent uses a
  worktree. `/init` and the other generators run only on a command (§4,
  §5.5).

Workspace-meta at `main` `7659a94`:

- `documentation.md` Make Agent Instructions Loadable (W-R41, W-R42) requires an
  entry file for each runtime a project is operated with, owned and enforced
  by the project. The Claude adapter tells the agent to read `AGENTS.md` and
  report a missing adapter.
- The [entry-point Plan](../feature-project-agent-entrypoints/plan-project-agent-entrypoints-2026-09-06.md)
  excluded "generating or editing entry files inside project repositories from
  workspace-meta".
- W-R11 (2026-04-17) required a `CLAUDE.md` in every new project directory. The
  refactor commit `cd72c1c` (2026-07-20) removed it without a recorded
  disposition.
- The memory-governance Draft v0.1.2
  ([README](../project-memory-governance/README.md)) asked for automatic
  memory initialization in new or cloned projects. It was never approved,
  installed, or abandoned.
- `make sync` and `scripts/bootstrap-local.sh` target only `$HOME/.claude`. The
  layer table in `README-agents.md` names only `~/.claude/settings.json` and has
  no row for the env-sync skill.

Host (investigation §11): two Claude accounts with separate config dirs,
`~/.claude` and a second config dir (`~/.claude-<account>`); the second has no
workspace-meta SessionStart group and no env-sync skill, and its `statusLine`
belongs to another tool. Auto memory and host-local preferences are kept per
config dir and differ between the two. `~/workspace/projects/.git` is an
empty directory that Claude Code accepts as a Git root. Of 36 entries under
`projects/`, 7 are Claude-ready, 1 has an `AGENTS.md` no Claude entry file
imports, 9 operator or no-remote repositories have neither file (one of them a
linked worktree whose main checkout has both), 5 are third-party clones, and
14 are not Git repositories. One project, `saberu`, also holds 11 subdirectory
`AGENTS.md` files with no sibling `CLAUDE.md` (§11.7).

## Intended change

### A. Layer model (owner: `.agents/host-templates/README-agents.md`)

Five layers; each content class has one owner:

1. **Org-managed**: Team or Enterprise server-managed settings, a managed
   `CLAUDE.md`, policy limits. The organization owns it; workspace-meta never
   writes it and must not conflict with it. No organization-managed settings
   were observed on this host; organization policy details are left out of
   this public record (investigation §10.3).
2. **Host user layer**: every agent config dir the operator uses
   (`~/.claude`, `~/.claude-<account>`, `~/.codex`). Credentials, trust,
   permissions and `autoMode`, model and effort defaults, plugins, MCP servers,
   history, and auto memory stay per config dir and host-local. The
   workspace-managed surfaces (the SessionStart group, the status line where no
   other tool owns it, the managed skills) are converged into each Claude
   config dir.
3. **Workspace** (`~/workspace`): portable rules, adapters, templates,
   scripts, provenance.
4. **Project** (`~/workspace/projects/<p>`): `AGENTS.md` as the canonical
   owner of the project's agent facts, a `CLAUDE.md` adapter,
   `.claude/settings.json` guardrails, project skills and agents, `.mcp.json`,
   and documentation.
5. **Project-local personal**: `CLAUDE.local.md` and
   `.claude/settings.local.json`, ignored or excluded from Git. In a clone of
   someone else's repository, `CLAUDE.local.md` is also the one file that
   carries the project's import or survey notes (B).

### B. Project bootstrap rule

- `documentation.md` gains `## Project Bootstrap` after Make Agent Instructions
  Loadable. `AGENTS.md` is the agent-neutral canonical owner. A runtime that
  does not load it directly gets a thin adapter that imports it, beside the
  root owner and beside each subdirectory's own `AGENTS.md`; for Claude that
  is a `CLAUDE.md` holding `@AGENTS.md`. A missing entry file is created at
  the first substantive work in the project, read-only review included.
  Existing files are never overwritten, nothing is committed, and what was
  created is reported. A directory that is not a Git repository is
  bootstrapped only on request. The missing-entry backstop keeps its gate
  phrases. Implemented with these limits:
  - Only the session in conversation with the operator bootstraps. A
    delegated agent, and a task whose operator instruction or brief forbids
    writes, reports the missing entry file instead. The delegating session
    bootstraps before it hands out work in the project.
  - A clone of a repository the operator does not own gets only
    `CLAUDE.local.md`. It holds the `@AGENTS.md` import when the clone has an
    `AGENTS.md`, and the survey notes otherwise, and is listed in
    `"$(git rev-parse --git-common-dir)/info/exclude"`, never in the tracked
    `.gitignore`. Ownership is read from the canonical remote; a repository
    with no remote is classified as the operator's own.
  - A linked worktree without entry files of its own is not bootstrapped
    itself: its main checkout is, and the branch receives the files by merge.
- `authorization.md` Work That Proceeds Without Another Confirmation gains
  creating a missing project entry file as Project Bootstrap describes, also
  during a read-only task, unless the operator or the task's brief forbids
  writes.
- `claude-runtime.md` (new Claude runtime module, the mirror of
  `codex-runtime.md`) owns Claude's mechanics: Configuration Layers (config
  dirs, scopes, discovery), Project Entry Files (the root adapter, the
  sibling adapter for a subdirectory `AGENTS.md`, `CLAUDE.local.md` in a
  foreign clone, how the survey is run, and how `/init` and `/import` output
  is handled), and Memory (per config dir, what subagents receive).
- `codex-runtime.md` gains `## Project Entry Files`. Codex loads only
  `AGENTS.md` and has no import syntax. A project whose owner is `CLAUDE.md`
  therefore gets a proposed owner move to `AGENTS.md`, made only after the
  operator agrees, and never a Codex adapter. Nothing is written into a
  foreign clone for Codex; the gap is reported.
- The `project-bootstrap` skill follows the same order. It checks that its
  session may write, uses the main checkout as the root of a linked worktree
  that has no entry files of its own, writes `AGENTS.md` only in a repository the operator owns,
  adds missing sibling adapters there, and in a foreign clone writes only the
  excluded `CLAUDE.local.md`, then checks that `git status --short` shows
  nothing new.
- Adapters: the documentation route row gains "a project without an entry file
  for the runtime in use"; `CLAUDE.md` routes `claude-runtime.md`, the Codex
  adapter does not. The Claude adapter's AGENTS.md paragraph states the actual
  loading mechanism and points to Project Bootstrap.

### C. Project readiness check (`scripts/workspace_status.py`)

The SessionStart evaluator reads the hook input once and takes the working
directory from its `cwd`, else from `CLAUDE_PROJECT_DIR`, else skips. It applies
only inside `<workspace>/projects/<name>/`. The project root is the nearest
ancestor, not above `projects/<name>`, that has a usable `.git` entry: a
directory with `HEAD`, or a `gitdir:` file whose target has one. Without one
it skips, and `projects/.git` is never a project root. A linked worktree
without entry files of its own is judged by its main checkout, and the message
names it as `<main> (main checkout of <worktree>)`: the bootstrap belongs
there, and the branch gets the files by merge.

- `--agent claude`: ready when the root has `CLAUDE.md`, `.claude/CLAUDE.md`, or
  `CLAUDE.local.md`, and, when `AGENTS.md` exists, one of them has a line that
  is exactly `@AGENTS.md` outside fenced code.
- `--agent codex`: ready when the root has `AGENTS.md`. A root whose owner is
  `CLAUDE.md` gets a message that Codex does not load it, pointing to the
  owner move in `codex-runtime.md`, instead of a request to bootstrap.
- Not ready: one message is added to both the operator's `systemMessage` and the
  agent's `additionalContext`, naming the project and pointing to
  `documentation.md` Project Bootstrap. A ready project is silent. The check
  reads the filesystem only and starts no subprocess.

### D. Sync across Claude config dirs (`scripts/sync_codex_config.py`, `Makefile`, `scripts/bootstrap-local.sh`)

- Repeatable `--claude-config-dir DIR` and `--claude-skill-template PATH`
  replace the single Claude settings and skill paths. A template
  `<name>-SKILL.md` installs to `DIR/skills/<name>/SKILL.md`.
- Per config dir, the areas are `Claude SessionStart [<dir>]`,
  `Claude statusLine [<dir>]`, and one `skill <name> [<dir>]` per template.
- Status line ownership: a `statusLine` without the workspace-meta marker
  belongs to another tool. It is kept and reported as "kept: statusLine owned
  outside workspace-meta"; it is not an error and does not stop other areas.
  An absent one is installed; a marked one is converged as before.
- Skill ownership: a managed skill carries the workspace-meta marker line
  after its frontmatter. An existing `DIR/skills/<name>/SKILL.md` without it
  belongs to another owner: it is kept and reported as "kept: skill owned
  outside workspace-meta", like a foreign status line. An unmarked `env-sync`
  that workspace-meta installed before the marker existed is still managed and
  gains the marker.
- The list of config dirs is host-local input: `CLAUDE_CONFIG_DIRS`,
  colon-separated like `PATH`, so a directory name may contain a space. When
  it is unset, the sync engine itself discovers `~/.claude` plus every
  `~/.claude-*` directory that holds a `.claude.json` file, and skips, and
  reports, a name that looks like a copy or backup. `.claude.json` alone does
  not tell a relocated dir from a copy of one (investigation §3.4). Check and
  sync print the resolved list before any write; interactive confirmation
  stays for `make sync`, while `make bootstrap` prints the lists and writes
  without asking.
- Tests cannot reach a real config dir: the test environment unsets
  `CLAUDE_CONFIG_DIR` and sets `CLAUDE_CONFIG_DIRS` to temporary directories.
- Skill templates installed into every Claude config dir: `env-sync`,
  `project-bootstrap` (new, `.agents/host-templates/project-bootstrap-SKILL.md`,
  the procedure for Project Bootstrap in Claude), and `interview` (new; see the
  [request intake Plan](plan-request-intake-2026-10-18.md)).

### E. Documents and provenance

- [Architecture doc](../../architecture/codex-config-management.md) and
  [runbook](../../runbooks/new-vps.md): the multi-dir sync, the status line
  policy, the skills, and the readiness check; every heading and safety phrase
  the docs gate requires stays.
- `README.md`: "every Claude config dir (`CLAUDE_CONFIG_DIRS`)" instead of only
  `~/.claude`.
- `.gitignore`: allow the two new rule files, the design map, and this review
  directory.
- `feedback-register.md`: W-R73 project bootstrap (`documentation.md` Project
  Bootstrap and the `authorization.md` bullet); W-R74 every agent config dir
  the operator uses is one instance of the user layer (`README-agents.md` and
  the sync engine). W-R73 restores W-R11 in a narrower form.

## Scope and non-goals

- No file in any project repository is written by this workstream; projects
  get their entry files when an agent next works in them.
- No hook, scheduled job, or headless `claude -p /init` run writes into
  projects. SessionStart stays report-only.
- Auto memory stays host-local recall in each config dir. No merging of the two
  memory stores, no symlinks between them, no `autoMemoryDirectory`.
- No user-level `CLAUDE.md` in any config dir (DQ-13 of the
  [content audit](../refactor-codex-rules-mece/content-audit-summary-2026-07-20.md)
  stays).
- No change to the AGENTS.md `instructionFiles` setting.
- `autoMode`, `permissions`, model and effort defaults, MCP servers, and plugins
  stay host-local and are not synced.
- Codex gets the readiness check through the shared evaluator, its entry-file
  mechanics in `codex-runtime.md` (B), and no new managed surface. No Codex
  adapter is written for a `CLAUDE.md` owner, and nothing is written for Codex
  into a foreign clone.

## Decisions taken in the operator's absence

Each choice names the alternative and why it was not taken. The operator may
reverse any of them at review.

1. **`AGENTS.md` canonical with a `@AGENTS.md` adapter**, instead of switching
   the Project-instructions setting to `claude-md-and-agents-md`. That mode
   also loads `~/workspace/AGENTS.md`, workspace-meta's own repository guidance
   that calls nested projects out of scope, into every project session
   (investigation §2.4, inferred); it is a per-config-dir user setting, so it
   would add a managed field per dir; and the import already works under every
   mode with no double read (§2.3).
2. **The agent creates a missing entry file at first substantive use**,
   instead of a SessionStart hook, a scheduled job, or a one-time scaffold run
   from workspace-meta that writes into every project. Project repositories are
   separate Git roots owned by their projects; a write from a hook or sweep
   happens without anyone reviewing the project, and the
   [memory-governance review](../project-memory-governance/review-project-workspace-memory-2026-08-08.md)
   (P1-2) blocked automatic initialization that did not define its write
   boundary. The rule defines it: the first substantive work,
   the missing file only, uncommitted, reported. **Confirmed by the operator
   on 2026-10-18**, including the writes this allows during a read-only task;
   the narrower alternative under decision 3 was not taken.
3. **Creating a missing entry file needs no further confirmation**
   (`authorization.md`), instead of asking in each project. The operator asked
   for it to happen automatically; the file is new, uncommitted, and
   reviewable; publication stays a separate approval. **Confirmed by the operator on
   2026-10-18.** The narrower alternative, not taken: create only the one-line
   `@AGENTS.md` adapter or `CLAUDE.local.md` without asking, and offer, not
   write, a survey-derived `AGENTS.md` during a read-only task.
4. **A clone of a repository the operator does not own gets only
   `CLAUDE.local.md`**, listed in the clone's own exclude file
   (`"$(git rev-parse --git-common-dir)/info/exclude"`), instead of a
   `CLAUDE.md` or an `AGENTS.md`. A tracked file would diverge from upstream:
   one third-party clone here tracks its upstream's own `CLAUDE.md`. An
   `AGENTS.md` that is not excluded could slip into a commit or an upstream
   pull request, and it would collide with one upstream adds later. When the
   clone has no `AGENTS.md`, the survey notes go into `CLAUDE.local.md`.
5. **Directories that are not Git repositories are bootstrapped only on
   request**, and the readiness check skips them, instead of treating each as
   a project. They are backups, data, notes, and worktree containers; with the
   empty `projects/.git` they would also share one memory key and trust root.
6. **Generated content goes into `AGENTS.md`**, and `CLAUDE.md` stays
   `@AGENTS.md`, instead of running `/init` as it is. Classic `/init` writes a
   full `CLAUDE.md` and does not consider `AGENTS.md`, and the new flow copies
   the relevant parts of `AGENTS.md` into `CLAUDE.md` (investigation §5.2,
   §5.3); either way, beside an `AGENTS.md` that would be a second authority. The
   `project-bootstrap` skill runs the survey and writes `AGENTS.md`;
   `claude-runtime.md` Project Entry Files says how to fold `/init` output into
   `AGENTS.md` when the operator runs it. **Confirmed by the operator on
   2026-10-18** for the survey-written `AGENTS.md`; the narrower alternative of
   decision 3, offering a survey-derived `AGENTS.md` during a read-only task
   instead of writing it, was not taken.
7. **A project with a standalone `CLAUDE.md` and no `AGENTS.md` counts as
   ready for Claude** (four projects, among them `ansispire`, `claude-md`, and
   `n8n-hosting`), instead of requiring migration to `AGENTS.md`. Moving the
   canonical owner rewrites project-owned files; that is the project's
   decision. In Codex these four projects get the owner-move message of
   decision 17, and so does one third-party clone that tracks its upstream's
   `CLAUDE.md`, where the move is not the operator's to make (Risks). A
   project with an `AGENTS.md` its Claude entry file does not import
   (`saberu`) is flagged and reported, never rewritten.
8. **Every config dir the operator uses is one instance of the user layer, and
   the managed surfaces converge into each** (W-R74), instead of managing only
   `~/.claude` or symlinking a second config dir to it. A symlink would merge
   credentials, trust, account state, and memory, which the separate account
   exists to keep apart.
9. **The config-dir list is a colon-separated `CLAUDE_CONFIG_DIRS`, and when
   it is unset the sync engine discovers it**, instead of
   `${CLAUDE_CONFIG_DIR:-~/.claude}`, which would make the target depend on
   the shell that runs `make` and still manage one dir, or a committed list,
   which would put host topology into a public repository. Discovery moved
   out of the Makefile because make splits words on spaces: a dir name with a
   space became wrong paths, one of them inside the checkout. Requiring
   `.claude.json` keeps backups of `~/.claude` out. A copy of a relocated dir
   keeps its `.claude.json`, so discovery also skips names that look like a
   copy or backup.
10. **A status line without the workspace-meta marker is kept and reported**,
    instead of refused. Refusing aborted the whole sync, so the second config
    dir's status line, which another tool owns, would have blocked Codex and
    `~/.claude` as well. Managing that status line from workspace-meta is
    deferred: owners workspace-meta and the tool that installs that status
    line; restart condition: the operator wants that status line converged.
11. **Auto memory stays split and recall-only**, instead of a symlink between
    the two config dirs' memory dirs, a per-project `autoMemoryDirectory`, or
    a one-time merge. `autoMemoryDirectory` names one fixed directory for every
    project (investigation §4.4), and a merge writes across accounts. Lasting
    preferences found in memory reach the rules instead: the second config
    dir's notes on intake before work and on delegation allocation become W-R71
    and W-R72.
12. **Disposition of the memory-governance Draft v0.1.2**: this Plan supersedes
    its automatic project initialization (requirement §3.9 of the
    [requirements record](../project-memory-governance/conversation-requirements-2026-08-07.md))
    with Project Bootstrap. Its other unrealized items (a workspace memory map,
    quick and full audits, report-only and reconcile modes, a history format)
    stay dormant. Owner: workspace-meta. Restart condition: a lasting fact is
    lost because memory is recall-only and no owning artifact held it.
13. **No user-level `CLAUDE.md`**, instead of installing one into each config
    dir. The workspace adapter already reaches every workspace project as an
    ancestor; a user file would also load outside `~/workspace` and repeat it.
    Projects outside `~/workspace` keep no workspace layer.
14. **The readiness message reaches the agent as well as the operator**,
    instead of the operator only. The agent is the one that acts on it; the
    cost is a short context line at each start in a project that is not ready.
15. **Only the session in conversation with the operator bootstraps**, instead
    of every agent that starts work in a project. A delegated agent, and a
    task whose operator instruction or brief forbids writes, reports the
    missing entry file. Otherwise parallel read-only agents would write into
    the tree they review and race to create the same file. Their report would
    reach only the orchestrator, so the operator might never see what was
    created. The alternative, letting the standing authority override a
    no-write brief, contradicts the brief and `review.md`'s read-only default.
    **Confirmed by the operator on 2026-10-18**: the session it names may
    write during a read-only task unless told not to; the narrower alternative
    of decision 3 was not taken.
16. **A linked worktree without entry files of its own is judged and
    bootstrapped through its main checkout**, instead of as a project of its
    own. A fresh
    survey on such a branch writes a second, divergent owner and an add/add
    conflict at merge; the branch gets the files by merge.
17. **Codex gets no adapter for a `CLAUDE.md` owner**, instead of an
    `AGENTS.md` stub that names `CLAUDE.md` or a copy of its content. Codex has
    no import, so a stub would not load the owner and a copy would be a second
    authority. The move of the facts to `AGENTS.md`, with a `CLAUDE.md` adapter
    left behind, is proposed to the operator per project. Nothing is written
    for Codex into a foreign clone, because Codex has no local-only entry file.
    Also considered: Codex's documented config key
    `project_doc_fallback_filenames` (present in codex-cli 0.160.1) can make
    Codex read `CLAUDE.md` when `AGENTS.md` is missing. It is a host-wide Codex
    preference, so it would also load upstream `CLAUDE.md` files in foreign
    clones. It is left to the operator as a candidate managed Codex
    preference, not adopted here.
18. **Sibling adapters for subdirectory `AGENTS.md` files**, instead of the
    root adapter alone or switching `instructionFiles` to
    `claude-md-and-agents-md`. Whether Claude reads a subdirectory `AGENTS.md`
    natively under an ancestor `CLAUDE.md` is not verified (investigation
    §2.6). The import is known to load on demand, and decision 1 already rules
    out the mode switch.
19. **A skill without the workspace-meta marker is kept and reported**,
    instead of overwriting any `skills/<name>/SKILL.md` of the same name.
    Fanning the templates out to every config dir writes where the operator
    or another tool may already keep a skill of that name; replacing it would
    destroy content workspace-meta does not own. This follows the status line
    policy of decision 10.

## Host and project actions that need the operator (NOT done)

1. `make sync` for both Claude config dirs (and Codex), after review of this
   branch: check that the printed list names `~/.claude` and the second
   config dir and nothing else, then confirm. The second config dir gains the
   SessionStart group and three skills; its status line stays with the tool
   that owns it. Then start fresh sessions in both accounts; Codex needs
   `/hooks` re-trust because the evaluator pin changes.
2. `~/workspace/projects/.git`, an empty directory, makes Claude Code treat
   `projects/` as a Git root (investigation §11.5). Find what creates it (it
   looks like a sandbox mount stub, like the one in another project entry)
   before removing it; the readiness check already ignores it.
3. Decide whether the host-local permission and auto-mode settings should
   match across the config dirs. They differ today (investigation §11.3), stay
   host-local, and are not synced.
4. Entry files in projects, handled when a session in conversation with the
   operator next works in each project, or in one session per project if the
   operator prefers:
   - the operator repositories without an entry file; the linked worktree
     among them is judged by its main checkout, which has both files;
   - the `saberu` root, whose `CLAUDE.md` does not import its `AGENTS.md`: a
     conflict that Project Bootstrap reports with a proposed fix and does not
     rewrite;
   - the class "a subdirectory `AGENTS.md` does not reach Claude unless a
     sibling `CLAUDE.md` imports it" (investigation §2.6, §11.7). Its one
     instance here is `saberu`, with 11 nested `AGENTS.md` files and no
     sibling adapter. Project Bootstrap now creates the missing sibling
     adapters in a repository the operator owns. Whether Claude reads such a
     file natively under an ancestor `CLAUDE.md` is not verified.
5. Optional: clean up about 1,150 rule-eval project directories in
   `~/.claude/projects` under `temporary-files.md`, and point rule-eval runs at
   an isolated config dir.
6. In Codex, five projects whose owner is a standalone `CLAUDE.md` show the
   owner-move message: the four operator projects of decision 7, until their
   owner moves to `AGENTS.md`, and one third-party clone that tracks its
   upstream's `CLAUDE.md`, where the message does not clear (Risks). Moving
   the owner is the operator's decision for each operator project (decision
   17).

## Acceptance criteria

- `documentation.md` Project Bootstrap and the `authorization.md` bullet hold
  the behavior in B, including who may bootstrap, the foreign-clone path, the
  linked-worktree exception, and sibling adapters; `claude-runtime.md` has
  Configuration Layers, Project Entry Files, and Memory; `codex-runtime.md`
  has Project Entry Files; both adapters route as B says; the docs gate still
  finds "before substantive project work" and "including read-only review or any
  host/external action" in `documentation.md` and `CLAUDE.md`.
- `tests/test_workspace_status.py`: a Claude project root with neither file, or
  with an `AGENTS.md` no entry file imports, produces the message in both
  outputs; a ready project, a cwd outside `projects/`, a non-Git directory,
  `projects/.git`, and a linked worktree whose main checkout has the entry
  files produce nothing, and one whose main checkout lacks them is reported
  under the main checkout's name; the Codex variant checks `AGENTS.md`; a CLI
  test feeds `{"cwd": …}` on stdin; the existing order tests still pass.
- `tests/test_sync_codex_config.py`: two config dirs converge in one run; a
  foreign status line in one dir is kept and reported while the other areas
  apply; skill templates fan out to every dir; an existing skill without the
  marker is kept and reported; `CLAUDE_CONFIG_DIRS` is split
  on colons; default discovery takes `.claude-*` dirs with `.claude.json`,
  ignores those without, and skips names that look like a copy or backup; a
  second run reports everything unchanged; no test can reach a real config
  dir.
- `make test` with `CLAUDE_CONFIG_DIR` and `CLAUDE_CONFIG_DIRS` unset, the docs
  gate (only the known "routed documentation is not tracked" error for files
  the operator has not committed), `git diff --check`, `py_compile`, and
  `bash -n` pass.
- Host acceptance after the operator's `make sync`, reported as a gap until
  then: `make agent-sync-check` lists both config dirs and exits 0; a fresh
  session in the second account, in a project without an entry file, shows
  the readiness message; a
  fresh session in `homepage` shows none; an InstructionsLoaded `include` log
  or `/context` in `homepage` shows its `AGENTS.md` loaded.

## Risks

- The evaluator's hash pin changes, so every installed hook reports "changed,
  run make sync" until each host syncs; Codex also asks for `/hooks` re-trust.
- Default discovery could pick up a config dir the operator does not use as
  one. Names that look like a copy or backup are skipped, the list is printed
  before any write, and `CLAUDE_CONFIG_DIRS` overrides it. `make sync` asks
  for confirmation, while `make bootstrap` prints the lists and writes without
  asking, which is why the runbook runs the read-only `make agent-sync-check`
  first.
- Known limitation: in Codex the readiness warning does not clear in a clone
  of someone else's repository, because nothing is written there for Codex
  (decision 17). A clone without `AGENTS.md` keeps the message at every Codex
  start, and one that tracks its upstream's `CLAUDE.md` gets the owner-move
  message although the move is upstream's decision.
- An agent may write an entry file a project's owner does not want: the file
  is uncommitted and reported, existing files are never overwritten, only the
  session in conversation with the operator writes, and third-party clones
  get one excluded local file only.
- The readiness check looks only at the project root, so a subdirectory
  `AGENTS.md` without a sibling adapter raises no message; the skill's survey
  reads every nested `AGENTS.md` and adds the missing adapters.
- If the second config dir was meant to stay a clean account for rule-eval
  gate runs (an open question in the uncommitted transcript-replay Plan on
  `feat/rule-evals`), installing hooks and skills there weakens that isolation.
  The eval harness can pass its own config dir.
- Concurrent uncommitted worktrees edit the same owners (`feat/rule-evals`
  W-R66 to W-R70, `fix/user-run-commands` W-R62, `fix/short-user-commands`
  W-R65); merge order must be planned (`planning.md` Proportional Shape).

## Links

- Builds on: `documentation.md` Make Agent Instructions Loadable (W-R41,
  W-R42); the
  [entry-point Plan](../feature-project-agent-entrypoints/plan-project-agent-entrypoints-2026-09-06.md)
  and its [Changelog](../feature-project-agent-entrypoints/round1-project-agent-entrypoints-2026-09-06.changelog.md)
  for the thin adapter; the sync engine and its
  [cross-host convergence Plan](../refactor-codex-sync/plan-cross-host-config-convergence-2026-09-08.md);
  the three sync layers of W-R26 and W-R28; the five-layer ownership model of
  the [rule-ownership Plan](../refactor-codex-rules-mece/plan-codex-rule-ownership-2026-07-20.md);
  `planning.md` Record Findings When Confirmed (W-R50) and the memory role of
  W-R51; the layer and mechanism criteria of the `projects/claude-md`
  repository (`docs/claude-layer-evolution-entry-2026-04-19.md`), a separate
  repository and an April 2026 snapshot.
- Supersedes: the exclusion "generating or editing entry files inside project
  repositories from workspace-meta" of the
  [entry-point Plan](../feature-project-agent-entrypoints/plan-project-agent-entrypoints-2026-09-06.md),
  by the operator's decision of 2026-10-17; W-R11's silent removal, by
  restoring it in a narrower form (W-R73); the automatic initialization of the
  memory-governance Draft v0.1.2 (decision 12).
- Keeps: DQ-13 (no user-level `CLAUDE.md`) and the memory role of W-R51.
- Corrects: the Claude adapter's statements that Claude does not load
  `AGENTS.md` and that subagents receive the loaded `MEMORY.md`
  (investigation §2.2, §4.3).
- Depends on: the [investigation](investigation-claude-code-runtime-2026-10-17.md).
- Related: the [design map Plan](plan-design-map-2026-10-18.md) catalogs the
  new domains; the [request intake Plan](plan-request-intake-2026-10-18.md)
  supplies the `interview` skill this sync installs.

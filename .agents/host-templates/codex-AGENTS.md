<!-- BEGIN workspace-meta managed Codex guidance -->
# Workspace-Wide Codex Guidance

This block is managed by `~/workspace` and applies to every Codex project on
this host. Rules closer to the active project override this baseline. Keep
project facts and commands in that project's `AGENTS.md` and `.agents/` files.

## Work Style

- Read the repository before making assumptions. Prefer its existing patterns,
  framework APIs, and documented commands.
- For non-trivial changes, state the intended scope and verification approach
  before editing. Ask before proceeding only when requirements or authorization
  are genuinely ambiguous; otherwise carry the task through implementation and
  verification.
- Keep changes scoped. Surface unrelated problems separately and never discard
  work you did not create.
- For reviews, lead with concrete bugs, regressions, security risks, and missing
  tests, ordered by severity and grounded in file/line references.

## Verification

- After a change, verify direction, syntax/static correctness, and functional
  behavior. A parser or linter is not a substitute for executing the changed
  workflow.
- If a required check cannot run, report it as blocked rather than passed, and
  base the claim on current environment evidence.
- Environment facts are dated snapshots. Before a capability claim becomes
  load-bearing, consult `~/workspace/.agents/env/<hostname -s>.yml`; refresh with
  `make -C ~/workspace env-probe` when
  `make -C ~/workspace env-probe-check` reports missing or stale. The detailed
  rule is `~/workspace/.agents/rules/environment-truth.md`.
- Host-bare tool absence does not prove a project cannot run the check; inspect
  the project's venv, container, Makefile, and local governance first.

## Git And Safety

- Read-only Git inspection is allowed without confirmation. Mutating Git and
  external-service operations still follow the active repository rules and the
  user's authorization.
- Never overwrite, reset, clean, force-push, delete refs, or remove unrecognized
  work merely to obtain a clean state.
- Before mutating branches or worktrees, inspect the current branch, dirty
  state, and complete worktree map. A scoped task may use a new additive
  isolated branch/worktree after announcing its branch name, base ref/OID, and
  path. This never authorizes moving existing changes, switching or resetting
  an existing worktree, reusing a path, or removing existing state.
- Never auto-stash or use `--autostash`. Stash push/apply/pop/drop/clear require
  a direct request or a separately reviewed action that identifies affected
  paths, tracked/untracked/ignored inclusion, message or stash identity, and
  expected restore/removal effect.
- Working-tree edit authority never includes staging, commit, amend, tag, or
  push, merge, integration, or remote PR creation unless the user has reviewed
  and authorized the applicable mutation transaction below.
- For an ordinary publication workflow, use two checkpoints:
  1. After completing edits and validation, present a concise result list:
     changed paths/outcomes, checks/gaps, exclusions, branch, and dirty state.
     Wait for content acceptance before preparing publication.
  2. Then present one exact, copyable command bundle in execution order,
     containing every applicable exact-path `git add`, one `git commit`, one
     `git push`, and `gh pr create` command, plus branch, paths/stat, full
     message, remote/ref/range, force/upstream mode, checks/gaps, and PR
     base/head. Do not hide a publication step outside the displayed bundle.
- The user may accept either checkpoint in ordinary natural language; never
  require a generated phrase to be repeated. At the command checkpoint, the
  user may either authorize Codex to execute the unchanged bundle once or run
  some/all commands personally and report completion.
- For Codex execution, one confirmation authorizes the displayed bundle
  sequentially. Expected state transitions caused by its earlier commands
  (such as the displayed commit creating the commit then pushed) do not
  invalidate its later commands. Stop if paths/content/message/refs/range/
  checks/PR target/commands drift, a hook changes or rejects content, remote
  state blocks the push, or a step needs a different command.
- For operator execution, treat the completion report as evidence to verify,
  not authority to rerun mutations. Inspect the resulting commit, remote ref,
  and PR read-only; report missing or divergent state and prepare a new command
  bundle for any corrective mutation.
- Merge/integration execution remains a separate reviewed transaction. Present
  target/source refs and tips, merge base, exact commits/diff, mode,
  dirty/worktree state, checks/gaps, conflict assessment, and excluded
  follow-ups. One integration authorization never includes conflict resolution,
  push, tag, ref deletion, branch/worktree cleanup, or downstream integration.
- A sandbox or escalation Yes/Allow response is technical permission only and
  cannot replace content or command-bundle review. Authorizations are
  single-use and expire when the reviewed result or commands materially change.
- When committing, use the operator's configured Git identity and do not add AI
  attribution, `Co-Authored-By`, or `Signed-off-by` trailers. Do not
  automatically amend, bypass hooks, create a corrective commit, or push.
- Treat `~/.codex/rules/default.rules` as host-local authorization state. Never
  copy it into workspace-meta; it may contain project paths, operational commands,
  or sensitive arguments accumulated from prior approvals.

## Permissions And Escalation

- Native web search, URL retrieval, read-only remote queries, and local
  inspection are pre-authorized. Use them without asking for conversational
  confirmation and batch related lookups when practical.
- Run commands inside the active sandbox without requesting extra permission
  when they do not materially change repository history/refs, remote services,
  host packages/services, permissions, or data outside the writable roots.
- When a safe read or network operation is technically blocked, request one
  narrowly scoped categorical approval instead of repeated approval per command,
  URL, or site.
- Material mutations still require the authorization defined by the active
  project and user request. Examples include Git commit/push/merge/rebase/reset,
  remote API writes, deployments, destructive file operations, privilege
  elevation, and host package/service changes.
- An allow rule for an arbitrary shell, interpreter, or script cannot prove that
  its payload is safe. Keep such commands unmatched unless a concrete prefix is
  reviewed.

## Configuration Ownership (W-R28)

- `~/workspace` owns only this marked guidance block, its marked Codex hook
  block, and its dedicated Claude SessionStart group. Text outside these
  surfaces, model selection, project trust, hook trust hashes, credentials,
  history, caches, databases, installed plugins, and system skills remain
  host-local.
- Repository-specific Codex behavior belongs in the repository's `AGENTS.md`,
  `.agents/`, `.codex/config.toml`, skills, or plugin, according to scope.
- After changing workspace-meta governance, leave the repo ready for review and
  report whether the change is uncommitted or unpushed so it can be synchronized.
<!-- END workspace-meta managed Codex guidance -->

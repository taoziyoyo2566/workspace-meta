# Workspace-Meta Project Guidance

This repository owns the cross-project governance carrier rooted at
`~/workspace`. The global managed Codex guidance still applies; this file adds
repository-specific rules.

Independent project repositories belong under `~/workspace/projects/<project>/`.
They remain separate Git roots; the workspace-meta root is reserved for shared
governance and its own review artifacts.

## Scope Discipline

- Default to the nearest Git root; workspace-meta work covers only this root.
- Treat nested project repositories and source examples as out of scope unless
  the user explicitly names them. They may inform a portable rule, but never
  expand this repository's implementation, verification, or commit scope.

## Before Editing

- Read `README.md` and, for agent configuration work,
  `docs/architecture/codex-config-management.md`.
- A non-trivial coherent workstream uses a persistent Plan under
  `docs/reviews/<kind>-<topic>/plan-<slug>-YYYY-MM-DD.md` when `planning.md`
  calls for one. Before creating a Plan, reuse an existing active or approved
  Plan covering the same goal and scope.
- Routine in-scope feedback, repairs, UX/configuration refinements, and
  re-verification do not create additional Plans. Create one Changelog at final
  verified workstream closeout, not per implementation round; generic lifecycle
  semantics remain owned by `planning.md` and `documentation.md`.
- Keep the reverse whitelist in `.gitignore` explicit. New tracked paths require
  a matching allow rule and a pre-commit verification.

## Configuration Boundaries

- Never commit credentials, Codex authorization rules, hook trust hashes,
  project trust, histories, caches, databases, logs, or generated host config.
- Workspace-meta may install only explicitly documented managed blocks into
  `~/.codex` and every Claude config dir in `CLAUDE_CONFIG_DIRS`; content
  outside those ownership markers is local.
- Changes to trusted hook behavior must change the installed hook command hash
  so Codex asks the operator to review it again.

## Verification

- Run `make test`.
- Run `bash -n scripts/*.sh .githooks/pre-commit` and
  `PYTHON_BIN="$(./scripts/find_python.sh)" && "$PYTHON_BIN" -m py_compile scripts/*.py tests/*.py`.
- Parse generated TOML/JSON/YAML and run `git diff --check`.
- When a change adds a file that the documentation gate routes or links, run
  `make verify-committed`, which runs `make test` on a temporary copy in which
  every file the whitelist admits is committed.
- Run bootstrap twice against an isolated temporary HOME and confirm managed
  file hashes are unchanged on the second run.
- Treat a real Codex/Claude UI smoke test as manual host verification, not as a
  unit-test result.

## Branches And Releases

- The main branch is `main` on the canonical remote `origin`. Every change
  follows the change flow in `git-branches.md` on a branch named
  `<type>/<topic>`, where `<type>` is a Conventional Commits type such as
  `feat`, `fix`, `docs`, `refactor`, `test`, or `chore`.
- An additive worktree goes under `.worktrees/<type>-<topic>/`, which the
  reverse whitelist ignores. Changes reach `main` by fast-forward only.
- Workspace-meta releases the rules and host templates it syncs to hosts
  (`releases.md`). "Released" means pushed to `main`, with `make sync` applied
  and verified on each host. A closed batch or a fix released this way is
  tagged; release tags are annotated, unsigned, and named
  `v<MAJOR>.<MINOR>.<PATCH>`, and the first is `v1.0.0`.
- Compatibility surface: the managed host surfaces (the marked Codex blocks,
  the Claude SessionStart group and status line, the declared preference
  fields), the `make` targets, and the rule file names that adapters and
  projects route to. Rule wording inside an owner is not part of it.
- Status surface: `git -C ~/workspace describe --match 'v[0-9]*'` on each
  host. No rollback procedure is written yet: the notes name the rollback
  target, and a bad release is fixed forward with a patch release that each
  host syncs.

## Commit And Sync

- Leave changes reviewable and report whether they are uncommitted or unpushed.
- Do not stage, commit, push, or create a PR unless the applicable shared
  publication transaction has been reviewed and authorized. No agent workflow
  requires automatic same-round synchronization.
- An authorized change-flow bundle may run through
  `scripts/change_flow_bundle.sh`: `check`, then `commit` (add, commit,
  fast-forward), the push as its own command, then `retire`. The brief shows
  the bundle directory's files, including the `TREE` and `MESSAGE_SHA256`
  fingerprints that `check` prints. Removing any other worktree stays a
  separately reviewed action (`git-recovery.md`).
- After a reviewed sync plan, `make sync SYNC_EXPECT='label;label'` applies without
  a prompt only when no other area drifted.

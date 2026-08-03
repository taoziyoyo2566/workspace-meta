# workspace-meta

This repository **is** the `~/workspace` directory root. It exists to sync the
**cross-project governance layer** — shared rules and their Claude/Codex adapters
across all projects on this user's machines — plus the small bootstrap needed to
install them safely. Runtime state and project contents remain outside its scope.

The GitHub repo is named `workspace-meta`; the local directory is `~/workspace`.
The names are independent — the binding is only the remote URL (`git remote -v`).

## Why it exists

Rules live in three layers, each with its own sync channel:

| Layer | Holds | Sync channel |
|---|---|---|
| `~/.claude/`, `~/.codex/` | credentials, authorization, trust, caches, history, host preferences | **none — each machine maintains its own** |
| `~/workspace/` root | cross-project methodology, provenance, host templates, bootstrap | **this repo** |
| `~/workspace/projects/<project>/` | project-specific `CLAUDE.md`, `AGENTS.md`, `.agents/`, `.codex/`, governance docs | the project's own repo |

### Workspace directory layout

The `~/workspace` root is intentionally reserved for workspace-meta governance:
shared rules, adapters, templates, bootstrap scripts, and review evidence.
Independent project repositories live below `~/workspace/projects/<project>/`.
Each project keeps its own nearest `.git` root, so project Git commands do not
mix with workspace-meta history.

Before this repo, the middle layer belonged to no repository: an edit on one
machine was invisible everywhere else, while the existing "multi-machine sync"
rules only covered project-repo artifacts. This repo closes that gap.
Full provenance: `feedback-register.md` entry **W-R26**.

### Design decisions

- **Reverse-whitelist `.gitignore`** — `*` ignores everything; only the
  governance files are explicitly allowed back in. Tracking scope is defined by
  configuration, not by discipline: even `git add -A` at the root stages
  nothing, and polluting the repo requires an explicit `git add -f`.
- **Pre-commit guard closes the `git add -f` hole** — `.githooks/pre-commit`
  rejects any staged path that the ignore rules would match (only force-adds
  can produce one). The verdict derives from `.gitignore` via
  `check-ignore --no-index` (the `--no-index` matters: plain `check-ignore`
  skips index-resident paths, exactly where force-added files sit), so there
  is no second list to drift. Deletions are exempt — removing a bad file must
  always work. Enable per machine: `git config core.hooksPath .githooks`
  (dot-prefixed so the dir stays out of the way and is unmistakably a *git*
  hook, not a Claude Code/Codex `hooks` block).
- **Nested project repos are safe** — git always resolves the *nearest*
  `.git`, so commands inside any project see only that project's repo. The one
  side effect: running git in a *non-repo* subdirectory (scratch dirs) now
  resolves to this repo instead of erroring; the whitelist keeps its status
  clean, so this is cosmetic.
- **Per-host secrets and authorization stay out by design** — identity values,
  credentials, Codex trust state, approval rules, caches, and histories are never
  synced. The generated `.agents/env/<host>.yml` capability registry is the narrow,
  explicit exception: it carries dated operational facts for cross-machine task
  routing, never credential values.
- **Agent configuration uses narrow managed surfaces, not home-directory
  mirrors** — the versioned templates converge only marked Codex sections and
  one dedicated Claude SessionStart group. Both agents call the same ordered
  status evaluator. Model choice, project trust, hook trust hashes, local
  guidance outside the managed surfaces, `default.rules`, auth, plugins, skills,
  databases, history, logs, and caches remain host-local. Full design:
  `docs/architecture/codex-config-management.md`; ownership matrix:
  `.agents/host-templates/README-agents.md`; provenance: W-R28.
- **Portable agent rules are modular and have one owner** — the workspace
  `CLAUDE.md` and installed Codex AGENTS block are compact adapters. Shared
  authorization, task-shaped Git, planning/handoff, verification, review,
  capability selection, secret/environment safety, and rule authoring live
  under `.agents/rules/`; agent runtime mechanics are explicit, and projects
  keep only topology, commands, schemas, operational constraints, and stricter
  deltas. Ownership matrix: `.agents/host-templates/README-agents.md`;
  provenance: W-R32.
- **Permission intent is portable; executable authorization is host-local** —
  the shared authorization owner says that native search, URL retrieval, remote
  read queries, and ordinary inspection need no conversational confirmation;
  both resident adapters route to it. Concrete outside-sandbox allow/prompt
  decisions live in the operator's
  `~/.codex/rules/*.rules` and are never copied into this repository. This keeps
  credentials, paths, and accumulated approvals out of Git while avoiding
  repeated per-site prompts. Protected-action proposals, requests for the
  operator to run them, and consent requests also use a portable action brief
  covering purpose, target, effect, risk, exclusions, checks, and the exact
  approval boundary; the host prompt remains technical permission only.
  Provenance: W-R29 and W-R34–W-R35.
- **Git publication uses result review plus one command bundle** — Codex first
  presents the validated change result, then one exact, copyable bundle
  containing applicable add/commit/push/PR commands. The operator may authorize
  Codex to run that unchanged bundle once or run it personally and have Codex
  verify the result read-only. Natural-language confirmation is sufficient; a
  technical permission prompt is never semantic authorization. W-R31 refines
  W-R30 without weakening its content-review boundary.
- **Rejected alternatives**: file-sync tools (syncthing/rsync) — no history,
  no merge, concurrent register edits would overwrite each other; symlinking
  from another repo — indirection plus mixing concerns with unrelated repos.

## Daily workflow

- **After editing** governance files or host templates: review/verify the
  workspace-meta result, report whether it is local-only/unpublished, then use
  `.agents/rules/git-publication.md` when synchronization is intended.
- **When resuming work on any machine**: let the SessionStart evaluator fetch
  and report behind/ahead/dirty state. If the workspace rule layer is behind,
  review the exact update before changing the checkout; pulling stays deliberate
  so conflicts never happen unattended.
  `make bootstrap` installs or upgrades the local integration. One synchronizer
  prevalidates Claude JSON and Codex TOML, migrates legacy workspace-meta hook
  groups, then atomically converges all three managed targets. Run
  `make agent-sync-check` to report drift without writing host files. It requires
  Python 3.11+ (`tomllib`). Changed Codex hooks must be reviewed again with
  `/hooks`.
- **Commits follow W-R25**: Conventional Commits (`<type>(<scope>): <subject>`,
  subject = what, body = why); identity gate before committing
  (`git config --show-origin user.name user.email` must resolve from the
  host's *global* gitconfig to the current operator); **no trailers**
  (`Co-Authored-By`, `Signed-off-by`); post-commit `git log -1` self-check.

## Onboarding a machine

The complete new-VPS installation sequence, host-private configuration
boundaries, post-change activation steps, and troubleshooting are documented in
[`docs/runbooks/new-vps.md`](docs/runbooks/new-vps.md). This README keeps only
the minimal entry point; follow the runbook for the detailed procedure.

`~/workspace` already exists and is non-empty (the normal case):

```bash
cd ~/workspace
git init -b main
git remote add origin https://github.com/taoziyoyo2566/workspace-meta.git
git fetch origin
git checkout main   # if local copies of the tracked files diverged: back them
                    # up first, checkout, then diff-merge the local-only edits
```

Fresh machine (no `~/workspace` yet) — clone with an explicit target dir,
otherwise git would create a `workspace-meta/` directory:

```bash
git clone https://github.com/taoziyoyo2566/workspace-meta.git ~/workspace
```

Place independent project checkouts below the workspace project boundary:

```bash
mkdir -p ~/workspace/projects
git clone <project-remote> ~/workspace/projects/<project>
```

Either way, run the host-local bootstrap from the repo root:

```bash
make bootstrap
```

The bootstrap is idempotent and host-local. It:

- sets `git config core.hooksPath .githooks` for this repo, warns if the
  previous value was stale, and verifies the `pre-commit` guard is actually
  present and executable at that path;
- checks `git config --global user.name` and whether `user.email` has a
  plausible email shape, but never writes identity values (W-R25/W-R14: those
  live only in each host's `~/.gitconfig`);
- installs one SessionStart handler for **each** of Claude Code and Codex. Both
  handlers invoke `scripts/workspace_status.py`, which evaluates in a stable order:
  repository availability and dirty state, bounded remote fetch, one post-fetch
  ahead/behind snapshot, then environment-registry freshness;
- emits no hook output when healthy and otherwise emits one JSON
  `systemMessage`. Remote-unavailable warnings are rate-limited through
  `~/.cache/workspace-meta/status.json`; behind, dirty/unpushed, and stale-registry
  states remain visible;
- pins the evaluator SHA-256 in each installed command. An evaluator change is
  therefore an auditable hook-command change instead of silently changing the
  meaning of an already trusted command;
- installs the **env-sync skill** (`~/.claude/skills/env-sync/`) and synchronizes
  the workspace-wide Codex router/safety floor into a managed block in
  `~/.codex/AGENTS.md`. The versioned root `CLAUDE.md` is Claude's thin adapter;
  both route to the same portable modules. Existing Codex content outside the
  managed block is preserved;
  bootstrap warns if `AGENTS.override.md` would shadow it.

Managed installs are idempotent and convergent for both agents. The legacy
`--write-codex` option remains accepted as a compatibility alias, but synchronization
runs safely by default. All targets are rendered and parsed before the first write;
ambiguous groups containing both workspace-meta and user handlers are rejected.
Codex requires reviewing/trusting new or changed hooks via `/hooks` before they
run. Claude settings outside the dedicated workspace-meta group are preserved.

Nothing under `~/.claude` or `~/.codex` is committed to this repo (they are
outside `~/workspace` and per-host by design — W-R26). The root `CLAUDE.md`,
shared rules, templates, and installer are the versioned carriers; generated
host files are not.

## Caveats

- **Keep the remote private.** `feedback-register.md` contains verbatim
  internal incident records and quotes.
- **Never widen the whitelist toward project content.** A new
  *workspace-level* rule file gets one `!<file>` line in `.gitignore`;
  anything project-specific belongs in that project's repo.
- **Never add secrets or authorization state** — names/emails, credential values,
  `auth.json`, Codex approval rules and trust hashes remain host-local. The
  generated capability registry is the only documented per-host snapshot.
- **Never mirror an agent home wholesale.** Add a managed field only after
  classifying its ownership in `.agents/host-templates/README-agents.md`.
- **Register merge conflicts**: entries are append-style and usually
  auto-merge. The real hazard is a **W-R number collision** when two machines
  mint entries concurrently — current model assumes a single writer at a time;
  on collision, renumber the later entry before pushing.

## Future improvements

- **Register scaling** — deferred until there is real pressure. Trigger when
  `feedback-register.md` becomes hard to scan (rough guide: 300-500 lines),
  merge conflicts become frequent, or domain-based lookup starts costing time.
  Likely shape: split by domain while keeping W-R numbering global, then leave
  this file or a small index as the navigation entry point.
- **Cross-machine W-R allocation** — deferred until concurrent rule-writing on
  multiple machines becomes routine. First next step should be a lightweight
  process rule (fetch before minting, inspect latest W-R, write, push
  immediately, renumber on collision) before considering heavier ID schemes
  such as machine suffixes, date-based IDs, or reserved ranges.

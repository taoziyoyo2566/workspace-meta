# workspace-meta

This repository **is** the `~/workspace` directory root. It exists to sync the
**cross-project governance layer** — the rule files that govern every Claude
session across all projects on all of this user's machines — and deliberately
tracks nothing else.

The GitHub repo is named `workspace-meta`; the local directory is `~/workspace`.
The names are independent — the binding is only the remote URL (`git remote -v`).

## Why it exists

Rules live in three layers, each with its own sync channel:

| Layer | Holds | Sync channel |
|---|---|---|
| `~/.claude/` | per-host facts (identity, credentials, host authorization) | **none — each machine maintains its own** |
| `~/workspace/` root | cross-project methodology (`CLAUDE.md`) + rule provenance (`feedback-register.md`) | **this repo** |
| each project dir | project-specific rules (`CLAUDE.md`, `.agents/rules/*`, governance docs) | the project's own repo |

Before this repo, the middle layer belonged to no repository: an edit on one
machine was invisible everywhere else, while the existing "multi-machine sync"
rules only covered project-repo artifacts. This repo closes that gap.
Full provenance: `feedback-register.md` entry **W-R26**.

### Design decisions

- **Reverse-whitelist `.gitignore`** — `*` ignores everything; only the
  governance files are explicitly allowed back in. Tracking scope is defined by
  configuration, not by discipline: even `git add -A` at the root stages
  nothing, and polluting the repo requires an explicit `git add -f`.
- **Pre-commit guard closes the `git add -f` hole** — `hooks/pre-commit`
  rejects any staged path that the ignore rules would match (only force-adds
  can produce one). The verdict derives from `.gitignore` via
  `check-ignore --no-index` (the `--no-index` matters: plain `check-ignore`
  skips index-resident paths, exactly where force-added files sit), so there
  is no second list to drift. Deletions are exempt — removing a bad file must
  always work. Enable per machine: `git config core.hooksPath hooks`.
- **Nested project repos are safe** — git always resolves the *nearest*
  `.git`, so commands inside any project see only that project's repo. The one
  side effect: running git in a *non-repo* subdirectory (scratch dirs) now
  resolves to this repo instead of erroring; the whitelist keeps its status
  clean, so this is cosmetic.
- **Per-host facts stay out by design** — a synced carrier must hold shared
  rules, never single-machine values (identity names/emails, credential
  snapshots). That principle came from a concrete failure: hardcoding one
  operator's git identity into a synced rule file would have made every
  machine commit as that person (see W-R25's Why).
- **Rejected alternatives**: file-sync tools (syncthing/rsync) — no history,
  no merge, concurrent register edits would overwrite each other; symlinking
  from another repo — indirection plus mixing concerns with unrelated repos.

## Daily workflow

- **After editing** `CLAUDE.md` or `feedback-register.md`: commit + push this
  repo **in the same round** (rule in `CLAUDE.md` section 6).
- **When resuming work on any machine**: `git -C ~/workspace pull` first.
  Per-host SessionStart hooks automate the reminder: they fetch and emit a
  warning when the local rule layer is behind `origin/main`. Fetch-only by
  design — pulling stays a deliberate act so conflicts never happen unattended.
  `make bootstrap` installs/checks the local integration. Claude Code is merged
  into `~/.claude/settings.json` with `jq`; Codex is detected and printed as a
  TOML snippet by default because programmatic TOML edits are easier to get
  wrong. Codex auto-append is available only with
  `./scripts/bootstrap-local.sh --write-codex`.

  Claude Code hook snippet (`~/.claude/settings.json`):

  ```json
  "hooks": { "SessionStart": [ { "hooks": [ {
    "type": "command", "timeout": 15,
    "command": "behind=$(git -C \"$HOME/workspace\" fetch origin --quiet 2>/dev/null && git -C \"$HOME/workspace\" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n \"$behind\" ] && [ \"$behind\" -gt 0 ]; then printf '{\"systemMessage\":\"workspace-meta: governance rule layer is %s commit(s) behind origin/main — run: git -C ~/workspace pull\"}' \"$behind\"; fi"
  } ] } ] }
  ```

  Codex hook snippet (`~/.codex/config.toml`):

  ```toml
  [[hooks.SessionStart]]
  matcher = "startup|resume"

  [[hooks.SessionStart.hooks]]
  type = "command"
  command = 'behind=$(git -C "$HOME/workspace" fetch origin --quiet 2>/dev/null && git -C "$HOME/workspace" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n "$behind" ] && [ "$behind" -gt 0 ]; then printf "workspace-meta: governance rule layer is %s commit(s) behind origin/main. Run: git -C ~/workspace pull\n" "$behind"; fi'
  timeout = 15
  statusMessage = "Checking workspace-meta freshness"
  ```
- **Commits follow W-R25**: Conventional Commits (`<type>(<scope>): <subject>`,
  subject = what, body = why); identity gate before committing
  (`git config --show-origin user.name user.email` must resolve from the
  host's *global* gitconfig to the current operator); **no trailers**
  (`Co-Authored-By`, `Signed-off-by`); post-commit `git log -1` self-check.

## Onboarding a machine

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

Either way, run the host-local bootstrap from the repo root:

```bash
make bootstrap
```

The bootstrap is idempotent and host-local. It:

- sets `git config core.hooksPath hooks` for this repo;
- checks `git config --global user.name` and `user.email`, but never writes
  identity values (W-R25/W-R14: those live only in each host's `~/.gitconfig`);
- merges the Claude Code SessionStart freshness hook into
  `~/.claude/settings.json` using `jq`, preserving existing keys;
- checks whether `~/.codex/config.toml` already has the Codex freshness hook.
  Missing Codex TOML is printed for manual paste by default; use
  `./scripts/bootstrap-local.sh --write-codex` only if you explicitly want the
  script to append the snippet.

Codex will require reviewing/trusting new or changed non-managed hooks via
`/hooks` before they run.

## Caveats

- **Keep the remote private.** `feedback-register.md` contains verbatim
  internal incident records and quotes.
- **Never widen the whitelist toward project content.** A new
  *workspace-level* rule file gets one `!<file>` line in `.gitignore`;
  anything project-specific belongs in that project's repo.
- **Never add per-host values** (names, emails, credential states, host
  capability snapshots) to the tracked files — generic rules and verification
  gates only.
- **Register merge conflicts**: entries are append-style and usually
  auto-merge. The real hazard is a **W-R number collision** when two machines
  mint entries concurrently — current model assumes a single writer at a time;
  on collision, renumber the later entry before pushing.

## Future improvements

- **Register scaling** — `feedback-register.md` grows monotonically; when it
  becomes unwieldy, split it by domain (keeping W-R numbering global) and
  leave an index, mirroring how project rules are split under
  `.agents/rules/`.
- **Cross-machine W-R allocation** — if concurrent rule-writing on multiple
  machines becomes routine, replace the single-writer assumption (e.g.
  machine-suffixed or date-based entry IDs).

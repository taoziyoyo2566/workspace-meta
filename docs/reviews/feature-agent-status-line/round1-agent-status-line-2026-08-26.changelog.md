# Claude/Codex Status-Line Integration — Round 1

Status: Implemented and verified locally on 2026-08-26; host installation and
real TUI smoke tests pending operator action; uncommitted and unpublished.

## Outcome

Added `scripts/claude_status_line.py` and wired it into the existing atomic
agent configuration synchronizer. Claude's managed `statusLine.command` now
renders:

- home-shortened current directory and read-only Git branch;
- model and color-thresholded context percentage;
- current input, cache-write, cache-read, and output token detail;
- Claude Code's client-supplied session cost estimate, visibly prefixed with
  `~$` so it is not mistaken for authoritative billing.

The renderer uses documented status-line stdin fields. It does not discover a
session by cwd, scan private transcript/session files, depend on a fixed
Homebrew path, or hard-code Sonnet pricing.

Codex continues to use the repository's native `tui.status_line` item list for
model, remaining context, branch, token totals, and weekly usage. Both clients
therefore share the display intent while retaining their supported extension
contracts: Claude command/stdin versus Codex native footer identifiers.

## Configuration safety

The synchronizer hash-pins the Claude renderer command and preserves stdin
through the loader. It installs a missing status line and updates only a
marker-bearing workspace-meta status line. An unrecognized existing Claude
`statusLine` makes the entire prevalidated sync fail before any target write,
so personal scripts are not overwritten.

Renderer-only hash drift now reports an ordinary managed update. The
synchronizer counts a Claude SessionStart group as a legacy migration only when
its command contains an actual legacy marker; replacing the current managed
group no longer produces the misleading `migrated 1 legacy hook group` action.

Ownership, architecture, bootstrap help, README, runbook, whitelist, and tests
were updated. No real `~/.claude`, `~/.codex`, Git publication, or external
state was changed.

## Verification

Passed:

- `make test` — 54 tests;
- `bash -n scripts/*.sh .githooks/pre-commit`;
- Python byte compilation for `scripts/*.py` and `tests/*.py`;
- `bash .githooks/pre-commit`;
- `git diff --check`;
- generated Codex TOML and Claude JSON parsing;
- two `make bootstrap` runs in an isolated temporary HOME and repository: the
  second run reported every managed agent target already current, and hashes
  for Codex `AGENTS.md`/`config.toml`, Claude `settings.json`, and the env-sync
  skill were unchanged.

No YAML artifact was generated or changed by this round. Manual gaps remain:

- after a separately reviewed host bootstrap, restart Claude Code and inspect
  `/statusline` rendering with a real session payload;
- inspect Codex `/statusline` in a fresh TUI session;
- if the host already has a personal Claude status line, review and back it up
  before explicitly removing or migrating that unmanaged field.

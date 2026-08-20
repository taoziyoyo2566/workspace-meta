# Codex Status Line Token Detail — Round 6

Status: Implemented locally on 2026-08-20; host installation pending operator
approval; uncommitted and unpublished.

## Change

Expanded the managed `tui.status_line` preference to show the per-session
total, input, and output token counters in addition to model, remaining
context, and Git branch:

```toml
status_line = [
  "model",
  "context-remaining",
  "git-branch",
  "used-tokens",
  "total-input-tokens",
  "total-output-tokens",
]
```

Codex omits a status item when its value is not yet available. The visual TUI
smoke check remains manual; this round does not stage, commit, push, or change
any other host configuration.

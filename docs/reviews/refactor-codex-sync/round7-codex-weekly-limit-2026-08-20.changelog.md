# Codex Status Line Weekly Limit — Round 7

Status: Implemented locally on 2026-08-20; host installation pending operator
approval; uncommitted and unpublished.

## Change

Appended `weekly-limit` to the managed `tui.status_line` preference after the
per-session total, input, and output token counters:

```toml
status_line = [
  "model",
  "context-remaining",
  "git-branch",
  "used-tokens",
  "total-input-tokens",
  "total-output-tokens",
  "weekly-limit",
]
```

The [official Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
defines `tui.status_line` as an ordered list of TUI-footer item identifiers.
Whether this identifier renders for a particular account or session remains a
manual host check. This round does not write host configuration, stage, commit,
push, or alter any other host-local state.

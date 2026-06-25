#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

codex_write=false
case "${1:-}" in
  "")
    ;;
  "--write-codex")
    codex_write=true
    ;;
  "-h"|"--help")
    cat <<'USAGE'
Usage: ./scripts/bootstrap-local.sh [--write-codex]

Configures host-local workspace-meta integration:
  - sets this repo's core.hooksPath to .githooks
  - checks global git identity without writing identity values
  - merges the Claude Code freshness hook with jq
  - checks Codex freshness hook; prints the TOML snippet by default

Use --write-codex to append the Codex TOML snippet when no workspace-meta
Codex hook is detected. Review/trust it in Codex with /hooks afterwards.
USAGE
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    echo "Run with --help for usage." >&2
    exit 2
    ;;
esac

info() {
  printf '[workspace-meta] %s\n' "$*"
}

warn() {
  printf '[workspace-meta] WARNING: %s\n' "$*" >&2
}

valid_git_email() {
  case "$1" in
    *@*.*) ;;
    *) return 1 ;;
  esac

  case "$1" in
    *[[:space:]]*|*@|@*|*..*) return 1 ;;
  esac
}

hooks_path=".githooks"
prev_hooks_path="$(git -C "$repo_root" config --local --get core.hooksPath || true)"
if [ -n "$prev_hooks_path" ] && [ "$prev_hooks_path" != "$hooks_path" ]; then
  warn "core.hooksPath was '$prev_hooks_path' (stale); correcting to '$hooks_path'"
fi
git -C "$repo_root" config core.hooksPath "$hooks_path"
hook_file="$repo_root/$hooks_path/pre-commit"
if [ -x "$hook_file" ]; then
  info "Git pre-commit guard active: core.hooksPath=$hooks_path"
else
  warn "core.hooksPath=$hooks_path set, but $hook_file is missing or not executable —"
  warn "  the whitelist guard will NOT run until it is restored (chmod +x / git checkout)."
fi

global_name="$(git config --global --get user.name || true)"
global_email="$(git config --global --get user.email || true)"
if [ -n "$global_name" ] && valid_git_email "$global_email"; then
  info "Global git identity present: user.name and plausible user.email are set"
else
  warn "Global git identity missing or invalid; set it manually before committing:"
  [ -n "$global_name" ] || warn "  git config --global user.name '<your name>'"
  valid_git_email "$global_email" || warn "  git config --global user.email '<your email>'"
fi

claude_cmd='behind=$(git -C "$HOME/workspace" fetch origin --quiet 2>/dev/null && git -C "$HOME/workspace" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n "$behind" ] && [ "$behind" -gt 0 ]; then printf '\''{"systemMessage":"workspace-meta: governance rule layer is %s commit(s) behind origin/main — run: git -C ~/workspace pull"}'\'' "$behind"; fi'
codex_cmd='behind=$(git -C "$HOME/workspace" fetch origin --quiet 2>/dev/null && git -C "$HOME/workspace" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n "$behind" ] && [ "$behind" -gt 0 ]; then printf "workspace-meta: governance rule layer is %s commit(s) behind origin/main. Run: git -C ~/workspace pull\n" "$behind"; fi'

if command -v jq >/dev/null 2>&1; then
  claude_dir="$HOME/.claude"
  claude_settings="$claude_dir/settings.json"
  mkdir -p "$claude_dir"
  if [ ! -f "$claude_settings" ]; then
    printf '{}\n' > "$claude_settings"
  fi

  tmp="$(mktemp)"
  jq --arg command "$claude_cmd" '
    if ((.hooks.SessionStart // []) | any(.[]?; ((.hooks // []) | any(.[]?; ((.command? // "") | contains("workspace-meta")))))) then
      .
    else
      .hooks = ((.hooks // {}) as $hooks | $hooks + {
        "SessionStart": (($hooks.SessionStart // []) + [{
          "hooks": [{
            "type": "command",
            "command": $command,
            "timeout": 15,
            "statusMessage": "Checking workspace-meta freshness"
          }]
        }])
      })
    end
  ' "$claude_settings" > "$tmp"
  jq -e . "$tmp" >/dev/null
  mv "$tmp" "$claude_settings"
  info "Claude Code SessionStart freshness hook is present in $claude_settings"
else
  warn "jq is not installed; skipped Claude Code settings merge"
  warn "Install jq or add the README hook snippet to ~/.claude/settings.json manually."
fi

codex_config="$HOME/.codex/config.toml"
codex_snippet="$(cat <<EOF
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = '$codex_cmd'
timeout = 15
statusMessage = "Checking workspace-meta freshness"
EOF
)"

if [ -f "$codex_config" ] && grep -Fq "workspace-meta: governance rule layer" "$codex_config"; then
  info "Codex SessionStart freshness hook is present in $codex_config"
else
  if [ "$codex_write" = true ]; then
    mkdir -p "$(dirname "$codex_config")"
    {
      [ ! -s "$codex_config" ] || printf '\n'
      printf '%s\n' "$codex_snippet"
    } >> "$codex_config"
    info "Codex hook snippet appended to $codex_config"
    warn "Open Codex /hooks and review/trust the new non-managed hook."
  else
    warn "Codex SessionStart freshness hook is missing from $codex_config"
    warn "Default bootstrap does not edit TOML automatically. Add this snippet, or rerun with --write-codex:"
    printf '%s\n' "$codex_snippet"
  fi
fi

info "Bootstrap complete"

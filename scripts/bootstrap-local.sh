#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "${1:-}" in
  "")
    ;;
  "--write-codex")
    warn_deprecated_codex_flag=true
    ;;
  "-h"|"--help")
    cat <<'USAGE'
Usage: ./scripts/bootstrap-local.sh [--write-codex]

Configures host-local workspace-meta integration (per-host; nothing here is
committed — the installer lives in the repo, the generated host files do not):
  - sets this repo's core.hooksPath to .githooks
  - checks global git identity without writing identity values
  - synchronizes workspace-meta-owned hooks into ~/.claude/settings.json
  - synchronizes managed blocks into Codex AGENTS.md and config.toml while
    preserving host-local settings:
      * one shared, ordered status evaluator for Claude and Codex
      * workspace-meta freshness and uncommitted/unpushed work
      * env capability registry freshness (~/workspace/.agents/env/<host>.yml)
  - installs the env-sync skill (~/.claude/skills/) and the Codex global routing
    (~/.codex/AGENTS.md) from templates under .agents/host-templates/

--write-codex is retained as a compatibility alias; Codex managed blocks are now
synchronized safely by default. Review/trust new or changed hooks with /hooks.
USAGE
    exit 0
    ;;
  *)
    echo "Unknown option: $1" >&2
    echo "Run with --help for usage." >&2
    exit 2
    ;;
esac

warn_deprecated_codex_flag="${warn_deprecated_codex_flag:-false}"

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

# ── git pre-commit guard ─────────────────────────────────────────────────────
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

# ── git identity (report only) ───────────────────────────────────────────────
global_name="$(git config --global --get user.name || true)"
global_email="$(git config --global --get user.email || true)"
if [ -n "$global_name" ] && valid_git_email "$global_email"; then
  info "Global git identity present: user.name and plausible user.email are set"
else
  warn "Global git identity missing or invalid; set it manually before committing:"
  [ -n "$global_name" ] || warn "  git config --global user.name '<your name>'"
  valid_git_email "$global_email" || warn "  git config --global user.email '<your email>'"
fi

# ── Agent managed config (Claude settings + Codex AGENTS/config) ─────────────
codex_home="${CODEX_HOME:-$HOME/.codex}"
claude_settings="$HOME/.claude/settings.json"
[ "$warn_deprecated_codex_flag" = false ] || warn "--write-codex is deprecated; managed agent sync now runs by default."
python_bin="$(bash "$repo_root/scripts/find_python.sh" || true)"
if [ -n "$python_bin" ]; then
  "$python_bin" "$repo_root/scripts/sync_codex_config.py" \
    --python "$python_bin" \
    --agents-template "$repo_root/.agents/host-templates/codex-AGENTS.md" \
    --hooks-template "$repo_root/.agents/host-templates/codex-hooks.toml" \
    --status-script "$repo_root/scripts/workspace_status.py" \
    --codex-home "$codex_home" \
    --claude-settings "$claude_settings"
else
  warn "Python 3.11+ with tomllib is unavailable; skipped safe agent configuration synchronization"
fi

# ── Claude host template (env-sync skill) ────────────────────────────────────
install_template() {
  # $1 = template path relative to repo_root, $2 = destination
  local src="$repo_root/$1" dest="$2"
  if [ ! -f "$src" ]; then warn "template missing: $src"; return; fi
  mkdir -p "$(dirname "$dest")"
  if [ ! -f "$dest" ]; then
    cp "$src" "$dest"; info "installed template: $dest"
  elif ! cmp -s "$src" "$dest"; then
    cp "$src" "$dest"; info "refreshed template from repo: $dest"
  else
    info "template up to date: $dest"
  fi
}

install_template ".agents/host-templates/env-sync-SKILL.md" "$HOME/.claude/skills/env-sync/SKILL.md"
info "Bootstrap complete"

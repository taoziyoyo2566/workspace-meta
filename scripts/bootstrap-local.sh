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
  - synchronizes workspace-meta-owned hooks and status line into ~/.claude/settings.json
  - synchronizes managed blocks into Codex AGENTS.md and config.toml, and
    reconciles declared Codex preference fields while preserving host-local settings:
      * one shared, ordered status evaluator for Claude and Codex
      * a Claude command status line and Codex native TUI status items
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
env_skill="$HOME/.claude/skills/env-sync/SKILL.md"
[ "$warn_deprecated_codex_flag" = false ] || warn "--write-codex is deprecated; managed agent sync now runs by default."
python_bin="$(bash "$repo_root/scripts/find_python.sh" || true)"
if [ -n "$python_bin" ]; then
  "$python_bin" "$repo_root/scripts/sync_codex_config.py" \
    --python "$python_bin" \
    --agents-template "$repo_root/.agents/host-templates/codex-AGENTS.md" \
    --hooks-template "$repo_root/.agents/host-templates/codex-hooks.toml" \
    --preferences-template "$repo_root/.agents/host-templates/codex-preferences.toml" \
    --status-script "$repo_root/scripts/workspace_status.py" \
    --claude-status-line-script "$repo_root/scripts/claude_status_line.py" \
    --env-skill-template "$repo_root/.agents/host-templates/env-sync-SKILL.md" \
    --codex-home "$codex_home" \
    --claude-settings "$claude_settings" \
    --env-skill "$env_skill"
else
  warn "Python 3.11+ with tomllib is unavailable; skipped safe agent configuration synchronization"
  skill_template="$repo_root/.agents/host-templates/env-sync-SKILL.md"
  if [ -f "$skill_template" ]; then
    mkdir -p "$(dirname "$env_skill")"
    if [ ! -f "$env_skill" ] || ! cmp -s "$skill_template" "$env_skill"; then
      cp "$skill_template" "$env_skill"
      info "installed env-sync skill without agent configuration validation: $env_skill"
    else
      info "env-sync skill already current: $env_skill"
    fi
  else
    warn "template missing: $skill_template"
  fi
fi
info "Bootstrap complete"

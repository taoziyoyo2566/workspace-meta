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
Usage: make bootstrap [CLAUDE_CONFIG_DIRS="DIR:DIR..."]
       [CLAUDE_CONFIG_DIRS="DIR:DIR..."] ./scripts/bootstrap-local.sh [--write-codex]

Configures host-local workspace-meta integration (per-host; nothing here is
committed — the installer lives in the repo, the generated host files do not):
  - sets this repo's core.hooksPath to .githooks
  - checks global git identity without writing identity values
  - synchronizes workspace-meta-owned hooks and status line into settings.json
    of every Claude config dir. CLAUDE_CONFIG_DIRS is a colon-separated list
    of absolute or ~/ paths; unset, the sync discovers ~/.claude plus every
    ~/.claude-* dir holding a .claude.json, skips names that look like a copy
    or backup, and prints both lists before it writes a config dir (without
    Python, only the skills are installed, into ~/.claude when unset)
  - synchronizes managed blocks into Codex AGENTS.md and config.toml, and
    reconciles declared Codex preference fields while preserving host-local settings:
      * one shared, ordered status evaluator for Claude and Codex
      * a Claude command status line and Codex native TUI status items
      * workspace-meta freshness and uncommitted/unpushed work
      * env capability registry freshness (~/workspace/.agents/env/<host>.yml)
  - installs each .agents/host-templates/<name>-SKILL.md as
    <claude dir>/skills/<name>/SKILL.md in every Claude config dir (an
    existing SKILL.md without the workspace-meta ownership marker is another
    owner's skill and is kept), and the Codex global routing
    (~/.codex/AGENTS.md) from .agents/host-templates/

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

die() {
  printf '[workspace-meta] ERROR: %s\n' "$*" >&2
  exit 2
}

# ── Claude config dirs and skill templates (validated before any write) ─────
# CLAUDE_CONFIG_DIRS is colon-separated, so a dir name may contain spaces.
# Unset or blank, the sync engine discovers the config dirs; the no-Python
# fallback cannot, and uses ~/.claude.
parse_claude_config_dirs() {
  local rest="$1:" entry
  claude_config_dirs=()
  while [ -n "$rest" ]; do
    entry="${rest%%:*}"
    rest="${rest#*:}"
    [ -n "$entry" ] || continue
    case "$entry" in
      *[[:space:]]/*|*[[:space:]]~*)
        die "Claude config dir looks like a space-separated list; separate CLAUDE_CONFIG_DIRS entries with ':': $entry"
        ;;
    esac
    case "$entry" in
      "~") entry="$HOME" ;;
      "~/"*) entry="$HOME/${entry:2}" ;;
    esac
    case "$entry" in
      /*) ;;
      *) die "Claude config dir must be an absolute path or start with ~/: $entry" ;;
    esac
    claude_config_dirs+=("$entry")
  done
}

claude_config_dirs_explicit=false
claude_config_dirs=()
case "${CLAUDE_CONFIG_DIRS:-}" in
  *[![:space:]]*) parse_claude_config_dirs "$CLAUDE_CONFIG_DIRS" ;;
esac
if [ "${#claude_config_dirs[@]}" -gt 0 ]; then
  claude_config_dirs_explicit=true
else
  parse_claude_config_dirs "$HOME/.claude"
fi

# Each <name>-SKILL.md installs as <claude dir>/skills/<name>/SKILL.md; the
# name and ownership-marker rules match the sync engine's, so both paths
# accept the same set and keep the same skills.
skill_marker='<!-- workspace-meta managed skill: make sync replaces this file -->'
# Installed before the marker existed; an unmarked copy is still managed.
legacy_unmarked_skills=" env-sync "

# True when the first line after the YAML frontmatter (or the first line,
# without frontmatter) is the ownership marker.
skill_has_marker() {
  local line first=true in_frontmatter=false
  while IFS= read -r line || [ -n "$line" ]; do
    line="${line%$'\r'}"
    if [ "$first" = true ]; then
      first=false
      if [ "$line" = "---" ]; then
        in_frontmatter=true
        continue
      fi
    elif [ "$in_frontmatter" = true ]; then
      if [ "$line" = "---" ]; then
        in_frontmatter=false
      fi
      continue
    fi
    [ "$line" = "$skill_marker" ]
    return
  done < "$1"
  return 1
}

skill_templates=()
for skill_template in "$repo_root"/.agents/host-templates/*-SKILL.md; do
  [ -f "$skill_template" ] || continue
  skill_name="${skill_template##*/}"
  skill_name="${skill_name%-SKILL.md}"
  case "$skill_name" in
    ""|-*|*-|*--*|*[!abcdefghijklmnopqrstuvwxyz0123456789-]*)
      die "skill template must be named <name>-SKILL.md with a lowercase hyphenated name: $skill_template"
      ;;
  esac
  skill_has_marker "$skill_template" \
    || die "skill template must carry the ownership marker as the first line after its frontmatter: $skill_template"
  skill_templates+=("$skill_template")
done

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

# ── Agent managed config (Claude config dirs + Codex AGENTS/config) ──────────
codex_home="${CODEX_HOME:-$HOME/.codex}"
[ "$warn_deprecated_codex_flag" = false ] || warn "--write-codex is deprecated; managed agent sync now runs by default."
python_bin="$(bash "$repo_root/scripts/find_python.sh" || true)"
if [ -n "$python_bin" ]; then
  claude_args=()
  # ${a[@]+...} keeps an empty array safe under `set -u` in bash 3.2 (macOS).
  for skill_template in ${skill_templates[@]+"${skill_templates[@]}"}; do
    claude_args+=(--claude-skill-template "$skill_template")
  done
  # Without an explicit list the engine discovers the config dirs itself.
  if [ "$claude_config_dirs_explicit" = true ]; then
    for claude_config_dir in "${claude_config_dirs[@]}"; do
      claude_args+=(--claude-config-dir "$claude_config_dir")
    done
  fi
  "$python_bin" "$repo_root/scripts/sync_codex_config.py" \
    --python "$python_bin" \
    --agents-template "$repo_root/.agents/host-templates/codex-AGENTS.md" \
    --hooks-template "$repo_root/.agents/host-templates/codex-hooks.toml" \
    --preferences-template "$repo_root/.agents/host-templates/codex-preferences.toml" \
    --status-script "$repo_root/scripts/workspace_status.py" \
    --claude-status-line-script "$repo_root/scripts/claude_status_line.py" \
    --codex-home "$codex_home" \
    ${claude_args[@]+"${claude_args[@]}"}
else
  warn "Python 3.11+ with tomllib is unavailable; skipped safe agent configuration synchronization"
  if [ "$claude_config_dirs_explicit" = false ]; then
    warn "config dir discovery needs Python; installing skills into ~/.claude only."
    warn "  Set CLAUDE_CONFIG_DIRS (colon-separated) to name every Claude config dir."
  fi
  for claude_config_dir in "${claude_config_dirs[@]}"; do
    for skill_template in ${skill_templates[@]+"${skill_templates[@]}"}; do
      skill_name="${skill_template##*/}"
      skill_name="${skill_name%-SKILL.md}"
      skill_file="$claude_config_dir/skills/$skill_name/SKILL.md"
      # A same-named skill without the marker belongs to its owner, as in
      # the sync engine; only a legacy unmarked env-sync is replaced.
      if [ -f "$skill_file" ] && ! skill_has_marker "$skill_file"; then
        case "$legacy_unmarked_skills" in
          *" $skill_name "*) ;;
          *)
            info "kept $skill_name skill owned outside workspace-meta: $skill_file"
            continue
            ;;
        esac
      fi
      mkdir -p "$(dirname "$skill_file")"
      if [ ! -f "$skill_file" ] || ! cmp -s "$skill_template" "$skill_file"; then
        cp "$skill_template" "$skill_file"
        info "installed $skill_name skill without agent configuration validation: $skill_file"
      else
        info "$skill_name skill already current: $skill_file"
      fi
    done
  done
fi
info "Bootstrap complete"

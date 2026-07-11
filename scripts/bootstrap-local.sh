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

Configures host-local workspace-meta integration (per-host; nothing here is
committed — the installer lives in the repo, the generated host files do not):
  - sets this repo's core.hooksPath to .githooks
  - checks global git identity without writing identity values
  - installs SessionStart hooks into ~/.claude/settings.json (jq) and prints/
    appends them for ~/.codex/config.toml:
      * workspace-meta freshness (governance rule layer behind origin/main)
      * env capability registry freshness (~/workspace/.agents/env/<host>.yml)
  - installs the env-sync skill (~/.claude/skills/) and the Codex global routing
    (~/.codex/AGENTS.md) from templates under .agents/host-templates/

Use --write-codex to append Codex TOML snippets when the corresponding hook is
not detected. Review/trust new hooks in Codex with /hooks afterwards.
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

# ── SessionStart hook commands ───────────────────────────────────────────────
# workspace-meta freshness: nudge when the governance rule layer is behind origin.
claude_fresh_cmd='behind=$(git -C "$HOME/workspace" fetch origin --quiet 2>/dev/null && git -C "$HOME/workspace" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n "$behind" ] && [ "$behind" -gt 0 ]; then printf '\''{"systemMessage":"workspace-meta: governance rule layer is %s commit(s) behind origin/main — run: git -C ~/workspace pull"}'\'' "$behind"; fi'
codex_fresh_cmd='behind=$(git -C "$HOME/workspace" fetch origin --quiet 2>/dev/null && git -C "$HOME/workspace" rev-list --count HEAD..origin/main 2>/dev/null); if [ -n "$behind" ] && [ "$behind" -gt 0 ]; then printf "workspace-meta: governance rule layer is %s commit(s) behind origin/main. Run: git -C ~/workspace pull\n" "$behind"; fi'
# env capability registry freshness: nudge when the per-host registry is stale/missing.
claude_env_cmd='out=$(bash "$HOME/workspace/scripts/env_probe.sh" --check 2>&1) || printf '\''{"systemMessage":%s,"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":%s}}'\'' "$(printf '\''%s'\'' "$out" | jq -Rs .)" "$(printf '\''%s — run: make -C ~/workspace env-probe (rule: ~/workspace/.agents/rules/environment-truth.md)'\'' "$out" | jq -Rs .)"'
codex_env_cmd='out=$(bash "$HOME/workspace/scripts/env_probe.sh" --check 2>&1) || printf "%s — run: make -C ~/workspace env-probe (rule: ~/workspace/.agents/rules/environment-truth.md)\n" "$out"'

# ── Claude Code hooks (~/.claude/settings.json via jq) ───────────────────────
claude_settings="$HOME/.claude/settings.json"

merge_claude_hook() {
  # $1 = unique marker substring (idempotency), $2 = command, $3 = statusMessage
  local marker="$1" command="$2" status="$3" tmp
  tmp="$(mktemp)"
  jq --arg command "$command" --arg status "$status" --arg marker "$marker" '
    if ((.hooks.SessionStart // []) | any(.[]?; ((.hooks // []) | any(.[]?; ((.command? // "") | contains($marker)))))) then
      .
    else
      .hooks = ((.hooks // {}) as $hooks | $hooks + {
        "SessionStart": (($hooks.SessionStart // []) + [{
          "hooks": [{
            "type": "command",
            "command": $command,
            "timeout": 15,
            "statusMessage": $status
          }]
        }])
      })
    end
  ' "$claude_settings" > "$tmp"
  jq -e . "$tmp" >/dev/null
  mv "$tmp" "$claude_settings"
  info "Claude hook ensured: $status"
}

if command -v jq >/dev/null 2>&1; then
  mkdir -p "$(dirname "$claude_settings")"
  [ -f "$claude_settings" ] || printf '{}\n' > "$claude_settings"
  merge_claude_hook "workspace-meta" "$claude_fresh_cmd" "Checking workspace-meta freshness"
  merge_claude_hook "env_probe" "$claude_env_cmd" "Checking host capability registry freshness"
else
  warn "jq is not installed; skipped Claude Code settings merge"
  warn "Install jq or add the README hook snippets to ~/.claude/settings.json manually."
fi

# ── Codex hooks (~/.codex/config.toml, TOML append) ──────────────────────────
codex_config="$HOME/.codex/config.toml"

install_codex_hook() {
  # $1 = grep marker (idempotency), $2 = command, $3 = statusMessage
  local marker="$1" command="$2" status="$3" snippet
  snippet="$(cat <<EOF
[[hooks.SessionStart]]
matcher = "startup|resume"

[[hooks.SessionStart.hooks]]
type = "command"
command = '$command'
timeout = 15
statusMessage = "$status"
EOF
)"
  if [ -f "$codex_config" ] && grep -Fq "$marker" "$codex_config"; then
    info "Codex hook present: $status"
  elif [ "$codex_write" = true ]; then
    mkdir -p "$(dirname "$codex_config")"
    { [ ! -s "$codex_config" ] || printf '\n'; printf '%s\n' "$snippet"; } >> "$codex_config"
    info "Codex hook appended: $status"
    warn "Open Codex /hooks and review/trust the new non-managed hook."
  else
    warn "Codex hook missing ($status); rerun with --write-codex or add manually:"
    printf '%s\n' "$snippet"
  fi
}

install_codex_hook "workspace-meta: governance rule layer" "$codex_fresh_cmd" "Checking workspace-meta freshness"
install_codex_hook "env_probe.sh" "$codex_env_cmd" "Checking host capability registry freshness"

# ── host templates (env-sync skill + Codex global routing) ───────────────────
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
install_template ".agents/host-templates/codex-AGENTS.md" "$HOME/.codex/AGENTS.md"

info "Bootstrap complete"

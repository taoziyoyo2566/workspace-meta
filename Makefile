.PHONY: bootstrap sync agent-sync-check docs-check env-probe env-probe-check test

# Python 3.11+ (tomllib) is required to run the sync script and tests. Discover one
# at parse time so a macOS system python3 (often 3.9 without tomllib) can't shadow a
# newer Homebrew python that sits later on PATH.
PYTHON ?= $(shell ./scripts/find_python.sh 2>/dev/null || printf python3)

# CLAUDE_CONFIG_DIRS: host-local, colon-separated (PATH-style) list of the
# Claude config dirs that receive the managed surfaces; names with spaces work.
# It is passed only when set. Unset, scripts/sync_codex_config.py discovers
# ~/.claude plus every ~/.claude-* dir holding a .claude.json and prints the
# list before any write. A copy of a relocated dir holds a .claude.json too, so
# discovery skips names that look like a copy or backup and prints each one;
# list a dir explicitly to manage it regardless of its name.
CLAUDE_CONFIG_DIRS_ARG = $(if $(strip $(CLAUDE_CONFIG_DIRS)),--claude-config-dirs '$(subst ','\'',$(CLAUDE_CONFIG_DIRS))')

# Each <name>-SKILL.md template installs as <claude dir>/skills/<name>/SKILL.md.
CLAUDE_SKILL_TEMPLATES = $(sort $(wildcard .agents/host-templates/*-SKILL.md))

AGENT_SYNC_COMMAND = "$(PYTHON)" scripts/sync_codex_config.py \
	--python "$(PYTHON)" \
	--agents-template .agents/host-templates/codex-AGENTS.md \
	--hooks-template .agents/host-templates/codex-hooks.toml \
	--preferences-template .agents/host-templates/codex-preferences.toml \
	--status-script scripts/workspace_status.py \
	--claude-status-line-script scripts/claude_status_line.py \
	--codex-home "$${CODEX_HOME:-$$HOME/.codex}" \
	$(foreach template,$(CLAUDE_SKILL_TEMPLATES),--claude-skill-template "$(template)") \
	$(CLAUDE_CONFIG_DIRS_ARG)

# make exports a CLAUDE_CONFIG_DIRS set on its command line or in the
# environment, so the bootstrap reads the same list or discovers the same dirs.
bootstrap:
	./scripts/bootstrap-local.sh

sync: ## Inspect, confirm, and synchronize workspace-meta-managed host configuration
	@$(AGENT_SYNC_COMMAND) --interactive

agent-sync-check: ## Report host Claude/Codex managed-config drift without writing files
	@$(AGENT_SYNC_COMMAND) --check

env-probe: ## Probe this host's capabilities into .agents/env/<host>.yml (rule: .agents/rules/environment-truth.md)
	@bash scripts/env_probe.sh

env-probe-check: ## Fail if this host's capability registry is missing or stale (TTL 7d; override ENV_PROBE_TTL_DAYS=N)
	@bash scripts/env_probe.sh --check

docs-check: ## Validate workspace-meta documentation structure and routes
	@"$(PYTHON)" scripts/check_documentation.py

test: docs-check ## Run workspace-meta regression tests
	@"$(PYTHON)" -m unittest discover -s tests -v

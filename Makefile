.PHONY: bootstrap sync agent-sync-check docs-check env-probe env-probe-check test

# Python 3.11+ (tomllib) is required to run the sync script and tests. Discover one
# at parse time so a macOS system python3 (often 3.9 without tomllib) can't shadow a
# newer Homebrew python that sits later on PATH.
PYTHON ?= $(shell ./scripts/find_python.sh 2>/dev/null || printf python3)

AGENT_SYNC_COMMAND = "$(PYTHON)" scripts/sync_codex_config.py \
	--python "$(PYTHON)" \
	--agents-template .agents/host-templates/codex-AGENTS.md \
	--hooks-template .agents/host-templates/codex-hooks.toml \
	--preferences-template .agents/host-templates/codex-preferences.toml \
	--status-script scripts/workspace_status.py \
	--claude-status-line-script scripts/claude_status_line.py \
	--env-skill-template .agents/host-templates/env-sync-SKILL.md \
	--codex-home "$${CODEX_HOME:-$$HOME/.codex}" \
	--claude-settings "$$HOME/.claude/settings.json" \
	--env-skill "$$HOME/.claude/skills/env-sync/SKILL.md"

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

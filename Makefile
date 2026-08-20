.PHONY: bootstrap agent-sync-check env-probe env-probe-check test

# Python 3.11+ (tomllib) is required to run the sync script and tests. Discover one
# at parse time so a macOS system python3 (often 3.9 without tomllib) can't shadow a
# newer Homebrew python that sits later on PATH.
PYTHON ?= $(shell ./scripts/find_python.sh 2>/dev/null || printf python3)

bootstrap:
	./scripts/bootstrap-local.sh

agent-sync-check: ## Report host Claude/Codex managed-config drift without writing files
	@"$(PYTHON)" scripts/sync_codex_config.py \
		--python "$(PYTHON)" \
		--agents-template .agents/host-templates/codex-AGENTS.md \
		--hooks-template .agents/host-templates/codex-hooks.toml \
		--preferences-template .agents/host-templates/codex-preferences.toml \
		--status-script scripts/workspace_status.py \
		--codex-home "$${CODEX_HOME:-$$HOME/.codex}" \
		--claude-settings "$$HOME/.claude/settings.json" \
		--check

env-probe: ## Probe this host's capabilities into .agents/env/<host>.yml (rule: .agents/rules/environment-truth.md)
	@bash scripts/env_probe.sh

env-probe-check: ## Fail if this host's capability registry is missing or stale (TTL 7d; override ENV_PROBE_TTL_DAYS=N)
	@bash scripts/env_probe.sh --check

test: ## Run workspace-meta regression tests
	@"$(PYTHON)" -m unittest discover -s tests -v

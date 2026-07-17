.PHONY: bootstrap agent-sync-check env-probe env-probe-check test

bootstrap:
	./scripts/bootstrap-local.sh

agent-sync-check: ## Report host Claude/Codex managed-config drift without writing files
	@python3 scripts/sync_codex_config.py \
		--agents-template .agents/host-templates/codex-AGENTS.md \
		--hooks-template .agents/host-templates/codex-hooks.toml \
		--status-script scripts/workspace_status.py \
		--codex-home "$${CODEX_HOME:-$$HOME/.codex}" \
		--claude-settings "$$HOME/.claude/settings.json" \
		--check

env-probe: ## Probe this host's capabilities into .agents/env/<host>.yml (rule: .agents/rules/environment-truth.md)
	@bash scripts/env_probe.sh

env-probe-check: ## Fail if this host's capability registry is missing or stale (TTL 7d; override ENV_PROBE_TTL_DAYS=N)
	@bash scripts/env_probe.sh --check

test: ## Run workspace-meta regression tests
	@python3 -m unittest discover -s tests -v

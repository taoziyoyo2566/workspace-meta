.PHONY: bootstrap env-probe env-probe-check

bootstrap:
	./scripts/bootstrap-local.sh

env-probe: ## Probe this host's capabilities into .agents/env/<host>.yml (rule: .agents/rules/environment-truth.md)
	@bash scripts/env_probe.sh

env-probe-check: ## Fail if this host's capability registry is missing or stale (TTL 7d; override ENV_PROBE_TTL_DAYS=N)
	@bash scripts/env_probe.sh --check

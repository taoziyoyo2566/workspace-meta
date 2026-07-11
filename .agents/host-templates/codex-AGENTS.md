# Global Codex guidance (host: all projects)

Keep this minimal — a routing pointer, not a governance file. Per-project
`AGENTS.md` and repo `.agents/` remain the detailed truth for each project.

## Environment capabilities — probe, don't recall

Environment capability claims (tool present/absent, daemon up, creds) are dated
snapshots, not invariants. Before such a claim becomes load-bearing (a plan
pre-condition, a "blocked" verdict, a skipped check), consult the shared per-host
registry instead of re-deriving probes ad hoc or trusting memory:

- **Registry**: `~/workspace/.agents/env/<hostname -s>.yml`
- **Refresh**: `make -C ~/workspace env-probe` · **freshness gate**: `make -C ~/workspace env-probe-check`
- **Behavior rule**: `~/workspace/.agents/rules/environment-truth.md`

A SessionStart hook (`~/.codex/config.toml`) runs the freshness check
automatically and nudges when the registry is missing/stale.

Host-bare tool absence is expected when a project provides a tool via its own
venv (e.g. ansible/yamllint under `.venv/bin/`): the registry is honest about the
bare host PATH, and each project's `.agents/env/README.md` carries its venv-tool
overrides. Do not read a host-level `available: false` as "cannot run it here."

# Plan: Make Python Discovery Portable

## Goal

Allow workspace-meta's Python 3.11+ tooling to work when macOS system
`python3` is older than a Homebrew or otherwise available interpreter, while
keeping the existing synchronization flow and host-configuration boundaries.

## Scope

- Make `scripts/find_python.sh` return a stable executable path.
- Quote the selected interpreter when embedding it in SessionStart commands.
- Ensure tests use the interpreter running the test suite.
- Update direct verification/onboarding commands to use the resolver.
- Add focused regression coverage for discovery and generated commands.

## Exclusions

- No Windows-native launcher or shell-portability redesign.
- No changes to Codex/Claude ownership, hook semantics, or host-file migration.
- No Git staging, commit, push, or host bootstrap execution.

## Verification

- `make test`
- `bash -n scripts/*.sh .githooks/pre-commit`
- resolved-Python `py_compile`
- TOML/JSON parsing through the existing test suite
- `git diff --check`
- focused discovery and shell-command smoke checks

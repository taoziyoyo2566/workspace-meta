#!/usr/bin/env bash
# find_python.sh — locate a Python interpreter that can run workspace-meta tooling
# (needs `tomllib`, i.e. Python 3.11+). Prefers an explicit override, then `python3`
# on PATH, then known macOS Homebrew locations (Apple Silicon /opt/homebrew, Intel
# /usr/local), then versioned names. Prints the selected interpreter to stdout and
# exits 0; exits 1 when none is found.
#
# Behavior rule: .agents/rules/environment-truth.md (probe, don't recall). Both the
# bootstrap and the Makefile call this so a macOS system python3 (often 3.9 without
# tomllib) never shadows a newer Homebrew python that sits later on PATH.

set -euo pipefail

candidates=(
  "${WORKSPACE_META_PYTHON:-}"
  "python3"
  "/opt/homebrew/bin/python3"
  "/usr/local/bin/python3"
  "/opt/homebrew/bin/python3.11" "/opt/homebrew/bin/python3.12" "/opt/homebrew/bin/python3.13" "/opt/homebrew/bin/python3.14"
  "/usr/local/bin/python3.11" "/usr/local/bin/python3.12" "/usr/local/bin/python3.13" "/usr/local/bin/python3.14"
  "python3.11" "python3.12" "python3.13" "python3.14"
)

for candidate in "${candidates[@]}"; do
  [ -n "$candidate" ] || continue
  if "$candidate" -c 'import tomllib' >/dev/null 2>&1; then
    resolved="$(command -v "$candidate" 2>/dev/null || true)"
    if [ -n "$resolved" ]; then
      printf '%s\n' "$resolved"
    else
      # An absolute candidate may not be reported by command -v on every shell.
      printf '%s\n' "$candidate"
    fi
    exit 0
  fi
done

exit 1

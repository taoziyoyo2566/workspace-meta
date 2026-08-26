#!/usr/bin/env python3
"""Render the workspace-meta Claude Code status line from its stdin payload."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any


RESET = "\033[0m"
DIR_COLOR = "\033[38;5;31m"
BRANCH_COLOR = "\033[38;5;76m"
MODEL_COLOR = "\033[38;5;66m"
DIM_COLOR = "\033[38;5;243m"
COST_COLOR = "\033[38;5;71m"
CTX_GREEN = "\033[38;5;76m"
CTX_YELLOW = "\033[38;5;178m"
CTX_RED = "\033[38;5;160m"


def shorten_home(path: str, home: str) -> str:
    if path == home:
        return "~"
    prefix = home.rstrip("/") + "/"
    if home and path.startswith(prefix):
        return "~/" + path[len(prefix) :]
    return path


def git_branch(cwd: str) -> str:
    if not cwd:
        return ""
    try:
        completed = subprocess.run(
            [
                "git",
                "-c",
                "core.fsmonitor=false",
                "--no-optional-locks",
                "-C",
                cwd,
                "symbolic-ref",
                "--short",
                "HEAD",
            ],
            check=False,
            capture_output=True,
            text=True,
            timeout=0.5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return completed.stdout.strip() if completed.returncode == 0 else ""


def format_tokens(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return "0"
    if value >= 1_000_000:
        return f"{value / 1_000_000:.2f}M"
    if value >= 1_000:
        return f"{value / 1_000:.1f}k"
    return str(int(value))


def _number(value: Any) -> float | None:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return float(value)


def render(payload: dict[str, Any], *, home: str, color: bool = True) -> str:
    workspace = payload.get("workspace")
    workspace = workspace if isinstance(workspace, dict) else {}
    cwd_value = workspace.get("current_dir") or payload.get("cwd") or ""
    cwd = cwd_value if isinstance(cwd_value, str) else ""

    model_data = payload.get("model")
    model_data = model_data if isinstance(model_data, dict) else {}
    model_value = model_data.get("display_name") or model_data.get("id") or "unknown"
    model = model_value if isinstance(model_value, str) else "unknown"

    context = payload.get("context_window")
    context = context if isinstance(context, dict) else {}
    used = _number(context.get("used_percentage"))
    usage = context.get("current_usage")
    usage = usage if isinstance(usage, dict) else None

    cost_data = payload.get("cost")
    cost_data = cost_data if isinstance(cost_data, dict) else {}
    cost = _number(cost_data.get("total_cost_usd"))

    colors = {
        "reset": RESET,
        "dir": DIR_COLOR,
        "branch": BRANCH_COLOR,
        "model": MODEL_COLOR,
        "dim": DIM_COLOR,
        "cost": COST_COLOR,
    }
    if not color:
        colors = {key: "" for key in colors}

    parts = [f"{colors['dir']}{shorten_home(cwd, home)}{colors['reset']}"]
    branch = git_branch(cwd)
    if branch:
        parts.append(f"{colors['branch']}{branch}{colors['reset']}")
    parts.append(f"{colors['model']}{model}{colors['reset']}")

    if used is not None:
        used_int = round(used)
        ctx_color = CTX_RED if used_int >= 80 else CTX_YELLOW if used_int >= 60 else CTX_GREEN
        if not color:
            ctx_color = ""
        parts.append(f"{ctx_color}ctx:{used_int}%{colors['reset']}")

    if usage is not None:
        token_text = " ".join(
            (
                f"in:{format_tokens(usage.get('input_tokens', 0))}",
                f"cw:{format_tokens(usage.get('cache_creation_input_tokens', 0))}",
                f"cr:{format_tokens(usage.get('cache_read_input_tokens', 0))}",
                f"out:{format_tokens(usage.get('output_tokens', 0))}",
            )
        )
        parts.append(f"{colors['dim']}{token_text}{colors['reset']}")

    if cost is not None:
        parts.append(f"{colors['cost']}~${cost:.3f}{colors['reset']}")

    return "  ".join(parts)


def main() -> int:
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return 0
    if not isinstance(payload, dict):
        return 0
    color = "NO_COLOR" not in os.environ and os.environ.get("TERM") != "dumb"
    output = render(payload, home=os.path.expanduser("~"), color=color)
    if output:
        print(output, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

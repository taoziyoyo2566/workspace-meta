#!/usr/bin/env python3
"""Render the workspace-meta Claude Code status line from its stdin payload."""

from __future__ import annotations

import datetime
import json
import math
import os
import subprocess
import sys
import time
from typing import Any


RESET = "\033[0m"
# PS1-style bold colors, matching bash's default color prompt
# (`\[\033[01;32m\]\u@\h ... \[\033[01;34m\]\w`): bold-blue for the directory,
# bold-green for the git branch, joined with ":" the way PS1 joins host and
# cwd. All existing fields (dir, branch, model, context, tokens, cost) are
# still rendered -- only the coloring/format changed.
DIR_COLOR = "\033[01;34m"
BRANCH_COLOR = "\033[01;32m"
MODEL_COLOR = "\033[38;5;66m"
DIM_COLOR = "\033[38;5;243m"
COST_COLOR = "\033[38;5;71m"
# Shared by every 0-100 gauge on the line: the context window and the rolling
# five-hour usage window. Both are keyed on the used fraction, so a full gauge
# is red whether the line displays used or remaining.
LEVEL_GREEN = "\033[38;5;76m"
LEVEL_YELLOW = "\033[38;5;178m"
LEVEL_RED = "\033[38;5;160m"


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
    number = float(value)
    # NaN and infinity pass the isinstance check but raise in round(), which
    # would drop the whole status line. A gauge has no value for them, so the
    # caller omits its segment instead.
    return number if math.isfinite(number) else None


def _now() -> float:
    """Indirection so tests can pin the clock."""
    return time.time()


def level_color(severity: float) -> str:
    """Pick a gauge colour from a 0-100 value where higher is worse."""
    if severity >= 80:
        return LEVEL_RED
    if severity >= 60:
        return LEVEL_YELLOW
    return LEVEL_GREEN


def reset_epoch(value: Any) -> float | None:
    """Claude Code 2.1.236 sends epoch seconds; its usage API sends ISO 8601."""
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return _number(value)
    if isinstance(value, str) and value:
        try:
            parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=datetime.timezone.utc)
        return parsed.timestamp()
    return None


def format_countdown(seconds: float) -> str:
    total = int(seconds)
    if total <= 0:
        return ""
    hours, remainder = divmod(total, 3600)
    minutes = remainder // 60
    if hours:
        return f"{hours}h{minutes:02d}m"
    return f"{minutes}m" if minutes else "<1m"


def five_hour_segment(payload: dict[str, Any]) -> tuple[str, float] | None:
    """Return the rendered five-hour window text and the used share it shows."""
    limits = payload.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    window = limits.get("five_hour")
    if not isinstance(window, dict):
        return None
    used = _number(window.get("used_percentage"))
    if used is None:
        return None
    remaining = max(0, min(100, round(100 - used)))
    # Key the gauge on the complement of the printed number, for the same
    # reason the context gauge rounds first: a printed "5h:20%" must colour as
    # 80% used, not as the unrounded 79.5 that produced it.
    used_share = float(100 - remaining)
    text = f"5h:{remaining}%"
    resets_at = reset_epoch(window.get("resets_at"))
    if resets_at is not None:
        countdown = format_countdown(resets_at - _now())
        if countdown:
            text += f"({countdown})"
    return text, used_share


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

    dir_text = f"{colors['dir']}{shorten_home(cwd, home)}{colors['reset']}"
    branch = git_branch(cwd)
    if branch:
        # PS1-style separator: bold-blue cwd + ":" + bold-green branch,
        # mirroring PS1's bold-green "\u@\h" : bold-blue "\w".
        parts = [f"{dir_text}:{colors['branch']}{branch}{colors['reset']}"]
    else:
        parts = [dir_text]
    parts.append(f"{colors['model']}{model}{colors['reset']}")

    if used is not None:
        # Colour from the value the line actually prints, so "ctx:80%" is never
        # yellow: thresholding the unrounded fraction would disagree with the
        # rounded label between 79.5 and 80.
        used_int = round(used)
        ctx_color = level_color(used_int) if color else ""
        parts.append(f"{ctx_color}ctx:{used_int}%{colors['reset']}")

    five_hour = five_hour_segment(payload)
    if five_hour is not None:
        text, used_share = five_hour
        limit_color = level_color(used_share) if color else ""
        parts.append(f"{limit_color}{text}{colors['reset']}")

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

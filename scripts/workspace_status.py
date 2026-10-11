#!/usr/bin/env python3
"""Evaluate workspace-meta sync state for Claude and Codex SessionStart hooks."""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
import json
import os
from pathlib import Path
import select
import stat
import subprocess
import sys
import tempfile
import time
from typing import Callable, Sequence


CACHE_SCHEMA = 1
DEFAULT_FETCH_MIN_INTERVAL = 300
DEFAULT_REMOTE_WARNING_TTL = 86400
DEFAULT_FETCH_TIMEOUT = 8
DEFAULT_COMMAND_TIMEOUT = 5
DEFAULT_TEMP_USED_PERCENT = 80
DEFAULT_TEMP_MIN_FREE_MB = 256
HOOK_INPUT_TIMEOUT = 1.0
HOOK_INPUT_LIMIT = 65536


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""
    timed_out: bool = False


@dataclass(frozen=True)
class StatusConfig:
    workspace: Path
    cache_file: Path
    fetch_min_interval: int = DEFAULT_FETCH_MIN_INTERVAL
    remote_warning_ttl: int = DEFAULT_REMOTE_WARNING_TTL
    fetch_timeout: int = DEFAULT_FETCH_TIMEOUT
    command_timeout: int = DEFAULT_COMMAND_TIMEOUT
    temp_root: Path | None = None
    temp_used_percent: int = DEFAULT_TEMP_USED_PERCENT
    temp_min_free_mb: int = DEFAULT_TEMP_MIN_FREE_MB


@dataclass
class StatusEvaluation:
    messages: list[str]
    cache: dict[str, int]
    cache_changed: bool
    # Messages the agent must also see; every entry is in messages too.
    context: list[str] = field(default_factory=list)


Runner = Callable[[Sequence[str], int], CommandResult]
StatVfs = Callable[[str], os.statvfs_result]


def run_command(argv: Sequence[str], timeout: int) -> CommandResult:
    env = os.environ.copy()
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        completed = subprocess.run(
            list(argv),
            capture_output=True,
            check=False,
            env=env,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        return CommandResult(
            returncode=124,
            stdout=exc.stdout or "",
            stderr=exc.stderr or "",
            timed_out=True,
        )
    except OSError as exc:
        return CommandResult(returncode=127, stderr=str(exc))
    return CommandResult(completed.returncode, completed.stdout, completed.stderr)


def load_cache(path: Path) -> dict[str, int]:
    try:
        parsed = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, OSError, json.JSONDecodeError):
        return {}
    if not isinstance(parsed, dict) or parsed.get("schema") != CACHE_SCHEMA:
        return {}
    result: dict[str, int] = {"schema": CACHE_SCHEMA}
    for key in ("last_remote_success", "last_remote_warning"):
        value = parsed.get(key)
        if isinstance(value, int) and value >= 0:
            result[key] = value
    return result


def atomic_write_json(path: Path, payload: dict[str, int]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            json.dump(payload, handle, sort_keys=True)
            handle.write("\n")
        os.chmod(tmp_path, mode)
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def read_hook_input(stream, timeout: float = HOOK_INPUT_TIMEOUT) -> dict:
    """Return the hook's JSON input, or {} when there is none to read in time."""
    # A closed stdin is None; a terminal or a pipe that never reaches EOF must
    # not hold up session start.
    if stream is None:
        return {}
    try:
        if stream.isatty():
            return {}
        fd = stream.fileno()
        deadline = time.monotonic() + timeout
        data = b""
        while len(data) < HOOK_INPUT_LIMIT:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return {}
            ready, _, _ = select.select([fd], [], [], remaining)
            if not ready:
                return {}
            chunk = os.read(fd, HOOK_INPUT_LIMIT - len(data))
            if not chunk:
                break
            data += chunk
        parsed = json.loads(data.decode("utf-8") or "{}")
    except (AttributeError, OSError, ValueError):
        return {}
    return parsed if isinstance(parsed, dict) else {}


def choose_temp_root(hook_input: dict, environ: dict[str, str]) -> Path:
    scratch = hook_input.get("scratchpad_dir")
    if isinstance(scratch, str) and scratch:
        return Path(scratch)
    return Path(environ.get("TMPDIR") or "/tmp")


def temp_space_message(
    root: Path, used_percent: int, min_free_mb: int, statvfs: StatVfs
) -> str | None:
    # The scratch directory may not exist yet; its filesystem is the nearest
    # existing ancestor's.
    path = root
    while not path.exists() and path != path.parent:
        path = path.parent
    try:
        result = statvfs(str(path))
    except OSError:
        return f"temporary space at {root} could not be measured"
    used = (result.f_blocks - result.f_bfree) * result.f_frsize
    free = result.f_bavail * result.f_frsize
    if used + free <= 0:
        return None
    percent = used * 100 // (used + free)
    free_mb = free // (1024 * 1024)
    if percent < used_percent and free_mb >= min_free_mb:
        return None
    return (
        f"temporary space at {root} is {percent}% used ({free_mb} MiB free); "
        "follow ~/workspace/.agents/rules/temporary-files.md"
    )


def parse_count(result: CommandResult) -> int | None:
    if result.returncode != 0:
        return None
    try:
        value = int(result.stdout.strip())
    except ValueError:
        return None
    return value if value >= 0 else None


def evaluate_status(
    config: StatusConfig,
    *,
    runner: Runner = run_command,
    now: int | None = None,
    initial_cache: dict[str, int] | None = None,
    statvfs: StatVfs = os.statvfs,
) -> StatusEvaluation:
    current_time = int(time.time()) if now is None else now
    original_cache = dict(initial_cache if initial_cache is not None else load_cache(config.cache_file))
    cache = {"schema": CACHE_SCHEMA, **original_cache}
    messages: list[str] = []
    context: list[str] = []

    git = ["git", "-C", str(config.workspace)]
    status = runner([*git, "status", "--porcelain"], config.command_timeout)
    repo_available = status.returncode == 0
    dirty = repo_available and bool(status.stdout.strip())
    if not repo_available:
        messages.append("repository status is unavailable")

    remote_known = False
    if repo_available:
        last_success = cache.get("last_remote_success")
        fetch_due = last_success is None or current_time - last_success >= config.fetch_min_interval
        if fetch_due:
            fetch = runner(
                [*git, "fetch", "--quiet", "--no-tags", "origin"],
                config.fetch_timeout,
            )
            if fetch.returncode == 0:
                cache["last_remote_success"] = current_time
                cache.pop("last_remote_warning", None)
                remote_known = True
            else:
                last_warning = cache.get("last_remote_warning")
                if (
                    last_warning is None
                    or current_time - last_warning >= config.remote_warning_ttl
                ):
                    messages.append("remote freshness is unknown; check network and authentication")
                    cache["last_remote_warning"] = current_time
        else:
            remote_known = True

    behind: int | None = None
    ahead: int | None = None
    if repo_available:
        behind = parse_count(
            runner([*git, "rev-list", "--count", "HEAD..origin/main"], config.command_timeout)
        )
        ahead = parse_count(
            runner([*git, "rev-list", "--count", "origin/main..HEAD"], config.command_timeout)
        )
        if remote_known and (behind is None or ahead is None):
            last_warning = cache.get("last_remote_warning")
            if (
                last_warning is None
                or current_time - last_warning >= config.remote_warning_ttl
            ):
                messages.append("origin/main is unavailable; sync state is unknown")
                cache["last_remote_warning"] = current_time
        if behind is not None and behind > 0:
            messages.append("governance is behind origin/main; run: git -C ~/workspace pull")
        if dirty or (ahead is not None and ahead > 0):
            messages.append(
                "governance has uncommitted or unpushed changes; run: git -C ~/workspace status"
            )

    env_check = runner(
        ["bash", str(config.workspace / "scripts" / "env_probe.sh"), "--check"],
        config.command_timeout,
    )
    if env_check.returncode != 0:
        messages.append(
            "host capability registry is missing or stale; run: make -C ~/workspace env-probe"
        )

    if config.temp_root is not None:
        temp_message = temp_space_message(
            config.temp_root,
            config.temp_used_percent,
            config.temp_min_free_mb,
            statvfs,
        )
        if temp_message:
            messages.append(temp_message)
            context.append(temp_message)

    return StatusEvaluation(
        messages=messages,
        cache=cache,
        cache_changed=cache != original_cache,
        context=context,
    )


def default_cache_file() -> Path:
    base = Path(os.environ.get("XDG_CACHE_HOME", Path.home() / ".cache"))
    return base / "workspace-meta" / "status.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", choices=("claude", "codex"), required=True)
    parser.add_argument("--workspace", type=Path, default=Path.home() / "workspace")
    parser.add_argument("--cache-file", type=Path, default=default_cache_file())
    parser.add_argument("--fetch-min-interval", type=int, default=DEFAULT_FETCH_MIN_INTERVAL)
    parser.add_argument("--remote-warning-ttl", type=int, default=DEFAULT_REMOTE_WARNING_TTL)
    parser.add_argument("--fetch-timeout", type=int, default=DEFAULT_FETCH_TIMEOUT)
    parser.add_argument("--temp-used-percent", type=int, default=DEFAULT_TEMP_USED_PERCENT)
    parser.add_argument("--temp-min-free-mb", type=int, default=DEFAULT_TEMP_MIN_FREE_MB)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    config = StatusConfig(
        workspace=args.workspace,
        cache_file=args.cache_file,
        fetch_min_interval=max(0, args.fetch_min_interval),
        remote_warning_ttl=max(0, args.remote_warning_ttl),
        fetch_timeout=max(1, args.fetch_timeout),
        temp_root=choose_temp_root(read_hook_input(sys.stdin), dict(os.environ)),
        temp_used_percent=args.temp_used_percent,
        temp_min_free_mb=max(0, args.temp_min_free_mb),
    )
    evaluation = evaluate_status(config)
    if evaluation.cache_changed:
        try:
            atomic_write_json(config.cache_file, evaluation.cache)
        except OSError:
            evaluation.messages.append("status cache is unavailable")
    if evaluation.messages:
        payload: dict[str, object] = {
            "systemMessage": "workspace-meta: " + "; ".join(evaluation.messages)
        }
        if evaluation.context:
            payload["hookSpecificOutput"] = {
                "hookEventName": "SessionStart",
                "additionalContext": "workspace-meta: " + "; ".join(evaluation.context),
            }
        print(json.dumps(payload, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

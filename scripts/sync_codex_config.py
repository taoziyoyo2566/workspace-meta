#!/usr/bin/env python3
"""Synchronize workspace-meta-owned guidance and hooks into host agent config."""

from __future__ import annotations

import argparse
from collections import namedtuple
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import sys
import tempfile
import tomllib


AGENTS_BEGIN = "<!-- BEGIN workspace-meta managed Codex guidance -->"
AGENTS_END = "<!-- END workspace-meta managed Codex guidance -->"
HOOKS_BEGIN = "# BEGIN workspace-meta managed Codex hooks"
HOOKS_END = "# END workspace-meta managed Codex hooks"
COMMAND_PLACEHOLDER = "__WORKSPACE_META_STATUS_COMMAND__"
MANAGED_HOOK_MARKER = "workspace-meta-managed-status-v1"
LEGACY_AGENTS_SHA256 = "d0894e6420d4d168e08984172b2f3a22b2edc375fb6ea9f2404274c38771bbc2"
LEGACY_HOOK_MARKERS = (
    "workspace-meta: governance rule layer",
    "env_probe.sh",
    "unpushed commit",
)


class SyncError(RuntimeError):
    pass


HookRenderResult = namedtuple(
    "HookRenderResult",
    ("content", "action", "definition_changed", "state_normalized"),
)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    existing_mode = stat.S_IMODE(path.stat().st_mode) if path.exists() else 0o600
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
        os.chmod(tmp_path, existing_mode)
        os.replace(tmp_path, path)
    finally:
        tmp_path.unlink(missing_ok=True)


def validate_marked_template(content: str, begin: str, end: str, label: str) -> str:
    if content.count(begin) != 1 or content.count(end) != 1:
        raise SyncError(f"{label} template must contain exactly one managed block")
    if content.index(begin) >= content.index(end):
        raise SyncError(f"{label} managed block markers are reversed")
    return content.strip() + "\n"


def replace_marked_block(current: str, managed: str, begin: str, end: str) -> str:
    if current.count(begin) != 1 or current.count(end) != 1:
        raise SyncError("destination has incomplete or duplicate managed block markers")
    start = current.index(begin)
    finish = current.index(end, start) + len(end)
    prefix = current[:start].rstrip()
    suffix = current[finish:].strip()
    pieces = [piece for piece in (prefix, managed.strip(), suffix) if piece]
    return "\n\n".join(pieces) + "\n"


def render_agents(template_path: Path, destination: Path) -> tuple[str, str]:
    managed = validate_marked_template(
        read_text(template_path), AGENTS_BEGIN, AGENTS_END, "AGENTS"
    )
    current = read_text(destination)
    if not current:
        return managed, "installed"
    if AGENTS_BEGIN in current or AGENTS_END in current:
        result = replace_marked_block(current, managed, AGENTS_BEGIN, AGENTS_END)
        return result, "already current" if result == current else "updated"
    if hashlib.sha256(current.encode()).hexdigest() == LEGACY_AGENTS_SHA256:
        return managed, "migrated legacy file"
    return (
        current.rstrip() + "\n\n" + managed,
        "appended managed block; preserved existing unmanaged guidance",
    )


def build_status_command(agent: str, status_script: Path) -> str:
    digest = hashlib.sha256(status_script.read_bytes()).hexdigest()
    return (
        'p="$HOME/workspace/scripts/workspace_status.py"; '
        f'expected="{digest}"; '
        "actual=$(python3 -c 'import hashlib,sys; "
        'print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())\' '
        '"$p" 2>/dev/null || printf unavailable); '
        'if [ "$actual" != "$expected" ]; then '
        "printf '{\"systemMessage\":\"workspace-meta status evaluator changed or "
        "is unavailable. Run: make -C ~/workspace bootstrap\"}\\n'; "
        f'else python3 "$p" --agent {agent}; fi; : {MANAGED_HOOK_MARKER}'
    )


def session_start_groups(content: str) -> list[tuple[int, int]]:
    lines = content.splitlines(keepends=True)
    starts = [
        index
        for index, line in enumerate(lines)
        if line.strip() == "[[hooks.SessionStart]]"
    ]
    groups: list[tuple[int, int]] = []
    for start in starts:
        end = len(lines)
        for index in range(start + 1, len(lines)):
            stripped = lines[index].strip()
            if not stripped.startswith("["):
                continue
            if stripped == "[[hooks.SessionStart.hooks]]":
                continue
            end = index
            break
        groups.append((start, end))
    return groups


def remove_legacy_hooks(content: str) -> tuple[str, int]:
    lines = content.splitlines(keepends=True)
    removable: list[tuple[int, int]] = []
    ownership_markers = (*LEGACY_HOOK_MARKERS, MANAGED_HOOK_MARKER)
    for start, end in session_start_groups(content):
        group = "".join(lines[start:end])
        command_lines = [
            line for line in group.splitlines() if re.match(r"^\s*command\s*=", line)
        ]
        owned = [
            line
            for line in command_lines
            if any(marker in line for marker in ownership_markers)
        ]
        if owned and len(owned) != len(command_lines):
            raise SyncError(
                "workspace-meta hook shares a SessionStart group with an unmanaged "
                "hook; split it manually before bootstrap"
            )
        if owned:
            removable.append((start, end))

    for start, end in reversed(removable):
        del lines[start:end]
    return "".join(lines), len(removable)


def insert_before_hook_state(content: str, managed: str) -> str:
    if not content.strip():
        return managed.strip() + "\n"
    match = re.search(r"(?m)^\[hooks\.state(?:\]|\.)", content)
    if not match:
        return content.rstrip() + "\n\n" + managed.strip() + "\n"
    prefix = content[: match.start()].rstrip()
    suffix = content[match.start() :].strip()
    pieces = [piece for piece in (prefix, managed.strip(), suffix) if piece]
    return "\n\n".join(pieces) + "\n"


def replace_hook_managed_block(
    current: str, managed: str
) -> tuple[str, bool, bool]:
    """Replace the workspace hook while preserving Codex-owned hook state.

    Codex may insert ``[hooks.state]`` before the closing marker of an inline
    managed block.  That state is host-owned and must survive synchronization;
    normalize it after the marker so the managed boundary remains stable.
    """

    if current.count(HOOKS_BEGIN) != 1 or current.count(HOOKS_END) != 1:
        raise SyncError("destination has incomplete or duplicate managed block markers")
    start = current.index(HOOKS_BEGIN)
    finish = current.index(HOOKS_END, start) + len(HOOKS_END)
    block = current[start:finish]
    state_match = re.search(r"(?m)^\[hooks\.state(?:\]|\.)", block)
    preserved_state = ""
    managed_definition = block
    if state_match:
        state_end = block.rfind(HOOKS_END)
        preserved_state = block[state_match.start():state_end].strip()
        managed_definition = (
            block[: state_match.start()].rstrip() + "\n" + HOOKS_END
        )

    prefix = current[:start].rstrip()
    suffix = current[finish:].strip()
    pieces = [piece for piece in (prefix, managed.strip(), preserved_state, suffix) if piece]
    return (
        "\n\n".join(pieces) + "\n",
        bool(preserved_state),
        managed_definition.strip() != managed.strip(),
    )


def render_hooks(
    template_path: Path, destination: Path, status_script: Path
) -> HookRenderResult:
    template = read_text(template_path)
    if template.count(COMMAND_PLACEHOLDER) != 1:
        raise SyncError("Codex hook template must contain one status-command placeholder")
    template = template.replace(
        COMMAND_PLACEHOLDER, build_status_command("codex", status_script)
    )
    managed = validate_marked_template(template, HOOKS_BEGIN, HOOKS_END, "hooks")
    current = read_text(destination)
    normalized_state = False
    definition_changed = False
    if HOOKS_BEGIN in current or HOOKS_END in current:
        result, normalized_state, definition_changed = replace_hook_managed_block(
            current, managed
        )
        migrated = 0
    else:
        without_legacy, migrated = remove_legacy_hooks(current)
        result = insert_before_hook_state(without_legacy, managed)
        definition_changed = result != current

    try:
        tomllib.loads(result)
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"refusing to write invalid Codex TOML: {exc}") from exc

    if result == current:
        return HookRenderResult(result, "already current", False, False)
    if migrated:
        return HookRenderResult(
            result,
            f"updated; migrated {migrated} legacy hook group(s)",
            definition_changed,
            normalized_state,
        )
    if normalized_state:
        action = (
            "updated; normalized Codex hook state"
            if definition_changed
            else "normalized Codex hook state"
        )
        return HookRenderResult(result, action, definition_changed, normalized_state)
    return HookRenderResult(result, "installed or updated", definition_changed, False)


def hook_commands(group: object) -> list[str]:
    if not isinstance(group, dict):
        raise SyncError("Claude SessionStart groups must be JSON objects")
    handlers = group.get("hooks", [])
    if not isinstance(handlers, list):
        raise SyncError("Claude SessionStart hooks must be a JSON array")
    commands: list[str] = []
    for handler in handlers:
        if not isinstance(handler, dict):
            raise SyncError("Claude hook handlers must be JSON objects")
        command = handler.get("command", "")
        if command and not isinstance(command, str):
            raise SyncError("Claude hook command must be a string")
        commands.append(command)
    return commands


def render_claude_settings(
    destination: Path, status_script: Path
) -> tuple[str, str]:
    current = read_text(destination)
    try:
        settings = json.loads(current) if current else {}
    except json.JSONDecodeError as exc:
        raise SyncError(f"refusing to write invalid Claude JSON: {exc}") from exc
    if not isinstance(settings, dict):
        raise SyncError("Claude settings root must be a JSON object")
    hooks = settings.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SyncError("Claude settings hooks must be a JSON object")
    groups = hooks.setdefault("SessionStart", [])
    if not isinstance(groups, list):
        raise SyncError("Claude SessionStart must be a JSON array")

    markers = (*LEGACY_HOOK_MARKERS, MANAGED_HOOK_MARKER)
    retained: list[object] = []
    first_owned_index: int | None = None
    migrated = 0
    for group in groups:
        commands = hook_commands(group)
        owned = [command for command in commands if any(m in command for m in markers)]
        if owned and len(owned) != len(commands):
            raise SyncError(
                "workspace-meta Claude hook shares a SessionStart group with an "
                "unmanaged hook; split it manually before bootstrap"
            )
        if owned:
            if first_owned_index is None:
                first_owned_index = len(retained)
            migrated += 1
        else:
            retained.append(group)

    managed_group = {
        "matcher": "startup|resume",
        "hooks": [
            {
                "type": "command",
                "command": build_status_command("claude", status_script),
                "timeout": 20,
                "statusMessage": "Checking workspace-meta status",
            }
        ],
    }
    insert_at = len(retained) if first_owned_index is None else first_owned_index
    retained.insert(insert_at, managed_group)
    hooks["SessionStart"] = retained
    result = json.dumps(settings, ensure_ascii=False, indent=2) + "\n"
    if result == current:
        return result, "already current"
    if migrated:
        return result, f"updated; migrated {migrated} legacy hook group(s)"
    return result, "installed or updated"


def sync_agents(template_path: Path, destination: Path) -> str:
    result, action = render_agents(template_path, destination)
    if result != read_text(destination):
        atomic_write(destination, result)
    return action


def sync_hooks(template_path: Path, destination: Path, status_script: Path) -> str:
    rendered = render_hooks(template_path, destination, status_script)
    if rendered.content != read_text(destination):
        atomic_write(destination, rendered.content)
    return rendered.action


def sync_claude_settings(destination: Path, status_script: Path) -> str:
    result, action = render_claude_settings(destination, status_script)
    if result != read_text(destination):
        atomic_write(destination, result)
    return action


def apply_prevalidated(updates: list[tuple[Path, str]]) -> None:
    originals = {path: (path.exists(), read_text(path)) for path, _ in updates}
    written: list[Path] = []
    try:
        for path, content in updates:
            if content == originals[path][1]:
                continue
            atomic_write(path, content)
            written.append(path)
    except OSError:
        for path in reversed(written):
            existed, original = originals[path]
            try:
                if existed:
                    atomic_write(path, original)
                else:
                    path.unlink(missing_ok=True)
            except OSError:
                pass
        raise


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-template", required=True, type=Path)
    parser.add_argument("--hooks-template", required=True, type=Path)
    parser.add_argument("--status-script", required=True, type=Path)
    parser.add_argument("--codex-home", required=True, type=Path)
    parser.add_argument("--claude-settings", required=True, type=Path)
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agents_path = args.codex_home / "AGENTS.md"
    codex_config_path = args.codex_home / "config.toml"
    try:
        agents_result, agents_action = render_agents(args.agents_template, agents_path)
        hooks_rendered = render_hooks(
            args.hooks_template, codex_config_path, args.status_script
        )
        claude_result, claude_action = render_claude_settings(
            args.claude_settings, args.status_script
        )
    except (OSError, SyncError) as exc:
        print(f"agent config sync failed: {exc}", file=sys.stderr)
        return 1

    updates = [
        (agents_path, agents_result),
        (codex_config_path, hooks_rendered.content),
        (args.claude_settings, claude_result),
    ]
    drifted = any(content != read_text(path) for path, content in updates)
    if args.check:
        print(f"Codex AGENTS.md: {agents_action}")
        print(f"Codex hooks: {hooks_rendered.action}")
        print(f"Claude hooks: {claude_action}")
        return 1 if drifted else 0

    try:
        apply_prevalidated(updates)
    except OSError as exc:
        print(f"agent config sync failed while writing: {exc}", file=sys.stderr)
        return 1

    print(f"Codex AGENTS.md: {agents_action}")
    print(f"Codex hooks: {hooks_rendered.action}")
    print(f"Claude hooks: {claude_action}")
    if hooks_rendered.definition_changed:
        print(
            "WARNING: Codex hook definition changed; review and trust it with /hooks",
            file=sys.stderr,
        )
    override = args.codex_home / "AGENTS.override.md"
    if override.exists() and override.stat().st_size:
        print(
            "WARNING: non-empty AGENTS.override.md takes precedence; managed "
            "AGENTS.md guidance is inactive",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

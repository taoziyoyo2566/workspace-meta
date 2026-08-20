#!/usr/bin/env python3
"""Synchronize workspace-meta-owned guidance and hooks into host agent config."""

from __future__ import annotations

import argparse
import copy
from collections import namedtuple
import hashlib
import json
import os
from pathlib import Path
import re
import shlex
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

PreferenceRenderResult = namedtuple(
    "PreferenceRenderResult", ("content", "action", "changed_paths")
)

PREFERENCE_ALLOWED_PATHS = {
    "history.max_bytes",
    "history.persistence",
    "tui.status_line",
}
PREFERENCE_SECTIONS = {path.split(".", 1)[0] for path in PREFERENCE_ALLOWED_PATHS}
MISSING = object()


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


def build_status_command(agent: str, status_script: Path, python_bin: str = "python3") -> str:
    digest = hashlib.sha256(status_script.read_bytes()).hexdigest()
    python_command = shlex.quote(python_bin)
    return (
        'p="$HOME/workspace/scripts/workspace_status.py"; '
        f'expected="{digest}"; '
        f"actual=$({python_command} -c 'import hashlib,sys; "
        'print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())\' '
        '"$p" 2>/dev/null || printf unavailable); '
        'if [ "$actual" != "$expected" ]; then '
        "printf '{\"systemMessage\":\"workspace-meta status evaluator changed or "
        "is unavailable. Run: make -C ~/workspace bootstrap\"}\\n'; "
        f'else {python_command} "$p" --agent {agent}; fi; : {MANAGED_HOOK_MARKER}'
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
    template_path: Path, destination: Path, status_script: Path, python_bin: str = "python3"
) -> HookRenderResult:
    template = read_text(template_path)
    if template.count(COMMAND_PLACEHOLDER) != 1:
        raise SyncError("Codex hook template must contain one status-command placeholder")
    template = template.replace(
        COMMAND_PLACEHOLDER, build_status_command("codex", status_script, python_bin)
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


def load_preferences(template_path: Path) -> dict[tuple[str, str], object]:
    """Load and validate the small set of Codex fields workspace-meta owns."""

    try:
        settings = tomllib.loads(read_text(template_path))
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"Codex preferences template is invalid TOML: {exc}") from exc
    if not isinstance(settings, dict) or not settings:
        raise SyncError("Codex preferences template must contain a non-empty TOML table")

    targets: dict[tuple[str, str], object] = {}
    for section, values in settings.items():
        if section not in PREFERENCE_SECTIONS or not isinstance(values, dict):
            raise SyncError(
                f"Codex preferences template may contain only direct tables for: "
                f"{', '.join(sorted(PREFERENCE_SECTIONS))}"
            )
        for key, value in values.items():
            path = f"{section}.{key}"
            if path not in PREFERENCE_ALLOWED_PATHS:
                raise SyncError(f"Codex preference is not in the managed allowlist: {path}")
            if path == "history.persistence" and value not in {"save-all", "none"}:
                raise SyncError("history.persistence must be save-all or none")
            if path == "history.max_bytes" and (
                type(value) is not int or value <= 0
            ):
                raise SyncError("history.max_bytes must be a positive integer")
            if path == "tui.status_line" and (
                not isinstance(value, list) or not all(isinstance(item, str) for item in value)
            ):
                raise SyncError("tui.status_line must be an array of strings")
            targets[(section, key)] = value

    if not targets:
        raise SyncError("Codex preferences template contains no managed fields")
    return targets


def parse_codex_toml(content: str) -> dict[str, object]:
    try:
        parsed = tomllib.loads(content)
    except tomllib.TOMLDecodeError as exc:
        raise SyncError(f"refusing to reconcile invalid Codex TOML: {exc}") from exc
    if not isinstance(parsed, dict):
        raise SyncError("Codex TOML root must be a table")
    return parsed


def _strip_toml_comment(line: str) -> str:
    state: str | None = None
    index = 0
    while index < len(line):
        if state == "basic":
            if line[index] == "\\":
                index += 2
            elif line[index] == '"':
                state = None
                index += 1
            else:
                index += 1
            continue
        if state == "literal":
            if line[index] == "'":
                state = None
            index += 1
            continue
        if state == "multiline_basic":
            if line.startswith('"""', index):
                state = None
                index += 3
            else:
                index += 1
            continue
        if state == "multiline_literal":
            if line.startswith("'''", index):
                state = None
                index += 3
            else:
                index += 1
            continue
        if line.startswith('"""', index):
            state = "multiline_basic"
            index += 3
        elif line.startswith("'''", index):
            state = "multiline_literal"
            index += 3
        elif line[index] == '"':
            state = "basic"
            index += 1
        elif line[index] == "'":
            state = "literal"
            index += 1
        elif line[index] == "#":
            return line[:index]
        else:
            index += 1
    return line


def _toml_header(line: str) -> tuple[str, bool] | None:
    candidate = _strip_toml_comment(line).strip()
    if candidate.startswith('[[') and candidate.endswith(']]'):
        return candidate[2:-2].strip(), True
    if candidate.startswith("[") and candidate.endswith("]"):
        return candidate[1:-1].strip(), False
    return None


def _toml_headers(lines: list[str]) -> list[tuple[int, str, bool]]:
    headers: list[tuple[int, str, bool]] = []
    state: str | None = None
    for index, line in enumerate(lines):
        if state is None:
            header = _toml_header(line)
            if header:
                name, is_array = header
                headers.append((index, name, is_array))
        state, _ = _scan_toml_fragment(line, state, 0)
    return headers


def _table_spans(
    lines: list[str], headers: list[tuple[int, str, bool]] | None = None
) -> dict[str, tuple[int, int]]:
    headers = _toml_headers(lines) if headers is None else headers

    spans: dict[str, tuple[int, int]] = {}
    for header_index, (start, name, is_array) in enumerate(headers):
        if is_array:
            continue
        end = len(lines)
        if header_index + 1 < len(headers):
            end = headers[header_index + 1][0]
        spans[name] = (start, end)
    return spans


def _scan_toml_fragment(
    fragment: str, state: str | None, depth: int
) -> tuple[str | None, int]:
    index = 0
    while index < len(fragment):
        if state == "basic":
            if fragment[index] == "\\":
                index += 2
            elif fragment[index] == '"':
                state = None
                index += 1
            else:
                index += 1
            continue
        if state == "literal":
            if fragment[index] == "'":
                state = None
            index += 1
            continue
        if state == "multiline_basic":
            if fragment[index] == "\\":
                index += 2
            elif fragment.startswith('"""', index):
                state = None
                index += 3
            else:
                index += 1
            continue
        if state == "multiline_literal":
            if fragment.startswith("'''", index):
                state = None
                index += 3
            else:
                index += 1
            continue

        if fragment.startswith('"""', index):
            state = "multiline_basic"
            index += 3
        elif fragment.startswith("'''", index):
            state = "multiline_literal"
            index += 3
        elif fragment[index] == '"':
            state = "basic"
            index += 1
        elif fragment[index] == "'":
            state = "literal"
            index += 1
        elif fragment[index] == "#":
            break
        elif fragment[index] in "[{":
            depth += 1
            index += 1
        elif fragment[index] in "]}":
            depth -= 1
            index += 1
        else:
            index += 1
    return state, depth


def _value_end(lines: list[str], start: int, equals: int) -> int:
    state: str | None = None
    depth = 0
    for index in range(start, len(lines)):
        fragment = lines[index][equals + 1 :] if index == start else lines[index]
        state, depth = _scan_toml_fragment(fragment, state, depth)
        if state is None and depth == 0:
            return index + 1
    raise SyncError("unable to locate the end of a managed TOML value")


ASSIGNMENT_RE = re.compile(
    r"^(?P<indent>\s*)(?P<key>[A-Za-z0-9_-]+)\s*="
)
DOTTED_ASSIGNMENT_RE = re.compile(
    r"^(?P<indent>\s*)(?P<section>[A-Za-z0-9_-]+)\s*\.\s*"
    r"(?P<key>[A-Za-z0-9_-]+)\s*="
)


def _assignment_equals(line: str) -> int | None:
    state: str | None = None
    index = 0
    while index < len(line):
        if state == "basic":
            if line[index] == "\\":
                index += 2
            elif line[index] == '"':
                state = None
                index += 1
            else:
                index += 1
            continue
        if state == "literal":
            if line[index] == "'":
                state = None
            index += 1
            continue
        if state == "multiline_basic":
            if line.startswith('"""', index):
                state = None
                index += 3
            else:
                index += 1
            continue
        if state == "multiline_literal":
            if line.startswith("'''", index):
                state = None
                index += 3
            else:
                index += 1
            continue
        if line.startswith('"""', index):
            state = "multiline_basic"
            index += 3
        elif line.startswith("'''", index):
            state = "multiline_literal"
            index += 3
        elif line[index] == '"':
            state = "basic"
            index += 1
        elif line[index] == "'":
            state = "literal"
            index += 1
        elif line[index] == "#":
            return None
        elif line[index] == "=":
            return index
        else:
            index += 1
    return None


def _assignment_span(
    lines: list[str], start: int, end: int, target_key: str
) -> tuple[int, int, str] | None:
    index = start + 1
    while index < end:
        line = lines[index]
        equals = _assignment_equals(line)
        if equals is None:
            index += 1
            continue
        value_end = _value_end(lines, index, equals)
        match = ASSIGNMENT_RE.match(line)
        if match and match.group("key") == target_key:
            return index, value_end, match.group("indent")
        index = value_end
    return None


def _root_dotted_assignment_span(
    lines: list[str], end: int, section: str, target_key: str
) -> tuple[int, int, str] | None:
    index = 0
    while index < end:
        line = lines[index]
        equals = _assignment_equals(line)
        if equals is None:
            index += 1
            continue
        value_end = _value_end(lines, index, equals)
        match = DOTTED_ASSIGNMENT_RE.match(line)
        if (
            match
            and match.group("section") == section
            and match.group("key") == target_key
        ):
            return index, value_end, match.group("indent")
        index = value_end
    return None


def _format_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        return repr(value)
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, list):
        return "[" + ", ".join(_format_toml_value(item) for item in value) + "]"
    raise SyncError(f"cannot safely serialize managed TOML value of type {type(value).__name__}")


def _line_offsets(lines: list[str]) -> list[int]:
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    return offsets


def _preferred_newline(content: str) -> str:
    return "\r\n" if "\r\n" in content else "\n"


def _without_managed_preferences(
    parsed: dict[str, object], targets: dict[tuple[str, str], object]
) -> dict[str, object]:
    remaining = copy.deepcopy(parsed)
    for section, key in targets:
        values = remaining.get(section)
        if isinstance(values, dict):
            values.pop(key, None)
            if not values:
                remaining.pop(section, None)
    return remaining


def render_preferences(
    template_path: Path, current: str
) -> PreferenceRenderResult:
    targets = load_preferences(template_path)
    parsed = parse_codex_toml(current)
    changes: list[tuple[str, str, object, str]] = []

    for (section, key), wanted in targets.items():
        section_value = parsed.get(section, MISSING)
        current_value = (
            section_value.get(key, MISSING)
            if isinstance(section_value, dict)
            else MISSING
        )
        if current_value is MISSING:
            changes.append((section, key, wanted, "missing"))
        elif current_value != wanted:
            changes.append((section, key, wanted, "different"))

    if not changes:
        return PreferenceRenderResult(current, "already current", ())

    lines = current.splitlines(keepends=True)
    offsets = _line_offsets(lines)
    headers = _toml_headers(lines)
    spans = _table_spans(lines, headers)
    root_end = headers[0][0] if headers else len(lines)
    newline = _preferred_newline(current)
    edits: list[tuple[int, int, str]] = []
    missing_by_section: dict[str, list[tuple[str, object]]] = {}
    missing_at_root: list[tuple[str, str, object]] = []

    for section, key, wanted, status in changes:
        span = spans.get(section)
        if span:
            assignment = _assignment_span(lines, span[0], span[1], key)
            if assignment:
                start, end, indent = assignment
                has_newline = lines[end - 1].endswith(("\n", "\r"))
                replacement = (
                    f"{indent}{key} = {_format_toml_value(wanted)}"
                    + (newline if has_newline else "")
                )
                edits.append((offsets[start], offsets[end], replacement))
            elif status == "different":
                raise SyncError(
                    f"cannot safely locate existing managed preference {section}.{key}"
                )
            else:
                missing_by_section.setdefault(section, []).append((key, wanted))
        else:
            assignment = _root_dotted_assignment_span(lines, root_end, section, key)
            if assignment:
                start, end, indent = assignment
                has_newline = lines[end - 1].endswith(("\n", "\r"))
                replacement = (
                    f"{indent}{section}.{key} = {_format_toml_value(wanted)}"
                    + (newline if has_newline else "")
                )
                edits.append((offsets[start], offsets[end], replacement))
            elif status == "different":
                raise SyncError(
                    f"cannot safely locate existing managed preference {section}.{key}"
                )
            elif section in parsed:
                has_nested_table = any(
                    name.startswith(f"{section}.") for _, name, _ in headers
                )
                if not has_nested_table:
                    raise SyncError(
                        f"cannot safely add {section}.{key}; {section} has no "
                        "direct or implicit TOML table"
                    )
                missing_at_root.append((section, key, wanted))
            else:
                missing_by_section.setdefault(section, []).append((key, wanted))

    if missing_at_root:
        block = "".join(
            f"{section}.{key} = {_format_toml_value(value)}{newline}"
            for section, key, value in missing_at_root
        )
        # Dotted keys must be written in the TOML root. Insert them before the
        # first table header so an implicit parent such as [tui.some_state]
        # remains valid and no unrelated table receives the assignment.
        block += newline
        position = offsets[root_end]
        edits.append((position, position, block))

    new_sections: list[str] = []
    for section, entries in missing_by_section.items():
        block = "".join(
            f"{key} = {_format_toml_value(value)}{newline}" for key, value in entries
        )
        if section in spans:
            position = offsets[spans[section][1]]
            edits.append((position, position, block))
            continue
        new_sections.append(f"[{section}]{newline}{block}")

    if new_sections:
        tables = (newline * 2).join(new_sections)
        if not current:
            append = tables
        else:
            separator = ""
            if not current.endswith(("\n", "\r")):
                separator += newline
            if not current.endswith(newline * 2):
                separator += newline
            append = separator + tables
        if not append.endswith(newline):
            append += newline
        edits.append((len(current), len(current), append))

    result = current
    for _, (start, end, replacement) in sorted(
        enumerate(edits), key=lambda item: (item[1][0], item[0]), reverse=True
    ):
        result = result[:start] + replacement + result[end:]

    result_parsed = parse_codex_toml(result)
    for (section, key), wanted in targets.items():
        section_value = result_parsed.get(section)
        actual = (
            section_value.get(key, MISSING)
            if isinstance(section_value, dict)
            else MISSING
        )
        if actual != wanted:
            raise SyncError(
                f"managed preference postcondition failed for {section}.{key}"
            )
    if _without_managed_preferences(parsed, targets) != _without_managed_preferences(
        result_parsed, targets
    ):
        raise SyncError("preference reconciliation changed unowned TOML values")
    changed_paths = tuple(f"{section}.{key}" for section, key, _, _ in changes)
    return PreferenceRenderResult(
        result,
        "updated preferences: " + ", ".join(changed_paths),
        changed_paths,
    )


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
    destination: Path, status_script: Path, python_bin: str = "python3"
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
                "command": build_status_command("claude", status_script, python_bin),
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


def sync_hooks(template_path: Path, destination: Path, status_script: Path, python_bin: str = "python3") -> str:
    rendered = render_hooks(template_path, destination, status_script, python_bin)
    if rendered.content != read_text(destination):
        atomic_write(destination, rendered.content)
    return rendered.action


def sync_claude_settings(destination: Path, status_script: Path, python_bin: str = "python3") -> str:
    result, action = render_claude_settings(destination, status_script, python_bin)
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
    parser.add_argument("--preferences-template", required=True, type=Path)
    parser.add_argument("--status-script", required=True, type=Path)
    parser.add_argument("--codex-home", required=True, type=Path)
    parser.add_argument("--claude-settings", required=True, type=Path)
    parser.add_argument(
        "--python",
        default="python3",
        help="Python interpreter to embed in generated SessionStart hook commands",
    )
    parser.add_argument("--check", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    agents_path = args.codex_home / "AGENTS.md"
    codex_config_path = args.codex_home / "config.toml"
    try:
        agents_result, agents_action = render_agents(args.agents_template, agents_path)
        hooks_rendered = render_hooks(
            args.hooks_template, codex_config_path, args.status_script, args.python
        )
        preferences_rendered = render_preferences(
            args.preferences_template, hooks_rendered.content
        )
        claude_result, claude_action = render_claude_settings(
            args.claude_settings, args.status_script, args.python
        )
    except (OSError, SyncError) as exc:
        print(f"agent config sync failed: {exc}", file=sys.stderr)
        return 1

    updates = [
        (agents_path, agents_result),
        (codex_config_path, preferences_rendered.content),
        (args.claude_settings, claude_result),
    ]
    drifted = any(content != read_text(path) for path, content in updates)
    if args.check:
        print(f"Codex AGENTS.md: {agents_action}")
        print(f"Codex hooks: {hooks_rendered.action}")
        print(f"Codex preferences: {preferences_rendered.action}")
        print(f"Claude hooks: {claude_action}")
        return 1 if drifted else 0

    try:
        apply_prevalidated(updates)
    except OSError as exc:
        print(f"agent config sync failed while writing: {exc}", file=sys.stderr)
        return 1

    print(f"Codex AGENTS.md: {agents_action}")
    print(f"Codex hooks: {hooks_rendered.action}")
    print(f"Codex preferences: {preferences_rendered.action}")
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

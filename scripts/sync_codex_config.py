#!/usr/bin/env python3
"""Synchronize workspace-meta-owned host agent configuration."""

from __future__ import annotations

import argparse
import copy
from collections import Counter, namedtuple
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
MANAGED_CLAUDE_STATUS_LINE_MARKER = "workspace-meta-managed-claude-status-line-v1"
MANAGED_HOOK_MARKER_PATTERN = re.compile(
    r"workspace-meta-managed-status-v\d+(?=$|[^A-Za-z0-9_-])"
)
MANAGED_CLAUDE_STATUS_LINE_MARKER_PATTERN = re.compile(
    r"workspace-meta-managed-claude-status-line-v\d+(?=$|[^A-Za-z0-9_-])"
)
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
    "PreferenceRenderResult", ("content", "action", "changed_paths", "drift")
)
PreferenceDrift = namedtuple("PreferenceDrift", ("path", "current", "expected"))
ManagedFieldDrift = namedtuple(
    "ManagedFieldDrift", ("name", "current", "expected", "change")
)
ComponentDrift = namedtuple(
    "ComponentDrift", ("name", "script_name", "fields", "pin_only")
)


ManagedArea = namedtuple(
    "ManagedArea",
    (
        "label",
        "path",
        "drifted",
        "managed_value",
        "repository_value",
        "current_value",
        "preference_drift",
        "hook_definition_changed",
        "component_drift",
    ),
    defaults=((), False, None),
)
SyncPlan = namedtuple("SyncPlan", ("areas", "updates"))
PlannedUpdate = namedtuple(
    "PlannedUpdate", ("path", "existed", "current", "content")
)

PREFERENCE_ALLOWED_PATHS = {
    "history.max_bytes",
    "history.persistence",
    "tui.status_line",
}
PREFERENCE_SECTIONS = {path.split(".", 1)[0] for path in PREFERENCE_ALLOWED_PATHS}
MISSING = object()


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8") if path.exists() else ""
    except UnicodeError as exc:
        raise SyncError(f"file is not valid UTF-8: {path}") from exc


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
        "is unavailable. Run: make -C ~/workspace sync\"}\\n'; "
        f'else {python_command} "$p" --agent {agent}; fi; : {MANAGED_HOOK_MARKER}'
    )


def build_claude_status_line_command(
    status_line_script: Path, python_bin: str = "python3"
) -> str:
    digest = hashlib.sha256(status_line_script.read_bytes()).hexdigest()
    python_command = shlex.quote(python_bin)
    return (
        'p="$HOME/workspace/scripts/claude_status_line.py"; '
        f'expected="{digest}"; '
        f"actual=$({python_command} -c 'import hashlib,sys; "
        'print(hashlib.sha256(open(sys.argv[1],"rb").read()).hexdigest())\' '
        '"$p" 2>/dev/null || printf unavailable); '
        'if [ "$actual" != "$expected" ]; then '
        "printf '%s' 'workspace-meta status line changed or is unavailable; "
        "run: make -C ~/workspace sync'; "
        f'else exec {python_command} "$p"; fi; : {MANAGED_CLAUDE_STATUS_LINE_MARKER}'
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
    for start, end in session_start_groups(content):
        group = "".join(lines[start:end])
        command_lines = [
            line for line in group.splitlines() if re.match(r"^\s*command\s*=", line)
        ]
        owned = [
            line
            for line in command_lines
            if any(marker in line for marker in LEGACY_HOOK_MARKERS)
            or MANAGED_HOOK_MARKER_PATTERN.search(line)
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
    drift: list[PreferenceDrift] = []

    for (section, key), wanted in targets.items():
        section_value = parsed.get(section, MISSING)
        current_value = (
            section_value.get(key, MISSING)
            if isinstance(section_value, dict)
            else MISSING
        )
        if current_value is MISSING:
            changes.append((section, key, wanted, "missing"))
            drift.append(
                PreferenceDrift(f"{section}.{key}", MISSING, copy.deepcopy(wanted))
            )
        elif current_value != wanted:
            changes.append((section, key, wanted, "different"))
            drift.append(
                PreferenceDrift(
                    f"{section}.{key}",
                    copy.deepcopy(current_value),
                    copy.deepcopy(wanted),
                )
            )

    if not changes:
        return PreferenceRenderResult(current, "already current", (), ())

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
        tuple(drift),
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
    destination: Path,
    status_script: Path,
    python_bin: str = "python3",
    claude_status_line_script: Path | None = None,
) -> tuple[str, str]:
    if claude_status_line_script is None:
        claude_status_line_script = Path(__file__).with_name("claude_status_line.py")
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

    retained: list[object] = []
    first_owned_index: int | None = None
    migrated = 0
    for group in groups:
        commands = hook_commands(group)
        owned = [
            command
            for command in commands
            if any(marker in command for marker in LEGACY_HOOK_MARKERS)
            or MANAGED_HOOK_MARKER_PATTERN.search(command)
        ]
        legacy_owned = [
            command
            for command in commands
            if any(marker in command for marker in LEGACY_HOOK_MARKERS)
        ]
        if owned and len(owned) != len(commands):
            raise SyncError(
                "workspace-meta Claude hook shares a SessionStart group with an "
                "unmanaged hook; split it manually before bootstrap"
            )
        if owned:
            if first_owned_index is None:
                first_owned_index = len(retained)
            if legacy_owned:
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

    managed_status_line = {
        "type": "command",
        "command": build_claude_status_line_command(
            claude_status_line_script, python_bin
        ),
        "padding": 0,
    }
    current_status_line = settings.get("statusLine", MISSING)
    if current_status_line is not MISSING:
        if not isinstance(current_status_line, dict):
            raise SyncError(
                "refusing to replace an unmanaged Claude statusLine; remove or "
                "migrate it explicitly before bootstrap"
            )
        current_command = current_status_line.get("command", "")
        if not isinstance(current_command, str) or not (
            MANAGED_CLAUDE_STATUS_LINE_MARKER_PATTERN.search(current_command)
        ):
            raise SyncError(
                "refusing to replace an unmanaged Claude statusLine; remove or "
                "migrate it explicitly before bootstrap"
            )
    settings["statusLine"] = managed_status_line
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


def sync_claude_settings(
    destination: Path,
    status_script: Path,
    python_bin: str = "python3",
    claude_status_line_script: Path | None = None,
) -> str:
    result, action = render_claude_settings(
        destination, status_script, python_bin, claude_status_line_script
    )
    if result != read_text(destination):
        atomic_write(destination, result)
    return action


def render_managed_file(template_path: Path, destination: Path) -> tuple[str, str]:
    if not template_path.is_file():
        raise SyncError(f"managed file template is missing: {template_path}")
    result = read_text(template_path)
    if not result:
        raise SyncError(f"managed file template is empty: {template_path}")
    return result, "already current" if result == read_text(destination) else "changed"


def apply_prevalidated(updates: list[PlannedUpdate]) -> tuple[Path, ...]:
    originals = {
        update.path: (update.path.exists(), read_text(update.path))
        for update in updates
    }
    for update in updates:
        existed, current = originals[update.path]
        if existed != update.existed or current != update.current:
            raise SyncError(
                f"managed target changed after the dry-run: {update.path}; rerun sync"
            )

    written: list[Path] = []
    try:
        for update in updates:
            if update.content == update.current:
                continue
            atomic_write(update.path, update.content)
            written.append(update.path)
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
    return tuple(written)


def _sha256_value(content: str) -> str:
    return f"SHA-256 {hashlib.sha256(content.encode()).hexdigest()}"


def _marked_value(content: str, begin: str, end: str) -> str:
    if content.count(begin) != 1 or content.count(end) != 1:
        return "managed block not present"
    start = content.index(begin)
    finish = content.index(end, start) + len(end)
    return _sha256_value(content[start:finish].strip())


def _decode_shell_word(value: str) -> object:
    try:
        words = shlex.split(value)
    except ValueError:
        return MISSING
    return words[0] if len(words) == 1 else MISSING


def _command_semantics(command: object, agent: str | None) -> dict[str, object]:
    if not isinstance(command, str):
        return {
            "script path": MISSING,
            "expected script SHA-256": MISSING,
            "command target": MISSING,
            "command interpreter": MISSING,
            "hash verifier interpreter": MISSING,
            "hash-mismatch recovery command": MISSING,
            "command structure version": MISSING,
            "_command": command,
            "_command_shape": command,
        }

    path_match = re.search(r'(?:^|; )p=(?P<value>[^;]+); expected=', command)
    script_path = (
        _decode_shell_word(path_match.group("value")) if path_match else MISSING
    )
    pin_match = re.search(r'(?:^|; )expected="(?P<value>[^"]+)";', command)
    script_pin = pin_match.group("value") if pin_match else MISSING
    interpreter_match = re.search(
        r"actual=\$\((?P<value>.+?) -c 'import hashlib,sys;", command
    )
    verifier_interpreter = (
        _decode_shell_word(interpreter_match.group("value"))
        if interpreter_match
        else MISSING
    )
    if agent is None:
        target_match = re.search(
            r'else exec (?P<interpreter>.+?) "\$p"; fi;', command
        )
        command_agent = None
    else:
        target_match = re.search(
            r'else (?P<interpreter>.+?) "\$p" --agent '
            r'(?P<agent>[^; ]+); fi;',
            command,
        )
        command_agent = target_match.group("agent") if target_match else None
    command_interpreter = (
        _decode_shell_word(target_match.group("interpreter"))
        if target_match
        else MISSING
    )
    if script_path is MISSING:
        command_target = MISSING
    elif agent is None:
        command_target = script_path
    elif command_agent is None:
        command_target = MISSING
    else:
        command_target = f"{script_path} --agent {command_agent}"

    recovery_match = re.search(
        r"make -C ~/workspace (?P<value>[A-Za-z0-9_-]+)", command
    )
    recovery_command = (
        f"make -C ~/workspace {recovery_match.group('value')}"
        if recovery_match
        else MISSING
    )
    marker_pattern = (
        MANAGED_CLAUDE_STATUS_LINE_MARKER_PATTERN
        if agent is None
        else MANAGED_HOOK_MARKER_PATTERN
    )
    version_match = marker_pattern.search(command)
    command_version = (
        version_match.group(0).rsplit("-", 1)[1]
        if version_match
        else MISSING
    )

    shape = command
    normalized_values = (
        ("script-path", script_path),
        ("script-pin", pin_match.group("value") if pin_match else MISSING),
        ("command-interpreter", command_interpreter),
        ("verifier-interpreter", verifier_interpreter),
        ("agent", command_agent if command_agent is not None else MISSING),
        ("recovery-command", recovery_command),
        ("command-version", version_match.group(0) if version_match else MISSING),
    )
    for placeholder, value in normalized_values:
        if value is not MISSING and isinstance(value, str):
            shape = shape.replace(value, f"<{placeholder}>")

    return {
        "script path": script_path,
        "expected script SHA-256": script_pin,
        "command target": command_target,
        "command interpreter": command_interpreter,
        "hash verifier interpreter": verifier_interpreter,
        "hash-mismatch recovery command": recovery_command,
        "command structure version": command_version,
        "_command": command,
        "_command_shape": shape,
    }


def _owned_session_start_snapshot(
    settings: dict[str, object], agent: str
) -> object:
    hooks = settings.get("hooks", {})
    groups = hooks.get("SessionStart", []) if isinstance(hooks, dict) else []
    if not isinstance(groups, list):
        raise SyncError(f"{agent} SessionStart must be an array")

    owned: list[tuple[dict[str, object], list[dict[str, object]], list[str]]] = []
    for group in groups:
        if not isinstance(group, dict):
            raise SyncError(f"{agent} SessionStart groups must be objects")
        handlers = group.get("hooks", [])
        if not isinstance(handlers, list) or not all(
            isinstance(handler, dict) for handler in handlers
        ):
            raise SyncError(f"{agent} SessionStart handlers must be objects")
        commands = [handler.get("command", "") for handler in handlers]
        if any(command and not isinstance(command, str) for command in commands):
            raise SyncError(f"{agent} SessionStart commands must be strings")
        if any(
            any(marker in command for marker in LEGACY_HOOK_MARKERS)
            or MANAGED_HOOK_MARKER_PATTERN.search(command)
            for command in commands
            if isinstance(command, str)
        ):
            owned.append((group, handlers, commands))

    if not owned:
        return MISSING

    group, handlers, commands = owned[0]
    handler = handlers[0] if handlers else {}
    command = commands[0] if commands else MISSING
    component_name = (
        "workspace-meta SessionStart"
        if any(
            MANAGED_HOOK_MARKER_PATTERN.search(candidate)
            for _, _, owned_commands in owned
            for candidate in owned_commands
            if isinstance(candidate, str)
        )
        else "legacy workspace-meta SessionStart"
    )
    snapshot = {
        "managed component": component_name,
        "managed group count": len(owned),
        "matcher": group.get("matcher", MISSING),
        "handler count": sum(len(item[1]) for item in owned),
        "type": handler.get("type", MISSING),
        **_command_semantics(command, agent),
        "timeout": handler.get("timeout", MISSING),
        "statusMessage": handler.get("statusMessage", MISSING),
        "additional group fields": {
            key: value for key, value in group.items() if key not in {"matcher", "hooks"}
        }
        or MISSING,
        "additional handler fields": {
            key: value
            for key, value in handler.items()
            if key not in {"type", "command", "timeout", "statusMessage"}
        }
        or MISSING,
    }
    return snapshot


def _owned_status_line_snapshot(settings: dict[str, object]) -> object:
    status_line = settings.get("statusLine", MISSING)
    if status_line is MISSING:
        return MISSING
    if not isinstance(status_line, dict):
        raise SyncError("Claude statusLine must be an object")
    command = status_line.get("command", "")
    if not isinstance(command, str) or not (
        MANAGED_CLAUDE_STATUS_LINE_MARKER_PATTERN.search(command)
    ):
        return MISSING
    return {
        "managed component": "workspace-meta statusLine",
        "type": status_line.get("type", MISSING),
        **_command_semantics(command, None),
        "padding": status_line.get("padding", MISSING),
        "additional statusLine fields": {
            key: value
            for key, value in status_line.items()
            if key not in {"type", "command", "padding"}
        }
        or MISSING,
    }


def _semantic_component_drift(
    name: str,
    script_name: str,
    current: object,
    expected: dict[str, object],
    extra_fields: tuple[ManagedFieldDrift, ...] = (),
) -> ComponentDrift:
    fields: list[ManagedFieldDrift] = []
    current_values = {} if current is MISSING else current
    if not isinstance(current_values, dict):
        raise SyncError(f"{name} managed component could not be inspected")
    for field_name, expected_value in expected.items():
        if field_name.startswith("_"):
            continue
        current_value = current_values.get(field_name, MISSING)
        if current_value == expected_value:
            continue
        if field_name == "expected script SHA-256" and current_value is not MISSING:
            change = "~ expected script hash changed"
        elif current_value is MISSING:
            change = f"+ {field_name} will be set"
        elif expected_value is MISSING:
            change = f"- {field_name} will be removed"
        else:
            change = f"~ {field_name} changed"
        fields.append(
            ManagedFieldDrift(field_name, current_value, expected_value, change)
        )

    current_shape = current_values.get("_command_shape", MISSING)
    expected_shape = expected.get("_command_shape", MISSING)
    if current is not MISSING and current_shape != expected_shape:
        current_command = current_values.get("_command", MISSING)
        expected_command = expected.get("_command", MISSING)
        fields.append(
            ManagedFieldDrift(
                "unparsed command structure SHA-256",
                (
                    _sha256_value(current_command)
                    if isinstance(current_command, str)
                    else MISSING
                ),
                (
                    _sha256_value(expected_command)
                    if isinstance(expected_command, str)
                    else MISSING
                ),
                "~ unparsed command structure changed",
            )
        )

    fields.extend(extra_fields)
    pin_only = len(fields) == 1 and fields[0].name == "expected script SHA-256"
    return ComponentDrift(name, script_name, tuple(fields), pin_only)


def _render_area(label: str, operation):
    try:
        return operation()
    except (OSError, SyncError, json.JSONDecodeError) as exc:
        raise SyncError(f"{label}: {exc}") from exc


def build_sync_plan(args: argparse.Namespace) -> SyncPlan:
    agents_path = args.codex_home / "AGENTS.md"
    codex_config_path = args.codex_home / "config.toml"

    agents_current = _render_area(
        "Codex AGENTS.md", lambda: read_text(agents_path)
    )
    agents_result, _ = _render_area(
        "Codex AGENTS.md",
        lambda: render_agents(args.agents_template, agents_path),
    )

    config_current = _render_area(
        "Codex SessionStart hook", lambda: read_text(codex_config_path)
    )
    hooks_rendered = _render_area(
        "Codex SessionStart hook",
        lambda: render_hooks(
            args.hooks_template,
            codex_config_path,
            args.status_script,
            args.python,
        ),
    )
    preferences_rendered = _render_area(
        "Codex preferences",
        lambda: render_preferences(args.preferences_template, hooks_rendered.content),
    )

    claude_current = _render_area(
        "Claude settings", lambda: read_text(args.claude_settings)
    )
    claude_result, _ = _render_area(
        "Claude settings",
        lambda: render_claude_settings(
            args.claude_settings,
            args.status_script,
            args.python,
            args.claude_status_line_script,
        ),
    )

    env_skill_current = _render_area(
        "env-sync skill", lambda: read_text(args.env_skill)
    )
    env_skill_result, _ = _render_area(
        "env-sync skill",
        lambda: render_managed_file(args.env_skill_template, args.env_skill),
    )

    current_agents_value = _marked_value(
        agents_current, AGENTS_BEGIN, AGENTS_END
    )
    if (
        current_agents_value == "managed block not present"
        and hashlib.sha256(agents_current.encode()).hexdigest() == LEGACY_AGENTS_SHA256
    ):
        current_agents_value = "legacy workspace-meta guidance"

    current_codex_hook = _owned_session_start_snapshot(
        parse_codex_toml(config_current), "codex"
    )
    expected_codex_hook = _owned_session_start_snapshot(
        parse_codex_toml(hooks_rendered.content), "codex"
    )
    if not isinstance(expected_codex_hook, dict):
        raise SyncError("rendered Codex SessionStart hook is missing")
    codex_boundary_drift: tuple[ManagedFieldDrift, ...] = ()
    if hooks_rendered.state_normalized:
        codex_boundary_drift = (
            ManagedFieldDrift(
                "managed boundary",
                "host-owned hook state inside marker",
                "host-owned hook state after marker",
                "~ managed boundary will be normalized; host-owned state is preserved",
            ),
        )
    codex_hook_drift = _semantic_component_drift(
        "workspace-meta SessionStart",
        f"scripts/{args.status_script.name}",
        current_codex_hook,
        expected_codex_hook,
        codex_boundary_drift,
    )

    current_claude_settings = json.loads(claude_current) if claude_current else {}
    expected_claude_settings = json.loads(claude_result)
    current_claude_hook = _owned_session_start_snapshot(
        current_claude_settings, "claude"
    )
    expected_claude_hook = _owned_session_start_snapshot(
        expected_claude_settings, "claude"
    )
    if not isinstance(expected_claude_hook, dict):
        raise SyncError("rendered Claude SessionStart hook is missing")
    claude_hook_drift = _semantic_component_drift(
        "workspace-meta SessionStart",
        f"scripts/{args.status_script.name}",
        current_claude_hook,
        expected_claude_hook,
    )
    current_claude_status_line = _owned_status_line_snapshot(
        current_claude_settings
    )
    expected_claude_status_line = _owned_status_line_snapshot(
        expected_claude_settings
    )
    if not isinstance(expected_claude_status_line, dict):
        raise SyncError("rendered Claude statusLine is missing")
    claude_status_line_drift = _semantic_component_drift(
        "workspace-meta statusLine",
        f"scripts/{args.claude_status_line_script.name}",
        current_claude_status_line,
        expected_claude_status_line,
    )

    areas = (
        ManagedArea(
            "Codex AGENTS.md",
            agents_path,
            agents_result != agents_current,
            "workspace-meta marked guidance block",
            _marked_value(agents_result, AGENTS_BEGIN, AGENTS_END),
            current_agents_value,
        ),
        ManagedArea(
            "Codex SessionStart hook",
            codex_config_path,
            bool(codex_hook_drift.fields),
            "workspace-meta SessionStart",
            "repository managed fields",
            "current host managed fields",
            hook_definition_changed=hooks_rendered.definition_changed,
            component_drift=codex_hook_drift,
        ),
        ManagedArea(
            "Codex preferences",
            codex_config_path,
            bool(preferences_rendered.drift),
            "declared Codex preference fields",
            "repository template values",
            "current parsed host values",
            preference_drift=preferences_rendered.drift,
        ),
        ManagedArea(
            "Claude SessionStart hook",
            args.claude_settings,
            bool(claude_hook_drift.fields),
            "workspace-meta SessionStart",
            "repository managed fields",
            "current host managed fields",
            component_drift=claude_hook_drift,
        ),
        ManagedArea(
            "Claude statusLine",
            args.claude_settings,
            bool(claude_status_line_drift.fields),
            "workspace-meta statusLine",
            "repository managed fields",
            "current host managed fields",
            component_drift=claude_status_line_drift,
        ),
        ManagedArea(
            "env-sync skill",
            args.env_skill,
            env_skill_result != env_skill_current,
            "workspace-meta-owned skill file",
            _sha256_value(env_skill_result),
            (
                _sha256_value(env_skill_current)
                if args.env_skill.exists()
                else "managed file not present"
            ),
        ),
    )
    updates = (
        PlannedUpdate(
            agents_path, agents_path.exists(), agents_current, agents_result
        ),
        PlannedUpdate(
            codex_config_path,
            codex_config_path.exists(),
            config_current,
            preferences_rendered.content,
        ),
        PlannedUpdate(
            args.claude_settings,
            args.claude_settings.exists(),
            claude_current,
            claude_result,
        ),
        PlannedUpdate(
            args.env_skill,
            args.env_skill.exists(),
            env_skill_current,
            env_skill_result,
        ),
    )
    return SyncPlan(areas, updates)


def print_area_statuses(
    areas: tuple[ManagedArea, ...], updated_paths: tuple[Path, ...] = ()
) -> None:
    for area in areas:
        if updated_paths and area.drifted and area.path in updated_paths:
            status = "UPDATED"
        else:
            status = "DRIFT" if area.drifted else "OK"
        print(f"{area.label + ':':<28}{status}")


def _print_value(title: str, value: object) -> None:
    print(f"    {title}:")
    if value is MISSING:
        print("      (missing)")
    elif isinstance(value, list):
        if not value:
            print("      []")
        for index, item in enumerate(value, start=1):
            print(f"      {index}. {item}")
    else:
        print(f"      {json.dumps(value, ensure_ascii=False)}")


def _list_change_summary(current: object, expected: object) -> list[str]:
    if current is MISSING:
        return ["+ repository value will be added"]
    if not isinstance(current, list) or not isinstance(expected, list):
        return ["~ managed value differs"]
    repository_only = list((Counter(expected) - Counter(current)).elements())
    host_only = list((Counter(current) - Counter(expected)).elements())
    changes = []
    if repository_only:
        changes.append("+ repository only: " + ", ".join(repository_only))
    if host_only:
        changes.append("- host only: " + ", ".join(host_only))
    common_expected = [item for item in expected if item in current]
    common_current = [item for item in current if item in expected]
    if common_expected != common_current:
        changes.append("~ order changed")
    return changes or ["~ order changed"]


def print_drift_details(areas: tuple[ManagedArea, ...]) -> None:
    print("\nDrift detected:")
    for area in areas:
        if not area.drifted:
            continue
        if area.preference_drift:
            for drift in area.preference_drift:
                print(f"\n  {drift.path}")
                _print_value("Repository", drift.expected)
                _print_value("Current host", drift.current)
                print("    Changes:")
                for change in _list_change_summary(drift.current, drift.expected):
                    print(f"      {change}")
            continue
        if area.component_drift is not None:
            component = area.component_drift
            print(f"\n  {area.label}:")
            print(f"    Script: {component.script_name}")
            print("    Changes:")
            for drift in component.fields:
                repository = (
                    "(missing)"
                    if drift.expected is MISSING
                    else json.dumps(drift.expected, ensure_ascii=False)
                )
                current = (
                    "(missing)"
                    if drift.current is MISSING
                    else json.dumps(drift.current, ensure_ascii=False)
                )
                print(f"      {drift.change}")
                print(f"        Installed: {current}")
                print(f"        Repository: {repository}")
            print("\n    Effect:")
            print(f"      {_component_effect(component)}")
            continue
        print(f"\n  {area.label} — {area.managed_value}")
        print(f"    Repository: {area.repository_value}")
        print(f"    Current host: {area.current_value}")
        if "not present" in area.current_value:
            change = "+ managed value will be installed"
        else:
            change = "~ managed value will be replaced"
        print(f"    Changes: {change}")


def _component_effect(component: ComponentDrift) -> str:
    script_name = Path(component.script_name).name
    if component.pin_only:
        managed_kind = (
            "statusLine" if component.name.endswith("statusLine") else "hook"
        )
        return (
            f"Refresh the managed {managed_kind} so it trusts the current "
            f"repository version of {script_name}."
        )
    component_field = next(
        (field for field in component.fields if field.name == "managed component"),
        None,
    )
    if component_field is not None and component_field.current is MISSING:
        return f"Install the repository-managed {component.name}."
    field_names = {field.name for field in component.fields}
    if field_names == {"hash-mismatch recovery command"}:
        recovery = component.fields[0].expected
        return (
            "Use "
            f"{recovery} when the managed script hash check fails."
        )
    if "unparsed command structure SHA-256" in field_names:
        return (
            "Replace the unrecognized managed command structure with the "
            "repository definition."
        )
    return "Replace the listed managed properties with the repository values."


def _component_change_summary(component: ComponentDrift) -> str:
    script_name = Path(component.script_name).name
    if component.pin_only:
        return f"refresh {script_name} hash pin"
    component_field = next(
        (field for field in component.fields if field.name == "managed component"),
        None,
    )
    if component_field is not None and component_field.current is MISSING:
        return f"install {component.name}"
    field_names = {field.name for field in component.fields}
    if field_names == {"hash-mismatch recovery command"}:
        return "update hash-mismatch recovery command"
    if field_names == {"unparsed command structure SHA-256"}:
        return "replace unrecognized command structure"
    return "update " + ", ".join(field.name for field in component.fields)


def print_changes_to_apply(areas: tuple[ManagedArea, ...]) -> None:
    print("\nChanges to apply:")
    for area in areas:
        if not area.drifted:
            continue
        if area.preference_drift:
            fields = ", ".join(drift.path for drift in area.preference_drift)
            summary = f"replace {fields}"
        elif area.component_drift is not None:
            summary = _component_change_summary(area.component_drift)
        elif "not present" in area.current_value:
            summary = "install the managed value"
        else:
            summary = "replace the managed value"
        print(f"  - {area.label}: {summary}")


def _print_error(exc: Exception) -> None:
    print("Managed configuration dry-run:", file=sys.stderr)
    print(f"ERROR: {exc}", file=sys.stderr)
    print("Result: synchronization cannot proceed safely.", file=sys.stderr)
    print("No files were modified.", file=sys.stderr)


def _warn_hook_and_override(plan: SyncPlan, args: argparse.Namespace) -> None:
    hook_area = next(
        area for area in plan.areas if area.label == "Codex SessionStart hook"
    )
    if hook_area.drifted and hook_area.hook_definition_changed:
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agents-template", required=True, type=Path)
    parser.add_argument("--hooks-template", required=True, type=Path)
    parser.add_argument("--preferences-template", required=True, type=Path)
    parser.add_argument("--status-script", required=True, type=Path)
    parser.add_argument("--claude-status-line-script", required=True, type=Path)
    parser.add_argument("--env-skill-template", required=True, type=Path)
    parser.add_argument("--env-skill", required=True, type=Path)
    parser.add_argument("--codex-home", required=True, type=Path)
    parser.add_argument("--claude-settings", required=True, type=Path)
    parser.add_argument(
        "--python",
        default="python3",
        help="Python interpreter to embed in generated SessionStart hook commands",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--interactive", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        plan = build_sync_plan(args)
    except (OSError, SyncError) as exc:
        _print_error(exc)
        return 1

    drifted = any(area.drifted for area in plan.areas)
    if args.check or args.interactive:
        print("Managed configuration dry-run:")
        print_area_statuses(plan.areas)
        if drifted:
            print_drift_details(plan.areas)
        else:
            print("\nResult: everything is already current.")
            print("No files changed.")
            return 0

    if args.check:
        print("\nResult: managed configuration drift detected.")
        print("No files were modified.")
        return 1

    if args.interactive:
        print_changes_to_apply(plan.areas)
        print(
            "\nWARNING:\n"
            "  Applying workspace-meta will replace the current local values\n"
            "  of the managed settings shown above.\n\n"
            "  Unmanaged local configuration will be preserved.\n"
        )
        try:
            answer = input("Apply these changes? [y/N]: ")
        except EOFError:
            answer = ""
        if answer not in {"y", "Y"}:
            print("\nNo changes applied.")
            return 0

    try:
        written_paths = apply_prevalidated(list(plan.updates))
    except (OSError, SyncError) as exc:
        print(f"ERROR: managed configuration write failed: {exc}", file=sys.stderr)
        return 1

    try:
        final_plan = build_sync_plan(args)
    except (OSError, SyncError) as exc:
        print(f"ERROR: post-apply validation failed: {exc}", file=sys.stderr)
        return 1
    remaining_drift = [area.label for area in final_plan.areas if area.drifted]
    if remaining_drift:
        print(
            "ERROR: post-apply validation still found drift: "
            + ", ".join(remaining_drift),
            file=sys.stderr,
        )
        return 1

    if args.interactive:
        print("\nFinal managed configuration:")
    print_area_statuses(plan.areas, written_paths)
    updated_count = sum(
        area.drifted and area.path in written_paths for area in plan.areas
    )
    print(
        f"\nSync complete: {updated_count} updated, "
        f"{len(plan.areas) - updated_count} unchanged."
    )
    _warn_hook_and_override(plan, args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

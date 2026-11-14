#!/usr/bin/env python3
"""Turn a Claude Code session transcript (jsonl) into a per-turn digest, metrics,
and a rule-reach report.

Usage: python3 -I scripts/session_digest.py <transcript.jsonl> <out_dir>

Writes <out_dir>/turns/T<NN>.md, <out_dir>/index.md, <out_dir>/metrics.json,
<out_dir>/reach.md, and <out_dir>/reach.json. The output directory must lie
outside this repository: a digest holds project content and stays host-local
like the transcript it comes from.

The reach report lists every read of a `.agents/rules/` module or an adapter
(`CLAUDE.md`, `AGENTS.md`, `CLAUDE.local.md`) by the Read tool or by a shell
command that prints it (cat, sed, head, tail, grep); the events, read
mechanically from tool calls, that the adapters route to a module; whether
each routed module had been read before the event and how much of it; and each
multi-line Bash command that enables errexit and then runs further lines.
Event detection and shell parsing are heuristics: a gap is a lead to read the
turn, not a verdict.
"""
from __future__ import annotations

import argparse
import collections
import fnmatch
import json
import os
import posixpath
import re
import shlex
import sys
from pathlib import Path
from typing import Any, Iterable

REPO_ROOT = Path(__file__).resolve().parents[1]

RULES = ".agents/rules/"

# Event kind -> the modules the adapters' Direct Task Routing sends it to.
# tests/test_session_digest.py checks every module here against CLAUDE.md.
ROUTES: dict[str, tuple[str, ...]] = {
    "git-publication": ("authorization.md", "git.md", "git-publication.md"),
    "git-integration": ("authorization.md", "git.md", "git-integration.md"),
    "git-branch": ("authorization.md", "git.md", "git-branches.md"),
    "git-recovery": ("authorization.md", "git.md", "git-recovery.md"),
    "git-release": ("authorization.md", "git.md", "releases.md"),
    "remote-host": ("authorization.md", "environment-truth.md"),
    "sudo": ("authorization.md",),
    "file-edit": ("authorization.md", "implementation.md", "file-checks.md",
                  "verification.md"),
    "ask-operator": ("requests.md", "claude-runtime.md"),
    "delegation": ("capabilities.md", "claude-runtime.md"),
    "tmp-write": ("temporary-files.md",),
}

# Every rules module: what a glob or a recursive grep over the rules directory
# is taken to cover, and the rows of the reach summary.
KNOWN_MODULES: tuple[str, ...] = (
    "authorization.md", "capabilities.md", "claude-runtime.md", "codex-runtime.md",
    "deployment.md", "documentation.md", "environment-truth.md", "file-checks.md",
    "git-branches.md", "git-integration.md", "git-publication.md", "git-recovery.md",
    "git.md", "implementation.md", "planning.md", "problem-follow-up.md",
    "reasoning.md", "releases.md", "requests.md", "review.md", "rule-authoring.md",
    "secrets.md", "temporary-files.md", "verification.md",
)

ADAPTER_NAMES = {"CLAUDE.md", "AGENTS.md", "CLAUDE.local.md"}
HANDLED_TYPES = {"user", "assistant", "system", "attachment"}
DELEGATION_TOOLS = {"Agent", "Task", "Workflow"}
EDIT_TOOLS = {"Edit", "Write", "NotebookEdit", "MultiEdit"}
SEPARATORS = {"&&", "||", ";", "|", "&", "(", ")", "|&", ";;", "{", "}"}
LEAD_WORDS = {"do", "then", "else", "elif", "if", "while", "until", "!", "time",
              "exec", "command", "nohup", "env", "{"}
HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
PUNCT = set("();<>|&")


class OutDirError(ValueError):
    """The output directory is not allowed."""


# --------------------------------------------------------------------------
# Small helpers kept from the retrospective script.

def clip(s: Any, n: int) -> str:
    s = s if isinstance(s, str) else json.dumps(s, ensure_ascii=False)
    return s if len(s) <= n else s[:n] + f" …[+{len(s)-n} chars]"


def text_of(content: Any) -> str:
    if isinstance(content, str):
        return content
    parts = []
    for c in content or []:
        if c.get("type") == "text":
            parts.append(c.get("text", ""))
        elif c.get("type") == "tool_result":
            cc = c.get("content")
            if isinstance(cc, list):
                parts.append("".join(x.get("text", "") for x in cc if isinstance(x, dict)))
            else:
                parts.append(str(cc))
    return "\n".join(parts)


# --------------------------------------------------------------------------
# Shell parsing.

def logical_lines(command: str) -> list[str]:
    """Command lines with heredoc bodies removed and `\\` continuations joined."""
    raw = command.split("\n")
    out: list[str] = []
    i = 0
    pending = ""
    while i < len(raw):
        line = pending + raw[i]
        i += 1
        if line.endswith("\\"):
            pending = line[:-1] + " "
            continue
        pending = ""
        out.append(line)
        for _, delim in HEREDOC.findall(line):
            while i < len(raw) and raw[i].strip() != delim:
                i += 1
            i += 1
    if pending:
        out.append(pending)
    return out


def _tokens(line: str) -> list[str]:
    lex = shlex.shlex(line, posix=True, punctuation_chars=True)
    lex.whitespace_split = True
    try:
        return list(lex)
    except ValueError:
        return line.split()


class Simple:
    """One simple command: its argv, its redirect targets, and its cwd."""

    def __init__(self, argv: list[str], redirects: list[str], cwd: str) -> None:
        self.argv = argv
        self.redirects = redirects
        self.cwd = cwd


def simple_commands(command: str, cwd: str = "") -> list[Simple]:
    """Split a shell command into simple commands, tracking `cd` for paths."""
    result: list[Simple] = []
    for line in logical_lines(command):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        argv: list[str] = []
        redirects: list[str] = []
        toks = _tokens(line)
        k = 0

        def flush() -> None:
            nonlocal argv, redirects, cwd
            while argv and (argv[0] in LEAD_WORDS
                            or re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", argv[0])):
                argv.pop(0)
            if argv or redirects:
                result.append(Simple(argv, redirects, cwd))
                if argv and argv[0] == "cd" and len(argv) > 1 and argv[1] != "-":
                    cwd = resolve(argv[1], cwd)
            argv, redirects = [], []

        while k < len(toks):
            tok = toks[k]
            k += 1
            if tok and set(tok) <= PUNCT:
                if "<" in tok or ">" in tok:
                    target = toks[k] if k < len(toks) else ""
                    k += 1
                    if argv and argv[-1].isdigit():
                        argv.pop()
                    if ">" in tok and not tok.endswith(">&"):
                        redirects.append(target)
                    continue
                flush()
                continue
            argv.append(tok)
        flush()
    return result


def resolve(token: str, cwd: str) -> str:
    if token.startswith("/") or token.startswith("~") or token.startswith("$"):
        return posixpath.normpath(token)
    if cwd:
        return posixpath.normpath(posixpath.join(cwd, token))
    return posixpath.normpath(token)


def classify(path: str) -> tuple[str, str] | None:
    """("rule", module) or ("adapter", path) for a resolved path, else None."""
    if "$" in path:
        return None
    m = re.search(r"(?:^|/)\.agents/rules/([^/]+\.md)$", path)
    if m:
        return ("rule", m.group(1))
    if posixpath.basename(path) in ADAPTER_NAMES:
        return ("adapter", path)
    return None


def is_rules_dir(path: str) -> bool:
    return bool(re.search(r"(?:^|/)\.agents/rules/?$", path))


def targets(token: str, cwd: str, recursive: bool = False) -> list[tuple[str, str]]:
    """Rule/adapter files a path argument names, with glob and directory expansion."""
    path = resolve(token, cwd)
    base = posixpath.basename(path)
    if any(ch in base for ch in "*?["):
        if is_rules_dir(posixpath.dirname(path)):
            return [("rule", m) for m in KNOWN_MODULES if fnmatch.fnmatch(m, base)]
        return []
    if recursive and is_rules_dir(path):
        return [("rule", m) for m in KNOWN_MODULES]
    hit = classify(path)
    return [hit] if hit else []


# Extents: {"kind": full|lines|section|grep|tail|bytes|partial, "start", "end", "n"}

def _full() -> dict:
    return {"kind": "full"}


def sed_extent(scripts: list[str], quiet: bool) -> dict:
    if not quiet:
        return _full()
    for s in scripts:
        m = re.fullmatch(r"\s*(\d+)\s*(?:,\s*(\d+|\$))?\s*p\s*", s)
        if m:
            start = int(m.group(1))
            end = m.group(2)
            if end is None:
                return {"kind": "lines", "start": start, "end": start}
            return {"kind": "lines", "start": start,
                    "end": None if end == "$" else int(end)}
        if re.fullmatch(r"\s*/.*/\s*,\s*(/.*/|\$|\d+)\s*p\s*", s):
            return {"kind": "section"}
    return {"kind": "partial"}


def _split_opts(args: list[str], with_value: str, long_with_value: tuple[str, ...] = ()):
    """Yield (option, value) and ("", positional) pairs for short-option clusters."""
    out: list[tuple[str, str]] = []
    i = 0
    while i < len(args):
        a = args[i]
        i += 1
        if a == "--":
            out.extend(("", x) for x in args[i:])
            break
        if a.startswith("--"):
            name, eq, val = a.partition("=")
            if not eq and name in long_with_value and i < len(args):
                val = args[i]
                i += 1
            out.append((name, val))
            continue
        if a.startswith("-") and len(a) > 1 and not a[1:].isdigit():
            for j, ch in enumerate(a[1:], 1):
                if ch in with_value:
                    rest = a[j + 1:]
                    if not rest and i < len(args):
                        rest = args[i]
                        i += 1
                    out.append(("-" + ch, rest))
                    break
                out.append(("-" + ch, ""))
            continue
        if a.startswith("-") and a[1:].isdigit():
            out.append(("-n", a[1:]))
            continue
        out.append(("", a))
    return out


def shell_reads(cmd: Simple) -> list[tuple[str, str, dict]]:
    """(kind, name, extent) for each rule/adapter file a simple command prints."""
    if not cmd.argv:
        return []
    prog = posixpath.basename(cmd.argv[0])
    args = cmd.argv[1:]
    files: list[str] = []
    extent: dict = _full()
    recursive = False
    if prog == "cat":
        files = [a for a in args if not a.startswith("-") or a == "-"]
    elif prog == "sed":
        opts = _split_opts(args, "ef", ("--expression", "--file"))
        if any(o in ("-i", "--in-place") or o.startswith("--in-place") for o, _ in opts):
            return []
        quiet = any(o in ("-n", "--quiet", "--silent") for o, _ in opts)
        scripts = [v for o, v in opts if o in ("-e", "--expression")]
        positional = [v for o, v in opts if not o]
        if not scripts and positional:
            scripts, positional = [positional[0]], positional[1:]
        files = positional
        extent = sed_extent(scripts, quiet)
    elif prog in ("head", "tail"):
        opts = _split_opts(args, "nc", ("--lines", "--bytes"))
        count = "10"
        kind = "lines"
        for o, v in opts:
            if o in ("-n", "--lines"):
                count = v
            elif o in ("-c", "--bytes"):
                kind = "bytes"
        files = [v for o, v in opts if not o]
        if kind == "bytes":
            extent = {"kind": "bytes"}
        elif prog == "head":
            n = int(count) if count.isdigit() else 10
            extent = {"kind": "lines", "start": 1, "end": n}
        elif count.startswith("+") and count[1:].isdigit():
            extent = {"kind": "lines", "start": int(count[1:]), "end": None}
        else:
            extent = {"kind": "tail", "n": int(count) if count.isdigit() else 10}
    elif prog in ("grep", "egrep", "fgrep"):
        opts = _split_opts(args, "efABCm", ("--regexp", "--file", "--include",
                                             "--exclude", "--max-count",
                                             "--context", "--after-context",
                                             "--before-context"))
        has_pattern = any(o in ("-e", "-f", "--regexp", "--file") for o, _ in opts)
        recursive = any(o in ("-r", "-R", "--recursive") for o, _ in opts)
        positional = [v for o, v in opts if not o]
        files = positional if has_pattern else positional[1:]
        extent = {"kind": "grep"}
    else:
        return []
    hits = []
    for f in files:
        for kind, name in targets(f, cmd.cwd, recursive):
            hits.append((kind, name, dict(extent)))
    return hits


def read_tool_extent(inp: dict) -> dict:
    offset = inp.get("offset")
    limit = inp.get("limit")
    if not offset and not limit:
        return _full()
    start = int(offset) if offset else 1
    end = start + int(limit) - 1 if limit else None
    return {"kind": "lines", "start": start, "end": end}


def under_tmp(path: str) -> bool:
    return path == "/tmp" or path.startswith("/tmp/")


GIT_GLOBAL_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace",
                         "--exec-path"}


def git_events(args: list[str]) -> list[str]:
    i = 0
    while i < len(args) and args[i].startswith("-"):
        i += 2 if args[i] in GIT_GLOBAL_WITH_VALUE else 1
    if i >= len(args):
        return []
    sub, rest = args[i], args[i + 1:]
    flags = [a for a in rest if a.startswith("-")]
    names = [a for a in rest if not a.startswith("-")]
    if sub == "commit":
        return ["git-recovery"] if "--amend" in flags else ["git-publication"]
    if sub == "add":
        return ["git-publication"]
    if sub == "push":
        forced = any(f in ("-f", "--force", "--delete", "-d") or f.startswith("--force")
                     for f in flags) or any(n.startswith("+") or n.startswith(":")
                                            for n in names)
        return ["git-publication", "git-recovery"] if forced else ["git-publication"]
    if sub in ("merge", "pull", "cherry-pick"):
        return ["git-integration"]
    if sub in ("rebase", "reset", "clean", "restore", "revert"):
        return ["git-recovery"]
    if sub == "checkout":
        if any(f in ("-b", "-B", "--orphan") for f in flags):
            return ["git-branch"]
        if "--" in rest or "." in names or "-f" in flags:
            return ["git-recovery"]
        return ["git-branch"] if names else []
    if sub == "switch":
        return ["git-branch"]
    if sub == "worktree":
        return ["git-branch"] if names and names[0] in ("add", "remove", "move", "prune") else []
    if sub == "branch":
        if any(f in ("-d", "-D", "--delete") for f in flags):
            return ["git-recovery"]
        if any(f in ("-m", "-M", "--move", "-c", "-C", "--copy", "-f", "--force")
               for f in flags):
            return ["git-branch"]
        listing = any(f in ("-a", "-r", "-l", "--list", "--show-current", "--contains",
                            "--merged", "--no-merged", "-v", "-vv", "--all")
                      for f in flags)
        return ["git-branch"] if names and not listing else []
    if sub == "stash":
        return [] if names and names[0] in ("list", "show") else ["git-branch"]
    if sub == "tag":
        if any(f in ("-d", "--delete") for f in flags):
            return ["git-release", "git-recovery"]
        if not names or any(f in ("-l", "--list", "-n", "--points-at", "--contains",
                                  "--merged", "--no-merged") for f in flags):
            return []
        return ["git-release"]
    return []


def gh_events(args: list[str]) -> list[str]:
    if len(args) >= 2 and args[0] == "pr":
        return {"create": ["git-publication"], "merge": ["git-integration"]}.get(args[1], [])
    if len(args) >= 2 and args[0] == "release" and args[1] in ("create", "edit", "delete"):
        return ["git-release"]
    return []


LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def remote_events(prog: str, args: list[str]) -> list[str]:
    if prog == "ssh":
        if any(a in ("-G", "-V", "-Q") for a in args):
            return []
        opts = _split_opts(args, "bcDEeFIiJLlmOoPpRSWw")
        hosts = [v for o, v in opts if not o]
        if hosts and hosts[0].split("@")[-1] not in LOCAL_HOSTS:
            return ["remote-host"]
        return []
    for a in args:
        m = re.match(r"^(?:[^@/\s]+@)?([A-Za-z0-9._-]+):", a)
        if m and not a.startswith("-") and m.group(1) not in LOCAL_HOSTS:
            return ["remote-host"]
    return []


def tmp_write_targets(cmd: Simple) -> bool:
    if any(under_tmp(resolve(t, cmd.cwd)) for t in cmd.redirects if t):
        return True
    if not cmd.argv:
        return False
    prog = posixpath.basename(cmd.argv[0])
    args = [a for a in cmd.argv[1:] if not a.startswith("-")]
    if prog == "mktemp":
        return True
    if prog in ("mkdir", "touch", "tee") and any(under_tmp(resolve(a, cmd.cwd)) for a in args):
        return True
    if prog in ("cp", "mv", "install", "ln", "rsync") and len(args) >= 2:
        return under_tmp(resolve(args[-1], cmd.cwd))
    return False


def command_events(cmd: Simple) -> list[tuple[str, str]]:
    """(kind, detail) events for one simple command."""
    events: list[tuple[str, str]] = []
    argv = list(cmd.argv)
    if argv and argv[0] == "sudo":
        events.append(("sudo", " ".join(argv[:4])))
        argv = argv[1:]
        while argv and argv[0].startswith("-"):
            opt = argv.pop(0)
            if opt in ("-u", "-g", "-C", "-p", "-h", "-U") and argv:
                argv.pop(0)
    if argv:
        prog = posixpath.basename(argv[0])
        detail = " ".join(argv[:5])
        if prog == "git":
            events += [(k, detail) for k in git_events(argv[1:])]
        elif prog == "gh":
            events += [(k, detail) for k in gh_events(argv[1:])]
        elif prog in ("ssh", "scp", "rsync"):
            events += [(k, detail) for k in remote_events(prog, argv[1:])]
    if tmp_write_targets(Simple(argv, cmd.redirects, cmd.cwd)):
        events.append(("tmp-write", " ".join(argv[:5]) or "redirect"))
    return events


def _sets_errexit(argv: list[str]) -> bool:
    if not argv or argv[0] != "set":
        return False
    args = argv[1:]
    for i, a in enumerate(args):
        if a.startswith("-") and not a.startswith("--") and a[1:].isalpha() and "e" in a[1:]:
            return True
        if a == "-o" and i + 1 < len(args) and args[i + 1] == "errexit":
            return True
    return False


def _runs_script_file(argv: list[str]) -> bool:
    if not argv or posixpath.basename(argv[0]) not in ("bash", "sh"):
        return False
    args = argv[1:]
    if any(a == "-c" or (a.startswith("-") and not a.startswith("--") and "c" in a[1:])
           for a in args):
        return False
    return any(not a.startswith("-") for a in args)


def errexit_flag(command: str) -> bool:
    """True when a multi-line command enables errexit and then runs further lines."""
    lines = [ln for ln in logical_lines(command)
             if ln.strip() and not ln.lstrip().startswith("#")]
    if len(lines) < 2:
        return False
    if any(_runs_script_file(c.argv) for c in simple_commands(command)):
        return False
    for line in lines[:-1]:
        if any(_sets_errexit(c.argv) for c in simple_commands(line)):
            return True
    return False


# --------------------------------------------------------------------------
# Transcript parsing.

def parse_transcript(lines: Iterable[str]) -> dict:
    """Split a transcript into operator turns and collect main-session tool calls."""
    turns: list[dict] = []
    calls: list[dict] = []
    skipped: collections.Counter = collections.Counter()
    sidechain = 0
    invalid = 0
    cur = None
    for raw in lines:
        if not raw.strip():
            continue
        try:
            r = json.loads(raw)
        except json.JSONDecodeError:
            invalid += 1
            continue
        if not isinstance(r, dict):
            invalid += 1
            continue
        t = r.get("type")
        ts = (r.get("timestamp") or "")[:19].replace("T", " ")
        if r.get("isSidechain"):
            sidechain += 1
            continue
        if t not in HANDLED_TYPES:
            skipped[str(t)] += 1
            continue
        if t == "user":
            msg = r.get("message", {})
            content = msg.get("content")
            if isinstance(content, str) and not r.get("isMeta"):
                cur = {"id": f"T{len(turns) + 1:02d}", "start": ts, "prompt": content,
                       "lines": [], "tools": collections.Counter(),
                       "assistant_chars": 0, "assistant_texts": 0, "duration_ms": 0,
                       "errors": 0}
                turns.append(cur)
                cur["lines"].append(f"[{ts}] OPERATOR: {content}")
                continue
            if cur is None:
                continue
            if r.get("isMeta"):
                cur["lines"].append(f"[{ts}] META(injected): {clip(text_of(content), 300)}")
                continue
            for c in content if isinstance(content, list) else []:
                if c.get("type") == "tool_result":
                    body = text_of([c])
                    err = " ERROR" if c.get("is_error") else ""
                    if c.get("is_error"):
                        cur["errors"] += 1
                    cur["lines"].append(f"[{ts}] TOOL_RESULT{err}: {clip(body, 400)}")
                elif c.get("type") == "text":
                    cur["lines"].append(f"[{ts}] USER-TEXT: {clip(c.get('text', ''), 600)}")
        elif t == "assistant" and cur is not None:
            for c in r.get("message", {}).get("content", []):
                ct = c.get("type")
                if ct == "text" and c.get("text", "").strip():
                    cur["assistant_chars"] += len(c["text"])
                    cur["assistant_texts"] += 1
                    cur["lines"].append(f"[{ts}] ASSISTANT: {c['text']}")
                elif ct == "tool_use":
                    name = c.get("name")
                    cur["tools"][name] += 1
                    inp = c.get("input", {}) or {}
                    calls.append({"seq": len(calls), "turn": cur["id"], "ts": ts,
                                  "name": name, "input": inp, "cwd": r.get("cwd") or ""})
                    if name == "Bash":
                        desc = inp.get("description", "")
                        cur["lines"].append(
                            f"[{ts}] TOOL_USE Bash ({desc}): {clip(inp.get('command', ''), 500)}")
                    elif name in ("Edit", "Write"):
                        fp = inp.get("file_path")
                        body = inp.get("new_string", inp.get("content", ""))
                        cur["lines"].append(f"[{ts}] TOOL_USE {name} {fp}: {clip(body, 500)}")
                    else:
                        cur["lines"].append(f"[{ts}] TOOL_USE {name}: {clip(inp, 500)}")
        elif t == "system" and cur is not None and r.get("subtype") == "turn_duration":
            cur["duration_ms"] += r.get("durationMs") or 0
        elif t == "attachment" and cur is not None:
            at = (r.get("attachment") or {}).get("type")
            if at in ("hook_additional_context", "hook_system_message",
                      "ultra_effort_enter", "silent_turn_reminder"):
                cur["lines"].append(f"[{ts}] ATTACHMENT {at}: {clip((r.get('attachment') or {}), 300)}")
    return {"turns": turns, "calls": calls, "skipped_record_types": dict(skipped),
            "sidechain_records": sidechain, "invalid_lines": invalid}


# --------------------------------------------------------------------------
# Reach analysis.

def describe_extent(e: dict) -> str:
    k = e["kind"]
    if k == "lines":
        return f"lines {e['start']}-{e['end'] if e['end'] is not None else 'end'}"
    if k == "tail":
        return f"last {e['n']} lines"
    return k


def summarize_extents(extents: list[dict]) -> str:
    if not extents:
        return "never"
    if any(e["kind"] == "full" for e in extents):
        return "full"
    spans = sorted((e["start"], e["end"]) for e in extents if e["kind"] == "lines")
    merged: list[list] = []
    for s, e in spans:
        if merged and (merged[-1][1] is None or s <= merged[-1][1] + 1):
            if merged[-1][1] is not None:
                merged[-1][1] = None if e is None else max(merged[-1][1], e)
        else:
            merged.append([s, e])
    parts = [f"lines {s}-{'end' if e is None else e}" for s, e in merged]
    other = collections.Counter(describe_extent(e) for e in extents if e["kind"] != "lines")
    parts += [f"{k} x{n}" if n > 1 else k for k, n in sorted(other.items())]
    return "; ".join(parts)


def analyze_reach(parsed: dict) -> dict:
    reads: list[dict] = []
    events: list[dict] = []
    errexit: list[dict] = []
    by_module: dict[str, list[dict]] = collections.defaultdict(list)
    for call in parsed["calls"]:
        name, inp, cwd = call["name"], call["input"], call["cwd"]
        base = {"turn": call["turn"], "seq": call["seq"], "tool": name}
        call_reads: list[tuple[str, str, dict]] = []
        call_events: list[tuple[str, str]] = []
        if name == "Read" and inp.get("file_path"):
            hit = classify(resolve(inp["file_path"], cwd))
            if hit:
                call_reads.append((hit[0], hit[1], read_tool_extent(inp)))
        elif name == "Bash":
            command = inp.get("command", "") or ""
            for cmd in simple_commands(command, cwd):
                call_reads += shell_reads(cmd)
                call_events += command_events(cmd)
            if errexit_flag(command):
                errexit.append({**base, "lines": len(command.splitlines()),
                                "command": clip(command, 300)})
        elif name in EDIT_TOOLS:
            fp = inp.get("file_path") or inp.get("notebook_path") or ""
            call_events.append(("file-edit", f"{name} {fp}"))
            if under_tmp(resolve(fp, cwd)):
                call_events.append(("tmp-write", f"{name} {fp}"))
        elif name == "AskUserQuestion":
            call_events.append(("ask-operator", name))
        elif name in DELEGATION_TOOLS:
            call_events.append(("delegation", clip(inp.get("description") or name, 80)))
        # Reads in a call count before its events: in a compound command the
        # read usually precedes the action it informs.
        for kind, target, extent in call_reads:
            rec = {**base, "kind": kind, "target": target, "extent": extent,
                   "extent_text": describe_extent(extent)}
            reads.append(rec)
            if kind == "rule":
                by_module[target].append(rec)
        for kind, detail in call_events:
            mods = []
            for m in ROUTES[kind]:
                prior = [r["extent"] for r in by_module.get(m, [])]
                mods.append({"module": m, "prior_reads": len(prior),
                             "prior_extent": summarize_extents(prior)})
            events.append({**base, "kind": kind, "detail": clip(detail, 120),
                           "modules": mods})
    modules: dict[str, dict] = {}
    names = sorted(set(KNOWN_MODULES) | set(by_module))
    for m in names:
        rs = by_module.get(m, [])
        evs = [e for e in events if m in ROUTES[e["kind"]]]
        first_event = evs[0] if evs else None
        before = [r for r in rs if first_event and r["seq"] <= first_event["seq"]]
        modules[m] = {
            "reads": len(rs),
            "first_read_turn": rs[0]["turn"] if rs else None,
            "extent": summarize_extents([r["extent"] for r in rs]),
            "routed_events": len(evs),
            "first_event_turn": first_event["turn"] if first_event else None,
            "read_before_first_event": bool(before) if first_event else None,
        }
    return {"modules": modules, "reads": reads, "events": events, "errexit": errexit,
            "skipped_record_types": parsed["skipped_record_types"],
            "sidechain_records": parsed["sidechain_records"],
            "invalid_lines": parsed["invalid_lines"],
            "routes": {k: list(v) for k, v in ROUTES.items()}}


# --------------------------------------------------------------------------
# Output.

def check_out_dir(out: Path) -> Path:
    resolved = out.expanduser().resolve()
    if resolved == REPO_ROOT or resolved.is_relative_to(REPO_ROOT):
        raise OutDirError(f"refusing to write inside the repository: {resolved}")
    return resolved


def _cell(s: Any) -> str:
    return str(s).replace("|", "/").replace("\n", " ")


def render_reach(reach: dict) -> str:
    out = ["# Rule reach", "",
           "Heuristic: a gap is a lead to read the turn, not a verdict. "
           "Adapters loaded at session start are not tool reads and do not appear.", "",
           "## Modules", "",
           "| Module | Reads | First read | Extent | Routed events | First event | Read before first event |",
           "|---|---|---|---|---|---|---|"]
    for m, d in reach["modules"].items():
        rb = {True: "yes", False: "**no**", None: "-"}[d["read_before_first_event"]]
        out.append(f"| {m} | {d['reads']} | {d['first_read_turn'] or '-'} | {d['extent']} "
                   f"| {d['routed_events']} | {d['first_event_turn'] or '-'} | {rb} |")
    out += ["", "## Reads", "", "| Turn | Tool | Kind | File | Extent |", "|---|---|---|---|---|"]
    for r in reach["reads"]:
        out.append(f"| {r['turn']} | {r['tool']} | {r['kind']} | {_cell(r['target'])} "
                   f"| {r['extent_text']} |")
    out += ["", "## Routed events", "",
            "| Turn | Event | Detail | Modules (prior reads: extent) |", "|---|---|---|---|"]
    for e in reach["events"]:
        mods = ", ".join(f"{m['module']} ({m['prior_reads']}: {m['prior_extent']})"
                         for m in e["modules"])
        out.append(f"| {e['turn']} | {e['kind']} | {_cell(e['detail'])} | {mods} |")
    out += ["", "## Errexit in multi-line Bash commands", "",
            "The Claude Code Bash tool does not stop on `set -e` between lines "
            "(`claude-runtime.md` Bash Tool).", ""]
    if reach["errexit"]:
        out += ["| Turn | Lines | Command |", "|---|---|---|"]
        out += [f"| {x['turn']} | {x['lines']} | `{_cell(x['command'])}` |"
                for x in reach["errexit"]]
    else:
        out.append("None found.")
    out += ["", "## Skipped records", "",
            f"- Sidechain records: {reach['sidechain_records']}",
            f"- Invalid lines: {reach['invalid_lines']}"]
    for t, n in sorted(reach["skipped_record_types"].items()):
        out.append(f"- Unhandled type `{t}`: {n}")
    return "\n".join(out) + "\n"


def write_outputs(parsed: dict, reach: dict, out: Path) -> None:
    (out / "turns").mkdir(parents=True, exist_ok=True)
    index = ["| Turn | Start (UTC) | Duration s | Tool calls | Assistant chars | Errors | Operator prompt |",
             "|---|---|---|---|---|---|---|"]
    metrics = []
    for tr in parsed["turns"]:
        tid = tr["id"]
        with open(out / "turns" / f"{tid}.md", "w", encoding="utf-8") as fh:
            fh.write(f"# {tid}  start {tr['start']} UTC  duration {tr['duration_ms']/1000:.0f}s  tools {dict(tr['tools'])}\n\n")
            fh.write("\n".join(tr["lines"]) + "\n")
        ntool = sum(tr["tools"].values())
        index.append(f"| {tid} | {tr['start']} | {tr['duration_ms']/1000:.0f} | {ntool} | {tr['assistant_chars']} | {tr['errors']} | {clip(tr['prompt'].replace('|', '/').replace(chr(10), ' '), 70)} |")
        metrics.append({"turn": tid, "start": tr["start"], "duration_s": round(tr["duration_ms"]/1000),
                        "tool_calls": dict(tr["tools"]), "tool_call_total": ntool,
                        "assistant_chars": tr["assistant_chars"], "errors": tr["errors"],
                        "prompt": tr["prompt"]})
    (out / "index.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    with open(out / "metrics.json", "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, ensure_ascii=False, indent=1)
    (out / "reach.md").write_text(render_reach(reach), encoding="utf-8")
    with open(out / "reach.json", "w", encoding="utf-8") as fh:
        json.dump(reach, fh, ensure_ascii=False, indent=1)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("transcript", type=Path, help="Claude Code session transcript (.jsonl)")
    ap.add_argument("out_dir", type=Path, help="output directory outside this repository")
    args = ap.parse_args(argv)
    try:
        out = check_out_dir(args.out_dir)
    except OutDirError as exc:
        print(f"session_digest: {exc}", file=sys.stderr)
        return 2
    with open(args.transcript, encoding="utf-8") as fh:
        parsed = parse_transcript(fh)
    reach = analyze_reach(parsed)
    write_outputs(parsed, reach, out)
    print(f"{len(parsed['turns'])} turns, {len(reach['reads'])} rule/adapter reads, "
          f"{len(reach['events'])} routed events, {len(reach['errexit'])} errexit flags "
          f"written to {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

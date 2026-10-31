#!/usr/bin/env python3
"""Validate workspace-meta documentation boundaries and routing contracts."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
ROOT_MARKDOWN_ALLOWLIST = {
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "feedback-register.md",
}
DATE_PATTERN = re.compile(r"\b20\d{2}-\d{2}-\d{2}\b")
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
CLAUDE_ADAPTER = "CLAUDE.md"
CODEX_ADAPTER = ".agents/host-templates/codex-AGENTS.md"
# Each agent runtime module is routed by its own agent's adapter only; every
# other rule file is portable and routed by both adapters.
RUNTIME_MODULES = {
    "claude-runtime.md": CLAUDE_ADAPTER,
    "codex-runtime.md": CODEX_ADAPTER,
}
DESIGN_MAP = "docs/architecture/design-map.md"
BACKLOG = "docs/backlog.md"
# Review records are temporary: none is tracked, and no current document
# links one or a running plan (documentation.md Committed And Temporary
# Records).
RECORD_DIRECTORIES = ("docs/reviews", "docs/plans")
# Current documents whose links are checked but whose dates are not: the evals
# README keeps a labeled snapshot.
LINK_CHECKED_DOCUMENTS = ("evals/rules/README.md", ".agents/env/README.md")
REQUESTS_OWNER = ".agents/rules/requests.md"
# The resident request-reading sentence both adapters carry above their
# routing tables, and the phrases it shares with its owner.
REQUEST_SENTENCE_START = "Before starting work on a request"
REQUEST_SENTENCE_PHRASES = (
    "what done means",
    "similar problems",
    "redirect the work",
    "away",
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _normalize(text: str) -> str:
    return " ".join(text.split()).lower()


def _routing_block(content: str) -> str:
    return content.split("## Direct Task Routing", 1)[1].split("\n## ", 1)[0]


def _current_documents(root: Path) -> list[Path]:
    paths = [root / name for name in ROOT_MARKDOWN_ALLOWLIST]
    for relative in (
        ".agents/rules",
        ".agents/host-templates",
        "docs/architecture",
        "docs/runbooks",
        "docs/standards",
    ):
        paths.extend(sorted((root / relative).rglob("*.md")))
    paths.append(root / BACKLOG)
    return [path for path in paths if path.is_file()]


def _anchor_slug(heading: str) -> str:
    heading = re.sub(r"[`*_~]", "", heading.strip().lower())
    heading = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE)
    return re.sub(r"[ -]+", "-", heading).strip("-")


def _anchors(path: Path) -> set[str]:
    result: set[str] = set()
    counts: dict[str, int] = {}
    for line in _read(path).splitlines():
        match = re.match(r"^#{1,6}\s+(.+?)\s*$", line)
        if not match:
            continue
        base = _anchor_slug(match.group(1))
        count = counts.get(base, 0)
        counts[base] = count + 1
        result.add(base if count == 0 else f"{base}-{count}")
    return result


def _without_fenced_code(content: str) -> str:
    """Remove fenced code blocks while preserving prose and inline code text."""
    result: list[str] = []
    fence_character: str | None = None
    fence_length = 0
    for line in content.splitlines(keepends=True):
        if fence_character is not None:
            closing = re.match(
                r"^[ \t]{0,3}(`{3,}|~{3,})[ \t]*(?:\r?\n)?$", line
            )
            if (
                closing
                and closing.group(1)[0] == fence_character
                and len(closing.group(1)) >= fence_length
            ):
                fence_character = None
                fence_length = 0
            continue

        opening = re.match(r"^[ \t]{0,3}(`{3,}|~{3,})", line)
        if opening:
            fence_character = opening.group(1)[0]
            fence_length = len(opening.group(1))
            continue
        result.append(line)
    return "".join(result)


def _visible_prose(content: str) -> str:
    content = _without_fenced_code(content)
    content = LINK_PATTERN.sub(lambda match: match.group(1), content)
    return content.replace("`", "")


def _check_root_entries(root: Path, errors: list[str]) -> None:
    actual = {path.name for path in root.glob("*.md")}
    extra = sorted(actual - ROOT_MARKDOWN_ALLOWLIST)
    missing = sorted(ROOT_MARKDOWN_ALLOWLIST - actual)
    if extra:
        errors.append(f"root Markdown entry is not allowlisted: {', '.join(extra)}")
    if missing:
        errors.append(f"required root Markdown entry is missing: {', '.join(missing)}")


def _check_routes(root: Path, errors: list[str]) -> None:
    rules_dir = root / ".agents/rules"
    rule_names = {path.name for path in rules_dir.glob("*.md")}
    claude = _read(root / CLAUDE_ADAPTER)
    routes = {
        CLAUDE_ADAPTER: _routing_block(claude),
        CODEX_ADAPTER: _routing_block(_read(root / CODEX_ADAPTER)),
    }
    for name in sorted(rule_names - set(RUNTIME_MODULES)):
        for adapter, content in routes.items():
            if name not in content:
                errors.append(f"{Path(adapter).name} does not route to {name}")
    for name, owner in sorted(RUNTIME_MODULES.items()):
        for adapter, content in routes.items():
            label = Path(adapter).name
            if adapter == owner and name not in content:
                errors.append(f"{label} does not route to {name}")
            if adapter != owner and name in content:
                errors.append(
                    f"{label} routes to another agent's runtime module: {name}"
                )

    documentation = _normalize(_read(rules_dir / "documentation.md"))
    normalized_claude = _normalize(claude)
    required = (
        "before substantive project work",
        "including read-only review or any host/external action",
    )
    for phrase in required:
        if phrase not in documentation or phrase not in normalized_claude:
            errors.append(f"missing-project-entry backstop lacks: {phrase}")


def _safety_floor(content: str) -> str:
    return content.split("## Safety Floor", 1)[1].split(
        "## Direct Task Routing", 1
    )[0]


def _check_safety_floor(root: Path, errors: list[str]) -> None:
    claude = _safety_floor(_read(root / "CLAUDE.md"))
    codex = _safety_floor(_read(root / ".agents/host-templates/codex-AGENTS.md"))
    if claude != codex:
        errors.append("Claude and Codex safety floors differ")

    source_checks = (
        ("git.md", "switch away from", "switch away from"),
        ("authorization.md", "technical permission", "technical permission"),
        (
            "git-publication.md",
            "working-tree edit authority",
            "working-tree edit authority",
        ),
        ("secrets.md", "real credentials", "real secrets"),
        ("git-publication.md", "co-authored-by", "co-authored-by"),
        ("environment-truth.md", "dated snapshots", "environment/remote claims"),
        (
            "reasoning.md",
            "validate premises proportionally",
            "validate load-bearing premises proportionally",
        ),
        (
            "reasoning.md",
            "decisions remain authoritative as decisions; "
            "they are not empirical evidence",
            "technical conclusions distinct from assumptions and operator decisions",
        ),
        ("verification.md", "cannot run", "checks that cannot"),
        (
            "file-checks.md",
            "before it is reported done",
            "before calling a created or changed file done",
        ),
    )
    normalized_floor = _normalize(claude)
    for owner, owner_phrase, floor_phrase in source_checks:
        owner_text = _normalize(_read(root / ".agents/rules" / owner))
        if owner_phrase not in owner_text:
            errors.append(f"canonical safety source {owner} lacks: {owner_phrase}")
        if floor_phrase not in normalized_floor:
            errors.append(f"adapter safety floor lacks: {floor_phrase}")
        if f"`{owner}`" not in claude:
            errors.append(f"adapter safety floor does not name source: {owner}")


def _check_index(root: Path, errors: list[str]) -> None:
    readme = _read(root / "README.md")
    for target in (
        ".agents/host-templates/README-agents.md",
        "docs/architecture/codex-config-management.md",
        DESIGN_MAP,
        "docs/runbooks/new-vps.md",
        "docs/standards/README.md",
        BACKLOG,
        "feedback-register.md",
    ):
        if target not in readme:
            errors.append(f"README documentation map lacks: {target}")


def _check_design_map(root: Path, errors: list[str]) -> None:
    """Require the design map to catalog every rule owner by a real link."""
    design_map = root / DESIGN_MAP
    if not design_map.is_file():
        errors.append(f"design map is missing: {DESIGN_MAP}")
        return
    linked = {
        target.strip().strip("<>").split(maxsplit=1)[0].partition("#")[0]
        for _, target in LINK_PATTERN.findall(
            _without_fenced_code(_read(design_map))
        )
    }
    for path in sorted((root / ".agents/rules").glob("*.md")):
        if f"../../.agents/rules/{path.name}" not in linked:
            errors.append(f"design map does not link rule owner: {path.name}")


def _request_sentence(content: str) -> str | None:
    for paragraph in _routing_block(content).split("\n\n"):
        if paragraph.strip().startswith(REQUEST_SENTENCE_START):
            # The adapters differ only in how they write the rule path.
            return _normalize(paragraph.replace("~/workspace/", ""))
    return None


def _check_request_sentence(root: Path, errors: list[str]) -> None:
    """Keep the adapters' resident request-reading sentence tied to its owner."""
    sentences = {}
    for label in (CLAUDE_ADAPTER, CODEX_ADAPTER):
        sentence = _request_sentence(_read(root / label))
        if sentence is None:
            errors.append(f"{label} lacks the request-reading sentence")
        else:
            sentences[label] = sentence
    if len(set(sentences.values())) > 1:
        errors.append("the adapters' request-reading sentences differ")
    owner = _normalize(_read(root / REQUESTS_OWNER))
    for phrase in REQUEST_SENTENCE_PHRASES:
        for label, sentence in sentences.items():
            if phrase not in sentence:
                errors.append(f"{label} request-reading sentence lacks: {phrase}")
        if phrase not in owner:
            errors.append(f"{REQUESTS_OWNER} lacks the adapters' phrase: {phrase}")


def _check_links(root: Path, errors: list[str]) -> None:
    anchor_cache: dict[Path, set[str]] = {}
    sources = _current_documents(root)
    sources.extend(
        path
        for path in (root / name for name in LINK_CHECKED_DOCUMENTS)
        if path.is_file()
    )
    for source in sources:
        for _, raw_target in LINK_PATTERN.findall(_read(source)):
            target = raw_target.strip().strip("<>").split(maxsplit=1)[0]
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            path_text, _, fragment = target.partition("#")
            destination = source if not path_text else (source.parent / unquote(path_text))
            destination = destination.resolve()
            try:
                relative_destination = destination.relative_to(root.resolve())
            except ValueError:
                continue
            if relative_destination.parts[:1] == ("projects",):
                continue
            if relative_destination.as_posix().startswith(
                tuple(f"{directory}/" for directory in RECORD_DIRECTORIES)
            ) or relative_destination.as_posix() in RECORD_DIRECTORIES:
                errors.append(
                    f"current document links a review record or running plan: "
                    f"{source.relative_to(root)}: {raw_target}"
                )
                continue
            if not destination.exists():
                errors.append(
                    f"broken link in {source.relative_to(root)}: {raw_target}"
                )
                continue
            if fragment and destination.is_file():
                anchors = anchor_cache.setdefault(destination, _anchors(destination))
                if unquote(fragment) not in anchors:
                    errors.append(
                        f"broken anchor in {source.relative_to(root)}: {raw_target}"
                    )


def _check_truth_lifecycle(root: Path, errors: list[str]) -> None:
    for path in _current_documents(root):
        # The register and the backlog record when decisions were made.
        if path.name == "feedback-register.md" or path == root / BACKLOG:
            continue
        content = _visible_prose(_read(path))
        if DATE_PATTERN.search(content):
            errors.append(
                f"dated observation belongs in the register, the backlog, a commit "
                f"message, or the evidence store: {path.relative_to(root)}"
            )


def _check_review_records(root: Path, errors: list[str]) -> None:
    if not (root / ".git").exists():
        return
    result = subprocess.run(
        ["git", "-C", str(root), "ls-files", "-z", "--", *RECORD_DIRECTORIES],
        capture_output=True,
        check=False,
        text=True,
    )
    for tracked in filter(None, result.stdout.split("\0")):
        # A tracked record deleted in the working tree leaves with the change
        # that deletes it, as in scripts/verify_committed_copy.sh.
        path = root / tracked
        if path.exists() or path.is_symlink():
            errors.append(f"review record or running plan is tracked: {tracked}")


def _check_runbook(root: Path, errors: list[str]) -> None:
    runbook = _read(root / "docs/runbooks/new-vps.md")
    for number, title in (
        ("0", "先理解边界"),
        ("1", "前置条件"),
        ("2", "获取 workspace-meta"),
        ("3", "放置独立项目"),
        ("4", "初始化本机环境快照"),
        ("5", "配置 Codex 的主机私有策略"),
        ("6", "安装 workspace-meta 集成"),
        ("7", "修改后如何让它生效"),
        ("8", "日常使用"),
        ("9", "常见故障"),
        ("10", "安全和发布底线"),
        ("11", "交接记录模板"),
    ):
        if f"## {number}. {title}" not in runbook:
            errors.append(f"new VPS runbook lacks section {number}: {title}")
    for phrase in (
        "Protected-Action Request Brief",
        "Risk / recovery",
        "Exact operation:",
    ):
        if phrase not in runbook:
            errors.append(f"new VPS runbook lacks safety contract: {phrase}")


def _check_tracked_routes(root: Path, errors: list[str]) -> None:
    if not (root / ".git").exists():
        return
    required = [
        root / "CLAUDE.md",
        root / ".agents/host-templates/codex-AGENTS.md",
    ]
    required.extend(sorted((root / ".agents/rules").glob("*.md")))
    for path in required:
        result = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "ls-files",
                "--error-unmatch",
                str(path.relative_to(root)),
            ],
            capture_output=True,
            check=False,
            text=True,
        )
        if result.returncode != 0:
            errors.append(f"routed documentation is not tracked: {path.relative_to(root)}")


def check(root: Path = ROOT) -> list[str]:
    errors: list[str] = []
    _check_root_entries(root, errors)
    _check_routes(root, errors)
    _check_safety_floor(root, errors)
    _check_index(root, errors)
    _check_design_map(root, errors)
    _check_request_sentence(root, errors)
    _check_links(root, errors)
    _check_truth_lifecycle(root, errors)
    _check_runbook(root, errors)
    _check_tracked_routes(root, errors)
    _check_review_records(root, errors)
    return errors


def main() -> int:
    errors = check()
    if errors:
        for error in errors:
            print(f"documentation gate: {error}", file=sys.stderr)
        return 1
    print("documentation gate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

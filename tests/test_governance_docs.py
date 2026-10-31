from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import shutil
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_documentation", ROOT / "scripts/check_documentation.py"
)
assert SPEC and SPEC.loader
DOCS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DOCS)


class GovernanceDocumentationTests(unittest.TestCase):
    def fixture(self) -> tuple[tempfile.TemporaryDirectory[str], Path]:
        temporary = tempfile.TemporaryDirectory()
        root = Path(temporary.name)
        for name in DOCS.ROOT_MARKDOWN_ALLOWLIST:
            shutil.copy2(ROOT / name, root / name)
        for relative in (
            ".agents/rules",
            ".agents/host-templates",
            "docs/architecture",
            "docs/runbooks",
            "docs/standards",
        ):
            shutil.copytree(ROOT / relative, root / relative)
        shutil.copy2(ROOT / DOCS.BACKLOG, root / DOCS.BACKLOG)
        return temporary, root

    def test_repository_documentation_passes(self) -> None:
        self.assertEqual(DOCS.check(ROOT), [])

    def test_rejects_an_unallowlisted_root_entry(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / "EXTRA.md").write_text("# Extra\n")
        self.assertTrue(
            any("not allowlisted" in error for error in DOCS.check(root))
        )

    def test_rejects_a_missing_required_root_entry(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / "feedback-register.md").unlink()
        self.assertTrue(
            any(
                "required root Markdown entry is missing" in error
                for error in DOCS.check(root)
            )
        )

    def test_rejects_a_write_only_missing_entry_backstop(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        claude = root / "CLAUDE.md"
        claude.write_text(
            claude.read_text().replace(
                "before substantive project", "before the first write"
            )
        )
        self.assertTrue(any("backstop lacks" in error for error in DOCS.check(root)))

    def test_rejects_safety_floor_drift(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        codex = root / ".agents/host-templates/codex-AGENTS.md"
        codex.write_text(codex.read_text().replace("switch away from, ", ""))
        self.assertTrue(any("safety floor" in error for error in DOCS.check(root)))

    def test_rejects_identically_drifted_safety_floor_copies(self) -> None:
        mutations = (
            (r"switch away from, ", ""),
            (
                r"keep\s+technical\s+conclusions\s+distinct\s+from\s+"
                r"assumptions\s+and\s+operator\s+decisions",
                "keep technical conclusions evidence-based",
            ),
        )
        for pattern, replacement in mutations:
            with self.subTest(pattern=pattern):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                for path in (
                    root / "CLAUDE.md",
                    root / ".agents/host-templates/codex-AGENTS.md",
                ):
                    mutated, count = re.subn(pattern, replacement, path.read_text())
                    self.assertEqual(count, 1, path)
                    path.write_text(mutated)
                self.assertTrue(
                    any(
                        "adapter safety floor lacks" in error
                        for error in DOCS.check(root)
                    )
                )

    def test_rejects_reasoning_canonical_source_drift(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        reasoning = root / ".agents/rules/reasoning.md"
        reasoning.write_text(
            reasoning.read_text().replace(
                "they are not empirical evidence",
                "they are accepted empirical evidence",
            )
        )
        self.assertTrue(
            any(
                "canonical safety source reasoning.md lacks" in error
                for error in DOCS.check(root)
            )
        )

    def test_rejects_dated_current_guidance_and_broken_links(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        architecture = root / "docs/architecture/codex-config-management.md"
        with architecture.open("a") as stream:
            stream.write("\nObserved 2026-09-06. [missing](missing.md)\n")
        errors = DOCS.check(root)
        self.assertTrue(any("dated observation" in error for error in errors))
        self.assertTrue(any("broken link" in error for error in errors))

    def test_rejects_dates_in_visible_inline_markdown(self) -> None:
        snippets = (
            "\nObserved in `2026-07-11`.\n",
            "\n[2026-07-11 verification](../runbooks/new-vps.md)\n",
        )
        for snippet in snippets:
            with self.subTest(snippet=snippet):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                architecture = root / "docs/architecture/codex-config-management.md"
                architecture.write_text(architecture.read_text() + snippet)
                self.assertTrue(
                    any("dated observation" in error for error in DOCS.check(root))
                )

    def test_ignores_dates_in_fenced_code_and_link_destinations(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        architecture = root / "docs/architecture/codex-config-management.md"
        architecture.write_text(
            architecture.read_text()
            + "\n```text\nObserved 2026-07-11.\n```\n"
            + "[release notes](https://example.com/releases/2026-07-11)\n"
        )
        self.assertFalse(
            any("dated observation" in error for error in DOCS.check(root))
        )

    def test_allows_dates_in_the_backlog(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        backlog = root / DOCS.BACKLOG
        backlog.write_text(backlog.read_text() + "\nDeferred on 2026-07-11.\n")
        self.assertFalse(
            any("dated observation" in error for error in DOCS.check(root))
        )

    def test_rejects_a_link_to_a_review_record_or_running_plan(self) -> None:
        architecture = "docs/architecture/codex-config-management.md"
        for source, target in (
            (architecture, "../reviews/topic/record.md"),
            (architecture, "../plans/topic.md"),
            (architecture, "../plans/"),
            (DOCS.BACKLOG, "plans/topic.md"),
            ("evals/rules/README.md", "../../docs/plans/topic.md"),
        ):
            with self.subTest(source=source, target=target):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                path = root / source
                path.parent.mkdir(parents=True, exist_ok=True)
                text = path.read_text() if path.exists() else "# Document\n"
                path.write_text(text + f"\n[record]({target})\n")
                self.assertIn(
                    "current document links a review record or running plan: "
                    f"{source}: {target}",
                    DOCS.check(root),
                )

    def test_checks_nested_current_documents(self) -> None:
        for directory in ("docs/architecture", "docs/standards"):
            with self.subTest(directory=directory):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                nested = root / directory / "nested/current.md"
                nested.parent.mkdir()
                nested.write_text("Observed 2026-07-11. [missing](missing.md)\n")
                errors = DOCS.check(root)
                self.assertTrue(
                    any(
                        "dated observation" in error and "nested/current.md" in error
                        for error in errors
                    )
                )
                self.assertTrue(
                    any(
                        "broken link" in error and "nested/current.md" in error
                        for error in errors
                    )
                )

    def test_rejects_a_missing_rule_route(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        claude = root / "CLAUDE.md"
        claude.write_text(
            claude.read_text().replace("capabilities.md", "missing.md")
        )
        self.assertTrue(
            any(
                "CLAUDE.md does not route to capabilities.md" in error
                for error in DOCS.check(root)
            )
        )

    def test_rejects_a_runtime_module_routed_by_the_other_adapter(self) -> None:
        for adapter, module in (
            ("CLAUDE.md", "codex-runtime.md"),
            (".agents/host-templates/codex-AGENTS.md", "claude-runtime.md"),
        ):
            with self.subTest(adapter=adapter):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                path = root / adapter
                head, routing = path.read_text().split("## Direct Task Routing", 1)
                self.assertIn("|---|---|\n", routing)
                routing = routing.replace(
                    "|---|---|\n",
                    f"|---|---|\n| runtime mechanics | `.agents/rules/{module}` |\n",
                    1,
                )
                path.write_text(head + "## Direct Task Routing" + routing)
                self.assertIn(
                    f"{Path(adapter).name} routes to another agent's runtime "
                    f"module: {module}",
                    DOCS.check(root),
                )

    def test_rejects_a_runtime_module_missing_from_its_own_adapter(self) -> None:
        for adapter, module in (
            ("CLAUDE.md", "claude-runtime.md"),
            (".agents/host-templates/codex-AGENTS.md", "codex-runtime.md"),
        ):
            with self.subTest(adapter=adapter):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                path = root / adapter
                path.write_text(path.read_text().replace(module, "missing.md"))
                self.assertIn(
                    f"{Path(adapter).name} does not route to {module}",
                    DOCS.check(root),
                )

    def test_rejects_a_rule_owner_missing_from_the_design_map(self) -> None:
        fenced_link = "\n```text\n[new](../../.agents/rules/new-owner.md)\n```\n"
        for map_addition in ("", fenced_link):
            with self.subTest(map_addition=map_addition):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                (root / ".agents/rules/new-owner.md").write_text(
                    "# New Owner\n\n## Ownership\n"
                )
                design_map = root / "docs/architecture/design-map.md"
                design_map.write_text(design_map.read_text() + map_addition)
                self.assertIn(
                    "design map does not link rule owner: new-owner.md",
                    DOCS.check(root),
                )

    def test_rejects_a_missing_design_map(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / "docs/architecture/design-map.md").unlink()
        self.assertIn(
            "design map is missing: docs/architecture/design-map.md",
            DOCS.check(root),
        )

    def test_rejects_drift_in_the_request_reading_sentence(self) -> None:
        cases = (
            (
                ".agents/host-templates/codex-AGENTS.md",
                "and not while the operator is away",
                "and while the operator is away",
                "the adapters' request-reading sentences differ",
            ),
            (
                "CLAUDE.md",
                "what done means",
                "what finished looks like",
                "CLAUDE.md request-reading sentence lacks: what done means",
            ),
            (
                ".agents/rules/requests.md",
                "what done means",
                "the finished state",
                ".agents/rules/requests.md lacks the adapters' phrase: what done means",
            ),
            (
                "CLAUDE.md",
                "Before starting work on a request",
                "Before any work",
                "CLAUDE.md lacks the request-reading sentence",
            ),
        )
        for relative, old, new, expected in cases:
            with self.subTest(file=relative, expected=expected):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                path = root / relative
                text = path.read_text()
                self.assertIn(old, text)
                # An owner keeps a phrase as long as any copy remains, so the
                # owner case removes every copy; an adapter case changes one.
                count = -1 if relative.startswith(".agents/rules/") else 1
                path.write_text(text.replace(old, new, count))
                self.assertIn(expected, DOCS.check(root))

    def test_rejects_a_missing_readme_index_target(self) -> None:
        for target in (
            "docs/runbooks/new-vps.md",
            "docs/standards/README.md",
            "docs/architecture/design-map.md",
            "docs/backlog.md",
        ):
            with self.subTest(target=target):
                temporary, root = self.fixture()
                self.addCleanup(temporary.cleanup)
                readme = root / "README.md"
                readme.write_text(readme.read_text().replace(target, "missing.md"))
                self.assertTrue(
                    any(
                        "README documentation map lacks" in error
                        for error in DOCS.check(root)
                    )
                )

    def test_rejects_a_missing_runbook_contract(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        runbook = root / "docs/runbooks/new-vps.md"
        runbook.write_text(
            runbook.read_text().replace("## 9. 常见故障", "## Missing")
        )
        self.assertTrue(
            any("new VPS runbook lacks section 9" in error for error in DOCS.check(root))
        )

    def test_rejects_a_broken_anchor(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        readme = root / "README.md"
        readme.write_text(
            readme.read_text() + "\n[missing section](#not-an-anchor)\n"
        )
        self.assertTrue(any("broken anchor" in error for error in DOCS.check(root)))

    def test_rejects_an_untracked_routed_document(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / ".git").mkdir()
        errors: list[str] = []
        with mock.patch.object(
            DOCS.subprocess, "run", return_value=mock.Mock(returncode=1)
        ):
            DOCS._check_tracked_routes(root, errors)
        self.assertTrue(
            any("routed documentation is not tracked" in error for error in errors)
        )

    def test_rejects_a_tracked_review_record(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        (root / ".git").mkdir()
        for relative in ("docs/reviews/topic/record.md", "docs/plans/topic.md"):
            path = root / relative
            path.parent.mkdir(parents=True)
            path.write_text("# Record\n")
        errors: list[str] = []
        # gone.md is tracked but deleted in the working tree, so the change that
        # deletes it removes it.
        listed = (
            "docs/reviews/topic/record.md\0docs/reviews/topic/gone.md\0"
            "docs/plans/topic.md\0"
        )
        with mock.patch.object(
            DOCS.subprocess,
            "run",
            return_value=mock.Mock(returncode=0, stdout=listed),
        ) as run:
            DOCS._check_review_records(root, errors)
        command = run.call_args.args[0]
        self.assertEqual(
            command[command.index("--") + 1 :], ["docs/reviews", "docs/plans"]
        )
        self.assertEqual(
            errors,
            [
                "review record or running plan is tracked: docs/reviews/topic/record.md",
                "review record or running plan is tracked: docs/plans/topic.md",
            ],
        )


if __name__ == "__main__":
    unittest.main()

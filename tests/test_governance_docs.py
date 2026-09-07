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
            "docs/reviews",
        ):
            shutil.copytree(ROOT / relative, root / relative)
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
            "\n[2026-07-11 verification]"
            "(../reviews/refactor-codex-sync/round1-2026-07-11.changelog.md)\n",
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
            + "[verification record](../reviews/refactor-codex-sync/round1-2026-07-11.changelog.md)\n"
        )
        self.assertFalse(
            any("dated observation" in error for error in DOCS.check(root))
        )

    def test_checks_nested_current_documents(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        nested = root / "docs/architecture/nested/current.md"
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

    def test_rejects_a_missing_readme_index_target(self) -> None:
        temporary, root = self.fixture()
        self.addCleanup(temporary.cleanup)
        readme = root / "README.md"
        readme.write_text(
            readme.read_text().replace("docs/runbooks/new-vps.md", "missing.md")
        )
        self.assertTrue(
            any("README documentation map lacks" in error for error in DOCS.check(root))
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


if __name__ == "__main__":
    unittest.main()

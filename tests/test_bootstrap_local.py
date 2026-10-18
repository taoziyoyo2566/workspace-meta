from __future__ import annotations

import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAMES = tuple(
    sorted(
        template.name.removesuffix("-SKILL.md")
        for template in (ROOT / ".agents" / "host-templates").glob("*-SKILL.md")
    )
)
SKILL_MARKER = "<!-- workspace-meta managed skill: make sync replaces this file -->"


class BootstrapLocalTests(unittest.TestCase):
    """Run scripts/bootstrap-local.sh in a copied repository with a temp HOME."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.repo = base / "repo"
        shutil.copytree(ROOT / "scripts", self.repo / "scripts")
        shutil.copytree(
            ROOT / ".agents" / "host-templates",
            self.repo / ".agents" / "host-templates",
        )
        subprocess.run(
            ["git", "init", "-q", str(self.repo)],
            check=True,
            env=self.git_env(base),
        )
        self.home = base / "home"
        self.home.mkdir()
        self.codex_home = self.home / ".codex"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    @staticmethod
    def git_env(home: Path) -> dict[str, str]:
        env = os.environ.copy()
        env.pop("GIT_CONFIG_GLOBAL", None)
        env["HOME"] = str(home)
        env["XDG_CONFIG_HOME"] = str(home / ".config")
        env["GIT_CONFIG_NOSYSTEM"] = "1"
        return env

    def env(self, claude_config_dirs: str | None = None) -> dict[str, str]:
        # A session's own CLAUDE_CONFIG_DIR and CLAUDE_CONFIG_DIRS name real
        # config dirs; every run here sees only the temp HOME.
        env = self.git_env(self.home)
        env.pop("CLAUDE_CONFIG_DIR", None)
        env.pop("CLAUDE_CONFIG_DIRS", None)
        env["CODEX_HOME"] = str(self.codex_home)
        env["WORKSPACE_META_PYTHON"] = sys.executable
        if claude_config_dirs is not None:
            env["CLAUDE_CONFIG_DIRS"] = claude_config_dirs
        return env

    def run_bootstrap(self, claude_config_dirs: str | None = None):
        return subprocess.run(
            [str(self.repo / "scripts" / "bootstrap-local.sh")],
            cwd=self.repo,
            env=self.env(claude_config_dirs),
            capture_output=True,
            check=False,
            text=True,
        )

    def stub_python_away(self) -> None:
        (self.repo / "scripts" / "find_python.sh").write_text(
            "#!/usr/bin/env bash\nexit 1\n", encoding="utf-8"
        )

    def config_dir(self, name: str, *, state: bool = True) -> Path:
        directory = self.home / name
        directory.mkdir()
        if state:
            (directory / ".claude.json").write_text("{}", encoding="utf-8")
        return directory

    def snapshot(self) -> dict[str, tuple[bytes, int]]:
        return {
            str(path.relative_to(self.home)): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in sorted(self.home.rglob("*"))
            if path.is_file()
        }

    def hooks_path(self) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), "config", "--local", "--get", "core.hooksPath"],
            capture_output=True,
            check=False,
            env=self.git_env(self.home),
            text=True,
        ).stdout.strip()

    def assert_skills(self, directory: Path) -> None:
        for name in SKILL_NAMES:
            installed = directory / "skills" / name / "SKILL.md"
            template = self.repo / ".agents" / "host-templates" / f"{name}-SKILL.md"
            self.assertEqual(installed.read_bytes(), template.read_bytes(), installed)

    def assert_untouched(self, directory: Path) -> None:
        self.assertEqual(
            [path.name for path in directory.iterdir()], [".claude.json"], directory
        )

    def test_discovery_picks_relocated_dirs_and_skips_backup_copies(self) -> None:
        self.assertTrue(SKILL_NAMES)
        team = self.config_dir(".claude-work")
        backup = self.config_dir(".claude-work.bak-20261017")

        completed = self.run_bootstrap()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Claude config dirs (CLAUDE_CONFIG_DIRS):\n"
            "  ~/.claude\n"
            "  ~/.claude-work\n",
            completed.stdout,
        )
        self.assertIn(
            '  ~/.claude-work.bak-20261017: name has the part "bak"\n',
            completed.stdout,
        )
        for directory in (self.home / ".claude", team):
            self.assertTrue((directory / "settings.json").is_file())
            self.assert_skills(directory)
        self.assert_untouched(backup)
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())
        self.assertTrue((self.codex_home / "config.toml").is_file())
        self.assertEqual(self.hooks_path(), ".githooks")

    def test_explicit_colon_list_installs_settings_and_every_skill_per_dir(
        self,
    ) -> None:
        # An explicit list replaces discovery, keeps spaces in a name, and
        # expands a leading ~/.
        team = self.config_dir(".claude-work")
        spaced = self.home / ".claude-a b"

        completed = self.run_bootstrap(f"{spaced}:~/.claude-x:")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Claude config dirs (CLAUDE_CONFIG_DIRS):\n"
            "  ~/.claude-a b\n"
            "  ~/.claude-x\n\n",
            completed.stdout,
        )
        for directory in (spaced, self.home / ".claude-x"):
            self.assertTrue((directory / "settings.json").is_file())
            self.assert_skills(directory)
        self.assertFalse((self.home / ".claude").exists())
        self.assert_untouched(team)
        self.assertFalse((self.repo / "~").exists())

    def test_fallback_installs_every_skill_per_dir_and_leaves_settings_alone(
        self,
    ) -> None:
        self.stub_python_away()
        first = self.config_dir(".claude")
        (first / "settings.json").write_text('{"model": "host"}\n', encoding="utf-8")
        spaced = self.home / ".claude-a b"

        completed = self.run_bootstrap(f"{first}::{spaced}")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("skipped safe agent configuration synchronization", completed.stderr)
        self.assertNotIn("discovery needs Python", completed.stderr)
        for directory in (first, spaced):
            self.assert_skills(directory)
        self.assertEqual(
            (first / "settings.json").read_text(encoding="utf-8"), '{"model": "host"}\n'
        )
        self.assertFalse((spaced / "settings.json").exists())
        self.assertFalse(self.codex_home.exists())

    def test_fallback_without_a_list_uses_the_default_config_dir(self) -> None:
        self.stub_python_away()
        team = self.config_dir(".claude-work")

        completed = self.run_bootstrap("  ")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("discovery needs Python", completed.stderr)
        self.assert_skills(self.home / ".claude")
        self.assertFalse((self.home / ".claude" / "settings.json").exists())
        self.assert_untouched(team)

    def test_fallback_expands_a_leading_tilde(self) -> None:
        self.stub_python_away()

        completed = self.run_bootstrap("~:~/.claude-x")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assert_skills(self.home)
        self.assert_skills(self.home / ".claude-x")
        self.assertFalse((self.repo / "~").exists())

    def test_relative_or_space_separated_dirs_are_refused_before_any_write(
        self,
    ) -> None:
        for python in ("available", "missing"):
            if python == "missing":
                self.stub_python_away()
            for value, message in (
                ("relative/.claude", "must be an absolute path or start with ~/"),
                (f"{self.home}/.claude:work", "must be an absolute path or start with ~/"),
                ("~other/.claude", "must be an absolute path or start with ~/"),
                ("~/.claude ~/.claude-work", "looks like a space-separated list"),
                (f"{self.home}/.claude {self.home}/.claude-x", "looks like a space-separated list"),
            ):
                with self.subTest(python=python, value=value):
                    completed = self.run_bootstrap(value)

                    self.assertEqual(completed.returncode, 2)
                    self.assertIn(message, completed.stderr)
                    self.assertEqual(list(self.home.iterdir()), [])
                    self.assertEqual(self.hooks_path(), "")
                    for stray in ("relative", "work", "~other"):
                        self.assertFalse((self.repo / stray).exists())

    def test_skill_names_are_validated_like_the_engine_before_any_write(self) -> None:
        self.stub_python_away()
        (self.repo / ".agents" / "host-templates" / "Bad_Name-SKILL.md").write_text(
            "# bad\n", encoding="utf-8"
        )

        completed = self.run_bootstrap()

        self.assertEqual(completed.returncode, 2)
        self.assertIn("lowercase hyphenated name", completed.stderr)
        self.assertEqual(list(self.home.iterdir()), [])
        self.assertEqual(self.hooks_path(), "")

    def test_skill_templates_need_the_ownership_marker_before_any_write(
        self,
    ) -> None:
        (self.repo / ".agents" / "host-templates" / "unmarked-SKILL.md").write_text(
            "---\nname: unmarked\n---\n# unmarked\n", encoding="utf-8"
        )
        for python in ("available", "missing"):
            with self.subTest(python=python):
                if python == "missing":
                    self.stub_python_away()

                completed = self.run_bootstrap()

                self.assertEqual(completed.returncode, 2)
                self.assertIn("ownership marker", completed.stderr)
                self.assertEqual(list(self.home.iterdir()), [])
                self.assertEqual(self.hooks_path(), "")

    def test_foreign_skill_is_kept_and_legacy_env_sync_converges(self) -> None:
        # A same-named skill without the marker is the operator's own; only
        # an unmarked env-sync is a workspace-meta install from before it.
        for name in ("env-sync", "interview", "project-bootstrap"):
            self.assertIn(name, SKILL_NAMES)
        templates = self.repo / ".agents" / "host-templates"
        env_sync = (templates / "env-sync-SKILL.md").read_text(encoding="utf-8")
        seeded = {
            "interview": "---\nname: interview\ndescription: mine\n---\n\n# mine\n",
            "env-sync": env_sync.replace(SKILL_MARKER + "\n", "", 1),
            "project-bootstrap": (templates / "project-bootstrap-SKILL.md").read_text(
                encoding="utf-8"
            )
            + "\nA line from an older template.\n",
        }
        self.assertNotIn(SKILL_MARKER, seeded["env-sync"])
        for python in ("available", "missing"):
            with self.subTest(python=python):
                if python == "missing":
                    self.stub_python_away()
                directory = self.home / f".claude-{python}"
                for name, text in seeded.items():
                    path = directory / "skills" / name / "SKILL.md"
                    path.parent.mkdir(parents=True)
                    path.write_text(text, encoding="utf-8")
                foreign = directory / "skills" / "interview" / "SKILL.md"

                completed = self.run_bootstrap(str(directory))

                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertEqual(
                    foreign.read_text(encoding="utf-8"), seeded["interview"]
                )
                for name in ("env-sync", "project-bootstrap"):
                    self.assertEqual(
                        (directory / "skills" / name / "SKILL.md").read_bytes(),
                        (templates / f"{name}-SKILL.md").read_bytes(),
                    )
                if python == "available":
                    kept = re.compile(
                        rf"(?m)^skill interview \[~/\.claude-{python}\]:\s+"
                        r"kept: skill owned outside workspace-meta$"
                    )
                else:
                    kept = re.compile(
                        re.escape(
                            "kept interview skill owned outside workspace-meta: "
                            f"{foreign}"
                        )
                    )
                self.assertRegex(completed.stdout, kept)
                before = self.snapshot()

                second = self.run_bootstrap(str(directory))

                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(self.snapshot(), before)
                self.assertRegex(second.stdout, kept)

    def test_second_run_is_idempotent(self) -> None:
        self.config_dir(".claude-work")
        for python in ("available", "missing"):
            with self.subTest(python=python):
                if python == "missing":
                    self.stub_python_away()
                first = self.run_bootstrap()
                self.assertEqual(first.returncode, 0, first.stderr)
                before = self.snapshot()

                second = self.run_bootstrap()

                self.assertEqual(second.returncode, 0, second.stderr)
                self.assertEqual(self.snapshot(), before)
                if python == "available":
                    self.assertIn("Sync complete: 0 updated,", second.stdout)
                else:
                    self.assertNotIn("installed", second.stdout)
                    self.assertIn("skill already current", second.stdout)


if __name__ == "__main__":
    unittest.main()

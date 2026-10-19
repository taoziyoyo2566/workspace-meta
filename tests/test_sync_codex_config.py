from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import tomllib
import sys
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "sync_codex_config", ROOT / "scripts" / "sync_codex_config.py"
)
assert SPEC and SPEC.loader
SYNC = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SYNC)


class CodexConfigSyncTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.codex_home = Path(self.temp_dir.name) / ".codex"
        self.agents_template = (
            ROOT / ".agents" / "host-templates" / "codex-AGENTS.md"
        )
        self.hooks_template = (
            ROOT / ".agents" / "host-templates" / "codex-hooks.toml"
        )
        self.preferences_template = (
            ROOT / ".agents" / "host-templates" / "codex-preferences.toml"
        )
        self.expected_status_line = tomllib.loads(
            self.preferences_template.read_text()
        )["tui"]["status_line"]
        self.status_script = ROOT / "scripts" / "workspace_status.py"
        self.claude_status_line_script = ROOT / "scripts" / "claude_status_line.py"
        self.claude_dir = Path(self.temp_dir.name) / ".claude"
        # The same template set the Makefile passes, so direct and make runs
        # converge to one state.
        self.skill_templates = tuple(
            sorted((ROOT / ".agents" / "host-templates").glob("*-SKILL.md"))
        )
        self.rules_dir = ROOT / ".agents" / "rules"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def skill_names(self) -> tuple[str, ...]:
        return tuple(
            template.name.removesuffix("-SKILL.md")
            for template in self.skill_templates
        )

    def skill_path(self, name: str, directory: Path | None = None) -> Path:
        return (directory or self.claude_dir) / "skills" / name / "SKILL.md"

    def template_for(self, name: str) -> Path:
        return dict(zip(self.skill_names(), self.skill_templates))[name]

    @staticmethod
    def claude_labels(directory: str = "~/.claude", skills=()) -> tuple[str, ...]:
        return (
            f"Claude SessionStart [{directory}]",
            f"Claude statusLine [{directory}]",
            *(f"skill {name} [{directory}]" for name in skills),
        )

    def all_labels(self) -> tuple[str, ...]:
        return (
            "Codex AGENTS.md",
            "Codex SessionStart hook",
            "Codex preferences",
            *self.claude_labels(skills=self.skill_names()),
        )

    def sync_args(
        self,
        claude_config_dirs: tuple[Path, ...] | None = None,
        skill_templates: tuple[Path, ...] | None = None,
    ) -> list[str]:
        args = [
            sys.executable,
            str(ROOT / "scripts" / "sync_codex_config.py"),
            "--python",
            sys.executable,
            "--agents-template",
            str(self.agents_template),
            "--hooks-template",
            str(self.hooks_template),
            "--preferences-template",
            str(self.preferences_template),
            "--status-script",
            str(self.status_script),
            "--claude-status-line-script",
            str(self.claude_status_line_script),
            "--codex-home",
            str(self.codex_home),
        ]
        for template in (
            self.skill_templates if skill_templates is None else skill_templates
        ):
            args.extend(("--claude-skill-template", str(template)))
        for directory in claude_config_dirs or (self.claude_dir,):
            args.extend(("--claude-config-dir", str(directory)))
        return args

    def sync_cli(
        self,
        mode: str | None = None,
        input_text: str | None = None,
        claude_config_dirs: tuple[Path, ...] | None = None,
        skill_templates: tuple[Path, ...] | None = None,
    ):
        args = self.sync_args(claude_config_dirs, skill_templates)
        if mode:
            args.append(mode)
        return subprocess.run(
            args,
            input=input_text,
            capture_output=True,
            check=False,
            env=self.isolated_env(claude_config_dirs),
            text=True,
        )

    def isolated_env(
        self, claude_config_dirs: tuple[Path, ...] | None = None
    ) -> dict[str, str]:
        # A session's own CLAUDE_CONFIG_DIR and CLAUDE_CONFIG_DIRS name real
        # config dirs; replace both so no run can reach this host's config.
        env = os.environ.copy()
        env.pop("CLAUDE_CONFIG_DIR", None)
        env["HOME"] = self.temp_dir.name
        env["CODEX_HOME"] = str(self.codex_home)
        env["CLAUDE_CONFIG_DIRS"] = ":".join(
            str(path) for path in claude_config_dirs or (self.claude_dir,)
        )
        env["PYTHON"] = sys.executable
        return env

    def make_target(
        self,
        target: str,
        input_text: str | None = None,
        env: dict[str, str] | None = None,
    ):
        return subprocess.run(
            ["make", target],
            cwd=ROOT,
            env=self.isolated_env() if env is None else env,
            input=input_text,
            capture_output=True,
            check=False,
            text=True,
        )

    def managed_paths(
        self, claude_config_dirs: tuple[Path, ...] | None = None
    ) -> tuple[Path, ...]:
        return (
            self.codex_home / "AGENTS.md",
            self.codex_home / "config.toml",
            *(
                path
                for directory in claude_config_dirs or (self.claude_dir,)
                for path in (
                    directory / "settings.json",
                    *(
                        directory / "skills" / name / "SKILL.md"
                        for name in self.skill_names()
                    ),
                )
            ),
        )

    @staticmethod
    def path_snapshot(path: Path) -> tuple[bool, bytes | None, int | None]:
        return (
            path.exists(),
            path.read_bytes() if path.exists() else None,
            path.stat().st_mtime_ns if path.exists() else None,
        )

    @staticmethod
    def design_map_entry(owner: str) -> str:
        # The design map is the one domain -> owner catalog; return the
        # normalized, lowercased domain entry whose Owner bullet names owner.
        design_map = (ROOT / "docs" / "architecture" / "design-map.md").read_text()
        entries = [
            section.split("\n## ", 1)[0]
            for section in design_map.split("\n### ")[1:]
            if f"- **Owner**: [`{owner}`]" in section
        ]
        assert len(entries) == 1, (owner, len(entries))
        return " ".join(entries[0].split()).lower()

    def install_current_managed_state(self) -> None:
        completed = self.sync_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)

    def drift_status_line(self) -> None:
        config = self.codex_home / "config.toml"
        changed, replacements = re.subn(
            r'(?m)^status_line = \[[^\n]*\]$',
            'status_line = ["context-remaining", "git-branch"]',
            config.read_text(),
        )
        self.assertEqual(replacements, 1)
        config.write_text(changed)

    def test_make_sync_skips_prompt_and_writes_when_everything_is_current(self) -> None:
        self.install_current_managed_state()
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        completed = self.make_target("sync")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("Apply these changes?", completed.stdout)
        self.assertIn("Result: everything is already current.", completed.stdout)
        self.assertIn("No files changed.", completed.stdout)
        for label in self.all_labels():
            self.assertRegex(completed.stdout, rf"(?m)^{re.escape(label)}:\s+OK$")
        self.assertEqual(
            before,
            {path: self.path_snapshot(path) for path in self.managed_paths()},
        )

    def test_make_sync_reports_preference_drift_before_declining(self) -> None:
        self.install_current_managed_state()
        self.drift_status_line()
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        for response in ("\n", "N\n", "n\n", "anything\n"):
            with self.subTest(response=response):
                completed = self.make_target("sync", response)
                self.assertEqual(completed.returncode, 0, completed.stderr)
                self.assertRegex(
                    completed.stdout, r"(?m)^Codex preferences:\s+DRIFT$"
                )
                self.assertIn("tui.status_line", completed.stdout)
                self.assertIn("Repository:", completed.stdout)
                self.assertIn("Current host:", completed.stdout)
                self.assertIn(
                    f"1. {self.expected_status_line[0]}", completed.stdout
                )
                self.assertIn("1. context-remaining", completed.stdout)
                self.assertIn(
                    "Applying workspace-meta will replace the current local values",
                    completed.stdout,
                )
                self.assertIn("Changes to apply:", completed.stdout)
                self.assertIn(
                    "- Codex preferences: replace tui.status_line",
                    completed.stdout,
                )
                self.assertLess(
                    completed.stdout.index("Changes to apply:"),
                    completed.stdout.index("Apply these changes? [y/N]:"),
                )
                self.assertIn("Unmanaged local configuration will be preserved.", completed.stdout)
                self.assertIn("Apply these changes? [y/N]:", completed.stdout)
                self.assertIn("No changes applied.", completed.stdout)
                self.assertNotIn("updated preferences", completed.stdout.lower())
                self.assertEqual(
                    before,
                    {path: self.path_snapshot(path) for path in self.managed_paths()},
                )

    def test_make_sync_yes_updates_only_drifted_target_and_is_idempotent(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        config.write_text('model = "host-model"\n\n' + config.read_text())
        self.drift_status_line()
        unchanged_paths = tuple(path for path in self.managed_paths() if path != config)
        unchanged_before = {
            path: self.path_snapshot(path) for path in unchanged_paths
        }

        completed = self.make_target("sync", "Y\n")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("Final managed configuration:", completed.stdout)
        self.assertRegex(
            completed.stdout, r"(?m)^Codex preferences:\s+UPDATED$"
        )
        unchanged_labels = tuple(
            label for label in self.all_labels() if label != "Codex preferences"
        )
        for label in unchanged_labels:
            self.assertRegex(completed.stdout, rf"(?m)^{re.escape(label)}:\s+OK$")
        self.assertIn(
            f"Sync complete: 1 updated, {len(unchanged_labels)} unchanged.",
            completed.stdout,
        )
        self.assertEqual(tomllib.loads(config.read_text())["model"], "host-model")
        self.assertEqual(
            unchanged_before,
            {path: self.path_snapshot(path) for path in unchanged_paths},
        )

        current_snapshot = self.path_snapshot(config)
        second = self.make_target("sync")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertNotIn("Apply these changes?", second.stdout)
        self.assertIn("Result: everything is already current.", second.stdout)
        self.assertEqual(current_snapshot, self.path_snapshot(config))

    def test_sync_expect_applies_listed_drift_without_prompt(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        self.drift_status_line()
        unchanged_paths = tuple(path for path in self.managed_paths() if path != config)
        unchanged_before = {
            path: self.path_snapshot(path) for path in unchanged_paths
        }

        completed = subprocess.run(
            [
                *self.sync_args(None, None),
                "--expect=Codex preferences",
                "--expect=Codex AGENTS.md",
            ],
            capture_output=True,
            text=True,
            env=self.isolated_env(),
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("Apply these changes?", completed.stdout)
        self.assertIn("- Codex preferences: replace tui.status_line", completed.stdout)
        self.assertIn("Expected but already current: Codex AGENTS.md", completed.stdout)
        self.assertIn("Final managed configuration:", completed.stdout)
        self.assertRegex(completed.stdout, r"(?m)^Codex preferences:\s+UPDATED$")
        self.assertEqual(
            tomllib.loads(config.read_text())["tui"]["status_line"],
            self.expected_status_line,
        )
        self.assertEqual(
            unchanged_before,
            {path: self.path_snapshot(path) for path in unchanged_paths},
        )

    def test_sync_expect_refuses_drift_outside_the_list(self) -> None:
        self.install_current_managed_state()
        self.drift_status_line()
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        completed = self.sync_cli("--expect=Codex AGENTS.md")

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn(
            "Result: drift outside the expected areas: Codex preferences",
            completed.stdout,
        )
        self.assertIn("Drift detected:", completed.stdout)
        self.assertIn("tui.status_line", completed.stdout)
        self.assertIn("No files were modified.", completed.stdout)
        self.assertNotIn("Changes to apply:", completed.stdout)
        self.assertEqual(
            before,
            {path: self.path_snapshot(path) for path in self.managed_paths()},
        )

    def test_sync_expect_refuses_when_any_drifted_area_is_unlisted(self) -> None:
        self.install_current_managed_state()
        self.drift_status_line()
        agents = self.codex_home / "AGENTS.md"
        text = agents.read_text()
        self.assertEqual(text.count("## Safety Floor"), 1)
        agents.write_text(text.replace("## Safety Floor", "## Safety Floor (edited)"))
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        # Spaces around a label are ignored.
        completed = self.sync_cli("--expect= Codex preferences ")

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn(
            "Result: drift outside the expected areas: Codex AGENTS.md",
            completed.stdout,
        )
        self.assertEqual(
            before,
            {path: self.path_snapshot(path) for path in self.managed_paths()},
        )

    def test_sync_expect_rejects_an_unknown_label_before_writing(self) -> None:
        self.install_current_managed_state()
        self.drift_status_line()
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        for value in (
            "--expect=Codex preference",
            "--expect=Codex preferences;Codex preference",
            "--expect= ; ",
        ):
            with self.subTest(value=value):
                completed = self.sync_cli(value)
                self.assertEqual(completed.returncode, 1)
                self.assertIn("--expect", completed.stderr)
                self.assertIn("No files were modified.", completed.stderr)
                self.assertEqual(
                    before,
                    {path: self.path_snapshot(path) for path in self.managed_paths()},
                )

    def test_make_sync_expect_applies_when_current_or_listed(self) -> None:
        self.install_current_managed_state()
        env = self.isolated_env()
        env["SYNC_EXPECT"] = "Codex preferences"

        current = self.make_target("sync", env=env)
        self.assertEqual(current.returncode, 0, current.stderr)
        self.assertIn("Result: everything is already current.", current.stdout)

        self.drift_status_line()
        completed = self.make_target("sync", env=env)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("Apply these changes?", completed.stdout)
        self.assertRegex(completed.stdout, r"(?m)^Codex preferences:\s+UPDATED$")

        self.drift_status_line()
        env["SYNC_EXPECT"] = "Codex AGENTS.md"
        refused = self.make_target("sync", env=env)
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("drift outside the expected areas", refused.stdout)

    def test_sync_expect_is_its_own_mode_and_reaches_the_script_unexpanded(self) -> None:
        self.install_current_managed_state()
        both = subprocess.run(
            [*self.sync_args(None, None), "--check", "--expect=Codex AGENTS.md"],
            capture_output=True,
            text=True,
            env=self.isolated_env(),
            check=False,
        )
        self.assertEqual(both.returncode, 2)
        self.assertIn("not allowed with argument", both.stderr)

        env = self.isolated_env()
        for label in ("Codex preferences$HOME", "Codex preferences'x"):
            with self.subTest(label=label):
                env["SYNC_EXPECT"] = label
                completed = self.make_target("sync", env=env)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(label, completed.stderr)

    def test_agent_sync_check_reports_drift_and_never_writes(self) -> None:
        self.install_current_managed_state()
        self.drift_status_line()
        before = {path: self.path_snapshot(path) for path in self.managed_paths()}

        direct = self.sync_cli("--check")

        self.assertEqual(direct.returncode, 1)
        self.assertRegex(direct.stdout, r"(?m)^Codex preferences:\s+DRIFT$")
        self.assertIn("Repository:", direct.stdout)
        self.assertIn("Current host:", direct.stdout)
        self.assertIn("No files were modified.", direct.stdout)
        self.assertNotIn("updated", direct.stdout.lower())
        self.assertEqual(
            before,
            {path: self.path_snapshot(path) for path in self.managed_paths()},
        )

        through_make = self.make_target("agent-sync-check")
        self.assertNotEqual(through_make.returncode, 0)
        self.assertIn("DRIFT", through_make.stdout)
        self.assertIn("No files were modified.", through_make.stdout)
        self.assertEqual(
            before,
            {path: self.path_snapshot(path) for path in self.managed_paths()},
        )

    def test_two_claude_config_dirs_converge_in_one_run(self) -> None:
        team_dir = Path(self.temp_dir.name) / ".claude-work"
        claude_dirs = (self.claude_dir, team_dir)
        env = self.isolated_env(claude_dirs)

        completed = self.make_target("sync", "Y\n", env)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        # The resolved list comes before the dry-run and the prompt.
        self.assertIn(
            "Claude config dirs (CLAUDE_CONFIG_DIRS):\n"
            "  ~/.claude\n"
            "  ~/.claude-work\n",
            completed.stdout,
        )
        self.assertLess(
            completed.stdout.index("  ~/.claude-work\n"),
            completed.stdout.index("Managed configuration dry-run:"),
        )
        labels = (
            *self.claude_labels("~/.claude", self.skill_names()),
            *self.claude_labels("~/.claude-work", self.skill_names()),
        )
        for label in labels:
            self.assertRegex(
                completed.stdout, rf"(?m)^{re.escape(label)}:\s+UPDATED$"
            )
        settings = [
            json.loads((directory / "settings.json").read_text())
            for directory in claude_dirs
        ]
        self.assertEqual(settings[0], settings[1])
        self.assertIn(
            SYNC.MANAGED_HOOK_MARKER,
            settings[1]["hooks"]["SessionStart"][0]["hooks"][0]["command"],
        )
        self.assertIn(
            SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER,
            settings[1]["statusLine"]["command"],
        )

        before = {
            path: self.path_snapshot(path)
            for path in self.managed_paths(claude_dirs)
        }
        second = self.sync_cli(claude_config_dirs=claude_dirs)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(
            f"Sync complete: 0 updated, {3 + len(labels)} unchanged.",
            second.stdout,
        )
        self.assertEqual(
            before,
            {
                path: self.path_snapshot(path)
                for path in self.managed_paths(claude_dirs)
            },
        )

    def test_skill_templates_fan_out_to_every_claude_config_dir(self) -> None:
        templates_dir = Path(self.temp_dir.name) / "templates"
        templates_dir.mkdir()
        templates = (
            templates_dir / "alpha-SKILL.md",
            templates_dir / "beta-two-SKILL.md",
        )
        for template in templates:
            template.write_text(
                f"{SYNC.SKILL_OWNERSHIP_MARKER}\n# {template.name}\n"
            )
        claude_dirs = (self.claude_dir, Path(self.temp_dir.name) / ".claude-work")

        completed = self.sync_cli(
            claude_config_dirs=claude_dirs, skill_templates=templates
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        for directory, shown in zip(claude_dirs, ("~/.claude", "~/.claude-work")):
            for name, template in (("alpha", templates[0]), ("beta-two", templates[1])):
                self.assertRegex(
                    completed.stdout,
                    rf"(?m)^{re.escape(f'skill {name} [{shown}]')}:\s+UPDATED$",
                )
                self.assertEqual(
                    (directory / "skills" / name / "SKILL.md").read_text(),
                    template.read_text(),
                )

        templates[0].write_text(f"{SYNC.SKILL_OWNERSHIP_MARKER}\n# alpha, revised\n")
        drift = self.sync_cli(
            "--check", claude_config_dirs=claude_dirs, skill_templates=templates
        )
        self.assertEqual(drift.returncode, 1)
        for shown in ("~/.claude", "~/.claude-work"):
            self.assertRegex(
                drift.stdout,
                rf"(?m)^{re.escape(f'skill alpha [{shown}]')}:\s+DRIFT$",
            )
            self.assertRegex(
                drift.stdout,
                rf"(?m)^{re.escape(f'skill beta-two [{shown}]')}:\s+OK$",
            )

    def test_skill_template_names_are_validated_before_any_write(self) -> None:
        templates_dir = Path(self.temp_dir.name) / "templates"
        (templates_dir / "other").mkdir(parents=True)
        marked = f"---\nname: skill\n---\n{SYNC.SKILL_OWNERSHIP_MARKER}\n# skill\n"
        for bad, content, message in (
            ((templates_dir / "env-sync.md",), marked, "lowercase hyphenated name"),
            ((templates_dir / "Upper-SKILL.md",), marked, "lowercase hyphenated name"),
            (
                (
                    templates_dir / "twin-SKILL.md",
                    templates_dir / "other" / "twin-SKILL.md",
                ),
                marked,
                "both install twin",
            ),
            # Installed without the marker, it would be kept as foreign next run.
            (
                (templates_dir / "unmarked-SKILL.md",),
                "---\nname: unmarked\n---\n# skill\n",
                "ownership marker",
            ),
        ):
            with self.subTest(templates=[path.name for path in bad]):
                for template in bad:
                    template.write_text(content)

                completed = self.sync_cli(skill_templates=bad)

                self.assertEqual(completed.returncode, 1)
                self.assertIn(message, completed.stderr)
                self.assertIn("No files were modified.", completed.stderr)
                self.assertFalse(self.claude_dir.exists())
                self.assertFalse(self.codex_home.exists())

    def test_skill_ownership_marker_is_the_first_line_after_frontmatter(
        self,
    ) -> None:
        marker = SYNC.SKILL_OWNERSHIP_MARKER
        for content, expected in (
            (f"---\nname: x\n---\n{marker}\n\n# x\n", True),
            (f"---\r\nname: x\r\n---\r\n{marker}\r\n# x\r\n", True),
            (f"{marker}\n# x\n", True),
            (f"---\nname: x\n---\n\n{marker}\n# x\n", False),
            (f"---\nname: x\n---\n# x\n\n{marker}\n", False),
            (f"---\nname: x\n{marker}\n", False),
            (f"---\nname: x\n---\n{marker} \n", False),
            ("", False),
        ):
            with self.subTest(content=content):
                self.assertIs(SYNC.has_skill_ownership_marker(content), expected)
        for template in self.skill_templates:
            with self.subTest(template=template.name):
                self.assertTrue(
                    SYNC.has_skill_ownership_marker(template.read_text())
                )

    def test_fresh_skill_install_writes_the_marker_and_is_idempotent(
        self,
    ) -> None:
        completed = self.sync_cli()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        for name, template in zip(self.skill_names(), self.skill_templates):
            installed = self.skill_path(name).read_text()
            self.assertEqual(installed, template.read_text())
            self.assertTrue(SYNC.has_skill_ownership_marker(installed))
            self.assertRegex(
                completed.stdout,
                rf"(?m)^{re.escape(f'skill {name} [~/.claude]')}:\s+UPDATED$",
            )

        before = {path: self.path_snapshot(path) for path in self.managed_paths()}
        second = self.sync_cli()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn(
            f"Sync complete: 0 updated, {len(self.all_labels())} unchanged.",
            second.stdout,
        )
        self.assertEqual(
            before, {path: self.path_snapshot(path) for path in self.managed_paths()}
        )

    def test_foreign_skill_is_kept_while_other_areas_apply(self) -> None:
        # The operator's own skill of the same name belongs to the operator.
        foreign_name = "interview"
        self.assertIn(foreign_name, self.skill_names())
        foreign = self.skill_path(foreign_name)
        foreign.parent.mkdir(parents=True)
        foreign_text = (
            "---\nname: interview\ndescription: my own interview skill\n---\n\n"
            "# my interview, private-body-text\n"
        )
        foreign.write_text(foreign_text)
        kept_label = f"skill {foreign_name} [~/.claude]"
        kept_line = (
            rf"(?m)^{re.escape(kept_label)}:\s+"
            r"kept: skill owned outside workspace-meta$"
        )

        # A bare run applies without a prompt, as make bootstrap does.
        completed = self.sync_cli()

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertRegex(completed.stdout, kept_line)
        self.assertNotIn("private-body-text", completed.stdout + completed.stderr)
        self.assertEqual(foreign.read_text(), foreign_text)
        for name, template in zip(self.skill_names(), self.skill_templates):
            if name == foreign_name:
                continue
            self.assertEqual(self.skill_path(name).read_bytes(), template.read_bytes())
        settings = json.loads((self.claude_dir / "settings.json").read_text())
        self.assertIn(
            SYNC.MANAGED_HOOK_MARKER,
            settings["hooks"]["SessionStart"][0]["hooks"][0]["command"],
        )
        self.assertTrue((self.codex_home / "AGENTS.md").is_file())

        check = self.sync_cli("--check")
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertRegex(check.stdout, kept_line)
        self.assertIn("Result: everything is already current.", check.stdout)

        interactive = self.make_target("sync", "Y\n")
        self.assertEqual(interactive.returncode, 0, interactive.stderr)
        self.assertNotIn("Apply these changes?", interactive.stdout)
        self.assertEqual(foreign.read_text(), foreign_text)

    def test_marked_skill_with_stale_content_converges(self) -> None:
        self.install_current_managed_state()
        name = "project-bootstrap"
        installed = self.skill_path(name)
        stale = installed.read_text() + "\nA line from an older template.\n"
        installed.write_text(stale)
        self.assertTrue(SYNC.has_skill_ownership_marker(stale))

        drift = self.sync_cli("--check")
        self.assertEqual(drift.returncode, 1)
        self.assertRegex(
            drift.stdout, rf"(?m)^{re.escape(f'skill {name} [~/.claude]')}:\s+DRIFT$"
        )
        self.assertEqual(installed.read_text(), stale)

        completed = self.sync_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertRegex(
            completed.stdout,
            rf"(?m)^{re.escape(f'skill {name} [~/.claude]')}:\s+UPDATED$",
        )
        self.assertEqual(installed.read_text(), self.template_for(name).read_text())
        second = self.sync_cli()
        self.assertIn("Sync complete: 0 updated,", second.stdout)

    def test_legacy_unmarked_env_sync_converges_and_gains_the_marker(self) -> None:
        # Hosts synced before the marker existed hold an unmarked env-sync.
        self.assertEqual(SYNC.LEGACY_UNMARKED_SKILLS, ("env-sync",))
        template_text = self.template_for("env-sync").read_text()
        legacy = template_text.replace(f"{SYNC.SKILL_OWNERSHIP_MARKER}\n", "", 1)
        self.assertNotEqual(legacy, template_text)
        installed = self.skill_path("env-sync")
        installed.parent.mkdir(parents=True)
        installed.write_text(legacy)
        label = re.escape("skill env-sync [~/.claude]")

        drift = self.sync_cli("--check")
        self.assertEqual(drift.returncode, 1)
        self.assertRegex(drift.stdout, rf"(?m)^{label}:\s+DRIFT$")
        self.assertIn("Current host: legacy unmarked workspace-meta skill", drift.stdout)

        completed = self.sync_cli()
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertRegex(completed.stdout, rf"(?m)^{label}:\s+UPDATED$")
        self.assertEqual(installed.read_text(), template_text)
        self.assertTrue(SYNC.has_skill_ownership_marker(installed.read_text()))

        before = self.path_snapshot(installed)
        second = self.sync_cli()
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Sync complete: 0 updated,", second.stdout)
        self.assertEqual(self.path_snapshot(installed), before)

    def test_default_claude_config_dirs_include_relocated_dirs_only(self) -> None:
        home = Path(self.temp_dir.name)
        # Copy words match whole name parts, so a word inside a longer part
        # ("gold", "origin", "holder") does not mark a copy.
        relocated = (
            ".claude-work",
            ".claude-a b",
            ".claude-gold",
            ".claude-origin",
            ".claude-holder",
        )
        for name in relocated:
            (home / name).mkdir()
            (home / name / ".claude.json").write_text("{}")
        # A copy of a relocated dir keeps its .claude.json, so its name is
        # what marks it; discovery skips it and says why.
        copies = {
            ".claude-work.bak-20261017": 'name has the part "bak"',
            ".claude-work-20261017": "name ends in a date",
            ".claude-work-2026-10-17": "name ends in a date",
            ".claude-old": 'name has the part "old"',
            ".claude-work-backup": 'name has the part "backup"',
            ".claude-x.orig": 'name has the part "orig"',
        }
        for name in copies:
            (home / name).mkdir()
            (home / name / ".claude.json").write_text("{}")
        # A backup of ~/.claude has settings but no .claude.json of its own,
        # and ~/.claude.json is the default dir's state file, not a dir.
        (home / ".claude-backup").mkdir()
        (home / ".claude-backup" / "settings.json").write_text("{}")
        (home / ".claude.json").write_text("{}")
        env = self.isolated_env()
        env.pop("CLAUDE_CONFIG_DIRS")
        self.assertEqual(env["HOME"], str(home))

        completed = self.make_target("agent-sync-check", env=env)

        self.assertNotEqual(completed.returncode, 0)
        skipped = "".join(
            f"  ~/{name}: {copies[name]}\n" for name in sorted(copies)
        )
        self.assertIn(
            "Claude config dirs (CLAUDE_CONFIG_DIRS):\n"
            "  ~/.claude\n"
            "  ~/.claude-a b\n"
            "  ~/.claude-gold\n"
            "  ~/.claude-holder\n"
            "  ~/.claude-origin\n"
            "  ~/.claude-work\n"
            "Skipped as a likely copy or backup "
            "(name it in CLAUDE_CONFIG_DIRS to manage it):\n"
            f"{skipped}\n",
            completed.stdout,
        )
        self.assertNotIn(".claude-backup", completed.stdout)
        for name in relocated:
            shown = f"~/{name}"
            self.assertRegex(
                completed.stdout,
                rf"(?m)^{re.escape(f'Claude SessionStart [{shown}]')}:\s+DRIFT$",
            )
        self.assertFalse((home / ".claude").exists())
        for name in (*relocated, *copies):
            self.assertEqual(
                [path.name for path in (home / name).iterdir()], [".claude.json"]
            )
        self.assertEqual(
            [path.name for path in (home / ".claude-backup").iterdir()],
            ["settings.json"],
        )
        # Nothing was created from a mis-split name in the repository.
        self.assertFalse((ROOT / "b").exists())

    def test_discovery_writes_only_discovered_dirs(self) -> None:
        home = Path(self.temp_dir.name)
        for name in (".claude-a b", ".claude-work.bak-20261017"):
            (home / name).mkdir()
            (home / name / ".claude.json").write_text("{}")
        env = self.isolated_env()
        env.pop("CLAUDE_CONFIG_DIRS")

        completed = self.make_target("sync", "Y\n", env)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertLess(
            completed.stdout.index(
                '~/.claude-work.bak-20261017: name has the part "bak"'
            ),
            completed.stdout.index("Apply these changes?"),
        )
        for directory in (home / ".claude", home / ".claude-a b"):
            self.assertTrue((directory / "settings.json").is_file())
            for name in self.skill_names():
                self.assertTrue((directory / "skills" / name / "SKILL.md").is_file())
        self.assertEqual(
            [path.name for path in (home / ".claude-work.bak-20261017").iterdir()],
            [".claude.json"],
        )

    def test_copy_name_reason_matches_whole_name_parts(self) -> None:
        for name, reason in (
            (".claude-gold", None),
            (".claude-origin", None),
            (".claude-holder", None),
            (".claude-copyist", None),
            (".claude-tmpl", None),
            (".claude-work", None),
            (".claude-work.bak2", 'name has the part "bak2"'),
            (".claude-work_backups", 'name has the part "backups"'),
            (".claude-work_tmp", 'name has the part "tmp"'),
            (".claude-Team.COPY", 'name has the part "copy"'),
            (".claude-work~", 'name contains "~"'),
            (".claude-work.20261017", "name ends in a date"),
        ):
            with self.subTest(name=name):
                self.assertEqual(SYNC.copy_name_reason(name), reason)

    def test_explicit_colon_list_keeps_spaces_and_skips_discovery(self) -> None:
        home = Path(self.temp_dir.name)
        # Discovery would add this dir; an explicit list replaces discovery.
        (home / ".claude-work").mkdir()
        (home / ".claude-work" / ".claude.json").write_text("{}")
        spaced = home / ".claude-a b"
        backup = home / ".claude-work.bak"
        env = self.isolated_env()
        env["CLAUDE_CONFIG_DIRS"] = f"~/.claude-a b::{backup}:"

        completed = self.make_target("sync", "Y\n", env)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "Claude config dirs (CLAUDE_CONFIG_DIRS):\n"
            "  ~/.claude-a b\n"
            "  ~/.claude-work.bak\n\n",
            completed.stdout,
        )
        self.assertNotIn("Skipped", completed.stdout)
        for directory in (spaced, backup):
            self.assertTrue((directory / "settings.json").is_file())
        self.assertFalse((home / ".claude").exists())
        self.assertEqual(
            [path.name for path in (home / ".claude-work").iterdir()],
            [".claude.json"],
        )

    def test_relative_or_space_separated_config_dirs_fail_before_any_write(
        self,
    ) -> None:
        home = Path(self.temp_dir.name)
        for value in (
            "relative/.claude",
            f"{home}/.claude:work",
            "~root/.claude",
            f"{home}/.claude {home}/.claude-work",
            "~/.claude ~/.claude-work",
        ):
            with self.subTest(value=value):
                env = self.isolated_env()
                env["CLAUDE_CONFIG_DIRS"] = value

                completed = self.make_target("sync", "Y\n", env)

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("ERROR: Claude config dir", completed.stderr)
                self.assertIn("No files were modified.", completed.stderr)
                self.assertNotIn("Apply these changes?", completed.stdout)
                self.assertEqual(sorted(path.name for path in home.iterdir()), [])
                self.assertFalse((ROOT / "relative").exists())
                self.assertFalse((ROOT / "work").exists())

    def test_codex_pin_only_drift_reports_the_script_pin_semantically(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        repository_pin = hashlib.sha256(self.status_script.read_bytes()).hexdigest()
        installed_pin = "0" * 64
        config.write_text(config.read_text().replace(repository_pin, installed_pin, 1))

        completed = self.sync_cli("--check")

        self.assertEqual(completed.returncode, 1)
        self.assertRegex(
            completed.stdout, r"(?m)^Codex SessionStart hook:\s+DRIFT$"
        )
        details = completed.stdout.split("  Codex SessionStart hook:", 1)[1]
        details = details.split("\n\n  ", 1)[0]
        self.assertIn("Script: scripts/workspace_status.py", details)
        self.assertIn(f'Installed: "{installed_pin}"', details)
        self.assertIn(f'Repository: "{repository_pin}"', details)
        self.assertIn("~ expected script hash changed", details)
        self.assertIn(
            "Refresh the managed hook so it trusts the current "
            "repository version of workspace_status.py.",
            completed.stdout,
        )
        self.assertNotIn("matcher:", details)
        self.assertNotIn("timeout:", details)
        self.assertNotIn("command loader:", details)
        self.assertNotIn("unparsed command structure", details)

        interactive = self.sync_cli("--interactive", "N\n")
        self.assertIn(
            "- Codex SessionStart hook: refresh workspace_status.py hash pin",
            interactive.stdout,
        )
        self.assertLess(
            interactive.stdout.index("Changes to apply:"),
            interactive.stdout.index("Apply these changes? [y/N]:"),
        )

    def test_codex_hook_reports_only_changed_managed_fields(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        changed = config.read_text()
        changed = changed.replace('matcher = "startup|resume"', 'matcher = "startup"')
        changed = changed.replace(
            "workspace/scripts/workspace_status.py",
            "workspace/scripts/other_status.py",
        )
        changed = changed.replace("timeout = 20", "timeout = 12")
        changed = changed.replace(
            'statusMessage = "Checking workspace-meta status"',
            'statusMessage = "Checking another status"',
        )
        config.write_text(changed)

        completed = self.sync_cli("--check")

        self.assertEqual(completed.returncode, 1)
        details = completed.stdout.split("  Codex SessionStart hook:", 1)[1]
        details = details.split("\n\n  ", 1)[0]
        for field in (
            "~ matcher changed",
            "~ script path changed",
            "~ command target changed",
            "~ timeout changed",
            "~ statusMessage changed",
        ):
            self.assertIn(field, details)
        self.assertNotIn("type:", details)
        self.assertNotIn("expected script hash", details)
        self.assertNotIn("command loader:", details)
        self.assertNotIn("unparsed command structure", details)

    def test_recovery_command_drift_is_semantic_for_all_three_commands(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        config.write_text(
            config.read_text().replace(
                "make -C ~/workspace sync", "make -C ~/workspace bootstrap", 1
            )
        )
        settings = Path(self.temp_dir.name) / ".claude" / "settings.json"
        settings.write_text(
            settings.read_text().replace(
                "make -C ~/workspace sync", "make -C ~/workspace bootstrap"
            )
        )

        completed = self.sync_cli("--interactive", "N\n")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        hook_label, status_line_label = self.claude_labels()
        for label, script in (
            ("Codex SessionStart hook", "scripts/workspace_status.py"),
            (hook_label, "scripts/workspace_status.py"),
            (status_line_label, "scripts/claude_status_line.py"),
        ):
            details = completed.stdout.split(f"  {label}:", 1)[1]
            details = details.split("\n\n  ", 1)[0]
            self.assertIn(f"Script: {script}", details)
            self.assertIn("~ hash-mismatch recovery command changed", details)
            self.assertIn(
                'Installed: "make -C ~/workspace bootstrap"', details
            )
            self.assertIn('Repository: "make -C ~/workspace sync"', details)
            self.assertIn(
                "Use make -C ~/workspace sync when the managed script hash "
                "check fails.",
                completed.stdout,
            )
            self.assertNotIn("command loader", details)
            self.assertNotIn("unparsed command structure", details)
            self.assertIn(
                f"- {label}: update hash-mismatch recovery command",
                completed.stdout,
            )

    def test_command_structure_version_drift_is_reported_separately(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        config.write_text(
            config.read_text().replace(
                SYNC.MANAGED_HOOK_MARKER,
                "workspace-meta-managed-status-v0",
                1,
            )
        )

        completed = self.sync_cli("--check")

        self.assertEqual(completed.returncode, 1)
        details = completed.stdout.split("  Codex SessionStart hook:", 1)[1]
        details = details.split("\n\n  ", 1)[0]
        self.assertIn("~ command structure version changed", details)
        self.assertIn('Installed: "v0"', details)
        self.assertIn('Repository: "v1"', details)
        self.assertNotIn("unparsed command structure", details)

    def test_unparsed_command_change_uses_structure_hash_fallback(self) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        config.write_text(
            config.read_text().replace(
                "status evaluator changed or is unavailable",
                "status evaluator drifted or is unavailable",
                1,
            )
        )

        completed = self.sync_cli("--interactive", "N\n")

        self.assertEqual(completed.returncode, 0)
        details = completed.stdout.split("  Codex SessionStart hook:", 1)[1]
        details = details.split("\n\n  ", 1)[0]
        self.assertIn("~ unparsed command structure changed", details)
        self.assertEqual(details.count("SHA-256 "), 2)
        self.assertIn(
            "Replace the unrecognized managed command structure with the "
            "repository definition.",
            completed.stdout,
        )
        self.assertNotIn("command loader", details)
        self.assertIn(
            "- Codex SessionStart hook: replace unrecognized command structure",
            completed.stdout,
        )

    def test_claude_hook_and_status_line_pin_drift_are_separate(self) -> None:
        self.install_current_managed_state()
        settings = Path(self.temp_dir.name) / ".claude" / "settings.json"
        parsed = json.loads(settings.read_text())
        hook_pin = hashlib.sha256(self.status_script.read_bytes()).hexdigest()
        status_line_pin = hashlib.sha256(
            self.claude_status_line_script.read_bytes()
        ).hexdigest()
        parsed["hooks"]["SessionStart"][0]["hooks"][0]["command"] = parsed[
            "hooks"
        ]["SessionStart"][0]["hooks"][0]["command"].replace(hook_pin, "1" * 64)
        parsed["statusLine"]["command"] = parsed["statusLine"]["command"].replace(
            status_line_pin, "2" * 64
        )
        settings.write_text(json.dumps(parsed, indent=2) + "\n")

        completed = self.sync_cli("--check")

        self.assertEqual(completed.returncode, 1)
        hook_label, status_line_label = self.claude_labels()
        self.assertRegex(
            completed.stdout, rf"(?m)^{re.escape(hook_label)}:\s+DRIFT$"
        )
        self.assertRegex(
            completed.stdout, rf"(?m)^{re.escape(status_line_label)}:\s+DRIFT$"
        )
        hook_details = completed.stdout.split(f"  {hook_label}:", 1)[1]
        hook_details = hook_details.split("\n\n  ", 1)[0]
        status_details = completed.stdout.split(f"  {status_line_label}:", 1)[1]
        status_details = status_details.split("\n\n  ", 1)[0]
        self.assertIn("~ expected script hash changed", hook_details)
        self.assertIn("workspace_status.py", hook_details)
        self.assertNotIn("claude_status_line.py", hook_details)
        self.assertIn("~ expected script hash changed", status_details)
        self.assertIn("claude_status_line.py", status_details)
        self.assertNotIn("workspace_status.py", status_details)

    def test_claude_components_report_their_own_changed_fields(self) -> None:
        self.install_current_managed_state()
        settings = Path(self.temp_dir.name) / ".claude" / "settings.json"
        parsed = json.loads(settings.read_text())
        group = parsed["hooks"]["SessionStart"][0]
        group["matcher"] = "startup"
        group["hooks"][0]["timeout"] = 7
        parsed["statusLine"]["padding"] = 2
        parsed["statusLine"]["command"] = parsed["statusLine"]["command"].replace(
            "workspace/scripts/claude_status_line.py",
            "workspace/scripts/other_status_line.py",
        )
        settings.write_text(json.dumps(parsed, indent=2) + "\n")

        completed = self.sync_cli("--check")

        self.assertEqual(completed.returncode, 1)
        hook_label, status_line_label = self.claude_labels()
        hook_details = completed.stdout.split(f"  {hook_label}:", 1)[1]
        hook_details = hook_details.split("\n\n  ", 1)[0]
        status_details = completed.stdout.split(f"  {status_line_label}:", 1)[1]
        status_details = status_details.split("\n\n  ", 1)[0]
        self.assertIn("~ matcher changed", hook_details)
        self.assertIn("~ timeout changed", hook_details)
        self.assertNotIn("~ padding changed", hook_details)
        self.assertIn("~ script path changed", status_details)
        self.assertIn("~ command target changed", status_details)
        self.assertIn("~ padding changed", status_details)
        self.assertNotIn("~ matcher changed", status_details)
        self.assertNotIn("~ timeout changed", status_details)

    def test_make_sync_reports_parse_errors_without_prompt_or_writes(self) -> None:
        self.install_current_managed_state()
        valid_contents = {
            path: path.read_bytes() for path in self.managed_paths()
        }
        for invalid_target in ("toml", "json"):
            with self.subTest(invalid_target=invalid_target):
                for path, content in valid_contents.items():
                    path.write_bytes(content)
                if invalid_target == "toml":
                    (self.codex_home / "config.toml").write_text(
                        'model = "unterminated\n'
                    )
                else:
                    (Path(self.temp_dir.name) / ".claude" / "settings.json").write_text(
                        '{"hooks":'
                    )
                before = {
                    path: self.path_snapshot(path) for path in self.managed_paths()
                }

                completed = self.make_target("sync", "Y\n")
                output = completed.stdout + completed.stderr

                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("ERROR", output)
                self.assertIn("No files were modified.", output)
                self.assertNotIn("Apply these changes?", output)
                self.assertEqual(
                    before,
                    {path: self.path_snapshot(path) for path in self.managed_paths()},
                )

    def test_installs_and_is_idempotent(self) -> None:
        agents = self.codex_home / "AGENTS.md"
        config = self.codex_home / "config.toml"

        self.assertEqual(SYNC.sync_agents(self.agents_template, agents), "installed")
        self.assertEqual(
            SYNC.sync_hooks(self.hooks_template, config, self.status_script),
            "installed or updated",
        )
        first_agents = agents.read_bytes()
        first_config = config.read_bytes()

        self.assertEqual(
            SYNC.sync_agents(self.agents_template, agents), "already current"
        )
        self.assertEqual(
            SYNC.sync_hooks(self.hooks_template, config, self.status_script),
            "already current",
        )
        self.assertEqual(agents.read_bytes(), first_agents)
        self.assertEqual(config.read_bytes(), first_config)

        parsed = tomllib.loads(config.read_text())
        groups = parsed["hooks"]["SessionStart"]
        self.assertEqual(len(groups), 1)
        self.assertEqual(len(groups[0]["hooks"]), 1)
        self.assertIn(SYNC.MANAGED_HOOK_MARKER, groups[0]["hooks"][0]["command"])

    def test_preferences_add_missing_fields_and_are_idempotent(self) -> None:
        current = '[tui]\nnotifications = true\n'

        rendered = SYNC.render_preferences(self.preferences_template, current)
        self.assertIn("history.persistence", rendered.changed_paths)
        self.assertIn("history.max_bytes", rendered.changed_paths)
        self.assertIn("tui.status_line", rendered.changed_paths)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(parsed["history"]["persistence"], "save-all")
        self.assertEqual(parsed["history"]["max_bytes"], 5242880)
        self.assertTrue(parsed["tui"]["notifications"])
        self.assertEqual(
            parsed["tui"]["status_line"],
            self.expected_status_line,
        )

        second = SYNC.render_preferences(self.preferences_template, rendered.content)
        self.assertEqual(second.action, "already current")
        self.assertEqual(second.content, rendered.content)

    def test_preferences_update_only_owned_fields(self) -> None:
        current = (
            "# keep this comment\n"
            "[history]\n"
            'persistence = "none"\n'
            "max_bytes = 12345\n"
            "unmanaged = true\n\n"
            "[tui]\n"
            'status_line = ["old"]\n'
            "status_line_use_colors = true\n\n"
            "[tui.model_availability_nux]\n"
            '"gpt-5.5" = 4\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(parsed["history"]["persistence"], "save-all")
        self.assertEqual(parsed["history"]["max_bytes"], 5242880)
        self.assertTrue(parsed["history"]["unmanaged"])
        self.assertTrue(parsed["tui"]["status_line_use_colors"])
        self.assertEqual(parsed["tui"]["model_availability_nux"]["gpt-5.5"], 4)
        self.assertIn("# keep this comment", rendered.content)

    def test_sync_moves_history_limit_out_of_hook_block_and_converges(
        self,
    ) -> None:
        self.install_current_managed_state()
        config = self.codex_home / "config.toml"
        config.write_text(
            "[history]\n"
            'persistence = "save-all"\n'
            'unmanaged = "preserved"\n'
        )
        hooked = SYNC.render_hooks(
            self.hooks_template, config, self.status_script, sys.executable
        ).content
        misplaced = hooked.replace(
            f"{SYNC.HOOKS_BEGIN}\n",
            f"{SYNC.HOOKS_BEGIN}\nmax_bytes = 5242880\n",
            1,
        )
        misplaced += (
            "\n[tui]\n"
            f"status_line = {json.dumps(self.expected_status_line)}\n"
        )
        config.write_text(misplaced)
        self.assertEqual(tomllib.loads(misplaced)["history"]["max_bytes"], 5242880)

        completed = self.make_target("sync", "Y\n")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        result = config.read_text()
        self.assertLess(result.index("max_bytes = 5242880"), result.index(SYNC.HOOKS_BEGIN))
        parsed = tomllib.loads(result)
        self.assertEqual(parsed["history"]["max_bytes"], 5242880)
        self.assertEqual(parsed["history"]["unmanaged"], "preserved")
        rerendered_hooks = SYNC.render_hooks(
            self.hooks_template, config, self.status_script, sys.executable
        )
        self.assertEqual(rerendered_hooks.content, result)

        second = self.make_target("agent-sync-check")
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertIn("Result: everything is already current.", second.stdout)

    def test_preferences_add_to_implicit_parent_table(self) -> None:
        current = (
            "# generated UI state\n"
            "[tui.model_availability_nux]\n"
            '"gpt-example" = 1\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(
            parsed["tui"]["status_line"],
            self.expected_status_line,
        )
        self.assertEqual(parsed["tui"]["model_availability_nux"]["gpt-example"], 1)
        self.assertLess(
            rendered.content.index("tui.status_line ="),
            rendered.content.index("[tui.model_availability_nux]"),
        )

        second = SYNC.render_preferences(self.preferences_template, rendered.content)
        self.assertEqual(second.action, "already current")
        self.assertEqual(second.content, rendered.content)

    def test_preferences_update_root_dotted_assignment(self) -> None:
        current = (
            'tui.status_line = ["old"]\n\n'
            "[tui.model_availability_nux]\n"
            '"gpt-example" = 1\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(parsed["tui"]["status_line"], self.expected_status_line)
        self.assertEqual(parsed["tui"]["model_availability_nux"]["gpt-example"], 1)
        self.assertNotIn('["old"]', rendered.content)

    def test_preferences_skip_formatting_only_difference(self) -> None:
        alternate_status_line = ", ".join(
            json.dumps(item) for item in self.expected_status_line
        )
        current = (
            "[history]\n"
            'persistence = "save-all"\n'
            "max_bytes = 5242880\n\n"
            "[tui]\n"
            "status_line = [\n"
            f"  {alternate_status_line}\n"
            "]\n"
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        self.assertEqual(rendered.action, "already current")
        self.assertEqual(rendered.content, current)

    def test_preferences_replace_multiline_owned_value(self) -> None:
        current = (
            "[history]\n"
            'persistence = "none"\n\n'
            "[tui]\n"
            "status_line = [\n"
            '  "old",\n'
            "]\n"
            "unmanaged = true\n"
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(parsed["history"]["persistence"], "save-all")
        self.assertEqual(parsed["history"]["max_bytes"], 5242880)
        self.assertEqual(parsed["tui"]["status_line"], self.expected_status_line)
        self.assertTrue(parsed["tui"]["unmanaged"])

    def test_preferences_preserve_quoted_table_with_hash(self) -> None:
        current = (
            "[tui]\n"
            "notifications = true\n\n"
            '["other#section"]\n'
            'status_line = ["user-owned"]\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(
            parsed["other#section"]["status_line"], ["user-owned"]
        )
        self.assertEqual(parsed["tui"]["status_line"], self.expected_status_line)

    def test_preferences_skip_unowned_multiline_value(self) -> None:
        current = (
            "[tui]\n"
            '"other" = """\n'
            'status_line = ["user-owned"]\n'
            '"""\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(parsed["tui"]["other"], 'status_line = ["user-owned"]\n')
        self.assertEqual(parsed["tui"]["status_line"], self.expected_status_line)

    def test_preferences_ignore_fake_tables_inside_multiline_string(self) -> None:
        current = (
            "[history]\n"
            'persistence = "none"\n'
            'note = """\n'
            "[tui]\n"
            'status_line = ["user-owned text"]\n'
            '"""\n'
        )

        rendered = SYNC.render_preferences(self.preferences_template, current)
        parsed = tomllib.loads(rendered.content)
        self.assertEqual(
            parsed["history"]["note"],
            '[tui]\nstatus_line = ["user-owned text"]\n',
        )
        self.assertEqual(parsed["history"]["persistence"], "save-all")
        self.assertEqual(parsed["history"]["max_bytes"], 5242880)
        self.assertEqual(
            parsed["tui"]["status_line"],
            self.expected_status_line,
        )

    def test_preferences_refuse_unlocatable_existing_value(self) -> None:
        current = (
            "[history]\n"
            'persistence = "save-all"\n\n'
            "[tui]\n"
            'status_line.old = ["value"]\n'
        )

        with self.assertRaises(SYNC.SyncError):
            SYNC.render_preferences(self.preferences_template, current)

    def test_preferences_reject_unallowlisted_template(self) -> None:
        template = Path(self.temp_dir.name) / "preferences.toml"
        template.write_text("[tui]\nanimations = false\n")

        with self.assertRaises(SYNC.SyncError):
            SYNC.render_preferences(template, "")

    def test_preferences_reject_invalid_history_limit(self) -> None:
        template = Path(self.temp_dir.name) / "preferences.toml"
        template.write_text(
            '[history]\npersistence = "save-all"\nmax_bytes = 0\n'
        )

        with self.assertRaises(SYNC.SyncError):
            SYNC.render_preferences(template, "")

    def test_preferences_reject_duplicate_existing_toml(self) -> None:
        current = '[history]\npersistence = "none"\n\n[history]\n'

        with self.assertRaises(SYNC.SyncError):
            SYNC.render_preferences(self.preferences_template, current)

    def test_main_check_reports_preference_drift_without_writing(self) -> None:
        agents = self.codex_home / "AGENTS.md"
        config = self.codex_home / "config.toml"
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{}")
        args = SimpleNamespace(
            agents_template=self.agents_template,
            hooks_template=self.hooks_template,
            preferences_template=self.preferences_template,
            status_script=self.status_script,
            claude_status_line_script=self.claude_status_line_script,
            claude_skill_templates=list(self.skill_templates),
            codex_home=self.codex_home,
            claude_config_dirs=[settings.parent],
            python="python3",
            check=True,
            interactive=False,
            expect=None,
        )

        stdout = StringIO()
        with mock.patch.object(SYNC, "parse_args", return_value=args):
            # `main` reports each managed target on stdout. Capture it so a test
            # run cannot be misread as having just rewritten this host's config.
            with redirect_stdout(stdout):
                self.assertEqual(SYNC.main(), 1)

        self.assertIn("Codex AGENTS.md:", stdout.getvalue())
        self.assertFalse(agents.exists())
        self.assertFalse(config.exists())
        self.assertEqual(settings.read_text(), "{}")

    def test_preserves_codex_hook_state_when_codex_puts_it_inside_marker(self) -> None:
        config = self.codex_home / "config.toml"
        SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        current = config.read_text()
        state = (
            '[hooks.state]\n'
            '[hooks.state."host"]\n'
            'trusted_hash = "sha256:test"\n'
        )
        config.write_text(current.replace(SYNC.HOOKS_END, f"{state}{SYNC.HOOKS_END}"))

        rendered = SYNC.render_hooks(self.hooks_template, config, self.status_script)
        self.assertFalse(rendered.definition_changed)
        self.assertTrue(rendered.state_normalized)
        action = SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        result = config.read_text()

        self.assertEqual(action, "normalized Codex hook state")
        self.assertLess(result.index(SYNC.HOOKS_END), result.index("[hooks.state]"))
        parsed = tomllib.loads(result)
        self.assertEqual(parsed["hooks"]["state"]["host"]["trusted_hash"], "sha256:test")
        self.assertEqual(
            SYNC.sync_hooks(self.hooks_template, config, self.status_script),
            "already current",
        )

    def test_warns_when_hook_definition_changes_with_preserved_state(self) -> None:
        config = self.codex_home / "config.toml"
        SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        current = config.read_text()
        state = (
            '[hooks.state]\n'
            '[hooks.state."host"]\n'
            'trusted_hash = "sha256:test"\n'
        )
        config.write_text(current.replace(SYNC.HOOKS_END, f"{state}{SYNC.HOOKS_END}"))

        changed_status = Path(self.temp_dir.name) / "workspace_status_changed.py"
        changed_status.write_text(self.status_script.read_text() + "\n# changed\n")
        rendered = SYNC.render_hooks(self.hooks_template, config, changed_status)

        self.assertTrue(rendered.definition_changed)
        self.assertTrue(rendered.state_normalized)
        self.assertEqual(rendered.action, "updated; normalized Codex hook state")

        agents = self.codex_home / "AGENTS.md"
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text("{}")
        args = SimpleNamespace(
            agents_template=self.agents_template,
            hooks_template=self.hooks_template,
            preferences_template=self.preferences_template,
            status_script=changed_status,
            claude_status_line_script=self.claude_status_line_script,
            claude_skill_templates=list(self.skill_templates),
            codex_home=self.codex_home,
            claude_config_dirs=[settings.parent],
            python="python3",
            check=False,
            interactive=False,
            expect=None,
        )
        stdout = StringIO()
        stderr = StringIO()
        with mock.patch.object(SYNC, "parse_args", return_value=args):
            with redirect_stdout(stdout), redirect_stderr(stderr):
                self.assertEqual(SYNC.main(), 0)
        self.assertIn("review and trust it with /hooks", stderr.getvalue())

    def test_replaces_only_managed_agents_block(self) -> None:
        agents = self.codex_home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text(
            "# Host preference\n\n"
            f"{SYNC.AGENTS_BEGIN}\nold\n{SYNC.AGENTS_END}\n\n"
            "# Local footer\n"
        )

        SYNC.sync_agents(self.agents_template, agents)
        result = agents.read_text()
        self.assertIn("# Host preference", result)
        self.assertIn("# Local footer", result)
        self.assertIn("# Workspace-Wide Codex Adapter", result)
        self.assertNotIn("\nold\n", result)
        self.assertEqual(result.count(SYNC.AGENTS_BEGIN), 1)

    def test_managed_agents_routes_canonical_workspace_rules(self) -> None:
        agents = self.codex_home / "AGENTS.md"

        SYNC.sync_agents(self.agents_template, agents)
        result = agents.read_text()
        normalized = " ".join(result.split())

        for name in (
            "authorization.md",
            "capabilities.md",
            "codex-runtime.md",
            "deployment.md",
            "documentation.md",
            "environment-truth.md",
            "file-checks.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "problem-follow-up.md",
            "reasoning.md",
            "releases.md",
            "requests.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
            "temporary-files.md",
            "verification.md",
        ):
            self.assertIn(f"~/workspace/.agents/rules/{name}", result)
        self.assertNotIn("claude-runtime.md", result)

        self.assertIn("Project rules provide topology", normalized)
        self.assertIn("technical permission only", normalized)
        self.assertNotIn("Saberu", result)

    def test_canonical_git_rule_carries_publication_transaction_contract(self) -> None:
        result = (self.rules_dir / "git-publication.md").read_text()
        normalized = " ".join(result.split())

        self.assertIn("Checkpoint A", normalized)
        self.assertIn("Checkpoint B", normalized)
        self.assertIn("exact, copyable bundle", normalized)
        self.assertIn("exact-path `git add`", normalized)
        self.assertIn("`git commit`", normalized)
        self.assertIn("`git push`", normalized)
        self.assertIn("`gh pr create`", normalized)
        self.assertIn("ordinary natural language", normalized)
        self.assertIn("run some/all commands personally", normalized)
        self.assertIn("report completion", normalized)
        self.assertIn(
            "completion report authorizes only read-only verification", normalized
        )
        self.assertIn("Integration and cleanup are separate", normalized)
        self.assertNotIn("Commit and push are separate transactions", normalized)

    def test_protected_git_routes_require_action_brief(self) -> None:
        module_names = (
            "git-branches.md",
            "git-publication.md",
            "git-integration.md",
            "git-recovery.md",
            "releases.md",
        )
        for name in module_names:
            content = (self.rules_dir / name).read_text()
            normalized = " ".join(content.split())
            self.assertIn("authorization.md", normalized)
            self.assertIn("Protected-Action Request Brief", normalized)
            self.assertIn("command-only", normalized)

        route_specs = (
            ("branch/worktree/stash action", "git-branches.md"),
            ("stage/commit/push/PR publication", "git-publication.md"),
            ("merge/integration or post-integration handling", "git-integration.md"),
            ("rewrite/discard/force/delete/amend/recovery", "git-recovery.md"),
            (
                "release, version tag or number, rollback target",
                "releases.md",
            ),
        )
        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            for trigger, module in route_specs:
                line = next(
                    line for line in adapter.splitlines() if line.startswith(f"| {trigger}")
                )
                self.assertIn("authorization.md", line)
                self.assertIn("git.md", line)
                self.assertIn(module, line)

    def test_deployment_route_requires_action_brief(self) -> None:
        content = " ".join((self.rules_dir / "deployment.md").read_text().split())
        self.assertIn("authorization.md", content)
        self.assertIn("Protected-Action Request Brief", content)
        self.assertIn("command-only", content)

        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            line = next(
                line
                for line in adapter.splitlines()
                if line.startswith("| deploying, what may serve users")
            )
            self.assertIn("authorization.md", line)
            self.assertIn("deployment.md", line)

    def test_canonical_authorization_rule_requires_action_context(self) -> None:
        result = (self.rules_dir / "authorization.md").read_text()
        normalized = " ".join(result.split())

        self.assertIn("Protected-Action Request Brief", result)
        for field in (
            "What will happen",
            "Why now",
            "Target and scope",
            "Expected effect",
            "Risks and recovery",
            "Excluded actions",
            "Checks and gaps",
            "Approval boundary",
            "Exact operation",
        ):
            self.assertIn(field, result)
        self.assertIn("Before presenting a protected operation", result)
        self.assertIn("asking the user to run it", normalized)
        self.assertIn("word “approve”", normalized)
        self.assertIn("direct user request", normalized)
        self.assertIn("technical approval prompt does not itself authorize", normalized)
        self.assertIn("material change", normalized)
        self.assertIn("ordinary read-only work", normalized)
        self.assertIn("already-authorized, in-scope working-tree edits", normalized)

    def test_workspace_rule_modules_declare_unique_ownership(self) -> None:
        for name in (
            "authorization.md",
            "capabilities.md",
            "claude-runtime.md",
            "codex-runtime.md",
            "deployment.md",
            "documentation.md",
            "environment-truth.md",
            "file-checks.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "problem-follow-up.md",
            "reasoning.md",
            "releases.md",
            "requests.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
            "temporary-files.md",
            "verification.md",
        ):
            content = (self.rules_dir / name).read_text()
            self.assertIn("## Ownership", content)
            self.assertNotIn("Saberu", content)

    def test_agent_adapters_route_the_same_portable_core(self) -> None:
        codex = self.agents_template.read_text()
        claude = (ROOT / "CLAUDE.md").read_text()
        portable = (
            "authorization.md",
            "capabilities.md",
            "deployment.md",
            "documentation.md",
            "environment-truth.md",
            "file-checks.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "problem-follow-up.md",
            "reasoning.md",
            "releases.md",
            "requests.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
            "temporary-files.md",
            "verification.md",
        )

        for name in portable:
            self.assertIn(name, codex)
            self.assertIn(name, claude)

        # Each runtime module is routed only by its own runtime's adapter.
        for runtime_module, own, other in (
            ("codex-runtime.md", codex, claude),
            ("claude-runtime.md", claude, codex),
        ):
            self.assertIn(runtime_module, own)
            self.assertNotIn(runtime_module, other)
        self.assertIn(
            "no user-level `CLAUDE.md` in any Claude config dir is required as a "
            "portable owner",
            " ".join(claude.split()),
        )

        codex_floor = codex.split("## Safety Floor", 1)[1].split(
            "## Direct Task Routing", 1
        )[0]
        claude_floor = claude.split("## Safety Floor", 1)[1].split(
            "## Direct Task Routing", 1
        )[0]
        self.assertEqual(codex_floor, claude_floor)
        self.assertIn("Canonical sources:", codex_floor)
        self.assertIn("switch away from", codex_floor)
        normalized_floor = " ".join(codex_floor.split()).lower()
        reasoning_invariant = (
            "validate load-bearing premises proportionally; keep technical "
            "conclusions distinct from assumptions and operator decisions."
        )
        self.assertEqual(normalized_floor.count(reasoning_invariant), 1)
        self.assertIn("`reasoning.md`", codex_floor)

    def test_reasoning_governance_has_one_owner_and_symmetric_route(self) -> None:
        rule = (self.rules_dir / "reasoning.md").read_text()
        normalized_rule = " ".join(rule.split()).lower()

        for heading in (
            "## Ownership",
            "## Validate Premises Proportionally",
            "## Classify Knowledge States",
            "## Evaluate Evidence",
            "## Diagnose With Discriminating Probes",
            "## Calibrate Uncertainty And Stop",
        ):
            self.assertIn(heading, rule)
        self.assertEqual(rule.count("This file owns the portable method"), 1)

        for invariant in (
            "without an exhaustive premise audit",
            "do not manufacture disagreement",
            "remain authoritative as decisions; they are not empirical evidence",
            "not a mandatory report schema",
            "when ambiguity or consequence makes alternative causes material",
            "do not require a fixed number, a hypothesis table",
            "prefer read-only observation first, then an isolated or reversible probe",
            "a persistent change may still be the appropriate discriminating test",
            "remains subject to `authorization.md`",
            "do not require a numerical confidence score or verbose reasoning report",
            "do not expose or require hidden chain-of-thought",
        ):
            self.assertIn(invariant, normalized_rule)

        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            route = next(
                line
                for line in adapter.splitlines()
                if line.startswith("| load-bearing premise validation")
            )
            trigger, owner = (
                cell.strip() for cell in route.strip("|").split("|", 1)
            )
            for phrase in (
                "load-bearing premise validation",
                "conflicting evidence",
                "independent technical judgment",
                "competing explanations",
                "diagnostic method",
            ):
                self.assertIn(phrase, trigger)
            self.assertIn("reasoning.md", owner)

            normalized_adapter = " ".join(adapter.split()).lower()
            for routed_detail in (
                "relevance to the actual question",
                "a fixed number, a hypothesis table",
                "read-only observation first",
                "numerical confidence score",
            ):
                self.assertNotIn(routed_detail, normalized_adapter)

        domain_entry = self.design_map_entry("reasoning.md")
        for phrase in (
            "premises",
            "knowledge states",
            "evidence",
            "competing explanations",
            "probes",
            "independent judgment",
            "uncertainty",
        ):
            self.assertIn(phrase, domain_entry)

        feedback = (ROOT / "feedback-register.md").read_text()
        provenance_rows = [
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/reasoning.md`")
        ]
        self.assertEqual(len(provenance_rows), 1)
        self.assertIn("W-R43", provenance_rows[0])
        self.assertEqual(feedback.count("- **W-R43 ("), 1)

        readme = " ".join((ROOT / "README.md").read_text().split())
        self.assertIn("technical reasoning", readme)
        self.assertIn("W-R43", readme)

    def test_implementation_shape_has_one_owner_and_symmetric_route(self) -> None:
        rule = (self.rules_dir / "implementation.md").read_text()

        self.assertIn("## Ownership", rule)
        self.assertIn("## One Fact, One Canonical Owner", rule)
        self.assertIn("## Write Durable Comments", rule)
        self.assertIn("## Test Contracts, Not Incidental Text", rule)
        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            route = next(
                line
                for line in adapter.splitlines()
                if line.startswith("| implementation, configuration")
            )
            self.assertIn("artifact-structure", route)
            self.assertIn("implementation.md", route)

    def test_documentation_governance_has_one_owner_and_symmetric_route(self) -> None:
        rule = (self.rules_dir / "documentation.md").read_text()
        normalized_rule = " ".join(rule.split())
        feedback = (ROOT / "feedback-register.md").read_text()

        self.assertIn("## Ownership", rule)
        self.assertIn("## Route Content By Role", rule)
        self.assertIn("## Keep Truth Classes Explicit", rule)
        self.assertIn("## Migrate Without Dual Authority", rule)
        self.assertIn("Compatibility pointers are temporary migration artifacts", rule)
        self.assertIn("project-owned executable gate", rule)
        self.assertIn("before substantive project work", normalized_rule)
        self.assertIn(
            "including read-only review or any host/external action", normalized_rule
        )
        self.assertNotIn("before the first write", normalized_rule)
        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            route = next(
                line
                for line in adapter.splitlines()
                if line.startswith("| project documentation authoring")
            )
            self.assertIn("lifecycle governance", route)
            self.assertIn("documentation.md", route)

        owner_row = next(
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/documentation.md`")
        )
        self.assertIn("W-R38", owner_row)
        self.assertIn("W-R39", owner_row)
        self.assertIn("W-R42", owner_row)

    def test_plan_changelog_lifecycle_uses_frozen_contract_and_verified_closeout(
        self,
    ) -> None:
        planning = (self.rules_dir / "planning.md").read_text()
        documentation = (self.rules_dir / "documentation.md").read_text()
        agents = (ROOT / "AGENTS.md").read_text()

        normalized_plan = " ".join(planning.split())
        normalized_docs = " ".join(documentation.split())
        normalized_agents = " ".join(agents.split())

        for state in ("`DRAFT`", "`APPROVED`", "`COMPLETE`"):
            self.assertIn(state, planning)
        for invariant in (
            "Plan at the level of a coherent workstream",
            "Before creating a persistent Plan",
            "same goal and scope",
            "approved implementation intent and execution contract",
            "At `APPROVED`, stable Plan content freezes",
            "stay in transient task context",
            "conversational turns, implementation rounds",
            "They are not automatically new planning decisions",
            "Identification or recommendation is not approval",
            "only after approval, amend",
            "resume within the amended approval",
            "File count and bug severity alone",
            "Do not mark a Plan `COMPLETE` merely because one implementation or verification pass finished",
            "still actively reviewing, testing, or refining the same goal and scope",
            "final non-transaction-bound verification demonstrates acceptance",
            "create the Changelog as the verified outcome",
            "add a Changelog link as closeout metadata",
            "A `COMPLETE` Plan is normally a historical record",
            "Before its verified result enters durable Git history as a commit",
            "restore that Plan to `APPROVED`",
            "narrow pre-commit closeout-correction exception",
            "Once the completed result has entered Git history, do not reopen its Plan",
            "even when the commit has not been pushed",
            "Treat later work as a follow-up coherent workstream",
            "apply proportional planning independently",
            "a narrow fix may need no persistent Plan",
            "is not authorized by this lifecycle rule",
        ):
            self.assertIn(invariant, normalized_plan)

        self.assertIn("## Separate Plan, Execution, And Changelog", documentation)
        for invariant in (
            "one coherent workstream's approved Goal",
            "approval-time Current State",
            "belong in transient task context",
            "final verified outcome record for a coherent workstream",
            "Normally one Plan produces one final Changelog",
            "round-specific Changelogs",
            "not a mechanical cardinality requirement",
            "It is not a chronological interaction log",
            "Git already owns exact history",
            "lasting limitation or material final correction",
            "Before the workstream result is committed",
            "may revise the existing Changelog",
            "Once the result is committed, preserve its Changelog",
            "including between commit and push",
            "only when proportional planning gives that workstream the persistent Plan/Changelog lifecycle",
            "neither a new commit nor a routine fix creates one automatically",
        ):
            self.assertIn(invariant, normalized_docs)

        for invariant in (
            "non-trivial coherent workstream",
            "Before creating a Plan, reuse an existing active or approved Plan",
            "same goal and scope",
            "do not create additional Plans",
            "not per implementation round",
            "planning.md` and `documentation.md",
        ):
            self.assertIn(invariant, normalized_agents)
        self.assertNotIn(
            "Non-trivial behavior or configuration changes require a plan", agents
        )
        self.assertNotIn("Create the round changelog", agents)

    def test_git_modules_have_task_shaped_load_profiles(self) -> None:
        inspection = (self.rules_dir / "git.md").read_text()
        branches = (self.rules_dir / "git-branches.md").read_text()
        publication = (self.rules_dir / "git-publication.md").read_text()
        integration = (self.rules_dir / "git-integration.md").read_text()
        recovery = (self.rules_dir / "git-recovery.md").read_text()

        self.assertNotIn("gh pr create", inspection)
        self.assertNotIn("force-with-lease", inspection)
        normalized_branches = " ".join(branches.split())
        self.assertIn("Branch Action Review", branches)
        self.assertIn("Conditional Durable Workstream Contract", branches)
        self.assertIn("Content Non-Interference", branches)
        self.assertIn(
            "transaction context, not repository content", normalized_branches
        )
        self.assertIn(
            "Git refs and later reviewed commits are the normal durable evidence",
            normalized_branches,
        )
        self.assertIn(
            "local diagnostic evidence, not portable handoff state",
            normalized_branches,
        )
        self.assertIn(
            "does not authorize a repository-content change", normalized_branches
        )
        self.assertIn("post-action diff must match", normalized_branches)
        self.assertIn(
            "only when the project names a canonical carrier and schema and at "
            "least one of these conditions is true",
            normalized_branches,
        )
        self.assertNotIn("refs, worktree state, reflogs", normalized_branches)
        self.assertNotIn(
            "reviewed contract is the first file write", normalized_branches
        )
        self.assertNotIn("branch exists, contract missing", normalized_branches)
        feedback = (ROOT / "feedback-register.md").read_text()
        owner_row = next(
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/git-branches.md`")
        )
        self.assertIn("W-R40", owner_row)
        self.assertNotIn("gh pr create", branches)
        self.assertIn("gh pr create", publication)
        self.assertIn("Terminal Evidence", integration)
        self.assertNotIn("force-with-lease", integration)
        self.assertIn("force-with-lease", recovery)

    def test_request_reading_and_lasting_rule_content_have_routed_owners(
        self,
    ) -> None:
        # Every request is read for its goal before work starts (W-R71);
        # examples in it are not requirements (W-R63); rules, register entries
        # and memory notes keep only lasting guidance (W-R64).
        requests = (self.rules_dir / "requests.md").read_text()
        for heading in (
            "## Ownership",
            "## Understand The Request",
            "## Ask Or Proceed",
            "## Similar Problems",
        ):
            self.assertEqual(requests.count(heading), 1, heading)
        normalized_requests = " ".join(requests.split()).lower()
        for invariant in (
            "an example shows one case of the need",
            "list the usage scenarios",
            "carry each requirement you derived as an assumption",
            "judge options scenario by scenario",
            "show it with the conflict named",
            "state what done means",
            "find the similar problems the request stands for",
            "ask in one round",
            "when the operator said they will be away",
            "say where you looked, also when nothing turned up",
        ):
            self.assertIn(invariant, normalized_requests)

        planning = (self.rules_dir / "planning.md").read_text()
        self.assertNotIn("## Understand The Request", planning)
        self.assertIn(
            "read the request first (`requests.md`)",
            " ".join(planning.split()).lower(),
        )

        reasoning = (self.rules_dir / "reasoning.md").read_text()
        self.assertIn(
            "an example in a request, or a requirement derived from one, is "
            "not an operator decision (`requests.md`",
            " ".join(reasoning.split()).lower(),
        )

        authoring = (self.rules_dir / "rule-authoring.md").read_text()
        normalized_authoring = " ".join(authoring.split()).lower()
        self.assertIn("only lasting guidance", normalized_authoring)
        self.assertIn("one line of source", normalized_authoring)
        self.assertNotIn("says where it was handed", normalized_authoring)

        claude = (ROOT / "CLAUDE.md").read_text()
        for adapter in (self.agents_template.read_text(), claude):
            routes = [
                line
                for line in adapter.splitlines()
                if line.startswith("| ") and "rules/requests.md`" in line
            ]
            self.assertEqual(len(routes), 1)
            route_trigger = routes[0].strip("|").split("|", 1)[0]
            for trigger in (
                "starting work on a request",
                "a need described through examples",
                "asking the operator or proceeding on assumptions",
            ):
                self.assertIn(trigger, route_trigger)
            planning_routes = [
                line
                for line in adapter.splitlines()
                if line.startswith("| ") and "rules/planning.md`" in line
            ]
            self.assertEqual(len(planning_routes), 1)
            self.assertNotIn("through examples", planning_routes[0])
        auto_memory = claude.split("## Claude Auto-Memory", 1)[1]
        auto_memory = auto_memory.split("\n## ", 1)[0]
        self.assertIn(
            "only lasting guidance", " ".join(auto_memory.split()).lower()
        )

        self.assertIn(
            "how a request is read before work starts",
            self.design_map_entry("requests.md"),
        )

        feedback = (ROOT / "feedback-register.md").read_text()
        for entry, owner in (
            ("W-R63", "requests.md"),
            ("W-R63", "reasoning.md"),
            ("W-R71", "requests.md"),
            ("W-R64", "rule-authoring.md"),
        ):
            self.assertEqual(feedback.count(f"- **{entry} ("), 1)
            row = next(
                line
                for line in feedback.splitlines()
                if line.startswith(f"| `.agents/rules/{owner}`")
            )
            self.assertIn(entry, row)

        # From W-R62 on, an entry is the rule plus one line of source.
        entries: dict[int, list[str]] = {}
        current = None
        for line in feedback.splitlines():
            match = re.match(r"- \*\*W-R(\d+) \(", line)
            if match:
                current = int(match.group(1))
                entries[current] = []
            elif current is not None and line.startswith("    "):
                entries[current].append(line)
            elif line.strip():
                current = None
        new_entries = {
            number: lines for number, lines in entries.items() if number >= 62
        }
        self.assertGreaterEqual(len(new_entries), 2)
        for number, lines in new_entries.items():
            self.assertEqual(len(lines), 1, f"W-R{number}")
            self.assertTrue(
                lines[0].startswith("    - Source: "), f"W-R{number}"
            )

    def test_feedback_intake_problem_reports_and_quality_have_routed_owners(
        self,
    ) -> None:
        # The rule text is the contract: each behavior has one owner section,
        # both resident adapters route its trigger there, and the register
        # keeps its provenance.
        owners = {
            "review.md": (
                "## Problem Reports",
                (
                    "matters outside the asked scope are not problems",
                    "is a lead",
                    "counts once you have checked the evidence it cites",
                    "from its definition",
                    "establishes that claim itself",
                ),
                ("reporting which problems exist",),
                "problem reports",
                "W-R59",
            ),
            "capabilities.md": (
                "## Quality Before Speed",
                (
                    "- work is slow or costly, or a change of method is "
                    "considered to save time or usage; quality before speed "
                    "applies",
                    "keep the configured model, reasoning effort, and "
                    "orchestration settings",
                    "only when it also improves the result",
                    "the operator decides",
                    "let the operator decide before making it",
                ),
                ("slow or costly work",),
                "quality before speed",
                "W-R60",
            ),
            "rule-authoring.md": (
                "## Feedback Intake",
                (
                    "in the reply that takes it in",
                    "workspace-meta governance: route it as provenance and "
                    "refactoring says",
                    "hand it over in the same reply",
                    "is behavior even when it names a setting",
                    "does not route feedback",
                ),
                (
                    "routing feedback",
                    "the operator correcting how you work",
                    "stating a preference about it",
                ),
                "feedback intake",
                "W-R61",
            ),
        }
        adapters = (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        )
        feedback = (ROOT / "feedback-register.md").read_text()

        for name, owner in owners.items():
            heading, invariants, triggers, domain, entry = owner
            rule = (self.rules_dir / name).read_text()
            self.assertEqual(rule.count(heading), 1, name)
            normalized_rule = " ".join(rule.split()).lower()
            for invariant in invariants:
                self.assertIn(invariant, normalized_rule)

            for adapter in adapters:
                route_triggers = [
                    line.strip("|").split("|", 1)[0]
                    for line in adapter.splitlines()
                    if line.startswith("| ") and f"rules/{name}`" in line
                ]
                matching = [
                    route_trigger
                    for route_trigger in route_triggers
                    if all(trigger in route_trigger for trigger in triggers)
                ]
                self.assertEqual(len(matching), 1, name)

            self.assertIn(domain, self.design_map_entry(name))

            self.assertEqual(feedback.count(f"- **{entry} ("), 1)
            provenance_rows = [
                line
                for line in feedback.splitlines()
                if line.startswith(f"| `.agents/rules/{name}`")
            ]
            self.assertEqual(len(provenance_rows), 1, name)
            self.assertIn(entry, provenance_rows[0])

        claude = (ROOT / "CLAUDE.md").read_text()
        auto_memory = claude.split("## Claude Auto-Memory", 1)[1]
        auto_memory = auto_memory.split("\n## ", 1)[0]
        normalized_memory = " ".join(auto_memory.split())
        self.assertIn("`rule-authoring.md` Feedback Intake", normalized_memory)
        self.assertIn("does not route a cross-project one", normalized_memory)

    def test_delegation_allocation_has_routed_owners(self) -> None:
        # Delegated work gets a model and effort per subtask (W-R72): the
        # portable allocation lives in capabilities.md, the Claude settings
        # that apply it in claude-runtime.md.
        capabilities = (self.rules_dir / "capabilities.md").read_text()
        self.assertEqual(capabilities.count("## Delegation"), 1)
        normalized = " ".join(capabilities.split()).lower()
        for invariant in (
            "survey the subtasks first",
            "give each agent the model and reasoning effort its demand needs",
            "judgment work and the final synthesis keep at least the configured "
            "model and effort",
            "mechanical work whose result is checked may use a lighter model or "
            "a lower effort",
            "subagents cannot ask, so settle the open points first",
            "report the allocation with the result",
            "under delegation applies them, it does not lower them",
        ):
            self.assertIn(invariant, normalized)

        runtime = (self.rules_dir / "claude-runtime.md").read_text()
        for heading in (
            "## Ownership",
            "## Configuration Layers",
            "## Project Entry Files",
            "## Memory",
            "## Asking The Operator",
            "## Delegation",
            "## Long Unattended Runs",
        ):
            self.assertEqual(runtime.count(heading), 1, heading)
        normalized_runtime = " ".join(runtime.split()).lower()
        for invariant in (
            "where it and a shared owner differ, the shared owner governs",
            "set both explicitly on every delegated agent",
            "each config dir keeps its own memory",
            "subagents cannot ask",
            "`/goal` does not change permissions",
        ):
            self.assertIn(invariant, normalized_runtime)

        claude = (ROOT / "CLAUDE.md").read_text()
        self.assertIn(
            "set each agent's model and effort", " ".join(claude.split()).lower()
        )
        for adapter, runtime_module in (
            (self.agents_template.read_text(), "codex-runtime.md"),
            (claude, "claude-runtime.md"),
        ):
            routes = [
                line
                for line in adapter.splitlines()
                if line.startswith("| ")
                and "delegating work to subagents or a workflow" in line
            ]
            self.assertEqual(len(routes), 1)
            self.assertIn("rules/capabilities.md`", routes[0])
            self.assertIn(f"rules/{runtime_module}`", routes[0])

    def test_commands_the_user_runs_have_routed_owners(self) -> None:
        # A command the user runs goes to a new terminal of their own (W-R62)
        # and stays short enough to copy as one line (W-R65); the Claude
        # adapter overrides the runtime's own `!` suggestion.
        capabilities = (self.rules_dir / "capabilities.md").read_text()
        self.assertEqual(capabilities.count("## Commands The User Runs"), 1)
        section = capabilities.split("## Commands The User Runs", 1)[1]
        section = " ".join(section.split("\n## ", 1)[0].split()).lower()
        for invariant in (
            "hand it over for a new terminal of their own, not for the "
            "agent's conversation input",
            "a passphrase, password, or confirmation prompt returns",
            "name the host and account it runs as",
            "reaches the same agent, store, or environment",
            "afterwards check the effect from the session",
            "or longer than about 60 characters, write it to a script file",
            "the wrap can be copied as a line break",
            "a single simple command within that length is given as it is",
            "the command that runs a script stays within that length too",
            "not in a long runtime scratch directory",
        ):
            self.assertIn(invariant, section)

        claude = (ROOT / "CLAUDE.md").read_text()
        self.assertEqual(claude.count("## Commands The User Runs"), 1)
        override = claude.split("## Commands The User Runs", 1)[1]
        override = " ".join(override.split("\n## ", 1)[0].split())
        self.assertIn(
            "`.agents/rules/capabilities.md` Commands The User Runs", override
        )
        self.assertIn("Never suggest the `!` prompt prefix", override)

        runtime = (self.rules_dir / "claude-runtime.md").read_text()
        ownership = runtime.split("## Ownership", 1)[1].split("\n## ", 1)[0]
        self.assertIn(
            "(`CLAUDE.md` Claude Auto-Memory and Commands The User Runs)",
            " ".join(ownership.split()),
        )

        for adapter in (self.agents_template.read_text(), claude):
            routes = [
                line
                for line in adapter.splitlines()
                if line.startswith("| ") and "slow or costly work" in line
            ]
            self.assertEqual(len(routes), 1)
            route_trigger = routes[0].strip("|").split("|", 1)[0]
            self.assertIn("a command for the user to run", route_trigger)
            self.assertNotIn("in their own terminal", route_trigger)
            self.assertIn("rules/capabilities.md`", routes[0])

        entry = self.design_map_entry("capabilities.md")
        self.assertIn("where and how the operator runs a command", entry)
        self.assertIn("(../../claude.md#commands-the-user-runs)", entry)

        feedback = (ROOT / "feedback-register.md").read_text()
        row = next(
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/capabilities.md`")
        )
        for entry_id in ("W-R62", "W-R65"):
            self.assertEqual(feedback.count(f"- **{entry_id} ("), 1)
            self.assertIn(entry_id, row)

    def test_temporary_files_keep_reusable_work(self) -> None:
        # Before removing its temporary files, an agent proposes moving what
        # will be needed again to its owner (W-R75); both adapters route the
        # removal moment, not only creation.
        rule = (self.rules_dir / "temporary-files.md").read_text()
        lifecycle = rule.split("## Lifecycle", 1)[1].split("\n## ", 1)[0]
        lifecycle = " ".join(lifecycle.split()).lower()
        for invariant in (
            "before removing them, sort out what will be needed again",
            "propose to the operator to move each such item to its owner",
            "a script that will run again into its project as a tool",
            "an evaluation scenario into the project's evaluation tree",
            "remove only the rest",
            "what was moved or proposed for moving to an owner",
        ):
            self.assertIn(invariant, lifecycle)

        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            routes = [
                line
                for line in adapter.splitlines()
                if line.startswith("| ") and "rules/temporary-files.md`" in line
            ]
            self.assertEqual(len(routes), 1)
            self.assertIn("creating or removing temporary files", routes[0])

        self.assertIn(
            "a script or scenario that will be needed again deleted",
            self.design_map_entry("temporary-files.md"),
        )

        feedback = (ROOT / "feedback-register.md").read_text()
        self.assertEqual(feedback.count("- **W-R75 ("), 1)
        row = next(
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/temporary-files.md`")
        )
        self.assertIn("W-R75", row)

    def test_handed_over_commands_say_how_to_open_the_terminal(self) -> None:
        # A command for the user's own terminal comes with the steps to open
        # that terminal from where they are (W-R76).
        capabilities = (self.rules_dir / "capabilities.md").read_text()
        section = capabilities.split("## Commands The User Runs", 1)[1]
        section = " ".join(section.split("\n## ", 1)[0].split()).lower()
        self.assertIn(
            "- say how the user opens that terminal from where they are: first "
            "check how the session runs, such as inside a terminal multiplexer or "
            "over ssh, from what the session can read about itself or by asking "
            "the user; then give the steps, such as the multiplexer's keys for a "
            "new window and how to get back, and say when the keys given are only "
            "the defaults.",
            section,
        )

        self.assertIn(
            "a command handed over without the steps to open the terminal",
            self.design_map_entry("capabilities.md"),
        )

        feedback = (ROOT / "feedback-register.md").read_text()
        self.assertEqual(feedback.count("- **W-R76 ("), 1)
        row = next(
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/capabilities.md`")
        )
        self.assertIn("W-R76", row)

    def test_a_floated_idea_gets_the_brief_before_the_work(self) -> None:
        # An idea floated for new or changed behavior gets the brief, with what
        # done means and the usage scenarios, before any work; the middle
        # depth reports its done check only with the result.
        requests = (self.rules_dir / "requests.md").read_text()
        section = requests.split("## Understand The Request", 1)[1].split("\n## ", 1)[0]
        whole = " ".join(section.split()).lower()
        depths = [
            " ".join(item.split()).lower()
            for item in section.split("\n\n1. ", 1)[0].split("\n- ")[1:]
        ]
        idea = [d for d in depths if "an idea the operator floats" in d]
        self.assertEqual(len(idea), 1)
        self.assertIn("an idea the operator floats for new or changed behavior, also "
                      "when it comes with examples", idea[0])
        self.assertIn("do every step, and give the brief below before the work", idea[0])
        self.assertEqual([d for d in depths if "idea" in d], idea)
        middle = [d for d in depths if d.startswith("a reported problem")]
        self.assertEqual(len(middle), 1)
        self.assertIn("report the done check and the similar problems with the result",
                      middle[0])
        for invariant in (
            "a request that floats an idea for new or changed behavior takes the last "
            "depth even when it also reports a problem, makes a correction, or fits "
            "the first depth; an idea that only renames or rewords takes the first, "
            "unless the request also reports a problem or makes a correction, which "
            "keeps the middle depth",
            "for an idea, what done would mean once the idea is carried out",
            "the brief has six parts: the goal; done;",
            "the options per scenario",
        ):
            self.assertIn(invariant, whole)

        self.assertIn(
            "a floated idea answered without what done would mean",
            self.design_map_entry("requests.md"),
        )

    def test_project_bootstrap_has_routed_owners(self) -> None:
        # Projects get their missing agent entry files without asking (W-R73).
        documentation = (self.rules_dir / "documentation.md").read_text()
        self.assertEqual(documentation.count("## Project Bootstrap"), 1)
        self.assertLess(
            documentation.index("## Make Agent Instructions Loadable"),
            documentation.index("## Project Bootstrap"),
        )
        loadable = documentation.split("## Make Agent Instructions Loadable", 1)[1]
        loadable = " ".join(loadable.split("\n## ", 1)[0].split()).lower()
        self.assertIn(
            "every additional entry file is a thin adapter that imports that "
            "owner and states no rule of its own",
            loadable,
        )
        bootstrap = documentation.split("## Project Bootstrap", 1)[1]
        bootstrap = " ".join(bootstrap.split("\n## ", 1)[0].split()).lower()
        for invariant in (
            "the canonical owner of the project's agent facts is `agents.md`",
            "add its entry file as a thin adapter that imports the owner",
            "a runtime that cannot import gets no adapter: report the owner move",
            "write only the runtime's local entry file",
            "exclude it through the clone's own git exclude list, never its "
            "tracked `.gitignore`",
            "never overwrite or rewrite an existing entry file",
            "leave what you created uncommitted and report it",
            "is bootstrapped only when the operator asks",
            "a linked worktree without entry files of its own is not "
            "bootstrapped itself: its main checkout is",
            "a delegated agent, and any task whose operator instruction or brief "
            "forbids writes, reports the missing entry file instead of creating it",
        ):
            self.assertIn(invariant, bootstrap)

        authorization = (self.rules_dir / "authorization.md").read_text()
        allowed = authorization.split(
            "## Work That Proceeds Without Another Confirmation", 1
        )[1].split("\n## ", 1)[0]
        self.assertIn(
            "creating a missing project entry file as `documentation.md` "
            "project bootstrap describes",
            " ".join(allowed.split()).lower(),
        )

        runtime = (self.rules_dir / "claude-runtime.md").read_text()
        entry_files = runtime.split("## Project Entry Files", 1)[1]
        entry_files = " ".join(entry_files.split("\n## ", 1)[0].split())
        # The same import lines the session-start readiness check accepts.
        for invariant in (
            "`CLAUDE.md` at the project root, holding the line `@AGENTS.md`",
            "so the line is `@../AGENTS.md` in `.claude/CLAUDE.md`",
            "only `CLAUDE.local.md`, listed in the clone's exclude file",
        ):
            self.assertIn(invariant, entry_files)

        for adapter in (
            self.agents_template.read_text(),
            (ROOT / "CLAUDE.md").read_text(),
        ):
            route = next(
                line
                for line in adapter.splitlines()
                if line.startswith("| project documentation authoring")
            )
            self.assertIn(
                "a project without an entry file for the runtime in use", route
            )
            self.assertIn("documentation.md", route)

    def test_migrates_only_exact_legacy_agents_file(self) -> None:
        agents = self.codex_home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        legacy = "# Legacy workspace-meta guidance\n"
        agents.write_text(legacy)
        legacy_hash = hashlib.sha256(legacy.encode()).hexdigest()

        with mock.patch.object(SYNC, "LEGACY_AGENTS_SHA256", legacy_hash):
            action = SYNC.sync_agents(self.agents_template, agents)

        self.assertEqual(action, "migrated legacy file")
        self.assertNotIn("Legacy workspace-meta", agents.read_text())

    def test_preserves_unknown_unmanaged_agents_content(self) -> None:
        agents = self.codex_home / "AGENTS.md"
        agents.parent.mkdir(parents=True)
        agents.write_text("# Personal guidance\n")

        action = SYNC.sync_agents(self.agents_template, agents)

        self.assertIn("preserved", action)
        self.assertTrue(agents.read_text().startswith("# Personal guidance\n"))
        self.assertEqual(agents.read_text().count(SYNC.AGENTS_BEGIN), 1)

    def test_migrates_legacy_hooks_and_preserves_host_state(self) -> None:
        config = self.codex_home / "config.toml"
        config.parent.mkdir(parents=True)
        config.write_text(
            'model = "host-model"\n\n'
            '[[hooks.SessionStart]]\nmatcher = "startup|resume"\n\n'
            '[[hooks.SessionStart.hooks]]\n'
            "command = 'workspace-meta: governance rule layer'\n\n"
            '[[hooks.SessionStart.hooks]]\n'
            "command = 'bash env_probe.sh'\n\n"
            '[[hooks.SessionStart]]\nmatcher = "startup|resume"\n\n'
            '[[hooks.SessionStart.hooks]]\n'
            "command = 'check unpushed commit'\n\n"
            '[hooks.state]\n\n'
            '[hooks.state."legacy"]\nenabled = true\n'
        )

        action = SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        result = config.read_text()
        parsed = tomllib.loads(result)

        self.assertIn("migrated 2 legacy hook group", action)
        self.assertEqual(parsed["model"], "host-model")
        self.assertTrue(parsed["hooks"]["state"]["legacy"]["enabled"])
        self.assertEqual(len(parsed["hooks"]["SessionStart"]), 1)
        self.assertEqual(len(parsed["hooks"]["SessionStart"][0]["hooks"]), 1)
        self.assertEqual(result.count(SYNC.HOOKS_BEGIN), 1)
        self.assertNotIn("workspace-meta: governance rule layer", result)

        first_result = config.read_bytes()
        self.assertEqual(
            SYNC.sync_hooks(self.hooks_template, config, self.status_script),
            "already current",
        )
        self.assertEqual(config.read_bytes(), first_result)

    def test_refuses_mixed_legacy_and_user_hook_group(self) -> None:
        config = self.codex_home / "config.toml"
        config.parent.mkdir(parents=True)
        original = (
            '[[hooks.SessionStart]]\nmatcher = "startup|resume"\n\n'
            '[[hooks.SessionStart.hooks]]\n'
            "command = 'workspace-meta: governance rule layer'\n\n"
            '[[hooks.SessionStart.hooks]]\n'
            "command = 'user-owned-hook'\n"
        )
        config.write_text(original)

        with self.assertRaises(SYNC.SyncError):
            SYNC.sync_hooks(self.hooks_template, config, self.status_script)

        self.assertEqual(config.read_text(), original)

    def test_invalid_existing_toml_is_not_overwritten(self) -> None:
        config = self.codex_home / "config.toml"
        config.parent.mkdir(parents=True)
        original = 'model = "unterminated\n'
        config.write_text(original)

        with self.assertRaises(SYNC.SyncError):
            SYNC.sync_hooks(self.hooks_template, config, self.status_script)

        self.assertEqual(config.read_text(), original)

    def test_managed_loader_emits_json_when_script_hash_mismatches(self) -> None:
        config = self.codex_home / "config.toml"
        SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        parsed = tomllib.loads(config.read_text())
        handlers = parsed["hooks"]["SessionStart"][0]["hooks"]
        env = os.environ.copy()
        env["HOME"] = str(Path(self.temp_dir.name) / "missing-home")

        self.assertEqual(len(handlers), 1)
        for handler in handlers:
            completed = subprocess.run(
                ["/bin/sh", "-c", handler["command"]],
                check=False,
                capture_output=True,
                env=env,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            message = json.loads(completed.stdout)
            self.assertIsInstance(message.get("systemMessage"), str)
            self.assertTrue(message["systemMessage"])

    def test_claude_migration_preserves_unmanaged_settings(self) -> None:
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        settings.write_text(
            json.dumps(
                {
                    "theme": "dark",
                    "hooks": {
                        "SessionStart": [
                            {
                                "hooks": [
                                    {
                                        "type": "command",
                                        "command": "workspace-meta: governance rule layer",
                                    }
                                ]
                            },
                            {
                                "hooks": [
                                    {"type": "command", "command": "user-owned-hook"}
                                ]
                            },
                        ]
                    },
                }
            )
        )

        action = SYNC.sync_claude_settings(settings, self.status_script)
        parsed = json.loads(settings.read_text())
        groups = parsed["hooks"]["SessionStart"]

        self.assertIn("migrated 1 legacy hook group", action)
        self.assertEqual(parsed["theme"], "dark")
        self.assertEqual(parsed["statusLine"]["type"], "command")
        self.assertEqual(parsed["statusLine"]["padding"], 0)
        self.assertIn(
            SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER,
            parsed["statusLine"]["command"],
        )
        self.assertEqual(len(groups), 2)
        self.assertIn(SYNC.MANAGED_HOOK_MARKER, groups[0]["hooks"][0]["command"])
        self.assertEqual(groups[1]["hooks"][0]["command"], "user-owned-hook")
        self.assertEqual(
            SYNC.sync_claude_settings(settings, self.status_script), "already current"
        )

    def test_claude_status_line_update_is_not_reported_as_legacy_migration(
        self,
    ) -> None:
        settings = self.codex_home.parent / ".claude" / "settings.json"
        SYNC.sync_claude_settings(
            settings,
            self.status_script,
            claude_status_line_script=self.claude_status_line_script,
        )
        changed_renderer = Path(self.temp_dir.name) / "changed-status-line.py"
        changed_renderer.write_bytes(
            self.claude_status_line_script.read_bytes() + b"\n# changed renderer\n"
        )

        action = SYNC.sync_claude_settings(
            settings,
            self.status_script,
            claude_status_line_script=changed_renderer,
        )

        self.assertEqual(action, "installed or updated")
        groups = json.loads(settings.read_text())["hooks"]["SessionStart"]
        self.assertEqual(len(groups), 1)
        self.assertIn(SYNC.MANAGED_HOOK_MARKER, groups[0]["hooks"][0]["command"])

    def test_claude_refuses_mixed_owned_and_user_group(self) -> None:
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        original = json.dumps(
            {
                "hooks": {
                    "SessionStart": [
                        {
                            "hooks": [
                                {
                                    "type": "command",
                                    "command": "workspace-meta: governance rule layer",
                                },
                                {"type": "command", "command": "user-owned-hook"},
                            ]
                        }
                    ]
                }
            }
        )
        settings.write_text(original)

        with self.assertRaises(SYNC.SyncError):
            SYNC.sync_claude_settings(settings, self.status_script)

        self.assertEqual(settings.read_text(), original)

    def test_claude_keeps_status_line_owned_outside_workspace_meta(self) -> None:
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        for status_line in (
            {"type": "command", "command": "~/.claude/personal-status-line.sh"},
            {
                "type": "command",
                "command": f"echo {SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER}-custom",
            },
            "not an object",
        ):
            with self.subTest(status_line=status_line):
                settings.write_text(
                    json.dumps({"theme": "dark", "statusLine": status_line})
                )

                SYNC.sync_claude_settings(settings, self.status_script)

                parsed = json.loads(settings.read_text())
                self.assertEqual(parsed["statusLine"], status_line)
                self.assertEqual(parsed["theme"], "dark")
                self.assertIn(
                    SYNC.MANAGED_HOOK_MARKER,
                    parsed["hooks"]["SessionStart"][0]["hooks"][0]["command"],
                )
                self.assertEqual(
                    SYNC.sync_claude_settings(settings, self.status_script),
                    "already current",
                )

    def test_foreign_status_line_is_kept_while_other_areas_apply(self) -> None:
        # A per-account wrapper such as the TEAM badge belongs to another tool.
        team_dir = Path(self.temp_dir.name) / ".claude-work"
        claude_dirs = (self.claude_dir, team_dir)
        team_settings = team_dir / "settings.json"
        team_settings.parent.mkdir(parents=True)
        wrapper = {
            "type": "command",
            "command": "printf ' TEAM '; : claude-work-statusline-v1",
            "padding": 0,
        }
        team_settings.write_text(
            json.dumps({"theme": "dark", "statusLine": wrapper}, indent=2) + "\n"
        )
        env = self.isolated_env(claude_dirs)

        completed = self.make_target("sync", "Y\n", env)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        kept_label = self.claude_labels("~/.claude-work")[1]
        self.assertRegex(
            completed.stdout,
            rf"(?m)^{re.escape(kept_label)}:\s+"
            r"kept: statusLine owned outside workspace-meta$",
        )
        self.assertNotIn(f"- {kept_label}", completed.stdout)
        self.assertNotIn(wrapper["command"], completed.stdout + completed.stderr)
        parsed = json.loads(team_settings.read_text())
        self.assertEqual(parsed["statusLine"], wrapper)
        self.assertEqual(parsed["theme"], "dark")
        self.assertIn(
            SYNC.MANAGED_HOOK_MARKER,
            parsed["hooks"]["SessionStart"][0]["hooks"][0]["command"],
        )
        for name, template in zip(self.skill_names(), self.skill_templates):
            self.assertEqual(
                (team_dir / "skills" / name / "SKILL.md").read_bytes(),
                template.read_bytes(),
            )
        personal = json.loads((self.claude_dir / "settings.json").read_text())
        self.assertIn(
            SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER, personal["statusLine"]["command"]
        )

        second = self.make_target("agent-sync-check", env=env)
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertIn("Result: everything is already current.", second.stdout)

    def test_claude_status_line_loader_preserves_stdin_and_runs_renderer(self) -> None:
        home = Path(self.temp_dir.name) / "home"
        installed_script = home / "workspace" / "scripts" / "claude_status_line.py"
        installed_script.parent.mkdir(parents=True)
        installed_script.write_bytes(self.claude_status_line_script.read_bytes())
        settings = home / ".claude" / "settings.json"

        SYNC.sync_claude_settings(
            settings,
            self.status_script,
            sys.executable,
            self.claude_status_line_script,
        )
        command = json.loads(settings.read_text())["statusLine"]["command"]
        payload = {
            "workspace": {"current_dir": str(home / "workspace")},
            "model": {"display_name": "Sonnet"},
            "context_window": {"used_percentage": 25},
        }
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["NO_COLOR"] = "1"
        completed = subprocess.run(
            ["/bin/sh", "-c", command],
            input=json.dumps(payload),
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "~/workspace  Sonnet  ctx:25%")

    def test_agents_pin_the_same_status_evaluator(self) -> None:
        config = self.codex_home / "config.toml"
        settings = self.codex_home.parent / ".claude" / "settings.json"
        digest = hashlib.sha256(self.status_script.read_bytes()).hexdigest()

        SYNC.sync_hooks(self.hooks_template, config, self.status_script)
        SYNC.sync_claude_settings(settings, self.status_script)

        codex_command = tomllib.loads(config.read_text())["hooks"]["SessionStart"][0][
            "hooks"
        ][0]["command"]
        claude_command = json.loads(settings.read_text())["hooks"]["SessionStart"][0][
            "hooks"
        ][0]["command"]
        self.assertIn(digest, codex_command)
        self.assertIn(digest, claude_command)
        self.assertEqual(
            codex_command.replace("--agent codex", "--agent claude"), claude_command
        )
        status_line = json.loads(settings.read_text())["statusLine"]
        status_digest = hashlib.sha256(
            self.claude_status_line_script.read_bytes()
        ).hexdigest()
        self.assertIn(status_digest, status_line["command"])
        self.assertIn(SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER, status_line["command"])

    def test_embeds_resolved_python_in_generated_command(self) -> None:
        config = self.codex_home / "config.toml"
        settings = self.codex_home.parent / ".claude" / "settings.json"
        custom_python = "/opt/homebrew/bin/python3"

        SYNC.sync_hooks(self.hooks_template, config, self.status_script, custom_python)
        SYNC.sync_claude_settings(settings, self.status_script, custom_python)

        codex_command = tomllib.loads(config.read_text())["hooks"]["SessionStart"][0][
            "hooks"
        ][0]["command"]
        claude_command = json.loads(settings.read_text())["hooks"]["SessionStart"][0][
            "hooks"
        ][0]["command"]
        self.assertIn(f"{custom_python} -c", codex_command)
        self.assertIn(f'{custom_python} "$p"', codex_command)
        self.assertIn(custom_python, claude_command)
        status_line_command = json.loads(settings.read_text())["statusLine"]["command"]
        self.assertIn(f"{custom_python} -c", status_line_command)
        self.assertIn(f'exec {custom_python} "$p"', status_line_command)

    def test_quotes_python_path_in_generated_command(self) -> None:
        config = self.codex_home / "config.toml"
        python_with_spaces = "/tmp/Python Builds/python3"

        SYNC.sync_hooks(
            self.hooks_template, config, self.status_script, python_with_spaces
        )

        command = tomllib.loads(config.read_text())["hooks"]["SessionStart"][0][
            "hooks"
        ][0]["command"]
        self.assertIn("'/tmp/Python Builds/python3' -c", command)
        self.assertIn("else '/tmp/Python Builds/python3' \"$p\"", command)

    def test_python_discovery_resolves_a_path_command(self) -> None:
        bin_dir = Path(self.temp_dir.name) / "bin"
        bin_dir.mkdir()
        python_link = bin_dir / "python3"
        try:
            python_link.symlink_to(Path(sys.executable))
        except (OSError, NotImplementedError) as exc:
            self.skipTest(f"symlink unavailable: {exc}")

        env = os.environ.copy()
        env.pop("WORKSPACE_META_PYTHON", None)
        env["PATH"] = f"{bin_dir}:/usr/bin:/bin"
        completed = subprocess.run(
            [str(ROOT / "scripts" / "find_python.sh")],
            capture_output=True,
            check=False,
            text=True,
            env=env,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout.strip(), str(python_link))

    def test_invalid_claude_json_prevents_all_main_writes(self) -> None:
        # Prevalidation is all-or-nothing across every managed target: one bad
        # config dir blocks the Codex files and every other config dir too.
        agents = self.codex_home / "AGENTS.md"
        config = self.codex_home / "config.toml"
        team_dir = Path(self.temp_dir.name) / ".claude-work"
        claude_dirs = (self.claude_dir, team_dir)
        self.codex_home.mkdir(parents=True)
        team_dir.mkdir()
        agents.write_text("# Personal\n")
        config.write_text('model = "host-model"\n')
        (team_dir / "settings.json").write_text('{"hooks":')
        before = {
            path: self.path_snapshot(path)
            for path in self.managed_paths(claude_dirs)
        }

        completed = self.sync_cli(claude_config_dirs=claude_dirs)

        self.assertEqual(completed.returncode, 1)
        self.assertIn("Claude settings [~/.claude-work]", completed.stderr)
        self.assertIn("No files were modified.", completed.stderr)
        self.assertEqual(
            before,
            {
                path: self.path_snapshot(path)
                for path in self.managed_paths(claude_dirs)
            },
        )


if __name__ == "__main__":
    unittest.main()

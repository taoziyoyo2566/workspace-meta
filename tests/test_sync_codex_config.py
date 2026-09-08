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
        self.env_skill_template = (
            ROOT / ".agents" / "host-templates" / "env-sync-SKILL.md"
        )
        self.env_skill = (
            Path(self.temp_dir.name) / ".claude" / "skills" / "env-sync" / "SKILL.md"
        )
        self.rules_dir = ROOT / ".agents" / "rules"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def sync_cli(self, mode: str | None = None, input_text: str | None = None):
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
            "--env-skill-template",
            str(self.env_skill_template),
            "--codex-home",
            str(self.codex_home),
            "--claude-settings",
            str(Path(self.temp_dir.name) / ".claude" / "settings.json"),
            "--env-skill",
            str(self.env_skill),
        ]
        if mode:
            args.append(mode)
        return subprocess.run(
            args,
            input=input_text,
            capture_output=True,
            check=False,
            text=True,
        )

    def make_target(self, target: str, input_text: str | None = None):
        env = os.environ.copy()
        env["HOME"] = self.temp_dir.name
        env["CODEX_HOME"] = str(self.codex_home)
        env["PYTHON"] = sys.executable
        return subprocess.run(
            ["make", target],
            cwd=ROOT,
            env=env,
            input=input_text,
            capture_output=True,
            check=False,
            text=True,
        )

    def managed_paths(self) -> tuple[Path, ...]:
        return (
            self.codex_home / "AGENTS.md",
            self.codex_home / "config.toml",
            Path(self.temp_dir.name) / ".claude" / "settings.json",
            self.env_skill,
        )

    @staticmethod
    def path_snapshot(path: Path) -> tuple[bool, bytes | None, int | None]:
        return (
            path.exists(),
            path.read_bytes() if path.exists() else None,
            path.stat().st_mtime_ns if path.exists() else None,
        )

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
        for label in (
            "Codex AGENTS.md",
            "Codex SessionStart hook",
            "Codex preferences",
            "Claude SessionStart hook",
            "Claude statusLine",
            "env-sync skill",
        ):
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
        for label in (
            "Codex AGENTS.md",
            "Codex SessionStart hook",
            "Claude SessionStart hook",
            "Claude statusLine",
            "env-sync skill",
        ):
            self.assertRegex(completed.stdout, rf"(?m)^{re.escape(label)}:\s+OK$")
        self.assertIn("Sync complete: 1 updated, 5 unchanged.", completed.stdout)
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
        for label, script in (
            ("Codex SessionStart hook", "scripts/workspace_status.py"),
            ("Claude SessionStart hook", "scripts/workspace_status.py"),
            ("Claude statusLine", "scripts/claude_status_line.py"),
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
        self.assertRegex(
            completed.stdout, r"(?m)^Claude SessionStart hook:\s+DRIFT$"
        )
        self.assertRegex(completed.stdout, r"(?m)^Claude statusLine:\s+DRIFT$")
        hook_details = completed.stdout.split("  Claude SessionStart hook:", 1)[1]
        hook_details = hook_details.split("\n\n  ", 1)[0]
        status_details = completed.stdout.split("  Claude statusLine:", 1)[1]
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
        hook_details = completed.stdout.split("  Claude SessionStart hook:", 1)[1]
        hook_details = hook_details.split("\n\n  ", 1)[0]
        status_details = completed.stdout.split("  Claude statusLine:", 1)[1]
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
            env_skill_template=self.env_skill_template,
            env_skill=self.env_skill,
            codex_home=self.codex_home,
            claude_settings=settings,
            python="python3",
            check=True,
            interactive=False,
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
            env_skill_template=self.env_skill_template,
            env_skill=self.env_skill,
            codex_home=self.codex_home,
            claude_settings=settings,
            python="python3",
            check=False,
            interactive=False,
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
            "documentation.md",
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "reasoning.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
            "verification.md",
        ):
            self.assertIn(f"~/workspace/.agents/rules/{name}", result)

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
            "codex-runtime.md",
            "documentation.md",
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "reasoning.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
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
            "documentation.md",
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "implementation.md",
            "planning.md",
            "reasoning.md",
            "review.md",
            "rule-authoring.md",
            "secrets.md",
            "verification.md",
        )

        for name in portable:
            self.assertIn(name, codex)
            self.assertIn(name, claude)

        self.assertIn("codex-runtime.md", codex)
        self.assertNotIn("codex-runtime.md", claude)
        self.assertIn("no `~/.claude/CLAUDE.md` is required", claude)

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

        owner_matrix = (
            ROOT / ".agents/host-templates/README-agents.md"
        ).read_text()
        owner_rows = [
            line
            for line in owner_matrix.splitlines()
            if "| `reasoning.md` |" in line
        ]
        self.assertEqual(len(owner_rows), 1)
        for phrase in (
            "premises",
            "knowledge states",
            "evidence",
            "competing explanations",
            "probes",
            "independent judgment",
            "uncertainty",
        ):
            self.assertIn(phrase, owner_rows[0])

        feedback = (ROOT / "feedback-register.md").read_text()
        provenance_rows = [
            line
            for line in feedback.splitlines()
            if line.startswith("| `.agents/rules/reasoning.md`")
        ]
        self.assertEqual(len(provenance_rows), 1)
        self.assertIn("W-R43", provenance_rows[0])
        self.assertEqual(feedback.count("- **W-R43 ("), 1)

        readme = (ROOT / "README.md").read_text()
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

    def test_claude_refuses_unmanaged_status_line(self) -> None:
        settings = self.codex_home.parent / ".claude" / "settings.json"
        settings.parent.mkdir(parents=True)
        for command in (
            "~/.claude/personal-status-line.sh",
            f"echo {SYNC.MANAGED_CLAUDE_STATUS_LINE_MARKER}-custom",
        ):
            with self.subTest(command=command):
                original = json.dumps(
                    {
                        "theme": "dark",
                        "statusLine": {
                            "type": "command",
                            "command": command,
                        },
                    }
                )
                settings.write_text(original)

                with self.assertRaisesRegex(
                    SYNC.SyncError,
                    "refusing to replace an unmanaged Claude statusLine",
                ):
                    SYNC.sync_claude_settings(settings, self.status_script)

                self.assertEqual(settings.read_text(), original)

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
        agents = self.codex_home / "AGENTS.md"
        config = self.codex_home / "config.toml"
        claude = self.codex_home.parent / ".claude" / "settings.json"
        self.codex_home.mkdir(parents=True)
        claude.parent.mkdir(parents=True)
        agents.write_text("# Personal\n")
        config.write_text('model = "host-model"\n')
        claude.write_text('{"hooks":')
        before = (agents.read_bytes(), config.read_bytes(), claude.read_bytes())

        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "sync_codex_config.py"),
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
                "--env-skill-template",
                str(self.env_skill_template),
                "--codex-home",
                str(self.codex_home),
                "--claude-settings",
                str(claude),
                "--env-skill",
                str(self.env_skill),
            ],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(before, (agents.read_bytes(), config.read_bytes(), claude.read_bytes()))


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import tomllib
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
        self.status_script = ROOT / "scripts" / "workspace_status.py"

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

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
        self.assertIn("# Workspace-Wide Codex Guidance", result)
        self.assertNotIn("\nold\n", result)
        self.assertEqual(result.count(SYNC.AGENTS_BEGIN), 1)

    def test_managed_agents_carries_git_publication_transaction_contract(self) -> None:
        agents = self.codex_home / "AGENTS.md"

        SYNC.sync_agents(self.agents_template, agents)
        result = agents.read_text()
        normalized = " ".join(result.split())

        self.assertIn("two checkpoints", normalized)
        self.assertIn("exact, copyable command bundle", normalized)
        self.assertIn("exact-path `git add`", normalized)
        self.assertIn("`git commit`", normalized)
        self.assertIn("`git push`", normalized)
        self.assertIn("`gh pr create`", normalized)
        self.assertIn("ordinary natural language", normalized)
        self.assertIn("run some/all commands personally", normalized)
        self.assertIn("report completion", normalized)
        self.assertIn(
            "treat the completion report as evidence to verify", normalized
        )
        self.assertIn("Merge/integration execution remains a separate", normalized)
        self.assertNotIn("Commit and push are separate transactions", normalized)

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
        self.assertEqual(len(groups), 2)
        self.assertIn(SYNC.MANAGED_HOOK_MARKER, groups[0]["hooks"][0]["command"])
        self.assertEqual(groups[1]["hooks"][0]["command"], "user-owned-hook")
        self.assertEqual(
            SYNC.sync_claude_settings(settings, self.status_script), "already current"
        )

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
                "python3",
                str(ROOT / "scripts" / "sync_codex_config.py"),
                "--agents-template",
                str(self.agents_template),
                "--hooks-template",
                str(self.hooks_template),
                "--status-script",
                str(self.status_script),
                "--codex-home",
                str(self.codex_home),
                "--claude-settings",
                str(claude),
            ],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(completed.returncode, 1)
        self.assertEqual(before, (agents.read_bytes(), config.read_bytes(), claude.read_bytes()))


if __name__ == "__main__":
    unittest.main()

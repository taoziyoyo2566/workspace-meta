from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import hashlib
import importlib.util
from io import StringIO
import json
import os
from pathlib import Path
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
        self.status_script = ROOT / "scripts" / "workspace_status.py"
        self.rules_dir = ROOT / ".agents" / "rules"

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
            status_script=changed_status,
            codex_home=self.codex_home,
            claude_settings=settings,
            python="python3",
            check=False,
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
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "planning.md",
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
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "planning.md",
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
            "environment-truth.md",
            "git.md",
            "git-branches.md",
            "git-integration.md",
            "git-publication.md",
            "git-recovery.md",
            "planning.md",
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

    def test_git_modules_have_task_shaped_load_profiles(self) -> None:
        inspection = (self.rules_dir / "git.md").read_text()
        branches = (self.rules_dir / "git-branches.md").read_text()
        publication = (self.rules_dir / "git-publication.md").read_text()
        integration = (self.rules_dir / "git-integration.md").read_text()
        recovery = (self.rules_dir / "git-recovery.md").read_text()

        self.assertNotIn("gh pr create", inspection)
        self.assertNotIn("force-with-lease", inspection)
        self.assertIn("Required Branch Task Contract", branches)
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

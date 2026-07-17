from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "workspace_status", ROOT / "scripts" / "workspace_status.py"
)
assert SPEC and SPEC.loader
STATUS = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = STATUS
SPEC.loader.exec_module(STATUS)


class FakeRunner:
    def __init__(self, workspace: Path, **responses: STATUS.CommandResult) -> None:
        self.workspace = workspace
        self.responses = responses
        self.calls: list[tuple[str, ...]] = []

    def __call__(self, argv: list[str], timeout: int) -> STATUS.CommandResult:
        del timeout
        command = tuple(argv)
        self.calls.append(command)
        if command[-2:] == ("status", "--porcelain"):
            return self.responses.get("status", STATUS.CommandResult(0))
        if "fetch" in command:
            return self.responses.get("fetch", STATUS.CommandResult(0))
        if command[-1] == "HEAD..origin/main":
            return self.responses.get("behind", STATUS.CommandResult(0, "0\n"))
        if command[-1] == "origin/main..HEAD":
            return self.responses.get("ahead", STATUS.CommandResult(0, "0\n"))
        if command[-1] == "--check":
            return self.responses.get("env", STATUS.CommandResult(0))
        raise AssertionError(f"unexpected command: {command}")


class WorkspaceStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.config = STATUS.StatusConfig(
            workspace=self.root / "workspace",
            cache_file=self.root / "cache" / "status.json",
            fetch_min_interval=300,
            remote_warning_ttl=86400,
            fetch_timeout=8,
            command_timeout=5,
        )

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_healthy_status_updates_remote_success_without_message(self) -> None:
        runner = FakeRunner(self.config.workspace)

        result = STATUS.evaluate_status(self.config, runner=runner, now=1000)

        self.assertEqual(result.messages, [])
        self.assertEqual(result.cache["last_remote_success"], 1000)
        self.assertTrue(result.cache_changed)

    def test_combines_actionable_states_in_stable_order(self) -> None:
        runner = FakeRunner(
            self.config.workspace,
            status=STATUS.CommandResult(0, " M README.md\n"),
            behind=STATUS.CommandResult(0, "2\n"),
            ahead=STATUS.CommandResult(0, "1\n"),
            env=STATUS.CommandResult(1, stderr="stale"),
        )

        result = STATUS.evaluate_status(self.config, runner=runner, now=1000)

        self.assertEqual(
            result.messages,
            [
                "governance is behind origin/main; run: git -C ~/workspace pull",
                "governance has uncommitted or unpushed changes; run: git -C ~/workspace status",
                "host capability registry is missing or stale; run: make -C ~/workspace env-probe",
            ],
        )

    def test_first_remote_failure_warns_and_records_warning(self) -> None:
        runner = FakeRunner(
            self.config.workspace,
            fetch=STATUS.CommandResult(1, stderr="offline"),
        )

        result = STATUS.evaluate_status(self.config, runner=runner, now=1000)

        self.assertIn("remote freshness is unknown", result.messages[0])
        self.assertEqual(result.cache["last_remote_warning"], 1000)

    def test_remote_failure_is_quiet_inside_warning_ttl(self) -> None:
        runner = FakeRunner(
            self.config.workspace,
            fetch=STATUS.CommandResult(1, stderr="offline"),
        )
        cache = {"schema": STATUS.CACHE_SCHEMA, "last_remote_warning": 900}

        result = STATUS.evaluate_status(
            self.config, runner=runner, now=1000, initial_cache=cache
        )

        self.assertEqual(result.messages, [])
        self.assertFalse(result.cache_changed)

    def test_remote_failure_warns_again_after_ttl(self) -> None:
        runner = FakeRunner(
            self.config.workspace,
            fetch=STATUS.CommandResult(1, stderr="offline"),
        )
        cache = {"schema": STATUS.CACHE_SCHEMA, "last_remote_warning": 1}

        result = STATUS.evaluate_status(
            self.config, runner=runner, now=90000, initial_cache=cache
        )

        self.assertIn("remote freshness is unknown", result.messages[0])
        self.assertEqual(result.cache["last_remote_warning"], 90000)

    def test_recent_success_skips_fetch(self) -> None:
        runner = FakeRunner(self.config.workspace)
        cache = {"schema": STATUS.CACHE_SCHEMA, "last_remote_success": 900}

        result = STATUS.evaluate_status(
            self.config, runner=runner, now=1000, initial_cache=cache
        )

        self.assertEqual(result.messages, [])
        self.assertFalse(any("fetch" in call for call in runner.calls))

    def test_missing_repository_and_registry_emit_one_json_contract(self) -> None:
        cache = self.root / "status.json"
        command = [
            "python3",
            str(ROOT / "scripts" / "workspace_status.py"),
            "--agent",
            "codex",
            "--workspace",
            str(self.root / "missing-workspace"),
            "--cache-file",
            str(cache),
            "--fetch-min-interval",
            "0",
        ]

        completed = subprocess.run(command, capture_output=True, check=False, text=True)
        payload = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("repository status is unavailable", payload["systemMessage"])
        self.assertIn("host capability registry", payload["systemMessage"])


if __name__ == "__main__":
    unittest.main()

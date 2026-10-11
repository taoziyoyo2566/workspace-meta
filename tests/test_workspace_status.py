from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
from types import SimpleNamespace
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

    def _temp_config(self, **overrides: object) -> STATUS.StatusConfig:
        values = {
            "workspace": self.config.workspace,
            "cache_file": self.config.cache_file,
            "temp_root": self.root / "scratch",
            "temp_used_percent": 80,
            "temp_min_free_mb": 256,
        }
        values.update(overrides)
        return STATUS.StatusConfig(**values)

    @staticmethod
    def _statvfs(total_mb: int, free_mb: int, reserved_mb: int = 0, seen=None):
        mib = 1024 * 1024

        def statvfs(path: str) -> SimpleNamespace:
            if seen is not None:
                seen.append(path)
            return SimpleNamespace(
                f_frsize=mib,
                f_blocks=total_mb,
                f_bfree=free_mb + reserved_mb,
                f_bavail=free_mb,
            )

        return statvfs

    def test_full_temp_space_warns_operator_and_agent(self) -> None:
        # Blocks reserved for root count as neither used nor free, as in df.
        result = STATUS.evaluate_status(
            self._temp_config(),
            runner=FakeRunner(self.config.workspace),
            now=1000,
            statvfs=self._statvfs(total_mb=1969, free_mb=73, reserved_mb=27),
        )

        self.assertEqual(len(result.messages), 1)
        self.assertIn("is 96% used (73 MiB free)", result.messages[0])
        self.assertIn("temporary-files.md", result.messages[0])
        self.assertEqual(result.context, result.messages)

    def test_low_free_space_warns_below_the_percent_threshold(self) -> None:
        result = STATUS.evaluate_status(
            self._temp_config(),
            runner=FakeRunner(self.config.workspace),
            now=1000,
            statvfs=self._statvfs(total_mb=1000, free_mb=255),
        )

        self.assertIn("(255 MiB free)", result.context[0])

    def test_healthy_temp_space_is_quiet(self) -> None:
        result = STATUS.evaluate_status(
            self._temp_config(),
            runner=FakeRunner(self.config.workspace),
            now=1000,
            statvfs=self._statvfs(total_mb=1942, free_mb=1500),
        )

        self.assertEqual(result.messages, [])
        self.assertEqual(result.context, [])

    def test_missing_scratch_is_measured_on_its_nearest_existing_parent(self) -> None:
        seen: list[str] = []
        scratch = self.root / "session" / "scratchpad"

        STATUS.evaluate_status(
            self._temp_config(temp_root=scratch),
            runner=FakeRunner(self.config.workspace),
            now=1000,
            statvfs=self._statvfs(total_mb=1000, free_mb=900, seen=seen),
        )

        self.assertEqual(seen, [str(self.root)])

    def test_unmeasurable_temp_space_is_reported(self) -> None:
        def failing_statvfs(path: str) -> SimpleNamespace:
            raise OSError(path)

        result = STATUS.evaluate_status(
            self._temp_config(),
            runner=FakeRunner(self.config.workspace),
            now=1000,
            statvfs=failing_statvfs,
        )

        self.assertIn("could not be measured", result.context[0])

    def _pipe(self, payload: bytes | None, close: bool = True):
        read_fd, write_fd = os.pipe()
        if payload:
            os.write(write_fd, payload)
        if close:
            os.close(write_fd)
        else:
            self.addCleanup(os.close, write_fd)
        stream = os.fdopen(read_fd, "r")
        self.addCleanup(stream.close)
        return stream

    def test_hook_input_reads_json_from_a_pipe(self) -> None:
        stream = self._pipe(b'{"scratchpad_dir": "/tmp/s"}')

        self.assertEqual(STATUS.read_hook_input(stream), {"scratchpad_dir": "/tmp/s"})

    def test_hook_input_without_usable_json_is_empty(self) -> None:
        self.assertEqual(STATUS.read_hook_input(None), {})
        self.assertEqual(STATUS.read_hook_input(self._pipe(None)), {})
        self.assertEqual(STATUS.read_hook_input(self._pipe(b"not json")), {})
        self.assertEqual(STATUS.read_hook_input(self._pipe(b"[1, 2]")), {})
        terminal = SimpleNamespace(isatty=lambda: True)
        self.assertEqual(STATUS.read_hook_input(terminal), {})

    def test_hook_input_left_open_returns_after_the_deadline(self) -> None:
        stream = self._pipe(b'{"scratchpad_dir": ', close=False)
        started = time.monotonic()

        self.assertEqual(STATUS.read_hook_input(stream, timeout=0.2), {})
        self.assertLess(time.monotonic() - started, 2)

    def test_closed_stdin_still_emits_the_json_contract(self) -> None:
        command = [
            "python3",
            str(ROOT / "scripts" / "workspace_status.py"),
            "--agent",
            "claude",
            "--workspace",
            str(self.root / "missing-workspace"),
            "--cache-file",
            str(self.root / "status.json"),
        ]

        completed = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            check=False,
            text=True,
            preexec_fn=lambda: os.close(0),
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("repository status is unavailable", json.loads(completed.stdout)["systemMessage"])

    def test_temp_root_prefers_hook_scratch_then_tmpdir(self) -> None:
        self.assertEqual(
            STATUS.choose_temp_root(
                {"scratchpad_dir": "/tmp/claude-1000/s/scratchpad"},
                {"TMPDIR": "/var/tmp"},
            ),
            Path("/tmp/claude-1000/s/scratchpad"),
        )
        self.assertEqual(
            STATUS.choose_temp_root({}, {"TMPDIR": "/var/tmp"}), Path("/var/tmp")
        )
        self.assertEqual(STATUS.choose_temp_root({}, {}), Path("/tmp"))

    def test_temp_warning_reaches_agent_context_from_hook_input(self) -> None:
        scratch = self.root / "session" / "scratchpad"
        command = [
            "python3",
            str(ROOT / "scripts" / "workspace_status.py"),
            "--agent",
            "claude",
            "--workspace",
            str(self.root / "missing-workspace"),
            "--cache-file",
            str(self.root / "status.json"),
            "--temp-used-percent",
            "0",
        ]

        completed = subprocess.run(
            command,
            input=json.dumps({"scratchpad_dir": str(scratch)}),
            capture_output=True,
            check=False,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        context = payload["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "SessionStart")
        self.assertIn(f"temporary space at {scratch}", context["additionalContext"])
        self.assertIn(f"temporary space at {scratch}", payload["systemMessage"])
        self.assertNotIn("repository status", context["additionalContext"])


if __name__ == "__main__":
    unittest.main()

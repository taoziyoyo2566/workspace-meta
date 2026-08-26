from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "claude_status_line.py"
SPEC = importlib.util.spec_from_file_location("claude_status_line", SCRIPT)
assert SPEC and SPEC.loader
STATUS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(STATUS)


class ClaudeStatusLineTests(unittest.TestCase):
    def payload(self) -> dict[str, object]:
        return {
            "cwd": "/Users/test/workspace",
            "workspace": {"current_dir": "/Users/test/workspace"},
            "model": {"id": "claude-sonnet-example", "display_name": "Sonnet"},
            "cost": {"total_cost_usd": 0.1234},
            "context_window": {
                "used_percentage": 81.2,
                "current_usage": {
                    "input_tokens": 1200,
                    "cache_creation_input_tokens": 2_000_000,
                    "cache_read_input_tokens": 999,
                    "output_tokens": 24_500,
                },
            },
        }

    def test_renders_requested_fields_from_official_payload(self) -> None:
        with mock.patch.object(STATUS, "git_branch", return_value="main"):
            rendered = STATUS.render(
                self.payload(), home="/Users/test", color=False
            )

        self.assertEqual(
            rendered,
            "~/workspace  main  Sonnet  ctx:81%  "
            "in:1.2k cw:2.00M cr:999 out:24.5k  ~$0.123",
        )

    def test_model_id_is_used_for_a_gateway_model_without_a_display_name(self) -> None:
        payload = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"id": "corp-sonnet-prod"},
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            self.assertEqual(
                STATUS.render(payload, home="/home/test", color=False),
                "/tmp/project  corp-sonnet-prod",
            )

    def test_context_threshold_colors(self) -> None:
        payload = self.payload()
        context = payload["context_window"]
        assert isinstance(context, dict)
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            context["used_percentage"] = 59
            self.assertIn(STATUS.CTX_GREEN, STATUS.render(payload, home="/tmp"))
            context["used_percentage"] = 60
            self.assertIn(STATUS.CTX_YELLOW, STATUS.render(payload, home="/tmp"))
            context["used_percentage"] = 80
            self.assertIn(STATUS.CTX_RED, STATUS.render(payload, home="/tmp"))

    def test_missing_optional_usage_and_cost_are_omitted(self) -> None:
        payload = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
            "context_window": {"used_percentage": None, "current_usage": None},
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            self.assertEqual(
                STATUS.render(payload, home="/home/test", color=False),
                "/tmp/project  Opus",
            )

    def test_cli_is_quiet_for_malformed_input(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            input="not-json",
            capture_output=True,
            check=False,
            text=True,
        )
        self.assertEqual(completed.returncode, 0)
        self.assertEqual(completed.stdout, "")

    def test_cli_works_outside_git_and_honors_no_color(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            payload = {
                "workspace": {"current_dir": temp_dir},
                "model": {"display_name": "Sonnet"},
                "cost": {"total_cost_usd": 0},
                "context_window": {"used_percentage": 25},
            }
            env = os.environ.copy()
            env["HOME"] = temp_dir
            env["NO_COLOR"] = "1"
            completed = subprocess.run(
                [sys.executable, str(SCRIPT)],
                input=json.dumps(payload),
                capture_output=True,
                check=False,
                env=env,
                text=True,
            )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(completed.stdout, "~  Sonnet  ctx:25%  ~$0.000")
        self.assertNotIn("\033", completed.stdout)


if __name__ == "__main__":
    unittest.main()

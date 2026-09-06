from __future__ import annotations

import datetime
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
            "~/workspace:main  Sonnet  ctx:81%  "
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
            self.assertIn(STATUS.LEVEL_GREEN, STATUS.render(payload, home="/tmp"))
            context["used_percentage"] = 60
            self.assertIn(STATUS.LEVEL_YELLOW, STATUS.render(payload, home="/tmp"))
            context["used_percentage"] = 80
            self.assertIn(STATUS.LEVEL_RED, STATUS.render(payload, home="/tmp"))

    def test_context_color_matches_the_printed_percentage(self) -> None:
        # 79.5 prints as "ctx:80%", so it must colour as 80 rather than as the
        # unrounded 79.5 that produced it. Integer fixtures never catch this.
        payload = self.payload()
        context = payload["context_window"]
        assert isinstance(context, dict)
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            context["used_percentage"] = 79.5
            self.assertIn(
                f"{STATUS.LEVEL_RED}ctx:80%", STATUS.render(payload, home="/tmp")
            )
            context["used_percentage"] = 59.5
            self.assertIn(
                f"{STATUS.LEVEL_YELLOW}ctx:60%", STATUS.render(payload, home="/tmp")
            )

    def test_renders_remaining_five_hour_window(self) -> None:
        payload = self.payload()
        payload["rate_limits"] = {
            "five_hour": {"used_percentage": 27.4, "resets_at": 1_000_000 + 8100}
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""), mock.patch.object(
            STATUS, "_now", return_value=1_000_000.0
        ):
            rendered = STATUS.render(payload, home="/Users/test", color=False)
        self.assertIn("ctx:81%  5h:73%(2h15m)  in:1.2k", rendered)

    def test_five_hour_window_accepts_iso_reset_and_drops_a_past_reset(self) -> None:
        window = {"used_percentage": 10, "resets_at": "2026-09-06T05:30:00Z"}
        payload = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
            "rate_limits": {"five_hour": window},
        }
        reset = datetime.datetime(
            2026, 9, 6, 5, 30, tzinfo=datetime.timezone.utc
        ).timestamp()
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            with mock.patch.object(STATUS, "_now", return_value=reset - 2700):
                self.assertEqual(
                    STATUS.render(payload, home="/home/test", color=False),
                    "/tmp/project  Opus  5h:90%(45m)",
                )
            with mock.patch.object(STATUS, "_now", return_value=reset + 60):
                self.assertEqual(
                    STATUS.render(payload, home="/home/test", color=False),
                    "/tmp/project  Opus  5h:90%",
                )

    def test_five_hour_window_is_omitted_when_absent_or_malformed(self) -> None:
        base = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
        }
        cases: list[dict[str, object]] = [
            {},
            {"rate_limits": None},
            {"rate_limits": {}},
            {"rate_limits": {"five_hour": None}},
            {"rate_limits": {"five_hour": {}}},
            {"rate_limits": {"five_hour": {"used_percentage": "high"}}},
            {"rate_limits": {"five_hour": {"used_percentage": True}}},
            {"rate_limits": {"five_hour": {"used_percentage": float("nan")}}},
            {"rate_limits": {"five_hour": {"used_percentage": float("inf")}}},
            {"rate_limits": {"seven_day": {"used_percentage": 10}}},
        ]
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            for extra in cases:
                with self.subTest(extra=extra):
                    self.assertEqual(
                        STATUS.render(
                            {**base, **extra}, home="/home/test", color=False
                        ),
                        "/tmp/project  Opus",
                    )

    def test_non_finite_gauges_omit_their_segment_instead_of_failing(self) -> None:
        base = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(value=value):
                    self.assertEqual(
                        STATUS.render(
                            {**base, "context_window": {"used_percentage": value}},
                            home="/home/test",
                            color=False,
                        ),
                        "/tmp/project  Opus",
                    )
                    self.assertEqual(
                        STATUS.render(
                            {**base, "cost": {"total_cost_usd": value}},
                            home="/home/test",
                            color=False,
                        ),
                        "/tmp/project  Opus",
                    )
                    # A broken reset drops only the countdown, not the gauge.
                    self.assertEqual(
                        STATUS.render(
                            {
                                **base,
                                "rate_limits": {
                                    "five_hour": {
                                        "used_percentage": 10,
                                        "resets_at": value,
                                    }
                                },
                            },
                            home="/home/test",
                            color=False,
                        ),
                        "/tmp/project  Opus  5h:90%",
                    )

    def test_five_hour_threshold_colors(self) -> None:
        window: dict[str, object] = {"used_percentage": 0}
        payload = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
            "rate_limits": {"five_hour": window},
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            window["used_percentage"] = 59
            self.assertIn(STATUS.LEVEL_GREEN, STATUS.render(payload, home="/tmp"))
            window["used_percentage"] = 60
            self.assertIn(STATUS.LEVEL_YELLOW, STATUS.render(payload, home="/tmp"))
            window["used_percentage"] = 80
            self.assertIn(STATUS.LEVEL_RED, STATUS.render(payload, home="/tmp"))

    def test_five_hour_color_matches_the_printed_remainder(self) -> None:
        # 79.6% used prints as "5h:20%", so the gauge must colour as 80% used.
        window: dict[str, object] = {"used_percentage": 79.6}
        payload = {
            "workspace": {"current_dir": "/tmp/project"},
            "model": {"display_name": "Opus"},
            "rate_limits": {"five_hour": window},
        }
        with mock.patch.object(STATUS, "git_branch", return_value=""):
            self.assertIn(
                f"{STATUS.LEVEL_RED}5h:20%", STATUS.render(payload, home="/tmp")
            )
            window["used_percentage"] = 59.6
            self.assertIn(
                f"{STATUS.LEVEL_YELLOW}5h:40%", STATUS.render(payload, home="/tmp")
            )

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

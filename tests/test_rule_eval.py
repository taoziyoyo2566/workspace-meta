from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import stat
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("rule_eval", ROOT / "scripts/rule_eval.py")
assert SPEC and SPEC.loader
EVAL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EVAL)

CHECK_TYPES = {"run_absent", "run_present", "text_absent", "text_present",
               "file_unchanged", "file_changed", "judge"}

# A stand-in for `claude -p`: the session prompt gets a reply with one run
# block and an edit to the roadmap; a judge prompt gets a pass verdict.
FAKE_CLAUDE = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
if args == ["--version"]:
    print("0.0.0 (fake)"); sys.exit(0)
prompt = args[args.index("-p") + 1]
print(json.dumps({"type": "system", "subtype": "init", "model": "fake-model"}))
if prompt.startswith("You are grading"):
    text = '{"verdict": "pass", "reason": "fake judge"}'
else:
    text = "I will look first.\n\n```run\nssh deploy 'cd ~/ops && ./deployctl status'\n```\n"
    if os.path.exists("docs/roadmap.md"):
        with open("docs/roadmap.md", "a") as f:
            f.write("\n- 2026-10-16 exception recorded\n")
    print(json.dumps({"type": "assistant", "message": {"content": [
        {"type": "tool_use", "name": "Edit", "input": {"file_path": "docs/roadmap.md"}}]}}))
print(json.dumps({"type": "result", "result": text, "total_cost_usd": 0.01, "is_error": False}))
'''


class RuleEvalTests(unittest.TestCase):
    def test_scenarios_are_well_formed(self) -> None:
        scenarios = EVAL.load_scenarios()
        ids = [s["id"] for s in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertGreaterEqual(len(scenarios), 10)
        kinds = {s["kind"] for s in scenarios}
        self.assertTrue({"target", "control", "regression"} <= kinds)
        for scenario in scenarios:
            self.assertTrue(scenario["checks"], scenario["id"])
            self.assertTrue(scenario["message"].strip(), scenario["id"])
            for check in scenario["checks"]:
                self.assertIn(check["type"], CHECK_TYPES, scenario["id"])
                if "pattern" in check:
                    re.compile(check["pattern"])
            for path in scenario["git_untracked"]:
                self.assertIn(path, scenario["files"], scenario["id"])
        # What the agent sees must not quote the rules, or a scenario leaks its
        # answer: no run of eight words from a rule file may appear in it.
        def shingles(text: str) -> set[tuple[str, ...]]:
            words = re.findall(r"[a-z0-9']+", text.lower())
            return {tuple(words[i:i + 8]) for i in range(len(words) - 7)}

        rules = set()
        for rule in [*(ROOT / ".agents/rules").glob("*.md"), ROOT / "CLAUDE.md"]:
            rules |= shingles(rule.read_text())
        for scenario in scenarios:
            seen = shingles(scenario["context"] + " " + scenario["message"])
            self.assertFalse(seen & rules, scenario["id"])

    def test_no_instruction_file_sits_in_the_eval_tree(self) -> None:
        names = {p.name for p in (ROOT / "evals").rglob("*")}
        self.assertNotIn("CLAUDE.md", names)
        self.assertNotIn("AGENTS.md", names)

    def test_run_blocks_and_stream_parsing(self) -> None:
        text = "x\n```run\nsudo docker ps\n```\n```bash\nrm -rf /\n```\n```run\nls\n```"
        self.assertEqual(EVAL.run_blocks(text), ["sudo docker ps", "ls"])
        # Only the exact info string counts: a pending command is not run.
        self.assertEqual(EVAL.run_blocks("```run-pending\nrm -f x\n```"), [])
        stream = "\n".join([
            json.dumps({"type": "system", "subtype": "init", "model": "m"}),
            "not json",
            json.dumps({"type": "assistant", "message": {"content": [
                {"type": "tool_use", "name": "Read", "input": {"file_path": "a"}}]}}),
            json.dumps({"type": "result", "result": "done", "total_cost_usd": 0.5}),
        ])
        out = EVAL.parse_stream(stream, 0)
        self.assertEqual((out["model"], out["text"], out["cost"], out["error"]),
                         ("m", "done", 0.5, None))
        self.assertEqual(out["tools"][0]["name"], "Read")
        self.assertIsNotNone(EVAL.parse_stream("", 1, "boom")["error"])

    def test_localize_points_rules_at_the_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ws = Path(tmp)
            (ws / "CLAUDE.md").write_text("see `~/workspace/.agents/rules/git.md`\n")
            EVAL.localize(ws)
            text = (ws / "CLAUDE.md").read_text()
            self.assertNotIn("~/workspace", text)
            self.assertIn(f"{ws}/.agents/rules/git.md", text)

    def test_export_rules_from_a_ref(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            label = EVAL.export_rules("HEAD", Path(tmp) / "rules")
            self.assertTrue(label.startswith("git:"))
            self.assertTrue((Path(tmp) / "rules/CLAUDE.md").is_file())
            self.assertTrue((Path(tmp) / "rules/.agents/rules/authorization.md").is_file())
            self.assertFalse((Path(tmp) / "rules/evals").exists())

    def test_output_on_tmpfs_is_refused(self) -> None:
        mounts = "/dev/vda3 / ext4 rw 0 0\ntmpfs /tmp tmpfs rw 0 0\n"
        self.assertEqual(EVAL.filesystem_type(Path("/tmp/x/y"), mounts), "tmpfs")
        self.assertEqual(EVAL.filesystem_type(Path("/home/u/x"), mounts), "ext4")
        self.assertEqual(EVAL.filesystem_type(Path("/tmpfoo"), mounts), "ext4")
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(EVAL, "filesystem_type", return_value="tmpfs"):
            with self.assertRaises(SystemExit):
                EVAL.main(["run", "--rules", "HEAD", "--label", "t", "--out", tmp,
                           "--scenario", "canary-rules-loaded"])

    def test_a_crashing_trial_is_ungraded_not_fatal(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, \
                mock.patch.object(EVAL, "run_trial", side_effect=FileNotFoundError("claude")):
            code = EVAL.main(["run", "--rules", "HEAD", "--label", "t", "--out", tmp,
                              "--trials", "1", "--scenario", "canary-rules-loaded",
                              "--judge-agent", "claude", "--allow-tmpfs"])
            self.assertEqual(code, 0)
            trial = json.loads((Path(tmp) / "results.json").read_text())["trials"][0]
            self.assertIsNone(trial["passed"])
            self.assertIn("FileNotFoundError", trial["crash"])

    def test_compare_flags_a_scenario_that_got_worse(self) -> None:
        def report(label, rows):
            return {"label": label, "rules": label, "summary": [
                {"scenario": s, "kind": k, "passed": p, "graded": 3} for s, k, p in rows]}
        before = report("before", [("t", "target", 0), ("c", "control", 3)])
        better = report("after", [("t", "target", 3), ("c", "control", 3)])
        worse = report("after", [("t", "target", 3), ("c", "control", 2)])
        table, ok = EVAL.compare(before, better)
        self.assertTrue(ok)
        self.assertIn("| t | target | 0/3 | 3/3 | better |", table)
        self.assertFalse(EVAL.compare(before, worse)[1])

    def test_judge_takes_the_majority(self) -> None:
        scenario = {"context": "c", "message": "m"}
        verdicts = iter([{"ok": True, "reason": "a", "cost": 0.0},
                         {"ok": False, "reason": "b", "cost": 0.0},
                         {"ok": True, "reason": "c", "cost": 0.0}])
        opts = mock.Mock(judge_votes=3)
        with mock.patch.object(EVAL, "judge_once", side_effect=lambda *a: next(verdicts)):
            out = EVAL.judge(scenario, "r", "", "q", opts, Path("/tmp/j"))
        self.assertEqual((out["ok"], out["votes"]), (True, "2/3"))
        split = iter([{"ok": True, "reason": "a", "cost": 0.0},
                      {"ok": False, "reason": "b", "cost": 0.0}])
        opts.judge_votes = 2
        with mock.patch.object(EVAL, "judge_once", side_effect=lambda *a: next(split)):
            self.assertIsNone(EVAL.judge(scenario, "r", "", "q", opts, Path("/tmp/j"))["ok"])

    def test_full_run_with_a_fake_claude(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "claude"
            fake.write_text(FAKE_CLAUDE)
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
            out = Path(tmp) / "out"
            with mock.patch.dict(os.environ, {"RULE_EVAL_CLAUDE": str(fake)}):
                code = EVAL.main(["run", "--rules", "HEAD", "--label", "t", "--out", str(out),
                                  "--trials", "1", "--jobs", "2", "--judge-votes", "1",
                                  "--judge-agent", "claude",
                                  "--scenario", "record-exception-decision",
                                  "--scenario", "read-without-sudo",
                                  "--scenario", "control-readonly-status", "--allow-tmpfs"])
            self.assertEqual(code, 0)
            report = json.loads((out / "results.json").read_text())
            by_id = {t["scenario"]: t for t in report["trials"]}
            self.assertTrue(by_id["record-exception-decision"]["passed"])
            self.assertIn("projects/ops/docs/roadmap.md",
                          by_id["record-exception-decision"]["changed"])
            self.assertTrue(by_id["read-without-sudo"]["passed"])
            self.assertTrue(by_id["control-readonly-status"]["passed"])
            self.assertEqual(report["cli"], "0.0.0 (fake)")


FAKE_CODEX = r'''#!/usr/bin/env python3
import json, os, sys
args = sys.argv[1:]
if args == ["--version"]:
    print("codex-cli 0.0.0 (fake)"); sys.exit(0)
prompt = args[-1]
home = os.environ["CODEX_HOME"]
agents = open(os.path.join(home, "AGENTS.md")).read() if os.path.exists(
    os.path.join(home, "AGENTS.md")) else ""
print(json.dumps({"type": "thread.started", "thread_id": "t"}))
if prompt.startswith("You are grading"):
    text = '{"verdict": "pass", "reason": "fake codex judge"}'
else:
    print(json.dumps({"type": "item.completed", "item": {
        "type": "command_execution", "command": "/bin/bash -lc 'sudo docker ps'"}}))
    text = "Workspace-Wide Codex Adapter\n# Authorization" if "Workspace-Wide Codex" in agents else "no adapter"
print(json.dumps({"type": "item.completed", "item": {"type": "agent_message", "text": text}}))
print(json.dumps({"type": "turn.completed", "usage": {}}))
'''


class CodexRunTests(unittest.TestCase):
    def test_codex_run_loads_the_version_template_and_counts_executed_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            fake = Path(tmp) / "codex"
            fake.write_text(FAKE_CODEX)
            fake.chmod(fake.stat().st_mode | stat.S_IEXEC)
            auth_home = Path(tmp) / "auth-home"
            auth_home.mkdir()
            (auth_home / "auth.json").write_text("{}")
            out = Path(tmp) / "out"
            with mock.patch.dict(os.environ, {"RULE_EVAL_CODEX": str(fake)}):
                code = EVAL.main(["run", "--agent", "codex", "--judge-agent", "codex",
                                  "--codex-auth-home", str(auth_home),
                                  "--rules", "HEAD", "--label", "t", "--out", str(out),
                                  "--trials", "1", "--judge-votes", "1",
                                  "--scenario", "canary-rules-loaded",
                                  "--scenario", "read-without-sudo", "--allow-tmpfs"])
            self.assertEqual(code, 0)
            report = json.loads((out / "results.json").read_text())
            by_id = {t["scenario"]: t for t in report["trials"]}
            self.assertTrue(by_id["canary-rules-loaded"]["passed"])
            # The executed `sudo docker ps` fails the read-only check.
            self.assertFalse(by_id["read-without-sudo"]["passed"])
            self.assertEqual(report["agent"], "codex")
            # Each run's CODEX_HOME is removed afterwards; the instructions it
            # ran with are kept, pointing at the evaluated copy.
            self.assertFalse(list(out.rglob("*-codex-home")))
            kept = list(out.rglob("session-AGENTS.md"))
            self.assertTrue(kept)
            for agents in kept:
                self.assertNotIn("~/workspace", agents.read_text())
                self.assertIn("Workspace-Wide Codex Adapter", agents.read_text())

    def test_codex_home_links_the_login_and_is_private(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            auth_home = Path(tmp) / "auth"
            auth_home.mkdir()
            (auth_home / "auth.json").write_text("{}")
            home = Path(tmp) / "home"
            EVAL.prepare_codex_home(None, home, auth_home)
            self.assertTrue((home / "auth.json").is_symlink())
            self.assertEqual(oct(home.stat().st_mode & 0o777), "0o700")

    def test_parse_codex_collects_messages_and_commands(self) -> None:
        stream = "\n".join(json.dumps(e) for e in [
            {"type": "item.completed", "item": {"type": "agent_message", "text": "a"}},
            {"type": "item.completed", "item": {"type": "command_execution", "command": "ls"}},
            {"type": "item.completed", "item": {"type": "agent_message", "text": "b"}},
        ])
        out = EVAL.parse_codex(stream, 0)
        self.assertEqual((out["text"], out["executed"], out["error"]), ("a\n\nb", ["ls"], None))
        self.assertIsNotNone(EVAL.parse_codex(json.dumps({"type": "turn.failed"}), 0)["error"])


class RuleContentTests(unittest.TestCase):
    """Rule changes evaluated with this tooling keep their owners (W-R66–W-R70)."""

    @staticmethod
    def norm(path: str) -> str:
        return " ".join((ROOT / path).read_text().split()).lower()

    def test_owners_hold_the_changes(self) -> None:
        auth = self.norm(".agents/rules/authorization.md")
        for phrase in (
            "read-only inspection runs as the account you are logged in with",
            "is privilege elevation even though it changes nothing",
            "privilege elevation, including for a read",
            "do not label them with letters, numbers, or names that already mean",
            "could select more than one target set, ask which one before acting",
            "a runtime denial stands even when the user approved the operation",
        ):
            self.assertIn(phrase, auth)
        planning = self.norm(".agents/rules/planning.md")
        self.assertIn("making an exception to a decision or procedure the artifact records",
                      planning)
        self.assertIn("asking whether to record a decision already made", planning)
        self.assertIn("when memory forbids what the operator now asks", planning)
        self.assertIn("a note that restricts what agents do names its scope",
                      self.norm(".agents/rules/rule-authoring.md"))

    def test_adapters_route_the_new_triggers(self) -> None:
        for adapter in ("CLAUDE.md", ".agents/host-templates/codex-AGENTS.md"):
            row = next(line for line in (ROOT / adapter).read_text().splitlines()
                       if line.startswith("| first write"))
            for trigger in ("privilege elevation even for a read", "a runtime denial",
                            "an approval request"):
                self.assertIn(trigger, row, adapter)

    def test_register_entries_are_one_rule_and_one_source(self) -> None:
        lines = (ROOT / "feedback-register.md").read_text().splitlines()
        for number in range(66, 71):
            start = next(i for i, line in enumerate(lines)
                         if line.startswith(f"- **W-R{number} ("))
            self.assertTrue(lines[start + 1].startswith("    - Source: "), number)
            following = lines[start + 2] if start + 2 < len(lines) else ""
            self.assertFalse(following.startswith("    "), number)


if __name__ == "__main__":
    unittest.main()

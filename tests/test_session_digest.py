from __future__ import annotations

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import re
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "session_digest", ROOT / "scripts" / "session_digest.py"
)
assert SPEC and SPEC.loader
DIGEST = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(DIGEST)

CWD = "/home/op/workspace"


def operator(text: str, ts: str) -> dict:
    return {"type": "user", "timestamp": ts, "cwd": CWD,
            "message": {"role": "user", "content": text}}


def tool(name: str, ts: str, cwd: str = CWD, sidechain: bool = False, **inp) -> dict:
    record = {"type": "assistant", "timestamp": ts, "cwd": cwd,
              "message": {"role": "assistant", "content": [
                  {"type": "tool_use", "id": f"tu-{ts}", "name": name, "input": inp}]}}
    if sidechain:
        record["isSidechain"] = True
    return record


def result(ts: str, text: str = "ok") -> dict:
    return {"type": "user", "timestamp": ts, "cwd": CWD, "message": {"role": "user", "content": [
        {"type": "tool_result", "tool_use_id": f"tu-{ts}", "content": text}]}}


def reply(text: str, ts: str) -> dict:
    return {"type": "assistant", "timestamp": ts, "cwd": CWD,
            "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}


ERREXIT_INLINE = "set -euo pipefail\ngit status --short\necho done"
ERREXIT_SCRIPT = ("cat > /home/op/s.sh <<'EOF'\nset -e\nfalse\necho after\nEOF\n"
                  "bash -e /home/op/s.sh")

RECORDS = [
    {"type": "permission-mode", "permissionMode": "default"},
    operator("first request", "2026-10-19T08:00:00Z"),
    tool("Read", "2026-10-19T08:00:01Z",
         file_path="/home/op/workspace/.agents/rules/git.md", offset=10, limit=20),
    tool("Read", "2026-10-19T08:00:02Z", file_path="/home/op/workspace/CLAUDE.md"),
    tool("Bash", "2026-10-19T08:00:03Z", command="sed -n 1,60p .agents/rules/file-checks.md"),
    tool("Bash", "2026-10-19T08:00:04Z",
         command="cd /home/op/workspace/.agents/rules && cat authorization.md && head -n 30 git-publication.md"),
    result("2026-10-19T08:00:04Z"),
    tool("Read", "2026-10-19T08:00:05Z", sidechain=True,
         file_path="/home/op/workspace/.agents/rules/review.md"),
    tool("Bash", "2026-10-19T08:00:06Z", sidechain=True, command="git push origin main"),
    reply("done with the first", "2026-10-19T08:00:07Z"),
    {"type": "system", "subtype": "turn_duration", "durationMs": 7000},
    operator("second request", "2026-10-19T09:00:00Z"),
    tool("Bash", "2026-10-19T09:00:01Z", command="git add -- a.txt && git commit -m 'x'"),
    tool("Bash", "2026-10-19T09:00:02Z", command="sudo systemctl restart foo"),
    tool("Bash", "2026-10-19T09:00:03Z", command="ssh dzire uptime; ssh -G dzire"),
    tool("Edit", "2026-10-19T09:00:04Z", file_path="/home/op/workspace/a.txt",
         old_string="a", new_string="b"),
    tool("Write", "2026-10-19T09:00:05Z", file_path="/tmp/notes/x.md", content="x"),
    tool("AskUserQuestion", "2026-10-19T09:00:06Z", questions=[]),
    tool("Agent", "2026-10-19T09:00:07Z", description="search", prompt="p"),
    tool("Bash", "2026-10-19T09:00:08Z", command=ERREXIT_INLINE),
    tool("Bash", "2026-10-19T09:00:09Z", command=ERREXIT_SCRIPT),
    tool("Bash", "2026-10-19T09:00:10Z", command="set -e && git status"),
    tool("Bash", "2026-10-19T09:00:11Z", command="git worktree add -b feat x && git branch -d old"),
    {"type": "brand-new-record", "payload": 1},
    operator("third request", "2026-10-19T10:00:00Z"),
]


class SessionDigestTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.transcript = self.root / "session.jsonl"
        self.transcript.write_text(
            "".join(json.dumps(r) + "\n" for r in RECORDS), encoding="utf-8")
        with self.transcript.open(encoding="utf-8") as fh:
            self.parsed = DIGEST.parse_transcript(fh)
        self.reach = DIGEST.analyze_reach(self.parsed)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def events(self, kind: str) -> list[dict]:
        return [e for e in self.reach["events"] if e["kind"] == kind]

    def test_turns_split_on_operator_messages(self) -> None:
        turns = self.parsed["turns"]
        self.assertEqual([t["id"] for t in turns], ["T01", "T02", "T03"])
        self.assertEqual([t["prompt"] for t in turns],
                         ["first request", "second request", "third request"])
        self.assertEqual(turns[0]["duration_ms"], 7000)
        self.assertEqual(sum(turns[0]["tools"].values()), 4)

    def test_sidechain_records_are_skipped(self) -> None:
        self.assertEqual(self.reach["sidechain_records"], 2)
        targets = [r["target"] for r in self.reach["reads"]]
        self.assertNotIn("review.md", targets)
        self.assertFalse(any("push" in e["detail"] for e in self.reach["events"]))

    def test_unknown_record_types_are_counted(self) -> None:
        self.assertEqual(self.reach["skipped_record_types"],
                         {"permission-mode": 1, "brand-new-record": 1})

    def test_rule_reads_by_read_tool_and_shell(self) -> None:
        reads = {(r["kind"], r["target"]): r for r in self.reach["reads"]}
        self.assertEqual(reads[("rule", "git.md")]["extent_text"], "lines 10-29")
        self.assertEqual(reads[("rule", "git.md")]["turn"], "T01")
        self.assertEqual(reads[("rule", "file-checks.md")]["extent_text"], "lines 1-60")
        self.assertEqual(reads[("rule", "file-checks.md")]["tool"], "Bash")
        self.assertEqual(reads[("rule", "authorization.md")]["extent_text"], "full")
        self.assertEqual(reads[("rule", "git-publication.md")]["extent_text"], "lines 1-30")
        self.assertIn(("adapter", "/home/op/workspace/CLAUDE.md"), reads)
        self.assertEqual(self.reach["modules"]["file-checks.md"]["extent"], "lines 1-60")
        self.assertIsNone(self.reach["modules"]["review.md"]["first_read_turn"])

    def test_shell_read_parsing(self) -> None:
        def reads(command: str, cwd: str = CWD) -> list[tuple[str, str]]:
            return [(name, DIGEST.describe_extent(ext))
                    for c in DIGEST.simple_commands(command, cwd)
                    for _, name, ext in DIGEST.shell_reads(c)]
        self.assertEqual(reads("grep -n -A25 '^## X' .agents/rules/documentation.md"),
                         [("documentation.md", "grep")])
        self.assertEqual(reads("sed -n '/^## A/,/^## /p' .agents/rules/planning.md | head -80"),
                         [("planning.md", "section")])
        self.assertEqual(reads("tail -n 5 .agents/rules/git.md"), [("git.md", "last 5 lines")])
        self.assertEqual(reads("sed -i 's/a/b/' .agents/rules/git.md"), [])
        self.assertEqual(reads("cat \"$f\""), [])
        self.assertEqual(len(reads("grep -n x *.md", CWD + "/.agents/rules")),
                         len(DIGEST.KNOWN_MODULES))

    def test_events_are_detected_and_routed(self) -> None:
        kinds = [e["kind"] for e in self.reach["events"]]
        for kind in ("git-publication", "sudo", "remote-host", "file-edit", "tmp-write",
                     "ask-operator", "delegation", "git-branch", "git-recovery"):
            self.assertIn(kind, kinds)
        self.assertEqual(len(self.events("git-publication")), 2)
        self.assertEqual(len(self.events("remote-host")), 1, "ssh -G is a config query")
        commit = self.events("git-publication")[1]
        self.assertEqual(commit["turn"], "T02")
        self.assertEqual([m["module"] for m in commit["modules"]],
                         list(DIGEST.ROUTES["git-publication"]))
        prior = {m["module"]: (m["prior_reads"], m["prior_extent"]) for m in commit["modules"]}
        self.assertEqual(prior["git.md"], (1, "lines 10-29"))
        self.assertEqual(prior["git-publication.md"], (1, "lines 1-30"))
        file_edit = self.events("file-edit")[0]
        prior = {m["module"]: m["prior_extent"] for m in file_edit["modules"]}
        self.assertEqual(prior["file-checks.md"], "lines 1-60")
        self.assertEqual(prior["verification.md"], "never")
        self.assertEqual(self.events("tmp-write")[0]["detail"], "Write /tmp/notes/x.md")
        self.assertEqual(self.reach["modules"]["temporary-files.md"]["read_before_first_event"],
                         False)

    def test_git_event_classification(self) -> None:
        self.assertEqual(DIGEST.git_events(["-C", "/r", "push", "--force", "o", "b"]),
                         ["git-publication", "git-recovery"])
        self.assertEqual(DIGEST.git_events(["merge", "--ff-only", "b"]), ["git-integration"])
        self.assertEqual(DIGEST.git_events(["rebase", "main"]), ["git-recovery"])
        self.assertEqual(DIGEST.git_events(["stash", "list"]), [])
        self.assertEqual(DIGEST.git_events(["branch", "-a"]), [])
        self.assertEqual(DIGEST.git_events(["tag", "v1.0"]), ["git-release"])
        self.assertEqual(DIGEST.git_events(["status", "--short"]), [])

    def test_errexit_flag(self) -> None:
        flagged = [x["seq"] for x in self.reach["errexit"]]
        self.assertEqual(len(flagged), 1)
        self.assertIn("set -euo pipefail", self.reach["errexit"][0]["command"])
        self.assertTrue(DIGEST.errexit_flag("set -o errexit\nfalse\necho after"))
        self.assertFalse(DIGEST.errexit_flag(ERREXIT_SCRIPT))
        self.assertFalse(DIGEST.errexit_flag("set -e && git status"))
        self.assertFalse(DIGEST.errexit_flag("set +e\nfalse\necho after"))
        self.assertFalse(DIGEST.errexit_flag("echo a\nset -e"))

    def test_main_writes_outputs(self) -> None:
        out = self.root / "digest"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(DIGEST.main([str(self.transcript), str(out)]), 0)
        self.assertEqual(sorted(p.name for p in (out / "turns").iterdir()),
                         ["T01.md", "T02.md", "T03.md"])
        metrics = json.loads((out / "metrics.json").read_text(encoding="utf-8"))
        self.assertEqual([m["turn"] for m in metrics], ["T01", "T02", "T03"])
        self.assertIn("| T02 |", (out / "index.md").read_text(encoding="utf-8"))
        reach_md = (out / "reach.md").read_text(encoding="utf-8")
        self.assertIn("lines 1-60", reach_md)
        self.assertIn("brand-new-record", reach_md)
        reach = json.loads((out / "reach.json").read_text(encoding="utf-8"))
        self.assertEqual(len(reach["errexit"]), 1)

    def test_refuses_out_dir_inside_repository(self) -> None:
        out = ROOT / "tmp-digest-should-not-exist"
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(DIGEST.main([str(self.transcript), str(out)]), 2)
        self.assertFalse(out.exists())
        self.assertIn("inside the repository", err.getvalue())
        with self.assertRaises(DIGEST.OutDirError):
            DIGEST.check_out_dir(ROOT)

    def test_routing_table_modules_are_routed_in_claude_md(self) -> None:
        text = (ROOT / "CLAUDE.md").read_text(encoding="utf-8")
        block = text.split("## Direct Task Routing", 1)[1].split("\n## ", 1)[0]
        routed = set(re.findall(r"`\.agents/rules/([a-z-]+\.md)`", block))
        named = {m for mods in DIGEST.ROUTES.values() for m in mods}
        self.assertTrue(named)
        self.assertEqual(named - routed, set())
        self.assertEqual(routed - set(DIGEST.KNOWN_MODULES), set())


if __name__ == "__main__":
    unittest.main()

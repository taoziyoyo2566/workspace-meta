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


class ProjectReadinessTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name).resolve()
        self.workspace = self.root / "workspace"
        self.projects = self.workspace / "projects"
        self.projects.mkdir(parents=True)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _project(self, name: str, git: str = "dir", **files: str) -> Path:
        root = self.projects / name
        root.mkdir(parents=True, exist_ok=True)
        if git == "dir":
            (root / ".git").mkdir()
            (root / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        elif git == "stub":
            (root / ".git").mkdir()
        elif git == "file":
            # A linked worktree of a repository kept outside projects/.
            admin = self.root / "elsewhere" / ".git" / "worktrees" / name
            admin.mkdir(parents=True)
            (admin / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
            (root / ".git").write_text(f"gitdir: {admin}\n", encoding="utf-8")
        self._write(root, files)
        return root

    @staticmethod
    def _write(root: Path, files: dict[str, str]) -> None:
        for relative, text in files.items():
            path = root / relative.replace("__", "/")
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")

    def _worktree(self, name: str, main: Path, **files: str) -> Path:
        """Add a linked worktree of main under projects/, as git worktree add does."""
        admin = main / ".git" / "worktrees" / name
        admin.mkdir(parents=True)
        (admin / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
        (admin / "commondir").write_text("../..\n", encoding="utf-8")
        root = self.projects / name
        root.mkdir(parents=True)
        (root / ".git").write_text(f"gitdir: {admin}\n", encoding="utf-8")
        self._write(root, files)
        return root

    def _root_for(self, cwd: Path | str) -> Path | None:
        return STATUS.choose_project_root({"cwd": str(cwd)}, {}, self.workspace)

    def _evaluate(self, root: Path | None, agent: str = "claude", read_file=None):
        config = STATUS.StatusConfig(
            workspace=self.workspace,
            cache_file=self.root / "cache" / "status.json",
            agent=agent,
            project_root=root,
        )
        kwargs = {} if read_file is None else {"read_file": read_file}
        return STATUS.evaluate_status(
            config, runner=FakeRunner(self.workspace), now=1000, **kwargs
        )

    def test_root_is_the_git_directory_above_cwd(self) -> None:
        root = self._project("app")
        (root / "src" / "pkg").mkdir(parents=True)

        self.assertEqual(self._root_for(root), root)
        self.assertEqual(self._root_for(root / "src" / "pkg"), root)

    def test_root_accepts_a_git_file_from_a_linked_worktree(self) -> None:
        root = self._project("app-v2", git="file")

        self.assertEqual(self._root_for(root), root)

    def test_relative_gitdir_resolves_from_the_git_file(self) -> None:
        outer = self._project("app")
        modules = outer / ".git" / "modules" / "sub"
        modules.mkdir(parents=True)
        (modules / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        sub = outer / "sub"
        sub.mkdir()
        (sub / ".git").write_text("gitdir: ../.git/modules/sub\n", encoding="utf-8")

        self.assertEqual(self._root_for(sub / "src"), sub)

    def test_git_file_pointing_to_a_missing_gitdir_is_not_a_root(self) -> None:
        outer = self._project("real", **{"CLAUDE.md": "# Real\n"})
        empty_admin = self.root / "pruned" / ".git" / "worktrees" / "empty"
        empty_admin.mkdir(parents=True)
        for pointer in (
            "gitdir: /nonexistent/worktrees/gone",
            "gitdir: ../.git/worktrees/gone",
            "gitdir:",
            f"gitdir: {empty_admin}",
        ):
            with self.subTest(pointer=pointer):
                sub = outer / "sub"
                sub.mkdir(exist_ok=True)
                (sub / ".git").write_text(pointer + "\n", encoding="utf-8")
                stale = self._project("stale", git="none")
                (stale / ".git").write_text(pointer + "\n", encoding="utf-8")

                # The stale pointer is skipped; the search goes on upward.
                self.assertEqual(self._root_for(sub), outer)
                self.assertEqual(self._evaluate(self._root_for(sub)).messages, [])
                self.assertIsNone(self._root_for(stale))

    def test_symlinked_projects_directory_is_followed(self) -> None:
        real_projects = self.root / "volume" / "projects"
        real_projects.mkdir(parents=True)
        workspace = self.root / "linked-workspace"
        workspace.mkdir()
        (workspace / "projects").symlink_to(real_projects, target_is_directory=True)
        app = real_projects / "app"
        (app / ".git").mkdir(parents=True)
        (app / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (app / "src").mkdir()

        root = STATUS.choose_project_root(
            {"cwd": str(workspace / "projects" / "app" / "src")}, {}, workspace
        )

        self.assertEqual(root, app)
        self.assertEqual(STATUS.project_name(app, workspace), "app")
        config = STATUS.StatusConfig(
            workspace=workspace,
            cache_file=self.root / "cache" / "status.json",
            project_root=root,
        )
        result = STATUS.evaluate_status(config, runner=FakeRunner(workspace), now=1000)
        self.assertEqual(len(result.messages), 1)
        self.assertTrue(
            result.messages[0].startswith("project app has no Claude entry file;")
        )

    def test_nested_repository_is_its_own_root(self) -> None:
        outer = self._project("app")
        nested = outer / ".build" / "dep"
        nested.mkdir(parents=True)
        (nested / ".git").mkdir()
        (nested / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")

        self.assertEqual(self._root_for(nested / "src"), nested)

    def test_empty_or_broken_git_entry_is_not_a_root(self) -> None:
        stub = self._project("tools", git="stub")
        broken = self._project("clone", git="none")
        (broken / ".git").write_text("not a gitdir pointer\n", encoding="utf-8")

        self.assertIsNone(self._root_for(stub))
        self.assertIsNone(self._root_for(broken))

    def test_directory_without_git_is_skipped(self) -> None:
        plain = self._project("notes", git="none")
        (plain / "sub").mkdir()

        self.assertIsNone(self._root_for(plain))
        self.assertIsNone(self._root_for(plain / "sub"))

    def test_cwd_outside_projects_is_skipped(self) -> None:
        (self.workspace / ".git").mkdir()

        self.assertIsNone(self._root_for(self.workspace))
        self.assertIsNone(self._root_for(self.workspace / ".worktrees" / "feat"))
        self.assertIsNone(self._root_for(self.root))
        self.assertIsNone(STATUS.choose_project_root({}, {}, self.workspace))
        self.assertIsNone(self._root_for("projects/app"))

    def test_projects_directory_itself_is_skipped(self) -> None:
        self._project("app")

        self.assertIsNone(self._root_for(self.projects))

    def test_projects_git_stub_is_never_a_project_root(self) -> None:
        (self.projects / ".git").mkdir()
        plain = self._project("notes", git="none")

        self.assertIsNone(self._root_for(plain))
        self.assertIsNone(self._root_for(self.projects))

    def test_project_dir_env_is_used_when_hook_has_no_cwd(self) -> None:
        root = self._project("app")
        other = self._project("other")

        self.assertEqual(
            STATUS.choose_project_root({}, {"CLAUDE_PROJECT_DIR": str(root)}, self.workspace),
            root,
        )
        self.assertEqual(
            STATUS.choose_project_root(
                {"cwd": str(other)}, {"CLAUDE_PROJECT_DIR": str(root)}, self.workspace
            ),
            other,
        )

    def test_check_is_off_without_a_project_root(self) -> None:
        def no_reads(path: Path) -> str | None:
            raise AssertionError(f"unexpected read: {path}")

        result = self._evaluate(None, read_file=no_reads)

        self.assertEqual(result.messages, [])
        self.assertEqual(result.context, [])

    def test_claude_without_entry_file_warns_operator_and_agent(self) -> None:
        root = self._project("app")

        result = self._evaluate(root)

        self.assertEqual(
            result.messages,
            [
                "project app has no Claude entry file; bootstrap it as "
                "~/workspace/.agents/rules/documentation.md Project Bootstrap "
                "describes before substantive work"
            ],
        )
        self.assertEqual(result.context, result.messages)

    def test_claude_entry_file_without_agents_md_is_ready(self) -> None:
        for entry in ("CLAUDE.md", ".claude__CLAUDE.md", "CLAUDE.local.md"):
            with self.subTest(entry=entry):
                root = self._project(f"app-{entry.replace('__', '-')}", **{entry: "# App\n"})

                self.assertEqual(self._evaluate(root).messages, [])

    def test_claude_entry_importing_agents_md_is_ready(self) -> None:
        root = self._project(
            "app", **{"AGENTS.md": "# Agents\n", "CLAUDE.local.md": "  @AGENTS.md  \n"}
        )

        self.assertEqual(self._evaluate(root).messages, [])

    def test_claude_entry_not_importing_agents_md_warns(self) -> None:
        root = self._project(
            "app",
            **{
                "AGENTS.md": "# Agents\n",
                "CLAUDE.md": "# App\nRead AGENTS.md and [@AGENTS.md](AGENTS.md).\n",
            },
        )

        result = self._evaluate(root)

        self.assertEqual(len(result.messages), 1)
        self.assertTrue(
            result.messages[0].startswith(
                "project app: no Claude entry file imports its AGENTS.md; bootstrap it as "
            )
        )
        self.assertEqual(result.context, result.messages)

    def test_dot_claude_entry_imports_agents_md_from_the_parent(self) -> None:
        ready = self._project(
            "app", **{"AGENTS.md": "# Agents\n", ".claude__CLAUDE.md": "@../AGENTS.md\n"}
        )
        wrong = self._project(
            "lib", **{"AGENTS.md": "# Agents\n", ".claude__CLAUDE.md": "@AGENTS.md\n"}
        )

        self.assertEqual(self._evaluate(ready).messages, [])
        self.assertEqual(len(self._evaluate(wrong).messages), 1)

    def test_import_inside_fenced_code_does_not_count(self) -> None:
        for fence in ("```", "~~~~"):
            with self.subTest(fence=fence):
                text = f"# App\n{fence}markdown\n@AGENTS.md\n{fence}\n"
                self.assertFalse(STATUS.imports_agents_md(text))
                self.assertTrue(STATUS.imports_agents_md(text + "@AGENTS.md\n"))
        # A shorter or different marker does not close the fence.
        self.assertFalse(STATUS.imports_agents_md("````\n```\n~~~~\n@AGENTS.md\n"))

    def test_codex_verdicts_follow_agents_md(self) -> None:
        bare = self._project("app")
        local_only = self._project("notes", **{"CLAUDE.local.md": "# Notes\n"})
        ready = self._project("lib", **{"AGENTS.md": "# Agents\n"})

        for root, name in ((bare, "app"), (local_only, "notes")):
            with self.subTest(project=name):
                result = self._evaluate(root, agent="codex")
                self.assertEqual(
                    result.messages,
                    [
                        f"project {name} has no AGENTS.md; bootstrap it as "
                        "~/workspace/.agents/rules/documentation.md Project Bootstrap "
                        "describes before substantive work"
                    ],
                )
                self.assertEqual(result.context, result.messages)
        self.assertEqual(self._evaluate(ready, agent="codex").messages, [])

    def test_codex_reports_a_claude_md_owner_as_an_owner_move(self) -> None:
        # Codex cannot import, so a CLAUDE.md owner needs moving, not a
        # second AGENTS.md beside it.
        for entry in ("CLAUDE.md", ".claude__CLAUDE.md"):
            with self.subTest(entry=entry):
                name = f"app-{entry.replace('__', '-')}"
                root = self._project(name, **{entry: "# App\n"})

                result = self._evaluate(root, agent="codex")

                self.assertEqual(
                    result.messages,
                    [
                        f"project {name}: Codex does not load its CLAUDE.md; "
                        "propose moving it to AGENTS.md as "
                        "~/workspace/.agents/rules/codex-runtime.md Project Entry "
                        "Files describes"
                    ],
                )
                self.assertEqual(result.context, result.messages)

    def test_linked_worktree_of_a_main_checkout_with_entry_files_is_silent(
        self,
    ) -> None:
        main = self._project("app", **{"AGENTS.md": "# Agents\n", "CLAUDE.md": "@AGENTS.md\n"})
        branch = self._worktree("app-v2", main)

        for agent in ("claude", "codex"):
            with self.subTest(agent=agent):
                self.assertEqual(self._root_for(branch), branch)
                result = self._evaluate(branch, agent=agent)
                self.assertEqual(result.messages, [])
                self.assertEqual(result.context, [])

    def test_linked_worktree_without_own_files_is_judged_by_its_main(self) -> None:
        # The bootstrap belongs in the main checkout; the branch gets the files
        # by merge, so the message names the main checkout.
        for main_files, agent, expected in (
            ({"CLAUDE.local.md": "# Local\n"}, "claude", None),
            ({".claude__CLAUDE.md": "# App\n"}, "claude", None),
            ({"AGENTS.md": "# Agents\n"}, "codex", None),
            ({"CLAUDE.md": "# App\n"}, "codex", ": Codex does not load its CLAUDE.md;"),
            ({"AGENTS.md": "# Agents\n"}, "claude", " has no Claude entry file;"),
            ({}, "claude", " has no Claude entry file;"),
            ({}, "codex", " has no AGENTS.md;"),
        ):
            with self.subTest(main=sorted(main_files), agent=agent):
                name = f"app{len(list(self.projects.iterdir()))}"
                main = self._project(name, **main_files)
                branch = self._worktree(f"{name}-v2", main)

                messages = self._evaluate(branch, agent=agent).messages

                if expected is None:
                    self.assertEqual(messages, [])
                else:
                    self.assertEqual(len(messages), 1)
                    self.assertTrue(
                        messages[0].startswith(
                            f"project {name} (main checkout of {name}-v2){expected}"
                        ),
                        messages[0],
                    )

    def test_linked_worktree_still_reports_its_own_conflicting_files(self) -> None:
        main = self._project("app", **{"AGENTS.md": "# Agents\n", "CLAUDE.md": "@AGENTS.md\n"})
        branch = self._worktree(
            "app-v2", main, **{"AGENTS.md": "# Agents\n", "CLAUDE.md": "# Own rules\n"}
        )

        messages = self._evaluate(branch).messages

        self.assertEqual(len(messages), 1)
        self.assertTrue(
            messages[0].startswith("project app-v2: no Claude entry file imports its AGENTS.md;")
        )

    def test_worktree_of_a_bare_repository_has_no_main_checkout(self) -> None:
        # The directory holding a bare repository is not a checkout, even
        # when it has entry files of its own.
        (self.projects / "CLAUDE.md").write_text("# Not a checkout\n", encoding="utf-8")
        (self.projects / "AGENTS.md").write_text("# Not a checkout\n", encoding="utf-8")
        common = self.projects / "repo.git"
        admin = common / "worktrees" / "feature"
        admin.mkdir(parents=True)
        (common / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (admin / "HEAD").write_text("ref: refs/heads/feature\n", encoding="utf-8")
        branch = self.projects / "feature"
        branch.mkdir()
        (branch / ".git").write_text(f"gitdir: {admin}\n", encoding="utf-8")

        self.assertIsNone(STATUS.main_checkout(branch))
        for agent in ("claude", "codex"):
            with self.subTest(agent=agent):
                self.assertEqual(len(self._evaluate(branch, agent=agent).messages), 1)

    def test_hints_name_existing_rule_sections(self) -> None:
        # Each prompt points the agent at a rule section; it must exist.
        for hint, rule, section in (
            (STATUS.PROJECT_BOOTSTRAP_HINT, "documentation.md", "Project Bootstrap"),
            (STATUS.CODEX_OWNER_MOVE_HINT, "codex-runtime.md", "Project Entry Files"),
        ):
            with self.subTest(rule=rule):
                self.assertIn(f"~/workspace/.agents/rules/{rule} {section}", hint)
                text = (ROOT / ".agents" / "rules" / rule).read_text(encoding="utf-8")
                self.assertEqual(text.count(f"\n## {section}\n"), 1)

    def test_nested_root_is_named_relative_to_projects(self) -> None:
        nested = self.projects / "app" / ".build" / "dep"
        nested.mkdir(parents=True)

        result = self._evaluate(nested)

        self.assertIn("project app/.build/dep has no Claude entry file", result.messages[0])

    def test_readiness_follows_existing_checks(self) -> None:
        root = self._project("app")
        config = STATUS.StatusConfig(
            workspace=self.workspace,
            cache_file=self.root / "cache" / "status.json",
            project_root=root,
        )
        runner = FakeRunner(self.workspace, env=STATUS.CommandResult(1))

        result = STATUS.evaluate_status(config, runner=runner, now=1000)

        self.assertEqual(len(result.messages), 2)
        self.assertIn("host capability registry", result.messages[0])
        self.assertIn("project app has no Claude entry file", result.messages[1])
        self.assertEqual(result.context, result.messages[1:])

    def test_unready_project_reaches_agent_context_from_hook_cwd(self) -> None:
        root = self._project("app")
        (root / "src").mkdir()
        env = os.environ.copy()
        env.pop("CLAUDE_PROJECT_DIR", None)
        command = [
            "python3",
            str(ROOT / "scripts" / "workspace_status.py"),
            "--agent",
            "claude",
            "--workspace",
            str(self.workspace),
            "--cache-file",
            str(self.root / "status.json"),
        ]

        completed = subprocess.run(
            command,
            input=json.dumps({"cwd": str(root / "src")}),
            capture_output=True,
            check=False,
            env=env,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 0, completed.stderr)
        expected = "project app has no Claude entry file; bootstrap it as "
        context = payload["hookSpecificOutput"]
        self.assertEqual(context["hookEventName"], "SessionStart")
        self.assertIn(expected, context["additionalContext"])
        self.assertIn(expected, payload["systemMessage"])
        self.assertNotIn("repository status", context["additionalContext"])


if __name__ == "__main__":
    unittest.main()

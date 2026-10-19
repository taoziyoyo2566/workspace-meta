import os
import re
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "change_flow_bundle.sh"
IDENTITY = "Operator <operator@example.invalid>"


class ChangeFlowBundleTests(unittest.TestCase):
    # A scratch main checkout with a bare remote, a change worktree, and a
    # bundle directory describing the reviewed change. Directory names hold
    # spaces so quoting mistakes show.

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name) / "scratch space"
        self.base_dir.mkdir()
        self.gitconfig = self.base_dir / "gitconfig"
        self.gitconfig.write_text(
            "[user]\n\tname = Operator\n\temail = operator@example.invalid\n"
            "[init]\n\tdefaultBranch = main\n"
        )
        self.env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith(("GIT_AUTHOR_", "GIT_COMMITTER_"))
        }
        self.env.update(
            {
                "HOME": str(self.base_dir),
                "GIT_CONFIG_GLOBAL": str(self.gitconfig),
                "GIT_CONFIG_NOSYSTEM": "1",
                "TMPDIR": str(self.base_dir),
            }
        )
        self.remote = self.base_dir / "remote.git"
        self.repo = self.base_dir / "main checkout"
        self.worktree = self.base_dir / "change worktree"
        self.bundle = self.base_dir / "bundle dir"
        self.git(self.base_dir, "init", "-q", "--bare", str(self.remote))
        self.git(self.base_dir, "init", "-q", str(self.repo))
        (self.repo / ".gitignore").write_text("*\n!.gitignore\n!a.txt\n!b.txt\n")
        (self.repo / "a.txt").write_text("a\n")
        self.git(self.repo, "add", ".gitignore", "a.txt")
        self.git(self.repo, "commit", "-q", "-m", "base")
        self.git(self.repo, "remote", "add", "origin", str(self.remote))
        self.git(self.repo, "push", "-q", "origin", "main")
        self.git(self.repo, "fetch", "-q", "origin")
        self.base = self.rev(self.repo, "main")
        self.git(
            self.repo, "worktree", "add", "-q", "-b", "fix/x", str(self.worktree), "main"
        )
        (self.worktree / "a.txt").write_text("a changed\n")
        (self.worktree / "b.txt").write_text("b\n")
        self.bundle.mkdir()
        self.write_env()
        (self.bundle / "paths.txt").write_text("a.txt\nb.txt\n")
        self.message = "fix: change a and add b\n\nWhy.\n"
        (self.bundle / "commit-msg.txt").write_text(self.message)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def write_env(self, **extra: str) -> None:
        values = {
            "REPO": str(self.repo),
            "WORKTREE": str(self.worktree),
            "BRANCH": "fix/x",
            "BASE": self.base,
        }
        values.update(extra)
        (self.bundle / "bundle.env").write_text(
            "".join(f"{key}={value}\n" for key, value in values.items())
        )

    def git(self, cwd: Path, *args: str, env: dict | None = None) -> str:
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            env=env or self.env,
            capture_output=True,
            text=True,
            check=True,
        ).stdout

    def rev(self, cwd: Path, ref: str) -> str:
        return self.git(cwd, "rev-parse", ref).strip()

    def run_bundle(self, action: str, env: dict | None = None) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPT), action, str(self.bundle)],
            cwd=self.base_dir,
            env=env or self.env,
            capture_output=True,
            text=True,
            check=False,
        )

    def record_fingerprints(self, **extra: str) -> dict:
        # The first check prints the reviewed fingerprints and stops.
        self.write_env(**extra)
        first = self.run_bundle("check")
        self.assertNotEqual(first.returncode, 0)
        self.assertIn("record these fingerprints", first.stderr, first.stderr)
        values = dict(re.findall(r"^(TREE|MESSAGE_SHA256)=(\w+)$", first.stdout, re.M))
        self.write_env(**extra, **values)
        return values

    def commit_and_push(self) -> None:
        self.record_fingerprints()
        committed = self.run_bundle("commit")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.git(self.repo, "push", "-q", "origin", "main")

    def assert_nothing_committed(self) -> None:
        self.assertEqual(self.rev(self.worktree, "HEAD"), self.base)
        self.assertEqual(self.rev(self.repo, "main"), self.base)

    def hook(self, name: str, body: str) -> None:
        hooks = self.base_dir / "hooks"
        hooks.mkdir(exist_ok=True)
        path = hooks / name
        path.write_text("#!/bin/sh\n" + body)
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        self.git(self.repo, "config", "core.hooksPath", str(hooks))

    def test_full_bundle_commits_merges_and_retires(self) -> None:
        self.record_fingerprints()
        self.assertEqual(self.run_bundle("check").returncode, 0)

        committed = self.run_bundle("commit")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        new = self.rev(self.repo, "main")
        self.assertEqual(self.rev(self.repo, f"{new}^"), self.base)
        self.assertEqual(
            self.git(self.repo, "log", "-1", "--format=%an <%ae>|%cn <%ce>").strip(),
            f"{IDENTITY}|{IDENTITY}",
        )
        quoted = subprocess.run(
            ["bash", "-c", 'printf "%q" "$1"', "_", str(self.repo)],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        self.assertIn(
            f"next: cd {quoted} && git push --no-follow-tags -- origin "
            f"{new}:refs/heads/main",
            committed.stdout,
        )

        early = self.run_bundle("retire")
        self.assertNotEqual(early.returncode, 0)
        self.assertIn("push first", early.stderr)
        self.assertTrue(self.worktree.exists())

        self.git(self.repo, "push", "-q", "origin", "main")
        retired = self.run_bundle("retire")
        self.assertEqual(retired.returncode, 0, retired.stderr)
        self.assertFalse(self.worktree.exists())
        self.assertNotIn("fix/x", self.git(self.repo, "branch", "--list"))

        again = self.run_bundle("retire")
        self.assertNotEqual(again.returncode, 0)
        self.assertIn("already retired", again.stderr)

    def test_check_stops_on_a_change_outside_paths(self) -> None:
        (self.worktree / "c.txt").write_text("unreviewed\n")
        (self.worktree / ".gitignore").write_text(
            "*\n!.gitignore\n!a.txt\n!b.txt\n!c.txt\n"
        )

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("differ from paths.txt", completed.stderr)

    def test_commit_stops_when_content_changed_after_review(self) -> None:
        self.record_fingerprints()
        (self.worktree / "a.txt").write_text("changed after the review\n")

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("changed since review", completed.stderr)
        self.assert_nothing_committed()
        self.assertEqual(self.git(self.worktree, "diff", "--cached", "--name-only"), "")

    def test_commit_stops_when_the_message_changed_after_review(self) -> None:
        self.record_fingerprints()
        (self.bundle / "commit-msg.txt").write_text("fix: something else\n")

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("commit-msg.txt changed since review", completed.stderr)
        self.assert_nothing_committed()

    def test_hooks_cannot_change_what_is_committed(self) -> None:
        # A pre-commit hook that rewrites commit-msg.txt does not reach the
        # commit, which uses the private copy of the reviewed message.
        self.record_fingerprints()
        self.hook(
            "pre-commit",
            f"printf 'feat: unreviewed\\n' > '{self.bundle / 'commit-msg.txt'}'\n",
        )
        committed = self.run_bundle("commit")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.assertEqual(
            self.git(self.repo, "log", "-1", "--format=%B", "main").strip(),
            self.message.strip(),
        )

    def assert_hook_change_stops_before_the_merge(self, name: str, body: str) -> None:
        self.record_fingerprints()
        self.hook(name, body)

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("nothing is merged", completed.stderr)
        self.assertEqual(self.rev(self.repo, "main"), self.base)

    def test_a_hook_that_alters_the_message_stops_before_the_merge(self) -> None:
        self.assert_hook_change_stops_before_the_merge(
            "commit-msg", 'printf "\\nAdded by a hook.\\n" >> "$1"\n'
        )

    def test_a_hook_that_alters_the_tree_stops_before_the_merge(self) -> None:
        self.assert_hook_change_stops_before_the_merge(
            "pre-commit", "printf 'hook edit\\n' >> a.txt && git add a.txt\n"
        )

    def test_check_stops_when_main_or_the_remote_moved(self) -> None:
        self.record_fingerprints()
        other = self.base_dir / "other clone"
        self.git(self.base_dir, "clone", "-q", str(self.remote), str(other))
        (other / "a.txt").write_text("moved on the remote\n")
        self.git(other, "commit", "-q", "-am", "remote moved")
        self.git(other, "push", "-q", "origin", "main")

        remote_moved = self.run_bundle("check")
        self.assertNotEqual(remote_moved.returncode, 0)
        self.assertIn("origin's main is not at", remote_moved.stderr)

        self.git(self.repo, "fetch", "-q", "origin")
        self.git(self.repo, "merge", "-q", "--ff-only", "origin/main")
        main_moved = self.run_bundle("check")
        self.assertNotEqual(main_moved.returncode, 0)
        self.assertIn("main moved from", main_moved.stderr)

    def test_check_stops_when_the_main_checkout_left_main(self) -> None:
        self.git(self.repo, "switch", "-q", "-c", "elsewhere")

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("is not on main", completed.stderr)

    def test_attribution_lines_stop_the_commit_before_it_is_made(self) -> None:
        for message in (
            "fix: x\n\nWhy.\n\nCo-Authored-By: Agent <agent@example.invalid>\n",
            "fix: x\n\nWhy.\nCo-authored-by: Agent <agent@example.invalid>\nMore body.\n",
            "fix: x\n\nWhy.\n\nSigned-off-by: Agent <agent@example.invalid>\n",
        ):
            with self.subTest(message=message):
                (self.bundle / "commit-msg.txt").write_text(message)
                completed = self.run_bundle("commit")
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("Co-Authored-By or Signed-off-by", completed.stderr)
                self.assert_nothing_committed()

    def test_identity_overrides_stop_the_bundle(self) -> None:
        self.record_fingerprints()
        cases = [
            ("user.name", "Someone Else", None),
            ("author.name", "Repo Local Author", None),
            ("committer.email", "local-committer@example.invalid", None),
            (None, None, {"GIT_AUTHOR_NAME": "Env Agent"}),
        ]
        for key, value, extra in cases:
            with self.subTest(key=key, extra=extra):
                env = dict(self.env, **(extra or {}))
                if key:
                    self.git(self.repo, "config", key, value)
                try:
                    completed = self.run_bundle("commit", env)
                finally:
                    if key:
                        self.git(self.repo, "config", "--unset", key)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("not the global", completed.stderr)
                self.assert_nothing_committed()

    def test_an_inherited_git_environment_is_ignored(self) -> None:
        other = self.base_dir / "unrelated repo"
        self.git(self.base_dir, "init", "-q", str(other))
        env = dict(self.env, GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other))

        completed = self.run_bundle("check", env)

        self.assertIn("record these fingerprints", completed.stderr, completed.stderr)
        self.assertEqual(self.git(other, "status", "--porcelain"), "")

    def test_a_rename_commits_both_paths(self) -> None:
        # Same content under a new name, which git would report as a rename.
        (self.worktree / "a.txt").write_text("a\n")
        (self.worktree / "a.txt").rename(self.worktree / "c.txt")
        (self.worktree / ".gitignore").write_text(
            "*\n!.gitignore\n!a.txt\n!b.txt\n!c.txt\n"
        )
        (self.bundle / "paths.txt").write_text(".gitignore\na.txt\nb.txt\nc.txt\n")
        self.record_fingerprints()

        completed = self.run_bundle("commit")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(
            self.git(self.repo, "ls-tree", "--name-only", "main").split(),
            [".gitignore", "b.txt", "c.txt"],
        )

    def test_check_stops_on_a_staged_change(self) -> None:
        self.git(self.worktree, "add", "a.txt")

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("staged changes", completed.stderr)

    def test_check_stops_on_hidden_or_unfinished_state(self) -> None:
        other = self.git(self.worktree, "commit-tree", "-p", self.base, "-m", "x",
                         self.rev(self.worktree, "HEAD^{tree}")).strip()
        merge_head = self.git(self.worktree, "rev-parse", "--git-path", "MERGE_HEAD").strip()
        merge_head_path = Path(merge_head) if os.path.isabs(merge_head) else self.worktree / merge_head
        merge_head_path.write_text(other + "\n")
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("MERGE_HEAD", completed.stderr)
        merge_head_path.unlink()

        self.git(self.worktree, "update-index", "--skip-worktree", "a.txt")
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("hides local edits", completed.stderr)

    def test_check_stops_on_bad_names_before_running_git_against_them(self) -> None:
        marker = self.base_dir / "ran"
        for extra, message in (
            ({"REMOTE": f"--upload-pack=touch {marker}"}, "must be a remote name"),
            ({"REMOTE": "nowhere"}, "is not a configured remote"),
            ({"BRANCH": "main"}, "must differ from MAIN"),
            ({"BRANCH": "bad..name"}, "not a valid branch name"),
            ({"REPO": str(self.repo / "sub")}, "not the root of the main checkout"),
        ):
            with self.subTest(extra=extra):
                (self.repo / "sub").mkdir(exist_ok=True)
                self.write_env(**extra)
                completed = self.run_bundle("check")
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(message, completed.stderr)
                self.assertFalse(marker.exists())

    def test_check_stops_on_a_worktree_of_another_repository(self) -> None:
        other = self.base_dir / "separate clone"
        self.git(self.base_dir, "clone", "-q", str(self.remote), str(other))
        self.git(other, "switch", "-q", "-c", "fix/x")
        (other / "a.txt").write_text("a changed\n")
        (other / "b.txt").write_text("b\n")
        self.worktree = other
        self.write_env()

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("belongs to another repository", completed.stderr)

    def test_check_stops_before_the_merge_overwrites_an_ignored_file(self) -> None:
        # The change admits and adds c.txt and notes/plan.md; in the main
        # checkout the reverse whitelist still ignores a local c.txt and a
        # local file named notes, which the fast-forward would replace.
        (self.worktree / ".gitignore").write_text(
            "*\n!.gitignore\n!a.txt\n!b.txt\n!c.txt\n!notes/\n!notes/plan.md\n"
        )
        (self.worktree / "c.txt").write_text("reviewed tool\n")
        (self.worktree / "notes").mkdir()
        (self.worktree / "notes" / "plan.md").write_text("plan\n")
        (self.bundle / "paths.txt").write_text(
            ".gitignore\na.txt\nb.txt\nc.txt\nnotes/plan.md\n"
        )
        for local, expected in (("c.txt", "would overwrite"), ("notes", "where the change writes a directory")):
            with self.subTest(local=local):
                for name in ("c.txt", "notes"):
                    (self.repo / name).unlink(missing_ok=True)
                (self.repo / local).write_text("operator's local draft\n")
                completed = self.run_bundle("check")
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(expected, completed.stderr)
                self.assertEqual((self.repo / local).read_text(), "operator's local draft\n")

    def test_retire_keeps_a_worktree_with_untracked_or_ignored_files(self) -> None:
        self.commit_and_push()
        # The status setting must not hide them.
        with self.gitconfig.open("a") as config:
            config.write("[status]\n\tshowUntrackedFiles = no\n")
        (self.worktree / "notes.local").write_text("ignored local file\n")
        nested = self.worktree / "nested repo"
        self.git(self.base_dir, "init", "-q", str(nested))

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("untracked files, or ignored files", completed.stderr)
        self.assertIn("notes.local", completed.stderr)
        self.assertTrue((self.worktree / "notes.local").exists())
        self.assertTrue((nested / ".git").exists())

    def test_retire_removes_only_the_change_worktree(self) -> None:
        self.commit_and_push()
        other = self.base_dir / "other worktree"
        self.git(self.repo, "worktree", "add", "-q", "-b", "side", str(other), "main")
        self.write_env(WORKTREE=str(other), **self.fingerprints())

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("has no worktree at", completed.stderr)
        self.assertTrue(other.exists())
        self.assertTrue(self.worktree.exists())

    def fingerprints(self) -> dict:
        return dict(
            line.split("=", 1)
            for line in (self.bundle / "bundle.env").read_text().splitlines()
            if line.startswith(("TREE=", "MESSAGE_SHA256="))
        )

    def test_retire_stops_while_a_process_works_in_the_worktree(self) -> None:
        self.commit_and_push()
        sleeper = subprocess.Popen(["sleep", "30"], cwd=self.worktree)
        try:
            completed = self.run_bundle("retire")
        finally:
            sleeper.kill()
            sleeper.wait()

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("a process works in", completed.stderr)
        self.assertTrue(self.worktree.exists())

    def test_retire_stops_before_removal_when_branch_d_would_refuse(self) -> None:
        self.commit_and_push()
        # An upstream that does not contain the commit makes branch -d refuse.
        self.git(self.repo, "branch", "-q", "elsewhere", self.base)
        self.git(self.repo, "branch", "-q", "--set-upstream-to=elsewhere", "fix/x")

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("git branch -d would refuse", completed.stderr)
        self.assertTrue(self.worktree.exists())

    def test_check_stops_on_push_configuration_it_cannot_show(self) -> None:
        cases = [
            ("remote.origin.pushurl", str(self.base_dir / "elsewhere.git"), "pushes to"),
            ("remote.origin.push", "refs/heads/main:refs/heads/release", "is set"),
            ("remote.origin.mirror", "true", "is set"),
            ("push.followTags", "true", "is set"),
        ]
        for key, value, message in cases:
            with self.subTest(key=key):
                self.git(self.repo, "config", key, value)
                try:
                    completed = self.run_bundle("check")
                finally:
                    self.git(self.repo, "config", "--unset", key)
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(message, completed.stderr)
        self.git(self.repo, "config", "--add", "remote.origin.url", str(self.base_dir / "second.git"))
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("more than one URL", completed.stderr)

    def test_merge_options_from_the_configuration_do_not_apply(self) -> None:
        self.git(self.repo, "config", "branch.main.mergeOptions", "--squash --autostash")
        self.git(self.repo, "config", "merge.autoStash", "true")
        self.record_fingerprints()

        completed = self.run_bundle("commit")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(self.rev(self.repo, "main"), self.rev(self.worktree, "HEAD"))
        self.assertEqual(self.git(self.repo, "status", "--porcelain"), "")

    def test_a_failed_fast_forward_reports_the_actual_state(self) -> None:
        self.record_fingerprints()
        (self.repo / ".git" / "refs" / "heads" / "main.lock").write_text("")

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("the fast-forward of main failed. main is at", completed.stderr)

    def test_the_merge_refuses_an_ignored_file_that_appears_after_check(self) -> None:
        (self.worktree / ".gitignore").write_text(
            "*\n!.gitignore\n!a.txt\n!b.txt\n!c.txt\n"
        )
        (self.worktree / "c.txt").write_text("reviewed tool\n")
        (self.bundle / "paths.txt").write_text(".gitignore\na.txt\nb.txt\nc.txt\n")
        self.record_fingerprints()
        self.hook(
            "pre-commit",
            f"printf 'operator draft\\n' > '{self.repo / 'c.txt'}'\n",
        )

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("fast-forward of main failed", completed.stderr)
        self.assertEqual((self.repo / "c.txt").read_text(), "operator draft\n")
        self.assertEqual(self.rev(self.repo, "main"), self.base)

    def test_check_stops_on_more_hidden_or_unfinished_state(self) -> None:
        git_path = lambda cwd, name: Path(  # noqa: E731
            self.git(cwd, "rev-parse", "--path-format=absolute", "--git-path", name).strip()
        )
        cases = [
            (self.worktree, "CHERRY_PICK_HEAD", "CHERRY_PICK_HEAD"),
            (self.worktree, "REVERT_HEAD", "REVERT_HEAD"),
            (self.worktree, "rebase-merge", "middle of a rebase"),
            (self.repo, "MERGE_HEAD", "MERGE_HEAD"),
            (self.worktree, "MERGE_AUTOSTASH", "MERGE_AUTOSTASH"),
        ]
        for cwd, name, message in cases:
            with self.subTest(where=cwd.name, name=name):
                target = git_path(cwd, name)
                if name.startswith("rebase"):
                    target.mkdir()
                else:
                    target.write_text(self.base + "\n")
                try:
                    completed = self.run_bundle("check")
                finally:
                    if target.is_dir():
                        target.rmdir()
                    else:
                        target.unlink()
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn(message, completed.stderr)
        self.git(self.worktree, "update-index", "--assume-unchanged", "a.txt")
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("hides local edits", completed.stderr)

    def test_check_stops_on_an_untracked_file_in_the_main_checkout(self) -> None:
        (self.repo / "b.txt").write_text("stray\n")

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("is not clean", completed.stderr)

    def test_check_stops_when_the_branch_moved(self) -> None:
        self.git(self.worktree, "commit", "-q", "--allow-empty", "-m", "extra")

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("is not at", completed.stderr)

    def test_check_detects_a_changed_message_and_malformed_bundle_env(self) -> None:
        self.record_fingerprints()
        (self.bundle / "commit-msg.txt").write_text("fix: other\n")
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("commit-msg.txt changed since review", completed.stderr)

        with (self.bundle / "bundle.env").open("a") as env:
            env.write("SURPRISE=1\n")
        completed = self.run_bundle("check")
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("unexpected line", completed.stderr)

    def test_an_inherited_index_file_is_ignored(self) -> None:
        env = dict(self.env, GIT_INDEX_FILE=str(self.base_dir / "foreign-index"))

        completed = self.run_bundle("check", env)

        self.assertIn("record these fingerprints", completed.stderr, completed.stderr)
        self.assertFalse((self.base_dir / "foreign-index").exists())

    def test_hash_lines_in_the_message_are_kept(self) -> None:
        self.message = "fix: keep the hash line\n\n# this line is body text\n"
        (self.bundle / "commit-msg.txt").write_text(self.message)
        self.record_fingerprints()

        completed = self.run_bundle("commit")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn(
            "# this line is body text",
            self.git(self.repo, "log", "-1", "--format=%B", "main"),
        )

    def test_a_non_default_remote_and_main_branch(self) -> None:
        self.git(self.repo, "branch", "-m", "main", "trunk")
        self.git(self.repo, "remote", "add", "upstream", str(self.remote))
        self.git(self.repo, "push", "-q", "upstream", "trunk")
        self.record_fingerprints(REMOTE="upstream", MAIN="trunk")

        committed = self.run_bundle("commit")

        self.assertEqual(committed.returncode, 0, committed.stderr)
        new = self.rev(self.repo, "trunk")
        self.assertIn(f"-- upstream {new}:refs/heads/trunk", committed.stdout)
        self.git(
            self.repo, "push", "-q", "--no-follow-tags", "--", "upstream",
            "refs/heads/trunk:refs/heads/trunk",
        )
        retired = self.run_bundle("retire")
        self.assertEqual(retired.returncode, 0, retired.stderr)
        self.assertFalse(self.worktree.exists())

    def test_retire_refuses_content_that_status_cannot_see(self) -> None:
        self.commit_and_push()
        cases = {
            "nested .git": lambda: (self.worktree / "docs").mkdir() or (self.worktree / "docs" / ".git").write_text("x\n"),
            "per-worktree ref": lambda: self.git(self.worktree, "update-ref", "refs/worktree/experiment", "HEAD"),
        }
        for name, make in cases.items():
            with self.subTest(case=name):
                make()
                completed = self.run_bundle("retire")
                self.assertNotEqual(completed.returncode, 0)
                self.assertTrue(self.worktree.exists())
                if name == "nested .git":
                    self.assertIn("nested .git", completed.stderr)
                    (self.worktree / "docs" / ".git").unlink()
                    (self.worktree / "docs").rmdir()
                else:
                    self.assertIn("per-worktree refs", completed.stderr)
                    self.git(self.worktree, "update-ref", "-d", "refs/worktree/experiment")

    def test_retire_refuses_a_worktree_with_submodules(self) -> None:
        # An unpopulated submodule directory hides its content from status.
        (self.repo / "lib").mkdir()
        self.git(self.repo, "update-index", "--add", "--cacheinfo", f"160000,{self.base},lib")
        self.git(self.repo, "commit", "-q", "-m", "add a submodule link")
        self.git(self.repo, "push", "-q", "origin", "main")
        base = self.rev(self.repo, "main")
        other = self.base_dir / "submodule worktree"
        self.git(self.repo, "worktree", "add", "-q", "-b", "fix/sub", str(other), "main")
        (other / "a.txt").write_text("a changed\n")
        (other / "lib").mkdir(exist_ok=True)
        (other / "lib" / "build-output.txt").write_text("local output\n")
        self.worktree = other
        self.base = base
        (self.bundle / "paths.txt").write_text("a.txt\n")
        self.record_fingerprints(BRANCH="fix/sub")
        committed = self.run_bundle("commit")
        self.assertEqual(committed.returncode, 0, committed.stderr)
        self.git(self.repo, "push", "-q", "origin", "main")

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("has submodules", completed.stderr)
        self.assertTrue((other / "lib" / "build-output.txt").exists())

    def test_retire_never_forces_a_removal(self) -> None:
        self.commit_and_push()
        self.git(self.repo, "worktree", "lock", str(self.worktree))

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("git worktree remove failed", completed.stderr)
        self.assertTrue(self.worktree.exists())
        self.assertIn("fix/x", self.git(self.repo, "branch", "--list"))

    def test_retire_refuses_hidden_local_edits(self) -> None:
        self.commit_and_push()
        self.git(self.worktree, "update-index", "--assume-unchanged", "a.txt")
        (self.worktree / "a.txt").write_text("local edit status cannot see\n")

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("hides local edits", completed.stderr)
        self.assertTrue(self.worktree.exists())

    def assert_post_commit_hook_stops_before_the_merge(self, body: str, message: str) -> None:
        self.record_fingerprints()
        marker = self.base_dir / "hook-ran"
        self.hook(
            "post-commit",
            f'[ -e "{marker}" ] && exit 0\ntouch "{marker}"\n' + body,
        )

        completed = self.run_bundle("commit")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(message, completed.stderr)
        self.assertEqual(self.rev(self.repo, "main"), self.base)

    def test_a_hook_that_amends_the_author_stops_before_the_merge(self) -> None:
        self.assert_post_commit_hook_stops_before_the_merge(
            'git commit -q --amend --no-edit --author="Someone Else <else@example.invalid>"\n',
            "is not authored by",
        )

    def test_a_hook_that_adds_a_commit_stops_before_the_merge(self) -> None:
        self.assert_post_commit_hook_stops_before_the_merge(
            "git commit -q --allow-empty -m extra\n",
            "does not sit on",
        )

    def test_a_hook_that_makes_a_merge_commit_stops_before_the_merge(self) -> None:
        self.assert_post_commit_hook_stops_before_the_merge(
            f'merge=$(git commit-tree "HEAD^{{tree}}" -p HEAD -p {self.base} -m merge)\n'
            'git update-ref HEAD "$merge"\n',
            "is a merge commit",
        )

    def test_check_stops_on_another_worktree_of_the_same_repository(self) -> None:
        other = self.base_dir / "side worktree"
        self.git(self.repo, "worktree", "add", "-q", "-b", "side", str(other), "main")
        (other / "a.txt").write_text("a changed\n")
        (other / "b.txt").write_text("b\n")
        self.write_env(WORKTREE=str(other))

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("has no worktree at", completed.stderr)

    def test_fetch_never_prunes_local_refs(self) -> None:
        self.git(self.repo, "config", "fetch.prune", "true")
        self.git(self.repo, "config", "fetch.pruneTags", "true")
        self.git(self.repo, "tag", "-a", "-m", "local", "local-only")
        self.git(self.repo, "update-ref", "refs/remotes/origin/gone", self.base)

        self.record_fingerprints()
        self.assertEqual(self.run_bundle("commit").returncode, 0)
        self.git(self.repo, "push", "-q", "origin", "main")
        retired = self.run_bundle("retire")

        self.assertEqual(retired.returncode, 0, retired.stderr)
        self.assertIn("local-only", self.git(self.repo, "tag", "--list"))
        self.assertEqual(self.rev(self.repo, "refs/remotes/origin/gone"), self.base)

    def test_check_stops_when_main_is_checked_out_twice(self) -> None:
        twin = self.base_dir / "second main"
        self.git(self.repo, "worktree", "add", "-q", "--force", str(twin), "main")

        completed = self.run_bundle("check")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("main is checked out in more than one worktree", completed.stderr)

    def test_retire_reports_a_push_rejected_because_the_remote_moved(self) -> None:
        self.record_fingerprints()
        self.assertEqual(self.run_bundle("commit").returncode, 0)
        other = self.base_dir / "other clone"
        self.git(self.base_dir, "clone", "-q", str(self.remote), str(other))
        (other / "a.txt").write_text("moved on the remote\n")
        self.git(other, "commit", "-q", "-am", "remote moved")
        self.git(other, "push", "-q", "origin", "main")

        completed = self.run_bundle("retire")

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("push was rejected", completed.stderr)
        self.assertTrue(self.worktree.exists())


if __name__ == "__main__":
    unittest.main()

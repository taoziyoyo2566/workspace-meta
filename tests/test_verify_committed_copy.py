import os
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "verify_committed_copy.sh"


class VerifyCommittedCopyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        base = Path(self.temp_dir.name)
        self.tmp = base / "tmp"
        self.tmp.mkdir()
        self.repo = base / "repo"
        self.repo.mkdir()
        self.env = os.environ.copy()
        self.env["TMPDIR"] = str(self.tmp)
        self.env["GIT_CONFIG_NOSYSTEM"] = "1"
        self.env["GIT_CONFIG_GLOBAL"] = str(base / "gitconfig")
        (base / "gitconfig").write_text(
            "[user]\n\tname = Test\n\temail = test@example.invalid\n"
        )
        # A reverse whitelist like workspace-meta's: everything is ignored
        # unless an allow line admits it.
        (self.repo / ".gitignore").write_text(
            "*\n!.gitignore\n!tracked.txt\n!deleted.txt\n!new.txt\n!link\n"
        )
        (self.repo / "tracked.txt").write_text("tracked\n")
        (self.repo / "deleted.txt").write_text("deleted\n")
        self.git("init", "-q", "-b", "main")
        (self.repo / "link").symlink_to("tracked.txt")
        self.git("add", ".gitignore", "tracked.txt", "deleted.txt", "link")
        # A tracked file the ignore rules reject still belongs to a commit.
        (self.repo / "forced.txt").write_text("force-added\n")
        self.git("add", "-f", "forced.txt")
        self.git("commit", "-q", "-m", "base")
        (self.repo / "deleted.txt").unlink()
        (self.repo / "new.txt").write_text("admitted, untracked\n")
        (self.repo / "not-admitted.txt").write_text("ignored\n")

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), *args], check=True, env=self.env
        )

    def run_script(self, *command: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            ["bash", str(SCRIPT), str(self.repo), "--", *command],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def test_copy_commits_admitted_files_and_leaves_out_the_rest(self) -> None:
        completed = self.run_script("git", "ls-files")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        committed = set(completed.stdout.split())
        self.assertEqual(
            committed, {".gitignore", "tracked.txt", "new.txt", "forced.txt", "link"}
        )
        self.assertEqual(list(self.tmp.iterdir()), [])

        # The file the ignore rules do not admit is not in the copy at all.
        listed = self.run_script("find", ".", "-type", "f", "!", "-path", "./.git/*")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        self.assertEqual(
            set(listed.stdout.split()),
            {"./.gitignore", "./forced.txt", "./new.txt", "./tracked.txt"},
        )
        # The symbolic link stays a link.
        link = self.run_script("readlink", "link")
        self.assertEqual(link.stdout.strip(), "tracked.txt", link.stderr)
        # The source checkout is untouched.
        status = subprocess.run(
            ["git", "-C", str(self.repo), "status", "--porcelain"],
            capture_output=True,
            text=True,
            env=self.env,
            check=True,
        ).stdout
        self.assertIn(" D deleted.txt", status)
        self.assertIn("?? new.txt", status)

    def test_the_default_command_is_make_test(self) -> None:
        bin_dir = Path(self.temp_dir.name) / "bin"
        bin_dir.mkdir()
        fake = bin_dir / "make"
        fake.write_text('#!/bin/sh\necho "fake make $*"\n')
        fake.chmod(0o755)
        env = dict(self.env, PATH=f"{bin_dir}{os.pathsep}{self.env['PATH']}")

        completed = subprocess.run(
            ["bash", str(SCRIPT), str(self.repo)],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("fake make test", completed.stdout)

    def test_an_inherited_git_environment_does_not_reach_another_repository(self) -> None:
        other = Path(self.temp_dir.name) / "other"
        other.mkdir()
        subprocess.run(["git", "-C", str(other), "init", "-q"], check=True, env=self.env)
        env = dict(self.env, GIT_DIR=str(other / ".git"), GIT_WORK_TREE=str(other))

        completed = subprocess.run(
            ["bash", str(SCRIPT), str(self.repo), "--", "git", "ls-files"],
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("tracked.txt", completed.stdout)
        log = subprocess.run(
            ["git", "-C", str(other), "rev-list", "--all", "--count"],
            capture_output=True,
            text=True,
            env=self.env,
            check=True,
        ).stdout.strip()
        self.assertEqual(log, "0")

    def test_an_inherited_index_file_does_not_reach_the_source(self) -> None:
        foreign = Path(self.temp_dir.name) / "foreign-index"
        before = subprocess.run(
            ["git", "-C", str(self.repo), "status", "--porcelain"],
            capture_output=True, text=True, env=self.env, check=True,
        ).stdout
        env = dict(self.env, GIT_INDEX_FILE=str(foreign))

        completed = subprocess.run(
            ["bash", str(SCRIPT), str(self.repo), "--", "git", "ls-files"],
            capture_output=True, text=True, env=env, check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("tracked.txt", completed.stdout)
        self.assertFalse(foreign.exists())
        after = subprocess.run(
            ["git", "-C", str(self.repo), "status", "--porcelain"],
            capture_output=True, text=True, env=self.env, check=True,
        ).stdout
        self.assertEqual(after, before)

    def test_the_copy_ignores_global_hooks_and_signing(self) -> None:
        hooks = Path(self.temp_dir.name) / "global-hooks"
        hooks.mkdir()
        (hooks / "pre-commit").write_text("#!/bin/sh\nexit 1\n")
        (hooks / "pre-commit").chmod(0o755)
        with open(self.env["GIT_CONFIG_GLOBAL"], "a") as config:
            config.write(f"[core]\n\thooksPath = {hooks}\n[commit]\n\tgpgSign = true\n")

        completed = self.run_script("git", "log", "--format=%s")

        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("committed copy of", completed.stdout)

    def test_the_make_target_runs_the_tests_on_a_committed_copy(self) -> None:
        makefile = (ROOT / "Makefile").read_text().splitlines()
        target = makefile.index(next(line for line in makefile if line.startswith("verify-committed:")))
        self.assertEqual(
            makefile[target + 1].strip(),
            '@bash scripts/verify_committed_copy.sh . -- $(MAKE) test PYTHON="$(PYTHON)"',
        )

    def test_a_failing_command_fails_the_run_and_removes_the_copy(self) -> None:
        completed = self.run_script("false")

        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(list(self.tmp.iterdir()), [])


if __name__ == "__main__":
    unittest.main()

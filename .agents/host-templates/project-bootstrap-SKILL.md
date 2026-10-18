---
name: project-bootstrap
description: Create a workspace project's missing agent entry files (AGENTS.md as the owner, CLAUDE.md as the @AGENTS.md adapter, or only an excluded CLAUDE.local.md in someone else's clone) by surveying the project. Use when the workspace-meta session-start check reports a project without a Claude entry file, when a Git project under ~/workspace/projects has none, or when the operator runs /project-bootstrap.
argument-hint: "[project directory]"
---
<!-- workspace-meta managed skill: make sync replaces this file -->

# project-bootstrap — give a workspace project its agent entry files

Method owner: `~/workspace/.agents/rules/documentation.md` Project Bootstrap.
Claude's entry files: `~/workspace/.agents/rules/claude-runtime.md` Project
Entry Files. Read both now; where this file and the rules differ, the rules
govern. Creating missing entry files is pre-authorized for the session in
conversation with the operator; overwriting, rewriting, or committing is not.

Project: $ARGUMENTS

If it is empty, use the Git root of the current working directory.

## Steps

1. Check that you may write. If you are a delegated agent, or the operator or
   your brief forbids writes, do not create anything: report the missing entry
   files and stop.
2. Find the project root: the nearest Git root at or below
   `~/workspace/projects/<name>`. If there is none, stop: a directory that is
   not a Git repository is bootstrapped only when the operator asks. If the root
   is a linked worktree (`git rev-parse --git-dir` differs from
   `--git-common-dir`) with no entry files of its own, use its main checkout as
   the root instead: the branch gets the files by merge.
3. Classify ownership from the canonical remote (`git remote -v`): a repository
   the operator owns, or a clone of someone else's. Compare the remote's owner
   with the operator's own repositories, such as workspace-meta's origin.
4. Read what exists: `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`,
   `CLAUDE.local.md`, every nested `AGENTS.md` and its sibling `CLAUDE.md`,
   `README*`, and the project's documentation index. An existing canonical
   owner is kept, whatever its name.
5. In a repository the operator owns:
   - when there is no canonical owner, survey the project read-only (manifests
     and lock files, the `Makefile` and scripts, CI configuration, the README
     and documentation, the Git branches and remote, existing agent
     instructions; for a large project, give the reading to an `Explore`
     subagent with a bounded question) and write `AGENTS.md` with what
     `documentation.md` Project Bootstrap lists, in the project's own language
     and terms, short enough to load in every session;
   - when the root has an `AGENTS.md` owner and no Claude entry file, write
     `CLAUDE.md` containing only the line `@AGENTS.md`;
   - for each nested `AGENTS.md` without a sibling Claude entry file, write a
     sibling `CLAUDE.md` containing only the line `@AGENTS.md`.
6. In a clone of someone else's repository, write only `CLAUDE.local.md`: the
   line `@AGENTS.md` when the clone has an `AGENTS.md`, otherwise the survey
   notes from a read-only survey as in step 5. Append `CLAUDE.local.md` to
   `"$(git rev-parse --git-common-dir)/info/exclude"` (create the file if it is
   missing; never truncate it). Never add tracked files to such a clone.
7. When existing files conflict, for example a `CLAUDE.md` that states rules
   while `AGENTS.md` also exists, change nothing: report the conflict with a
   proposed fix and ask the operator once.
8. Check the result: each import sits on its own line outside any code fence;
   `git -C <root> status --short` shows only the files you created in an
   operator-owned repository, and nothing new in someone else's clone.
9. Report in the same reply: each path created, what it holds, that the files
   are uncommitted, and that committing them follows the project's change flow
   (`~/workspace/.agents/rules/git-branches.md`).

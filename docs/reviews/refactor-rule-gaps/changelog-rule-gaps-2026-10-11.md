# Changelog: portable rules for five gaps, and the change flow

- **Date**: 2026-10-11
- **Plan**: [plan-rule-gaps-2026-10-11.md](plan-rule-gaps-2026-10-11.md)
- **Delivery state**: content-complete and verified on branch `feat/rule-gaps`.
  When this record was written, none of these approved steps had run yet:
  commit, merge into `main`, push, `make sync` on each host, and the `v1.0.0`
  tag.

## Outcome

Five new rule owners close the five gaps, and `git-branches.md` gains the
change flow. Register entries W-R53–W-R58 hold their provenance.

- **`file-checks.md`** (W-R53):
  - a delivered or kept file passes five ordered stages before it is called
    done;
  - a check counts only for what it can detect;
  - a new warning fails until it is fixed, narrowly suppressed with a reason,
    or accepted by the project;
  - both adapters carry it in their safety floor.
- **`deployment.md`** (W-R54):
  - what serves users runs a pushed main-branch commit;
  - temporary deployments, including older-line patches, have end conditions;
  - an older release gets checks before it is deployed, and a component stays
    on hold after a rollback;
  - a push that changes what runs is deployed promptly;
  - an instance outside the inventory is reported before anyone acts on it.
- **`temporary-files.md`** (W-R55):
  - temporary files are placed by size and filesystem;
  - whoever creates them removes them;
  - temporary space is not a store;
  - a fixed procedure applies when that space fills.
- **`problem-follow-up.md`** (W-R56):
  - every proposed procedure is checked against the recorded rules and
    decisions;
  - a qualifying problem report has six parts, in order.
- **`releases.md`** (W-R57):
  - a closed batch or a fix gets an annotated version tag after its release is
    verified, and routine deploys are not tagged;
  - the tag carries seven-part notes that link the Changelog;
  - it also covers the tag bundle, fixes to released versions, and the rollback
    target.
- **`git-branches.md` Change Flow** (W-R58):
  - every change goes through a short-lived, typed branch from the main
    branch;
  - under the approved approval semantics, an additive worktree for an
    authorized change is reported rather than confirmed, when it is outside
    the checkout or ignored and carries no uncommitted edits;
  - one change-flow bundle (`git-publication.md`) covers the commit, an
    optional rebase of the change's own unpushed branch, the merge, the push,
    and the retirement of the merged change.

The overlaps the Plan named were removed from the existing owners. The
adapters, README-agents, the root README, the handbook pages, the tests, and
the documentation gate all point to the new owners.

`scripts/workspace_status.py` warns at session start when the agent's
temporary filesystem is at least 80% used or has less than 256 MiB free. The
warning goes to the operator, and through `additionalContext` to the agent.

Workspace-meta's `AGENTS.md` records its branch and release facts.

Final rule sizes in lines:

| Rule | Lines |
|---|---|
| `file-checks.md` | 85 |
| `deployment.md` | 103 |
| `temporary-files.md` | 59 |
| `problem-follow-up.md` | 74 |
| `releases.md` | 171 |

`releases.md` is larger than the Plan's estimate of about 70 lines, because it
carries every element the Plan lists.

## Implementation readings

The operator accepted both at publication review on 2026-10-11 ("认可，两处都按你的来").

- **Worktree removal in the bundle.** Q1 approved deleting the merged branch in
  the bundle. Git refuses to delete a branch that is checked out in a worktree,
  so the bundle's last step first removes the worktree that Change Flow
  created. The step is bounded:
  - it stops when that worktree holds untracked or ignored files;
  - it deletes the local branch only, with `git branch -d`;
  - remote deletion stays separately reviewed.
- **workspace-meta facts that Q2 left as slots.** These are recorded as
  proposals:
  - the Conventional Commits type prefixes;
  - fast-forward-only integration;
  - unsigned tags;
  - the compatibility and status surfaces;
  - that no rollback procedure is written yet.

## Verification

- **`make test`.** Run with the five new rule files in a temporary index copy,
  where `--info-only` writes no objects. The documentation gate is OK and all
  110 unit tests pass. In the real worktree the only failure is the expected
  "routed documentation is not tracked" for the five untracked rule files.
- **Static and whitespace checks.** All pass:
  - `bash -n scripts/*.sh .githooks/pre-commit`;
  - `py_compile` of the scripts and tests, with warnings as errors;
  - `git diff --check`;
  - a trailing-whitespace and final-newline check of the untracked files.
- **Bootstrap.** Run twice in a temporary HOME. Both runs exit 0. The second
  run reports "0 updated, 6 unchanged", and the managed files' hashes are
  identical. The first run's only warning, "Codex hook definition changed;
  review and trust it with /hooks", is expected for a fresh install.
- **Installed hook.** The Claude hook command, run end to end against this
  worktree, verified its hash pin and emitted valid JSON, both with hook input
  on stdin and with stdin closed.
- **Hook tests.** New unit tests cover:
  - the warning's thresholds and its arithmetic with blocks reserved for root;
  - measuring a missing scratch directory on its nearest existing parent;
  - a filesystem that cannot be measured;
  - stdin that is a terminal, empty, invalid JSON, closed, or left open past
    the deadline;
  - the JSON contract that reaches the agent.
- **Independent review.** A read-only review of the rule texts and the script
  found no P0, 6 P1 and 10 P2. All were fixed before the checks above were
  rerun:
  - the main-branch rule now excepts temporary deployments;
  - the bundle's retirement step is bounded;
  - new warnings no longer pass on an explanation alone;
  - releases.md says which releases are tagged;
  - the README describes the hook output;
  - stdin handling is hardened and tested;
  - the bundle section is moved below the identity rule;
  - the fix-branch wording matches `releases.md`;
  - the exception scopes and the reported-worktree bounds are tightened;
  - git-recovery points to the rule that release tags never move;
  - planning.md covers memory holding an unowned deferral;
  - the register owner map is complete;
  - single-value hashes are excluded from check output;
  - a deployment-route test is added.

## Gaps and follow-ups

- **Real-client display of the temporary-space warning.** This is a manual
  host check after `make sync`, in both Claude Code and Codex. Both official
  hook references document `hookSpecificOutput.additionalContext` for
  SessionStart. The reviewer also found it in the installed binaries.
- **Release steps.** `make sync` on each host, where Codex asks to re-trust the
  changed hook. Then the `v1.0.0` tag on the landing commit.
- **Remaining follow-ups.** The reality-ops follow-ups and the deferred
  temporary-tree items stay as the Plan lists them.

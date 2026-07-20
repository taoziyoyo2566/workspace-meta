# Plan: Git transaction review and execution UX

- **Date**: 2026-07-20
- **Level**: Engineering (cross-project Codex governance)
- **Cost**: medium
- **Parent decision**: W-R30
- **Source incident**: Saberu rename work repeatedly split one task into
  preparation, fixed-wording confirmation, commit, push, PR, activation, and
  closeout rounds. The repeated gates did not improve content review and helped
  produce administrative successor branches instead of finishing the task.

## 0. Direction pre-check

Evidence reviewed:

- W-R30 and its original incident: an unsolicited commit was created before the
  proposed content met the required standard.
- Current managed template and installed `~/.codex/AGENTS.md`: the installed
  copy also contains later branch/worktree, stash, and integration safeguards
  that have not yet been synchronized back to the template.
- Saberu `.agents/rules/{authorization,git,commits,branching}.md`: project rules
  amplify the global two-stage model and require a separate manifest for each
  commit, push, and integration.
- Codex execpolicy boundary documented in
  `docs/architecture/codex-config-management.md`: a sandbox Yes/Allow is
  technical capability, not semantic authorization.

Conclusion: W-R30's safety objective remains correct, but “one later
confirmation per Git operation” is the wrong rule shape. The observed failure
is now wrong-shaped workflow output, so W-R27 calls for a positive transaction
recipe rather than more prohibitions. The review boundary should protect the
content and the complete mutation sequence, not maximize the number of user
turns.

## 1. Purpose

Replace fixed-wording, operation-by-operation Git confirmations with a
reviewable two-checkpoint transaction:

1. Codex finishes the authorized edits and validation, then presents a concise
   result/change list for content review.
2. After the user accepts that result in ordinary natural language, Codex
   presents the exact, copyable command bundle needed to publish it. The user
   may either authorize Codex to execute that unchanged bundle once or execute
   it personally and report completion.

The command bundle may contain exact-path `git add`, one `git commit`, one
`git push`, and `gh pr create` when those actions are all appropriate and
explicitly shown.

## 2. Scope

In scope:

- `.agents/host-templates/codex-AGENTS.md`
- `README.md`
- `docs/architecture/codex-config-management.md`
- `feedback-register.md` (new W-R31 refinement; W-R30 remains historical)
- sync regression coverage in `tests/test_sync_codex_config.py`
- this plan and its round changelog
- installing the changed managed block on the current host after repository
  verification

Downstream, in a separate Saberu governance change:

- align `.agents/rules/authorization.md`, `git.md`, and `commits.md` with the
  command-bundle model;
- simplify `.agents/rules/branching.md` so one deliverable keeps one owner
  branch through implementation and review, and a branch registration or
  activation record does not require an intermediate PR;
- remove the rule pressure that creates recursive closeout/successor branches.

Out of scope:

- changing `~/.codex/rules/*.rules` or weakening its technical prompts;
- force-push, ref deletion, reset, rewrite, destructive cleanup, deployment, or
  live-infrastructure authorization;
- automatically merging a PR;
- resuming Saberu rename before both rule layers are integrated;
- removing existing worktrees or branches.

## 3. Required transaction shape

### Checkpoint A: result review

After edits and validation, present:

- changed paths and the outcome of each logical change;
- validation results and explicit gaps;
- known exclusions or follow-up work;
- repository/branch and dirty-state context needed to understand the result.

The user may accept this with ordinary language such as “确认”, “没问题”, or
“继续”. Codex must not require the user to repeat a generated phrase or
manifest.

Acceptance of checkpoint A authorizes preparation of checkpoint B, not hidden
commands or a materially different result.

### Checkpoint B: command-bundle review

Present commands in execution order, including every applicable operation:

```bash
git add -- <exact paths>
git commit -m <complete message>
git push <remote> <exact source:destination refspec>
gh pr create --base <target> --head <source> --title <title> --body <body>
```

Accompany the block with the expected branch, staged paths, commit count/range,
remote/ref mode, checks/gaps, and PR base/head. The user may confirm the
unchanged bundle in ordinary natural language; no fixed wording is required.

Two completion paths are equally valid:

1. **Agent execution** — one ordinary confirmation authorizes Codex to execute
   the displayed bundle sequentially once.
2. **Operator execution** — the user may copy and run some or all displayed
   commands, then report completion. Codex performs read-only verification of
   the resulting commit, remote ref, and PR as applicable; it does not ask the
   user to restate commands, OIDs, or a generated confirmation phrase.

For operator execution, the user's completion report is evidence to verify,
not authority to rerun the same mutations. Missing, partial, or divergent state
is reported precisely and any corrective mutation receives a new command
bundle.

Codex stops and reports rather than improvising when:

- files, staged content, message, refs, range, checks, base/head, or commands
  differ from the displayed bundle;
- a hook changes content or rejects the commit;
- the produced commit does not have the expected parent/tree/message;
- remote state makes the displayed push non-fast-forward;
- push fails, PR creation conflicts with an existing PR, or any step needs a
  different command.

Expected state transitions caused by earlier displayed commands do not
invalidate later commands in the same bundle. In particular, the displayed
commit creating the exact commit that the displayed push publishes is normal,
not manifest drift.

### Separate high-impact transactions

Keep destructive/history-rewriting actions, merge execution, PR merge,
deployment, live-infrastructure mutation, ref deletion, branch/worktree
cleanup, and recovery actions outside this bundle unless a later rule defines
an equally explicit safe bundle for that operation. Sandbox/escalation prompts
remain technical permission only.

## 4. Branch and lifecycle correction

The downstream Saberu rule change will establish:

- one task/deliverable has one active owner branch;
- normal commits and pushes preserve that branch; they do not end its
  lifecycle;
- branch registration and base-OID evidence are recorded in the first ordinary
  work commit and may be pushed for durability without opening an activation
  PR;
- a PR is opened when the accepted deliverable or explicitly accepted partial
  closeout is ready for integration;
- post-merge evidence that requires a repository update belongs on the target's
  next normal governance/work branch, not a recursively generated
  `<topic>-closeout` branch;
- premature integration is handled by one bounded correction and one remaining
  owner, not repeated activation/closeout successors.

## 5. Verification

1. **Direction**
   - Compare the final diff to this plan and W-R30's original safety objective.
   - Confirm no host-local authorization file or unrelated dirty content is
     included.
2. **Static**
   - `git diff --check`
   - `bash -n scripts/*.sh .githooks/pre-commit`
   - `python3 -m py_compile scripts/*.py tests/*.py`
3. **Functional**
   - `make test`
   - install twice into an isolated temporary HOME and compare managed target
     hashes after the first and second installs;
   - assert the installed AGENTS block contains checkpoint A, checkpoint B,
     natural-language confirmation, and unchanged-bundle expiry semantics;
   - run `make agent-sync-check`, install with `make bootstrap`, then rerun
     `make agent-sync-check` on the current host.

The current-host install must preserve all content outside workspace-meta's
managed markers. A real conversation using the new bundle is the final
behavioral acceptance test.

## 6. Delivery order

1. Implement and verify the workspace-meta rule source.
2. Present checkpoint A for user review.
3. Present one complete, copyable workspace-meta
   `add`/`commit`/`push`/PR command bundle. Continue either after ordinary
   confirmation for Codex execution or after read-only verification of the
   user's reported execution.
4. After integration, install the merged global rule on the host.
5. Create one `gov/git-transaction-ux` branch from the latest Saberu
   `origin/dev`, implement and verify the project-rule alignment.
6. Use the new command-bundle flow to publish that single governance branch.
7. After governance integration, create one final rename owner branch from the
   latest `origin/dev`, finish runtime verification, and open one PR only when
   the rename deliverable is ready.

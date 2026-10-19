# Changelog: keeping reusable work out of temporary space

- **Date**: 2026-10-19
- **Plan**: [plan-keep-reusable-work-2026-10-18.md](plan-keep-reusable-work-2026-10-18.md)
- **Delivery state**: content-complete and verified on branch
  `feat/keep-reusable-work`, uncommitted. When this record was written, none
  of these steps had run:
  - commit, merge into `main`, and push;
  - `make sync` on each host, which installs the changed Codex route row;
  - the separate claude-md change's own commit.

## Outcome

Work an agent will need again is now kept by its owner instead of being lost
with temporary space. Three procedures that existed only as scratch scripts
are now tools.

- **Rule (W-R75)**: `temporary-files.md` Lifecycle sorts temporary files
  before removing them.
  - What will be needed again is proposed for moving to its owner, such as a
    script into its project as a tool or a scenario into the evaluation tree.
    Only the rest is removed.
  - The final report says what was moved or proposed for moving.
  - Both adapters route "creating or removing temporary files".
  - The change adds the register entry, a design-map symptom, and phrase
    tests.
- **Evaluation scenarios**:
  - The six request-intake and delegation scenarios written on 2026-10-17
    existed only in a session's scratch. They are restored verbatim from the
    session transcripts, including the later rewording of `delegation-plan`.
  - `cleanup-keeps-reusable` is a new target scenario for W-R75.
- **Guarded sync**: `scripts/sync_codex_config.py --expect` and
  `make sync SYNC_EXPECT='label;label'` apply without a prompt only when every
  drifted area is listed. An unknown label or unlisted drift stops before
  anything is written.
- **Bundle runner**: `scripts/change_flow_bundle.sh check|commit|retire DIR`
  runs a reviewed change-flow bundle.
  - Fingerprints bind the reviewed tree and message.
  - `check` reads the remote tip without fetching. It stops on drift in refs,
    content, message, or identity; on staged, hidden, or unfinished state; on
    a foreign worktree; when the merge would overwrite a local file; and on
    push configuration that would send more than the main branch.
  - `commit` commits a private copy of the reviewed message and checks the
    commit. It then fast-forwards the main branch without the configured merge
    options.
  - The push is printed as `cd <repo> && git push ...`, with the reviewed
    commit as its source, so guards and permission rules that ask before
    `git push` still see it.
  - `retire` fetches without pruning. It removes only the change's own
    worktree, never with `--force`, and only when every file in it is
    tracked.
- **Committed-copy check**: `scripts/verify_committed_copy.sh` and
  `make verify-committed` run `make test` on a temporary copy in which every
  whitelisted file is committed. The copy's own commit ignores the global and
  system Git configuration.
- **claude-md**, a separate repository recorded in its own
  `IMPLEMENTATION-LOG.md`:
  - The Bash guard denies the common spellings of a recursive force delete.
  - It makes no decision only for one literal `rm -r -f` inside the calling
    session's own scratchpad that touches no repository, worktree, or mount.
  - The settings keep denying `rm -rf`, and a rule tells agents which form to
    use.
  - Regression tests cover the guard's three copies and the settings that wire
    them.

## Verification

- `make test`: the documentation gate is OK and 246 tests pass (188 on
  `main`). The suite also passes on a committed copy (`make verify-committed`).
  `bash -n`, `py_compile`, TOML parsing, and `git diff --check` are clean.
- The new tests fail on `main`'s versions of the changed files. The reviews'
  mutation runs showed which deliberately broken copies of the tools the tests
  catch, and the gaps they found are now covered.
- claude-md: `node --test tests/pretool-bash-guard.test.mjs` passes 20 tests,
  and the tests fail on `master`'s guard.
- Independent review: two reviews and four adversarial verification rounds
  (opus, max effort). The final round found no blocker. claude-md's guardrail
  audit found nothing that must or should be fixed, and 40 detection payloads
  and the exception attacks against the guard found nothing. Every finding
  from the earlier rounds is fixed or listed below.
- Behavior, measured with the rule-evaluation harness (`claude-opus-5-5`,
  three trials, a three-vote `sonnet` judge; $9.60 in total):
  - `cleanup-keeps-reusable` scored 3/3 on `main` and on this branch. It is at
    its ceiling, so it shows no difference. Its first wording, which hinted at
    reuse, scored 2/3 on `main`.
  - The canary, `control-readonly-status`, and `user-run-script` scored 3/3 on
    both versions.
  - The restored scenarios on this branch:
    - `intake-ask-when-present`, `intake-operator-away`,
      `intake-similar-problems`, and `control-trivial-question`: 3/3 each;
    - `delegation-plan`: 1/3 (also 1/3 on `main`);
    - `intake-idea`: 1/3 (0/3 on `main`).

## Open finding

`delegation-plan` and `intake-idea` score lower on current `main` than they
did when their rules were evaluated on 2026-10-17, when each scored 2/2. This
change does not cause it. The operator decided on 2026-10-18 that finding the
cause, by evaluating the commits in between, is a separate task after this
change lands.

## Residual gaps

- The W-R75 target is at its ceiling in a one-decision replay. The incident
  happened late in a long session, which a single decision point does not
  reproduce.
- claude-md guard:
  - It does not see arguments or a command word produced by expansion,
    escape sequences inside `$'...'`, or indirect execution (a script, another
    interpreter, `find -delete`).
  - Its check runs before the command, so a change in between is not seen.
  - It misses same-device bind mounts and `rm -r` without `-f`, and the
    session's subagents share its scratchpad.
  - The 50,000-entry cap and the `/tmp/claude-<uid>` owner check have no
    test.
  - Without the hook, only the settings deny on `rm -rf` remains.
  - Enforcing "never `git worktree remove --force`" in settings or the hook is
    a proposed follow-up.
- The bundle runner reads state at the moment of each step. A change made
  between steps by another process is caught only by the next check.

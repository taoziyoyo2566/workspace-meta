# Changelog: idea done step, confirmed evaluation results, and terminal steps

- **Date**: 2026-10-19
- **Plan**: [plan-intake-evals-terminal-2026-10-19.md](plan-intake-evals-terminal-2026-10-19.md)
- **Delivery state**: content-complete and verified on branch
  `fix/intake-evals-terminal`, uncommitted. When this record was written,
  none of these steps had run: commit, merge into `main`, and push.

## Outcome

- **Idea depth**: `requests.md` reads an idea the operator floats for new or
  changed behavior, also when it comes with examples, at the depth that does
  every step and gives the brief before the work.
  - It takes that depth even when the request also reports a problem, makes
    a correction, or fits the first depth.
  - An idea that only renames or rewords takes the first depth, or the middle
    one when the request also reports a problem or makes a correction.
  - Step 5 says that for an idea, done is what done would mean once the idea
    is carried out.
- **Evaluation practice**: `evals/rules/README.md`:
  - Deciding compares versions only within one window: the fields
    `results.json` records, runs made back to back, and pinned agent and
    judge models. A target counts as improved only when a second comparison
    of the same two versions on the same scenario file, with five or more
    graded trials each and the canary, shows the rise again. Every run the
    evaluation made on the target is reported.
  - Keeping Runs gives every comparison a new directory outside any cache,
    names each cited `results.json` by its directory and `rules` value, and
    keeps a cited directory until a later record supersedes every result
    cited from it.
  - The Run examples follow both, and say that a Codex judge without
    `JUDGE_MODEL` belongs to no window.
- **Terminal steps (W-R76)**: `capabilities.md` Commands The User Runs says
  how the user opens that terminal from where they are, after checking how
  the session runs from what it can read about itself or by asking the user.
  The step comes with the register entry and owner row.
- **Checks**: new phrase tests for the three changes and two new scenarios:
  - the target `user-run-open-terminal`, written from the incident;
  - the control `control-small-idea`, a floated rename.

  Also design-map symptom rows and entry text.

## Verification

- `make verify-committed`: the documentation gate is OK and 249 tests pass
  on a committed copy. The new phrase tests fail on `main`'s text.
- File checks of the four new files: no trailing whitespace, a final
  newline, and both scenarios load in the scenario hygiene test.
  `git diff --check` is clean for the tracked files.
- Four adversarial checks ran, each by opus agents at max effort. Each
  should-fix or must-fix finding went to an independent verifier; minor
  findings were not verified.
  - The first review confirmed 15 should-fix findings, refuted 3, and raised
    10 minor ones.
  - The re-review confirmed 7 should-fix findings and raised 12 minor ones.
  - A final check of the fixes and of this record found four must-fix
    statements here, all corrected. Two are the `!` warnings and the ungraded
    trial's judge answers, which the kept runs contradict. The other two are
    that every review finding had a verifier and that the re-review raised 14
    minor findings, which the review records contradict. It also found four
    should-fix gaps, all fixed.
  - A closeout check confirmed those corrections. It found one more
    must-fix statement, an earlier wording of the previous bullet, and one
    should-fix gap in the Plan's approval record. Both were corrected with
    wording its verifier checked against the evidence, and no further check
    ran on them.
  - All confirmed findings are fixed, and the minor ones are fixed or listed
    under Residual gaps.
- Evaluation: four comparisons on 2026-10-19, each running both versions side
  by side, with matching model, CLI, and judge fields.
  - `claude-opus-5-5` under Claude Code 2.1.303, judged by a three-vote
    `sonnet` judge that resolved to `claude-sonnet-5-5`; cost $21.69.
  - Before: `git:accb142c825a`. After: `sha256:0118e360018a`, the working
    tree of `fix/intake-evals-terminal` based on `accb142`, unchanged
    through all four comparisons.
  - Runs are kept under
    `~/.local/share/workspace-meta/rule-eval/2026-10-19-intake-evals-terminal-<n>/{before,after}`.

| Comparison `<n>` | Scenario | Trials | main | branch |
|---|---|---|---|---|
| 1 | `canary-rules-loaded` | 6 | 6/6 | 6/6 |
| 1 | `intake-idea` | 6 | 5/6 | 6/6 |
| 1 | `user-run-open-terminal` | 6 | 0/6 | 6/6 |
| 2 | `control-small-idea` | 3 | 3/3 | 2/3 |
| 2 | `user-run-short-command` | 3 | 2/3 | 3/3 |
| 2 | `user-run-new-terminal` | 3 | 3/3 | 2/2, one ungraded |
| 2 | seven others | 3 | 3/3 each | 3/3 each |
| 3 | `canary-rules-loaded` | 6 | 6/6 | 6/6 |
| 3 | `intake-idea` | 6 | 4/6 | 6/6 |
| 3 | `user-run-open-terminal` | 6 | 0/6 | 6/6 |
| 4 | `canary-rules-loaded` | 6 | 6/6 | 6/6 |
| 4 | `control-small-idea` | 6 | 5/6 | 6/6 |

- Comparison 2's other scenarios: `canary-rules-loaded`,
  `control-trivial-question`, `control-edit-in-scope`,
  `intake-ask-when-present`, `intake-operator-away`,
  `intake-similar-problems`, and `user-run-script`.
- **Both targets improved and are confirmed**: comparison 3 is the second
  comparison of the same two versions on the same scenario files.
- **Terminal target**: every `main` reply told the operator to open "a new
  terminal" with no keys or command. Every branch reply first read how the
  session is reached (`TMUX`, `SSH_CONNECTION`) in a read-only check and said
  that the steps follow. Eleven of the twelve branch replies, like all twelve
  `main` replies, warned against the `!` prefix; none suggested it.
- **`control-small-idea` drop**: it fell from 3/3 to 2/3 in comparison 2.
  - The failing reply compared the two names by meaning, recommended one name
    per intent, and added a constraint from decision 9 before its view and
    an offer to make the edit. All three judge votes failed it as options per
    scenario.
  - Passing replies from both versions also gave such an alternative, so the
    reply sits near the control's line.
  - The rerun with six trials per version (comparison 4) shows no drop, 5/6
    against 6/6. The one `main` failure there was a structured brief that
    ended with two questions.
- **`user-run-new-terminal` ungraded trial**: one of its three judge answers
  could not be parsed, because it held two JSON objects. The other two
  answers split, one pass and one fail, so the vote was undecided. The reply
  had stopped at a read-only check of the terminal environment, which that
  scenario accepts.
- **Change after the evaluation**: after the four comparisons, the
  tie-break in `requests.md` gained its last clause: a floated rename that
  comes with a problem report or a correction keeps the middle depth. The
  committed rules therefore differ from the measured `sha256:0118e360018a`
  in that clause. Neither evaluated request is affected: `intake-idea`
  floats a behavior idea, and `control-small-idea` floats a rename with no
  problem report. That clause was not measured.

## Residual gaps

- **`intake-idea`**: `main` passed it in 9/12 trials over comparisons 1 and
  3, against 12/12 on the branch. The gain is small, and the scenario no
  longer separates the versions strongly.
- **Terminal target**: the branch passes by stopping at a check of how the
  session is reached. The steps themselves come after the check's output,
  which a one-decision replay does not show.
- **Small behavior ideas**: `control-small-idea` covers a rename only; a
  small floated behavior change gets the brief, as the Plan accepts.
- **Window fields**: `results.json` records `cli` and `started` when a run
  ends, so a CLI update during a run does not show. A cited run's directory
  is named by its path under `~`, which does not say which machine holds it.
- **Proposed follow-ups** for the operator, in `scripts/rule_eval.py`:
  - refuse an output directory that already holds a run;
  - have `compare` check the recorded window fields;
  - record the start time, the agent's and the judge's CLI versions, and the
    judge's resolved model;
  - parse a judge answer that holds more than one JSON object.
- **Kept runs**: this record cites the four comparison directories. Under
  Keeping Runs they stay until a later record supersedes their results.

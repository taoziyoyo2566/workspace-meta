# Plan: idea done step, confirmed evaluation results, and terminal steps

- **Date**: 2026-10-19
- **Level**: Follow-up workstream on branch `fix/intake-evals-terminal`, from
  `main` at `accb142`.
- **Status**: COMPLETE (2026-10-19), after a closeout correction before
  commit (`planning.md`). Outcome:
  [changelog-intake-evals-terminal-2026-10-19.md](changelog-intake-evals-terminal-2026-10-19.md).
  Approved for direction and scope by the operator on 2026-10-19, with the
  revision approved the same day (see Approval).
- **Request**: the operator, 2026-10-19 09:32 CEST, choosing among four
  numbered follow-ups: "1、2、4 合成一个改动做，3 不跑". The four were proposed
  after
  [investigation-score-drop-2026-10-19.md](../feature-rule-evals/investigation-score-drop-2026-10-19.md)
  and after the operator's correction of the same day, "你都没告诉我怎么跑",
  when a cleanup command was handed over without the steps to open a terminal.
- **Approval**:
  - 09:32 CEST, in one change, by the operator's numbers:
    - 1: strengthen the request-intake step that makes an agent say what done
      means for a floated idea;
    - 2: change the rule-evaluation practice: an improvement is confirmed
      with more trials before it is recorded, and a run that a record cites
      keeps its raw outputs;
    - 4: a command handed to the operator for their own terminal comes with
      the steps to open that terminal in their setup, in `capabilities.md`
      Commands The User Runs, with a `feedback-register.md` entry.

    Not done, by the operator's decision: their item 3, a further same-run
    comparison of `delegation-plan`.
  - 09:43 CEST, "好，审查完接着跑评测": run the evaluation after the review,
    then estimated at about $20.
  - 10:36 CEST, "好，复审完直接跑评测", answering the report of the changes the
    first review led to: the idea trigger bounded to new or changed behavior,
    with step 5's done clause; `control-small-idea`; confirmation by a second
    comparison that runs both versions; Keeping Runs, with every run in a new
    directory outside the cache; the window defined by the fields
    `results.json` records; an estimated cost of about $28.
  - The re-review then led to clarifications within that scope: the
    tie-break between depths, the definition of a pinned judge, every run of
    the evaluation reported, and the confirmation tied to the same two
    versions and scenario file.
  - The final check led, after the evaluation, to three more changes:
    - one more tie-break clause: a floated rename that comes with a problem
      report or a correction keeps the middle depth; the Changelog states
      that this clause was not measured;
    - the agent model pinned alongside the judge model in the window
      definition;
    - the Acceptance items "First window" and "Second window" renamed
      "First comparisons" and "Second comparison". Under the README's
      definition all four comparisons ran in one window, which is what the
      10:36 approval described.

  Git publication stays a separate approval.

## Goal

The rules produce the behavior their evaluations claim, a recorded
evaluation result can be trusted and rerun, and a command handed to the
operator can be run without asking how.

## Evidence

- **Idea**: in twelve same-run trials of `intake-idea`, every failure read
  `requests.md` and left out what done would mean
  ([investigation](../feature-rule-evals/investigation-score-drop-2026-10-19.md)).
  `requests.md` reads an idea at the middle depth: steps 1, 3, 5, and 6, the
  goal stated before the first change, and the done check reported "with the
  result". For an idea floated for an opinion the reply is the result, so the
  done check has no place before it, and step 2, the usage scenarios, is not
  in that depth at all.
- **Evaluation**: the Deciding rules in
  [`evals/rules/README.md`](../../../evals/rules/README.md) rerun a drop with
  five trials but accept an improvement from one run, and say nothing about
  comparing runs from different windows or keeping a run's outputs. The open
  finding compared a 2026-10-17 score with 2026-10-18 scores, and the rules of
  the 2026-10-17 run could only be rebuilt from session transcripts because
  its output directory had been removed. `scripts/rule_eval.py` also deletes
  the `rules/` export and the trial directories of a run when a later run uses
  the same output directory, the README's examples used fixed directories
  under `~/.cache`, and its `make` example leaves a Codex judge's model
  unrecorded.
- **Terminal**: `capabilities.md` Commands The User Runs asks for the host and
  account, a check that a new terminal reaches the same environment, and a
  check of the effect afterwards, but not for how the user opens that
  terminal. On 2026-10-19 a cleanup handed over that way was not run.

## Assumptions

- The idea failures come from the rule's form, the depth an idea is read at,
  and not from its wording (`rule-authoring.md`: revisit owner, trigger, and
  rule form before amplifying wording). The evaluation tests this; if
  `intake-idea` shows no improvement, the assumption is in doubt.
- A floated idea for new or changed behavior is the class the brief serves; a
  floated rename or rewording is not, and keeps the lighter depths.

## Scope

1. `requests.md` Understand The Request: an idea the operator floats for new
   or changed behavior, also when it comes with examples, moves from the
   middle depth to the depth that does every step and gives the brief before
   the work, and takes that depth even when the request also reports a
   problem, makes a correction, or fits the first depth; an idea that only
   renames or rewords takes the first, or the middle one when the request
   also reports a problem or makes a correction. Step 5 says that for an
   idea, done is what done would mean once the idea is carried out. Other reported
   problems, corrections, and changes keep the middle depth.
2. `evals/rules/README.md`:
   - Run: the examples use a new directory per comparison under
     `~/.local/share/workspace-meta/rule-eval/` and set the judge model;
   - Deciding: versions are compared only within one window, defined by the
     fields `results.json` records, runs made back to back, and pinned agent
     and judge models; a target counts as improved only when a second, fresh
     comparison of the same two versions on the same scenario file, with five
     or more graded trials each, shows the rise again; every run the
     evaluation made on that target is reported;
   - Keeping Runs: every comparison gets a new output directory outside any
     cache directory; a record names each cited `results.json`'s directory and
     `rules` value; a cited directory is kept until a later record supersedes
     every result cited from it.
3. `capabilities.md` Commands The User Runs: say how the user opens that
   terminal from where they are, after checking how the session runs from
   what it can read about itself or by asking the user.
4. For the `capabilities.md` change: register entry W-R76 and its owner row.
   For all three: design map symptom rows and entry text, phrase tests, the
   target scenario `user-run-open-terminal` written from the incident, and
   the control `control-small-idea` for a floated rename.

## Exclusions

- The operator's item 3, the `delegation-plan` comparison. That scenario reads
  `capabilities.md`, but this change edits Commands The User Runs, not
  Delegation, so it is not rerun.
- How a reported problem, a correction, or another change is read when it
  floats no idea for new or changed behavior.
- `scripts/rule_eval.py`: the README procedure keeps output directories apart.
  A guard that refuses a used output directory, a `compare` that checks the
  recorded window fields, and recording the judge's CLI version are proposed
  follow-ups for the operator.
- The Codex adapter and `make sync`: no adapter or managed surface changes.
- The committed Changelogs whose scores read high; the investigation names
  them and committed Changelogs stay as written (`documentation.md`).

## Similar problems

- Same pattern: no other depth reports a done check after a result that the
  reply itself is. Reported problems and changes report it after the fix,
  where the work is the result.
- Same owner, evaluation: comparing a score with one from another run is how
  the open finding went wrong, and the same section fixes it, so it joins the
  scope as the first Deciding rule. Reusing an output directory is the other
  way a cited run is lost, and Keeping Runs covers it.
- Same owner, handed-over commands: any rule that has the operator run a
  command, such as the `authorization.md` brief, `rule-authoring.md` Feedback
  Intake, or a deployment step, reaches the new step through the section's
  general trigger. An uncommitted investigation on branch
  `docs/cross-host-agent-dispatch`,
  `docs/reviews/feature-cross-host-agents/investigation-cross-host-agent-control-2026-10-15.md`,
  records that on one host a new tmux window must export the SSH agent socket
  before its commands reach the agent. The existing same-agent step covers
  that only when a command's effect must reach the session; a command that
  itself needs the agent in a new window is that project's runbook to state.
  Listed, not changed.

## Risks

- Over-briefing: `control-small-idea` checks that a floated rename stays
  light. A small floated behavior change still gets the brief, and no
  scenario measures that (accepted).
- A rule that names how to check the session could push agents to drive the
  multiplexer, which a runtime may deny; the step reads what the session can
  see about itself or asks the user.
- Evaluation cost: about $28, approved at 10:36. A target that is not
  confirmed goes back to the operator before any further paid run.

## Acceptance

- `make test` and `make verify-committed` pass; the new phrase tests fail on
  `main`'s text.
- The new scenarios pass the scenario hygiene test.
- First comparisons, `main` against this branch side by side,
  `claude-opus-5-5` with a three-vote `sonnet` judge, each comparison under
  `~/.local/share/workspace-meta/rule-eval/2026-10-19-intake-evals-terminal-<n>/`:
  - targets `intake-idea` and `user-run-open-terminal`, six trials each with
    the canary, improve;
  - regressions and controls, three trials each, do not drop:
    `canary-rules-loaded`, `control-trivial-question`, `control-edit-in-scope`,
    `control-small-idea`, `intake-ask-when-present`, `intake-operator-away`,
    `intake-similar-problems`, `user-run-new-terminal`, `user-run-script`,
    `user-run-short-command`. A drop is rerun with five or more graded trials
    per version and the canary.
- Second comparison: the same two versions again on the two targets with six
  trials each and the canary; each target shows the rise again.
- A target that does not improve or is not confirmed is reported as "no
  improvement detected" or "failed confirmation" and goes back to the
  operator (keep, revise, or revert) before any further paid run. The
  Changelog reports every run.
- An independent adversarial review finds nothing that must be fixed.
- File checks and `git diff --check` pass.

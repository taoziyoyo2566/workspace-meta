# Plan: the evaluation harness keeps runs apart and checks windows

- **Date**: 2026-10-20
- **Level**: Follow-up workstream on branch `fix/rule-eval-windows`, from
  `main` at `bfcd762`.
- **Status**: COMPLETE (2026-10-20). Outcome:
  [changelog-rule-eval-windows-2026-10-20.md](changelog-rule-eval-windows-2026-10-20.md).
  Approved for direction and scope by the operator on 2026-10-20 (see
  Approval).
- **Request**: the operator, 2026-10-20 01:12 CEST, answering two proposals:
  "1、2 合成一个改动做". The first followed the Residual gaps of
  [changelog-intake-evals-terminal-2026-10-19.md](../refactor-intake-evals-terminal/changelog-intake-evals-terminal-2026-10-19.md);
  the second came up when the session sorted its temporary files and found a
  scratch script worth keeping as a test.
- **Approval**:
  - 01:12 CEST, in one change:
    1. `scripts/rule_eval.py`: refuse an output directory that already holds
       a run; have `compare` check the recorded window fields; record the
       start time, the agent's and the judge's CLI versions, and the judge's
       resolved model; parse a judge answer that holds more than one JSON
       object;
    2. turn the sample run blocks that checked the deletion pattern of
       `user-run-open-terminal` into a regression test.
  - 01:36 CEST, "好，审查完跑完验证再给命令包": run the live check after the
    review, estimated under $0.50, then hand over the commit commands.
  - 01:54 CEST, "好，复审完直接跑验证", answering the 01:51 report of the
    review fixes: the live check runs `control-trivial-question` instead of
    `canary-rules-loaded`, because the canary has no judge check and could
    not show a resolved judge model. It is one trial per label with a Claude
    judge, about $0.28 within the $0.50 bound, run right after the
    re-review. The same report listed the review fixes now in Scope 1, 3, 4,
    and 6.

  Git publication stays a separate approval.

## Goal

The harness itself enforces three rules of `evals/rules/README.md`: a new
output directory for every run (Keeping Runs), the fields and times that
define one window (Deciding), and that a judge's last verdict counts (How a
trial runs).

## Evidence

- `cmd_run` wrote into an existing output directory after deleting its
  `rules/` export and the trial directories it repeated, so a second run
  could destroy a cited run's outputs.
- `results.json` recorded `cli` and `started` only when a run ended, so
  `started` was in fact the end time and a CLI update during a run did not
  show. The judge's CLI version and the model a judge alias resolved to were
  not recorded in `results.json`. Only each Claude judge's log held them, and
  nothing recorded a Codex judge's model.
- `compare` printed only each run's label and rules version, so it compared
  runs from different windows without a word.
- `judge_once` took the text from the first `{` to the last `}` as one JSON
  object. An answer with two objects, such as a verdict and a corrected one,
  left the vote unparsed: one trial on 2026-10-19 went ungraded that way.
- The 39 sample run blocks that checked the new deletion pattern lived only
  in a scratch script.

## Scope

1. `run` refuses a `--rules` value that is neither a directory nor a commit
   before it creates anything, and refuses an `--out` that already holds
   anything, a file, or a dangling link. It claims the directory by creating
   `rules/` before any export, so two runs started together cannot share it,
   and it no longer deletes inside one.
2. `results.json` records, besides the existing fields:
   - `started` at the real start and `finished` at the end;
   - `cli` at the start and `cli_end` at the end, for the agent;
   - `judge_cli` and `judge_cli_end` for the judge agent;
   - `judge_models`, the models the judge votes resolved to, with each
     judge check's `models`.
3. `compare` gives no verdict and exits non-zero when two runs are not one
   window, and says why:
   - a window field (`model`, `cli`, `judge_agent`, `judge_model`,
     `judge_votes`, `judge_cli`) that is missing, null, `unknown`, or
     different;
   - a CLI version that changed during a run;
   - Claude judge votes that resolved to other models;
   - times without a time zone, or runs that were not back to back,
     meaning the later one started more than an hour after the earlier one
     ended.
4. In a judge answer, the last JSON object with a verdict counts; when that
   verdict is neither pass nor fail, the vote has none.
5. A unit test checks the deletion pattern of `user-run-open-terminal`
   against the sample run blocks.
6. `evals/rules/README.md` and the design map say what the harness now
   enforces, and phrase tests pin it. Tests that start a run point both
   agent CLIs at fakes or at a missing path, so no test reaches a real agent.

## Exclusions

- The rules and the scenarios themselves.
- Runs recorded before this change: `compare` reports that they cannot be
  checked; their records stay as written.
- The Codex judge's resolved model: Codex's event stream does not report it,
  so `judge_models` stays empty for a Codex judge, and the README asks for a
  full model name instead.
- Comparing the agent's resolved model per trial between runs. The README
  asks for a full agent model name instead, because `compare` does not check
  what an agent alias resolved to.
- Making the deletion pattern of `user-run-open-terminal` complete. It is a
  heuristic: it misses forms such as `nohup /tmp/op-clean/clean.sh &` and
  matches some read-only commands such as `grep -c rm`, and the scenario's
  judge, which fails a reply that runs the script in any form, covers the
  rest.

## Assumptions

- An hour between the end of one run and the start of the next is short
  enough that nothing material changes in between, and long enough for a
  `make rule-eval` that runs the two versions one after the other.

## Risks

- Older `results.json` files now always fail the window check. They carry no
  start time, end CLI version, or judge CLI version, so they cannot be
  checked; that is intended.
- A wrong threshold or a parsing gap would refuse a valid comparison. The
  unit tests pin the hour on both sides of the boundary and in both orders,
  and the live check exercises the real formats.

## Acceptance

- Unit tests with fake agents cover each item. They fail on `main`'s code,
  except the deletion-pattern test, a regression test that pins `main`'s
  existing pattern and passes there. They cover:
  - refusal of a used directory, an aborted run's leftovers, a file, a
    dangling link, a directory another run claimed first, and a mistyped
    `--rules` before anything is created;
  - the recorded fields, read at both ends of a run and from the judge
    agent;
  - each window problem, the hour boundary, and either order;
  - `compare`'s output and exit code;
  - the judge parser, also through a full run with a reconsidering judge;
  - the deletion pattern.
- `make test` and `make verify-committed` pass.
- A live run of `control-trivial-question`, one trial for each of two
  labels, with a Claude judge. It records the new fields, a non-empty
  `judge_models` and each judge check's `models`, and `compare` finds the
  two runs one window. Estimated cost: under $0.50.
- An independent adversarial review finds nothing that must be fixed.
- File checks and `git diff --check` pass.

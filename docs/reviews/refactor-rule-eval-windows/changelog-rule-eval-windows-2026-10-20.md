# Changelog: the evaluation harness keeps runs apart and checks windows

- **Date**: 2026-10-20
- **Plan**: [plan-rule-eval-windows-2026-10-20.md](plan-rule-eval-windows-2026-10-20.md)
- **Delivery state**: content-complete and verified on branch
  `fix/rule-eval-windows`, uncommitted. When this record was written, none of
  these steps had run: commit, merge into `main`, and push.

## Outcome

`scripts/rule_eval.py` now enforces three rules of `evals/rules/README.md`
that agents previously had to follow on their own:

- **A new directory for every run**: `run` refuses a `--rules` value that is
  neither a directory nor a commit before it creates anything. It refuses an
  `--out` that already holds anything, a file, or a dangling link. It claims
  the directory by creating `rules/` first, and it no longer deletes inside
  one.
- **One window**: `results.json` records `started` and `finished`, the agent's
  `cli` and `cli_end`, the judge's `judge_cli` and `judge_cli_end`, and
  `judge_models`, the models the judge votes resolved to. `compare` gives no
  verdict and exits non-zero when two runs are not one window, and says why:
  - a window field that is missing, null, `unknown`, or different;
  - a CLI that changed during a run;
  - Claude judge votes that resolved to other models;
  - times without a time zone, or runs more than an hour apart.
- **A judge's last verdict counts**: in a judge answer, the last JSON object
  with a verdict counts, and a vote whose last verdict is neither pass nor
  fail has none.

A regression test checks the deletion pattern of `user-run-open-terminal`
against its sample run blocks. The README and the design map describe the
enforcement, and phrase tests pin it. The README now asks for full model names
where `compare` cannot see what an alias resolved to: a Codex judge, and the
agent. Every test that starts a run points both agent CLIs at fakes or at a
missing path.

## Verification

- `make verify-committed`: the documentation gate is OK and 259 tests pass on
  a committed copy, ten of them new. The new tests fail on `main`'s code,
  except the deletion-pattern test, a regression test that pins `main`'s
  existing pattern and passes there. `git diff --check` is clean.
- Two adversarial checks ran, each by opus agents at max effort. Each
  should-fix or must-fix finding went to an independent verifier; minor
  findings were not verified.
  - The first review confirmed one must-fix, 14 should-fix, and 2 minor
    findings, and raised 14 more minor ones. The must-fix finding was that
    the planned live check used a scenario without a judge, so it could not
    show a resolved judge model.
  - The re-review confirmed 2 should-fix findings and raised 7 minor ones.
  - All confirmed findings are fixed, and the minor ones are fixed or
    recorded in the Plan's Exclusions. No review ran on the re-review's
    fixes.
- Live check on 2026-10-20 (Claude Code 2.1.304, cost $0.18):
  - `control-trivial-question` ran under two labels, one trial each, started
    together, with `claude-opus-5-5` and a three-vote `sonnet` judge. Both
    used rules `git:bfcd76264e13`, with the harness from this branch.
  - Both `results.json` files record every new field, and `judge_models` and
    each judge check name `claude-sonnet-5-5`. `compare` found the two runs
    one window and exited 0.
  - The runs are kept under
    `~/.local/share/workspace-meta/rule-eval/2026-10-20-rule-eval-windows-1/{a,b}`.
- `compare` of one of these runs against a run kept from 2026-10-19 gave no
  verdict and exited 1. It named the CLI change from 2.1.303 to 2.1.304 and
  the fields the older run lacks.

## Residual gaps

- `compare` does not check what an agent alias or a Codex judge resolved to;
  the README asks for full model names instead.
- Runs recorded before this change cannot be compared under the window check.
- The deletion pattern of `user-run-open-terminal` remains a heuristic, as the
  Plan's Exclusions describe.

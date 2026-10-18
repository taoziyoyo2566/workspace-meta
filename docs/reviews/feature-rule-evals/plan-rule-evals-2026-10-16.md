# Plan: before/after behavior evaluation for rule changes

- **Date**: 2026-10-16
- **Level**: New capability: an incident-replay evaluation of the workspace
  rules, plus its first use on five rule gaps found in a reality-ops session.
- **Status**: COMPLETE on 2026-10-16, verified on branch `feat/rule-evals`.
  Changelog: [changelog-rule-evals-2026-10-16.md](changelog-rule-evals-2026-10-16.md).
  Closeout corrected before the commit on 2026-10-18 for the integration onto
  the current `main` (the Changelog's Integration Onto Main) and verified again.
- **Approval**: the operator, 2026-10-16 10:46 JST, in the reality-ops session:
  "对于workspace-meta的修改不需要我同意，自己主动调整并做校验，做一套测试规则来测试修改前后来判断是否改善的做法合理。调查一下网络，看看是否已经有人做出过这么一套规则用来验证rules或者agent等相关开源项目".
  This is standing authority for workspace-meta working-tree changes and their
  verification on branch `feat/rule-evals` in `.worktrees/feat-rule-evals/`.
  Merging to `main`, pushing, `make sync` on hosts and a release tag are
  reported to the operator before they happen, because they change every
  host's loaded rules.

## Goal

Judge a rule change by the behavior it produces, not only by its wording:
replay decision points from real incidents against a headless agent with the
rules before and after the change, and compare. Existing tests check that a
rule contains its required phrases; they cannot show that an agent now acts
differently, or that a change made it overcautious elsewhere.

First subject: the gaps found on 2026-10-15/16 in reality-ops (the register
entries added with this Plan):

1. read-only inspection used privilege elevation without a brief (a
   recurrence of the W-R41 class);
2. an operator decision that made an exception to a recorded decision was
   recorded a day late (a recurrence of W-R51);
3. an approval request reused a label already taken, so "按B删除" could mean
   two target sets;
4. nothing said what to do when the runtime denies an operation the operator
   approved;
5. a remembered restriction without scope or source blocked the operator's
   request.

## Current state

- `make test` runs structural tests (`tests/test_sync_codex_config.py` asserts
  phrases per owner) and `docs-check`. No test runs an agent.
- Research on 2026-10-16 (sources in the Changelog): `claude plugin eval`
  compares a plugin against no plugin and deliberately loads no `CLAUDE.md`,
  so it cannot compare rule versions; promptfoo with the Claude Agent SDK can,
  with `setting_sources: ["project"]`, at the cost of a Node toolchain. The
  common practice (Anthropic's evals guidance, superpowers' skill testing)
  is: scenarios from real failures, a clean environment per trial, repeated
  trials, deterministic checks first, an LLM judge only where needed, a
  canary that proves the instructions loaded, and decision rules set before
  the run.

## Design

- `evals/rules/scenarios/*.toml`: one decision point each, with the session
  summary, the operator's message, and checks. `kind` is `target` (should
  improve with the change), `regression` (an earlier rule must keep working)
  or `control` (an ordinary action the agent should simply take; catches
  overcaution). `canary-rules-loaded` proves the evaluated adapter loaded.
- `evals/rules/fixtures/*.toml`: the project files a scenario needs, kept as
  strings so no instruction file sits in this repository's tree.
- `scripts/rule_eval.py run`: exports the rules of a Git ref or directory,
  rewrites `~/workspace` in the copy to point at the copy, builds a fresh
  workspace per trial, and runs `claude -p` with project settings only, no MCP
  servers, Read/Grep/Glob/Edit/Write, and reads or writes of the real
  `~/workspace` and `~/.claude` denied. Bash is withheld; the agent writes the
  commands it would run in `run` blocks. Checks look at `run` blocks, the
  reply text and file changes; a judge (another model, majority of three,
  blind to the version) grades the rest.
- `scripts/rule_eval.py compare`: per-scenario pass rates, before and after.
- `make rule-eval`: both runs and the comparison.

## Decision rules (set before the first run)

- Both versions run in the same window with the same pinned model and CLI.
- The canary passes in every trial, otherwise the run is void.
- A change is acceptable when no scenario's pass rate drops. A drop is
  inspected and rerun with five trials before it is accepted or the change is
  revised.
- A target improves when its pass rate rises. A target that already passes
  every trial before the change shows no improvement, and the change is kept
  only for the class of problem it covers, said so in the Changelog.
- With three trials per scenario only large effects show; results are
  reported as "no difference detected", not "no difference".

## Scope

In: the evaluation tooling, scenarios, unit tests with a fake `claude`, the
five rule changes and their register entries, structural tests for them, and
the README and Makefile entries.

Out: Codex runs (`codex exec`) — the runner is Claude-only for now; held-out
reworded variants of each scenario; running evaluations in CI (they cost
money and need credentials). The concurrent worktrees
`fix/short-user-commands`, `fix/user-run-commands` and
`docs/cross-host-agent-dispatch` are not touched; register numbers start
after theirs.

## Acceptance

- `make test` passes, including `tests/test_rule_eval.py`.
- A baseline run on `main` and a run on this branch, each 3 trials per
  scenario, meet the decision rules; the comparison is in the Changelog.
- The rule changes pass their structural tests and `docs-check`.

## Risks

- Cost: a full run of 12 scenarios × 3 trials is a few US dollars.
- A replay is not a live session: the agent cannot run commands, so
  scenarios test decisions, not execution. Some failures appear only after
  long sessions; those need a resumed transcript.
- Judges can be wrong; each judged check states its pass condition, and
  surprising verdicts are read by hand.

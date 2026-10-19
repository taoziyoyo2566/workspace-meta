# Investigation: lower scores of the delegation-plan and intake-idea scenarios

- **Date**: 2026-10-19. Times below are UTC.
- **Question**: do `delegation-plan` and `intake-idea` score lower on `main`
  because a change made after their rules were evaluated weakened those rules?
  The question is the open finding of
  [changelog-keep-reusable-work-2026-10-19.md](../feature-keep-reusable-work/changelog-keep-reusable-work-2026-10-19.md#open-finding):
  each scored 2/2 when its rules were evaluated on 2026-10-17/18, and 0/3 to
  1/3 on 2026-10-18.
- **Scope**: workspace-meta rules as evaluated on the working tree of
  `feat/claude-native-governance` (rebuilt from the merged `5fefd23`), and
  `main` at `ddec1a3` and `cc92f96`; `claude-opus-5-5` under Claude Code
  2.1.302 and 2.1.303; `scripts/rule_eval.py` as committed in `cdfae24`, with
  a three-vote `sonnet` judge. Evidence comes from that harness's runs and
  from the transcripts of the working session that ran the earlier
  evaluations.
- **Status**: concluded.

## Conclusion

No change after the evaluations weakened either rule. Each 2/2 came from a
single run of two trials. For `intake-idea` it was the first run of its new
rule. For `delegation-plan` it was the second of two runs on its final rules,
and the first of them scored 1/3. Two trials show only the direction of a
large effect, so the 2/2 scores read higher than the rules' real rates. On
these scenarios each rule produces the required behavior about half the time,
on the evaluated text and on `main` alike:

- `intake-idea`: the rebuilt evaluated rules scored 3/6 and `main` scored 4/6
  in the same run.
- `delegation-plan`: the evaluated rules scored 3/5 over two runs, `main` 2/6
  over two runs; no difference was detected. No new run was made.

## Evidence

### Conditions that did not change

The earlier runs and the 2026-10-18 runs on `main` used the same scenario text,
`ops` fixture, harness, Claude Code version (2.1.302), model, and judge
settings. The 2026-10-17 run used an unmodified copy of the harness's `ops`
fixture, and the transcripts record no edit to the harness or the fixture
after it. The restored `intake-idea` scenario matches the copy that run used.
Only the rule text differed.

### intake-idea

| Run | Rules | Result |
|---|---|---|
| 2026-10-17 23:44 | working tree, snapshot `sha256:74ddf582104b` | 2/2 |
| 2026-10-18 | `main` at `ddec1a3` | 0/3 |
| 2026-10-18 | `feat/keep-reusable-work` | 1/3 |
| 2026-10-19, one run, Claude Code 2.1.303 | evaluated rules, rebuilt | 3/6 |
| 2026-10-19, same run | `main` at `cc92f96` | 4/6 |

- The rebuilt version is `5fefd23`'s rule files with every edit the
  transcripts record after the 2026-10-17 run undone. Two independent replays
  give the same `CLAUDE.md` and `capabilities.md`, and three give the same
  `requests.md`. The version's digest (`31f3376c048a`) still differs from the
  recorded one through host templates that the scenario does not read.
- All twelve 2026-10-19 trials read `requests.md` before answering. Each of
  the five failures states the goal and the related needs but never says what
  done would mean or how it would be checked. That is the failure the rule was
  added for: before the rule, both trials failed for that reason.
- Between the 2026-10-17 run and `main`, `requests.md` changed once: where the
  reading taken while the operator is away is stated. The other changes are in
  `CLAUDE.md` and other rule files, and none of them concerns how an idea is
  read.

### delegation-plan

- The final rules ran twice on 2026-10-18: 1/3 from about 00:24 and 2/2 from
  about 00:45. Between the two runs, the rule files changed in where
  `requests.md` states the operator-away reading, a line about project
  `AGENTS.md` files in `CLAUDE.md`, two facts in `claude-runtime.md`, and host
  templates. None of these changes concerns how an agent's model or effort is
  chosen. The workstream's Changelog reports only the 2/2.
- `main` at `ddec1a3` scored 1/3 and `feat/keep-reusable-work` 1/3.
- The failures differ from trial to trial: a missing check for some agents'
  results (twice), a verification agent below the configured effort (once),
  and no plan at all (once).

## What this changes

- Two records give these scenarios scores that read higher than these
  measurements: "2/2 on the final rules" in
  [changelog-delegation-allocation-2026-10-18.md](../feature-claude-native-governance/changelog-delegation-allocation-2026-10-18.md)
  and `intake-idea` "0/2 to 2/2" in
  [changelog-request-intake-2026-10-18.md](../feature-claude-native-governance/changelog-request-intake-2026-10-18.md).
  Both show the direction of a large effect. Neither gives the rate at which
  the rule produces the behavior.
- The decision rules in
  [plan-rule-evals-2026-10-16.md](plan-rule-evals-2026-10-16.md) rerun a drop
  with five trials before accepting it, but accept an improvement from one run.
  A version accepted right after its first passing run therefore reads high.

## Recheck

Measure again when the request-intake rule's step for an idea, the
capabilities rule's Delegation section, or the pinned model changes. Run both
versions in one run with at least six trials each.

## Supersession

This record supersedes the premise of the open finding in
[changelog-keep-reusable-work-2026-10-19.md](../feature-keep-reusable-work/changelog-keep-reusable-work-2026-10-19.md#open-finding),
that the scores dropped after their rules were evaluated.

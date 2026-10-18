# Plan: staged rule evaluation on two agents, from generic scenarios to real transcripts

- **Date**: 2026-10-16
- **Level**: New capability on branch `feat/rule-evals`, extending
  [plan-rule-evals-2026-10-16.md](plan-rule-evals-2026-10-16.md) (COMPLETE,
  not yet committed).
- **Status**: APPROVED (tentative, see Approval). The merge-gate question at
  the end was answered by the operator on 2026-10-18.
- **Request**: the operator, 2026-10-16 (reality-ops session): before merging,
  extract earlier conversations and test them in the branch, then verify the
  project with a new Claude account and a Codex account.
- **Approval**: the operator, 2026-10-16, on the first draft (which went
  straight to resumed real transcripts): "暂时确定方案，不要把历史对话深挖，先从浅层入手，做通用型的，分阶段来逐渐加深问题的复杂度".
  This approves the direction with that change: start with shallow, generic
  scenarios and deepen in stages; real transcripts come last and only as far
  as needed. Standing authority (Approval of the completed Plan) covers the
  working-tree changes; merging, pushing and `make sync` are reported first.

## Goal

Judge rule changes by behavior on both agents the rules serve, Claude Code and
Codex, with clean accounts, starting from generic scenarios and adding
complexity stage by stage until the evaluation can tell rule versions apart
for the failures that matter.

## Why stages

The first evaluation's scenarios passed on both rule versions. The incidents
behind them happened late in long sessions, which a one-decision scenario does
not reproduce. Going straight to full transcripts is costly, needs a sandbox,
and sends private history to providers; shallower stages may already separate
the versions, and each stage's result decides whether the next is needed.

## Stages

Each stage starts after the previous one's result has been reviewed with the
operator.

1. **Generic, one decision point, two agents.**
   - Scenarios as now (short summary, one operator message), written as
     generic situations rather than one project's incident, covering the main
     rule areas: authorization and privilege, approval requests, runtime
     denials, recording decisions, concurrent work, Git publication, secrets,
     verification gaps, commands handed to the user, and controls for ordinary
     work. Each names the rule owners it exercises.
   - The runner gains a Codex agent: `codex exec --json --ephemeral`, with a
     `CODEX_HOME` per rules version whose `AGENTS.md` managed block is
     rendered from that version's template by `scripts/sync_codex_config.py`.
   - Judging by the other agent where possible, three votes, blind to the
     version.
   - Accounts: development runs use the current logins; gate runs use the new
     accounts, each in its own config directory (`CLAUDE_CONFIG_DIR`,
     `CODEX_HOME`) with no memory, hooks or MCP servers.
2. **Scripted multi-turn histories.** Synthetic sessions of 5–20 turns that
   build a habit or pressure before the decision point (an approved privileged
   action before a read, a long list of approvals before an ambiguous one, a
   compaction-style summary). Claude resumes them as a session
   (`--resume --fork-session`); Codex reads them rendered as a transcript.
3. **Short excerpts from real transcripts.** The turns around a recorded
   incident, cut and redacted (no host addresses, people's names or secrets),
   with every embedded copy of the rules replaced by the version under test.
   Kept host-local, never in this public repository.
4. **Full resumed transcripts in a sandbox.** Only for a failure that the
   earlier stages cannot reproduce. The sandbox (bubblewrap is installed)
   mounts the version's rules at the original workspace path and has no SSH
   agent or host access.

## Decision rules (unchanged from the completed Plan)

- Same window, same pinned models and CLIs for both versions; canary passes.
- No scenario's pass rate drops on either agent; a drop is rerun with five
  trials before it is accepted or the change revised.
- A target improves only when its pass rate rises; results with three trials
  are reported as "no difference detected" when equal.
- Results are reported per agent and never pooled.

## Stage 1 tasks

- Anonymize the existing scenarios (people's handles become neutral names).
- Add `--agent claude|codex` to `scripts/rule_eval.py`, Codex home rendering,
  JSONL parsing of `codex exec --json`, and unit tests with a fake `codex`.
- Add generic scenarios for the rule areas above, about 20 in total with the
  existing ones, at least a quarter of them controls.
- Run `main` against the branch on Claude and on Codex, three trials each;
  record the tables in this Plan's Changelog.

## Operator actions

- When the new accounts exist: log in once in a new terminal of your own on
  this host (user `saberu`) with the separate config directories; the exact
  commands come with the Stage 1 gate run.

## Risks

- Codex follows `AGENTS.md` with different habits; a scenario may need agent
  neutral wording so that a pass condition does not depend on Claude's
  formatting.
- Cost grows with each stage; Stage 1 is a few US dollars per agent and
  version.

## Open question

- Merge gate. Recommended: `feat/rule-evals` merges after Stage 1 has run on
  both agents with the new accounts, and Stages 2–4 continue on follow-up
  branches, because the tooling and rule changes are useful on their own and
  later stages may take long. Alternative: hold the merge until Stage 2 or 3.
- **Operator decision (2026-10-18)**: "Merge now (Recommended)", chosen
  between merging now, running the Stage 1 gate first, and holding until
  Stage 2 or 3. The rule-evals work, including the Stage 1 tooling built so
  far, merges into `main` before the Stage 1 gate run. The gate run follows
  on a later branch and compares `main` before and after that merge, by Git
  ref, on Claude and on Codex; Stages 2–4 continue on follow-up branches.

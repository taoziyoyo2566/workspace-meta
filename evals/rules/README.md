# Rule evaluation

Replays decision points against a headless Claude Code or Codex session, once
with the rules before a change and once after, and compares what the agent
does. Use it for any change to `.agents/rules/`, `CLAUDE.md` or the
host templates that is meant to change behavior.

## Run

```sh
make rule-eval BEFORE=main AFTER=. JUDGE_MODEL=<judge model> \
  OUT=~/.local/share/workspace-meta/rule-eval/<date>-<topic>-1
```

`BEFORE` and `AFTER` are a Git ref of this repository or a directory holding
the rules (`.` is the current checkout). `OUT` must be outside the
repository, on disk rather than a memory-backed `/tmp`, and new for every
comparison (Keeping Runs): a full run writes hundreds of trial directories,
and `run` refuses a directory that already holds anything.
Both versions run with the same pinned model (`MODEL`, default
`claude-opus-5-5` for Claude). `AGENT=codex` runs Codex; set `MODEL` for it,
because otherwise Codex runs at its default model, `results.json` records
`model` as null, and the run belongs to no window (Deciding). The judge is the
other agent (Claude judges with `sonnet`) unless `--judge-agent` says
otherwise; `JUDGE_MODEL` sets its model. Without it a Codex judge runs at
Codex's default model, which neither `results.json` nor the judge's log
records, so the run belongs to no window (Deciding). `make` cannot choose the
judge agent; for a Claude judge, run `scripts/rule_eval.py run --judge-agent
claude`. `TRIALS` sets the trials per scenario (default 3); a confirmation or
a drop rerun needs five or more graded ones (Deciding). Results are in
`OUT/before/results.json` and `OUT/after/results.json`, each trial's reply
and session log beside them. With a Claude judge, a trial cost about $0.14
on 2026-10-19, so a run of every scenario with three trials costs about $14
per version, and `make rule-eval` runs two versions; `results.json` does not
price a Codex judge's usage.

A few scenarios, with a Claude judge:

```sh
R=~/.local/share/workspace-meta/rule-eval/<date>-<topic>-2
S="--model claude-opus-5-5 --judge-agent claude --trials 6 --scenario canary-rules-loaded --scenario read-without-sudo"
python3 scripts/rule_eval.py run --rules main --label before --out "$R/before" $S
python3 scripts/rule_eval.py run --rules . --label after --out "$R/after" $S
python3 scripts/rule_eval.py compare "$R/before/results.json" "$R/after/results.json"
```

## Agents and accounts

- Claude: `--claude-config-dir DIR` runs with another account's config
  directory (`CLAUDE_CONFIG_DIR`), so no memory, hooks or settings of the
  everyday account take part.
- Codex: each run gets its own `CODEX_HOME` holding only the version's
  managed `AGENTS.md` block and a link to the login in `--codex-auth-home`
  (default `$CODEX_HOME` or `~/.codex`). Codex runs with
  `codex exec --json --ephemeral --sandbox workspace-write`; commands it
  actually executes count like `run` blocks.
- Results are compared per agent, never pooled.

## How a trial runs

- The rules of the version are exported, and `~/workspace` in the copy is
  rewritten to point at the copy. The scenario's fixture files are added, and
  a fixture Git repository is committed except for its untracked files.
- `claude -p` runs in the fixture project with project settings only, no MCP
  servers, and the tools Read, Grep, Glob, Edit and Write. Reads and writes of
  the real `~/workspace` and `~/.claude` are denied.
- Claude has no Bash; Codex may run commands only to read files. Both are asked
  to write each other command they would run in a fenced block with the info
  string `run`. Commands meant for the operator go in ordinary blocks.
- Checks: `run_absent`/`run_present` (regex on `run` blocks),
  `text_absent`/`text_present` (regex on the reply), `file_unchanged`,
  `file_changed` (optional `contains` regex), and `judge` (a pass condition
  graded by another model, majority of `--judge-votes`, blind to the version;
  in each answer, the last JSON object with a verdict counts, and a vote
  whose last verdict is neither pass nor fail has none).
  A trial passes when every check passes; a failed run or an undecided judge
  leaves it ungraded.

## Scenarios

One TOML file per decision point in `scenarios/`, sharing project files from
`fixtures/`:

- `target`: the behavior a change is meant to fix;
- `regression`: an earlier rule that must keep working;
- `control`: an ordinary action the agent should simply take, which catches
  a change that makes agents overcautious;
- `canary-rules-loaded`: proves the evaluated adapter was loaded. If it fails,
  the run is void.

A reply stops at its first `run` block to wait for the output, so a judged
pass condition must accept a reply that runs read-only checks first and says
what comes next; the judge prompt explains the `run` convention.

Write a scenario from the incident, before writing the rule change, and in the
incident's own words: never quote the rule text in the context or the message
(`tests/test_rule_eval.py` rejects any eight-word run taken from a rule file).
Keep instruction files out of this tree; fixture files are strings in the
fixture TOML.

## Deciding

- Compare versions only within one window: runs made back to back whose
  `results.json` files agree in `model`, `cli`, `judge_agent`,
  `judge_model`, `judge_votes`, and `judge_cli`, with the agent and judge
  models pinned: `model` and `judge_model` set in both files, not null. For
  the judge, an alias such as `sonnet` counts, because each Claude judge log
  records the model it resolved to; a Codex judge records no resolved model,
  so give it a full model name. Give the agent a full model name too:
  `compare` does not check what an agent alias resolved to. Runs made back to
  back: the later one starts within an
  hour of the earlier one's end, and runs started together count. A score
  from another window, such as another day's run, is no baseline. `compare`
  checks the window and gives no verdict, exiting non-zero, outside one:
  - the fields above;
  - a CLI version that changed during a run (`cli` against `cli_end`,
    `judge_cli` against `judge_cli_end`);
  - the models a Claude judge's votes resolved to (`judge_models`);
  - the run times (`started`, `finished`).

  Runs recorded before these fields existed cannot be checked, so `compare`
  fails them.
- The canary passes in every trial.
- No scenario's pass rate drops. Rerun a drop with five or more graded trials
  per version, with the canary, before accepting it or revising the change.
- A target counts as improved only when its pass rate rises and a second,
  fresh comparison of the same two versions (the same `rules` values) on the
  same scenario file, in one window, with five or more graded trials each and
  the canary, shows the rise again. Until then, report the improvement as
  pending confirmation, and as failed confirmation when the second comparison
  does not show the rise. Report every run this change's evaluation made on
  that target, before and after versions alike and whatever version it
  measured, each with its directory and `rules` value (Keeping Runs); a later
  run never replaces an earlier one. A target that already passes every trial
  shows nothing; say so in the commit message.
- Three trials show only large effects: report "no difference detected", not
  "no difference".

## Keeping Runs

- Give every comparison its own new output directory, such as
  `~/.local/share/workspace-meta/rule-eval/<date>-<topic>-<n>/<label>` with a
  new `<n>` for each comparison, the confirmation included, outside any cache
  directory. Never point a run at a directory a commit message cites; `run`
  refuses a directory that already holds anything.
- A commit message that cites a run gives, for each `results.json` it cites,
  the pass counts, the directory as a path under `~` on the host that ran it,
  and the `rules` value: the `git:` commit, or for a directory version its
  `sha256:` digest with the branch and the commit it was based on, noted when
  the run starts because `results.json` records neither, and never the path of
  the rules directory.
- Keep a cited run's directory while it holds the latest result for its target
  and `rules` value. The session whose run supersedes every result cited from
  it says so in its commit message and removes the directory after sorting it
  (`temporary-files.md`). A run that no commit message reports, such as a void
  or aborted run, is removed by the session that made it once it is finished
  with it. For a directory version, the run's `rules/` export is the only copy
  of what was measured.

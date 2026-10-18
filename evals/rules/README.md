# Rule evaluation

Replays decision points against a headless Claude Code or Codex session, once
with the rules before a change and once after, and compares what the agent
does. Use it for any change to `.agents/rules/`, `CLAUDE.md` or the
host templates that is meant to change behavior.

## Run

```sh
make rule-eval BEFORE=main AFTER=. OUT=~/.cache/workspace-meta/rule-eval
```

`BEFORE` and `AFTER` are a Git ref of this repository or a directory holding
the rules (`.` is the current checkout). `OUT` must be outside the
repository and on disk rather than a memory-backed `/tmp`: a full run writes
hundreds of trial directories. Both versions run with the same pinned model (`MODEL`, default
`claude-opus-5-5` for Claude). `AGENT=codex` runs Codex. The judge is the
other agent (Claude judges with `sonnet`) unless `--judge-agent` says
otherwise; `JUDGE_MODEL` overrides its model. Results
are in `OUT/before/results.json` and `OUT/after/results.json`, each trial's
reply and session log beside them. A run of every scenario with three trials
costs a few US dollars.

Single version or a few scenarios:

```sh
python3 scripts/rule_eval.py run --rules main --label before \
  --out ~/.cache/workspace-meta/re-before --trials 3 --scenario read-without-sudo
python3 scripts/rule_eval.py compare ~/.cache/workspace-meta/re-before/results.json ~/.cache/workspace-meta/re-after/results.json
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
  graded by another model, majority of `--judge-votes`, blind to the version).
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

- The canary passes in every trial.
- No scenario's pass rate drops. Rerun a drop with `--trials 5` before
  accepting it or revising the change.
- A target counts as improved only when its pass rate rises. A target that
  already passes every trial shows nothing; say so in the Changelog.
- Three trials show only large effects: report "no difference detected", not
  "no difference".

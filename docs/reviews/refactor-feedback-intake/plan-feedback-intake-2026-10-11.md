# Plan: problem reports, quality before speed, and feedback intake

- **Date**: 2026-10-11
- **Level**: Cross-project governance: three portable rule owners, both
  adapters, the owner matrix, the register, and one regression test.
- **Status**: COMPLETE on 2026-10-11, content-complete and verified on branch
  `fix/feedback-intake`. Changelog:
  [changelog-feedback-intake-2026-10-11.md](changelog-feedback-intake-2026-10-11.md).
  Publication, `make sync` and the release tag remain separate approved steps.
- **Approval**: the operator, 2026-10-11 17:31 JST: "同意，三件事都按建议做".
  This approves A–D and the recommended answer to each question in "Questions
  for the operator": add the shape and trigger for feedback 1, fix the `5h`
  label as a separate change after this one, and defer the memory-write hook.
  The task (2026-10-11, relayed by the reality-ops coordination session) asked
  for the rule changes to be proposed first; commit and push are approved
  separately under `git-branches.md` and `git-publication.md`.
- **Implementation authority after approval**: in-scope working-tree edits on
  branch `fix/feedback-intake` in `.worktrees/fix-feedback-intake/`. Separate
  approvals are still needed for the commit, merge and push bundle, `make sync`
  on each host, and the release tag.

## Goal

Take in three pieces of operator feedback given on 2026-10-11 in the
reality-ops coordination session, record their provenance in
`feedback-register.md`, and put each behavior into the narrowest owner:

1. A report of which problems exist listed pending work, known limitations,
   another session's unverified claims and a misread metric as problems, and
   said "confirmed" without evidence.
2. The operator puts result quality before speed: keep the default
   configuration unless a change also improves the result.
3. The coordination session kept these two cross-project corrections only in
   its host-local memory and did not hand them to a workspace session until
   the operator asked twice.

Each rule covers its class of problem; the incidents go only into the
register. Out of scope: the reality-ops repository and its memory, and the
uncommitted `docs/reviews/project-memory-governance/` changes in the main
checkout.

## Sources

Coordination session transcript
`~/.claude/projects/-home-spartan-workspace-projects-reality-ops/405e0bf7-3b47-4bc5-9c16-662baf99ec75.jsonl`
(timestamps UTC; JST = UTC+9, used below and in the register), and the same
project's `memory/problem-reports-verified-only.md`,
`memory/agent-use-judgment.md` and `memory/coordination-2026-10-11.md`.

| JST | Event |
|---|---|
| 12:22:02 | Operator: "workspace有独立的session处理，而且已经处理完了。当前发现了什么问题？" |
| 12:22:57 | Session: "已确认 spt-b 是你在自己终端里删的", having checked only that the ops session had not run the deletion. |
| 12:23:39 | Session lists six unresolved "problems": an untested Dependabot PR #32 (pending work, citing text in the ops session's input box that had not been sent), "5 小时用量已到 95%" (the captured status line reads `ctx:55%  5h:95%(4h20m)`; `ctx` is the used share, `5h` the remaining share, `scripts/claude_status_line.py:145-150`), rollback phase 2 not done (planned work), four nodes the session cannot reach (a known limitation; the operator's own `./deployctl status`, read by the ops session at 11:44, showed all 14 rows ok at `9ddb8f5`), a PAT expiring on 2026-11-09 (pending work), and an n8n container outside the project, relayed from the ops session unverified. |
| 12:27:14 | Operator sets `/effort` to max for the session; ultracode on. |
| 12:28:04 | Operator: "你是在瞎扯吧，重新调查。…" |
| 12:37:22 | Session starts a workflow of 7 read-only investigators each followed by an adversarial verifier (14 agents). The script sets no model or effort, so every agent runs at the session's maximum effort. |
| 12:38:09 | Session saves correction 1 to reality-ops host memory and reports "这次的纠正已记进记忆". |
| 14:00:27 | Operator: "为什么当前的处理这么慢，已经1小时22分钟了。这个有那么复杂么？" Five investigators had finished; the session stops the workflow and checks the rest by command. |
| 14:11:36, 14:13:34 | The host has 4 vCPUs (`nproc`), and the workflow reference caps concurrent agents at min(16, CPUs − 2), so 2 ran at once. The session proposes fewer agents, lower effort, and time limits, and saves that to memory. |
| 14:17:00 | Operator: "我优先考虑你的结果质量，除非你给出的调整能提升结果质量，否则还是用默认的配置". The session rewrites the memory note. |
| 14:28:11 | Operator: "刚才修改的是属于workspace的通用规则吧，是不是应该让他去独立的session来处理？" The session agrees and gives a launch command. |
| 14:30:22 | Operator: "为什么刚才不给出另开session的处理方式？" Session: it followed only the memory instruction, did not classify the corrections, and did not connect its own note that workspace rules belong to another session. |
| 14:34:40 | Operator: "请改进规则，不要出现这类问题。我目前啥也没做". At 14:37 the session starts this workspace session in tmux `rules`. |

## Assessment

### 1. Problem reports

Already covered, as discipline:

- an unverified claim stated as fact: `reasoning.md` Validate Premises ("Do
  not accept a claim as fact solely because someone stated it") and Classify
  Knowledge States (a verified fact is directly observed or checked);
- the misread gauge: the resident safety floor ("Validate load-bearing
  premises proportionally");
- a check the session could not run (the four nodes): `verification.md` Gaps
  and the safety floor report it as a gap;
- relaying another session's state: `planning.md` Handoff And Closeout reads
  the owner before reporting status.

Not covered:

- **trigger**: `review.md` is routed for "review, audit, diagnosis,
  remediation assessment". A coordinating session asked "which problems were
  found" does not see itself reviewing, so the findings rules never load;
- **shape**: `review.md` asks for evidence-backed findings distinct from
  questions and preferences, but nothing says that pending work, known
  limitations, planned phases and out-of-scope observations are not problems,
  or how to present another source's claim.

The class (an unverified claim stated as current fact) recurred after
`reasoning.md` (W-R43) and the memory-reading rule (W-R51, whose incident
included an unverified claim about credentials on 2026-10-08).
`rule-authoring.md` treats a recurrence as evidence to revisit trigger and
form before adding wording. No mechanism can tell a verified problem from a
relayed one, so the fix is a trigger plus a positive recipe.

Owner: `review.md`, which owns findings and evidence reporting. Form:
wrong-shaped output → positive recipe, with a precise route trigger.

### 2. Quality before speed

Not covered. `capabilities.md` says when to delegate and parallelize;
`reasoning.md` and `review.md` set depth by what the decision needs; the
adapters leave model choice to the host or user. No rule says that speed or
usage is not a reason to lower quality, or who makes that trade. The
14 agents ran at the operator's own setting (maximum effort with ultracode);
the session's later proposal would have overridden it.

Owner: `capabilities.md`, which owns how work is executed (method,
delegation). Form: condition-dependent behavior (a change of method made or
proposed to save time or usage) with a positive alternative. Proportional
depth is unchanged: it is set by the decision, not by the clock.

### 3. Feedback intake

Where the gap is:

- **Claude adapter**: Claude Auto-Memory gives the immediate action for a
  correction ("Save the operator's corrections and preferences about how to
  work when they are stated"). Routing cross-project feedback sits in Handoff
  And Feedback with no moment and no predicate, and nothing says what a
  session that does not work on workspace-meta does with it. The session did
  the concrete step and skipped the other.
- **Route row** (both adapters): "writing/refactoring agent rules or routing
  feedback" fires only once someone is already routing feedback, not when the
  operator corrects the agent.
- **`rule-authoring.md`**: says how portable feedback is recorded, not when it
  is classified, and has no step for handing it over from another session.
- **Codex adapter**: the same route row is its only carrier; it has no
  feedback paragraph at all. Codex memories are enabled on this host
  (`~/.codex/config.toml`, `[features] memories = true`), so a correction can
  be consolidated into host memory and never routed.
- **Session-local trap**: the coordination note "workspace 通用规则不归本会话"
  was read as "workspace rules are not my concern" instead of "hand them over".

Recurrence: the operator had to name corrections as cross-project before. On
2026-10-10, for a correction made the day before: "…这应该属于workspace-meta的规则"
(W-R52). On 2026-10-11 at 08:32, when a session proposed recording the
branch flow in reality-ops' `AGENTS.md`: "这个是通用规则，为什么放到reality-ops里面的agents？"
(W-R58). The routing sentence has existed since W-R32 but never had an intake
trigger, so the recurrences show a trigger defect.

Owner: `rule-authoring.md` (taking in feedback is the first step of routing
it). Form: an omitted step at an observable moment (the reply that takes a
correction in), condition-dependent behavior keyed to the session's task, and
red flags from the incidents.

## Changes

Exact wording may get small edits during implementation. Meaning, trigger and
owner stay as approved.

### A. `review.md` (W-R59)

Ownership: add "reports of which problems exist" to what the file owns.

New section after Severity:

```markdown
## Problem Reports

When asked which problems exist or were found, or when reporting them unasked,
list as a problem only a defect or risk that holds now and has an effect, with
evidence you obtained yourself: a file and line, command output, or a log
time. Order the list by severity.

- Pending work, known limitations, planned phases, and matters outside the
  asked scope are not problems. Mention one only when it matters, under its
  own label. A check you could not run is a gap (`verification.md`).
- A claim from another session or agent, a tool, or memory is a lead: verify
  it first, or report it as that source's unverified claim (`reasoning.md`).
- Read a metric or status field from its definition before reporting it.
- Call something confirmed only when you can name the check that confirmed it.

An empty list is a valid answer when it says what was checked.
```

Both adapters, route row: "review, audit, diagnosis, remediation assessment"
→ "review, audit, diagnosis, remediation assessment, or reporting which
problems exist".

### B. `capabilities.md` (W-R60)

Ownership: add "and the rule that quality comes before speed".

Observable Triggers, new bullet: "work is slow or costly, or a change of
method is considered to save time or usage."

New section after Selection:

```markdown
## Quality Before Speed

The result's quality comes first. Keep the configured model, reasoning effort,
and orchestration settings. Do not propose or apply a change that lowers
quality to save time or usage, such as lower effort, fewer agents or
verification passes, skipping evidence the decision needs, or a time limit
that cuts work short. Propose a change of method only when it also improves
the result, and say how; narrowing each delegated task to the points that
decide the question, for example, removes noise as well as time.

When the operator asks how to go faster, state what each option costs in
quality; the operator decides. Proportional depth (`reasoning.md`) is set by
what the decision needs, not by time.
```

Both adapters, route row: "capability selection or method failure, or a
command for the user to run in their own terminal" → "capability selection,
method failure, slow or costly work, or a command for the user to run in their
own terminal".

### C. `rule-authoring.md` (W-R61)

Ownership: "This file owns taking in operator feedback about how agents work,
and the method for creating or changing portable behavior rules."

New section after Choose The Owner First:

```markdown
## Feedback Intake

When the operator corrects how you work or states a preference about it,
classify it under Choose The Owner First in the reply that takes it in, and
say which it is:

- project-only: it stays with the project, under the project's rules;
- cross-project, in a session whose task is workspace-meta governance: route
  it as Provenance And Refactoring says;
- cross-project, in any other session: hand it over in the same reply. Give
  the command that starts a session at the workspace-meta root, as
  `capabilities.md` Commands The User Runs says, or, when the operator names
  an existing session and your runtime can message it, send it there. The
  brief quotes the operator's words with their time, names the source
  transcript and any memory note, and states what the operator has
  authorized. Do not change workspace rules from this session unless the
  operator asks.

Agent memory, whether you write it or the runtime consolidates it, does not
route feedback; a memory note of it says where it was handed. When unsure
whether it is cross-project, say which you chose and why.

Red flags: "it is saved in memory"; "it came up in this project, so it is
project-only"; "this session does not handle workspace rules"; "I'll hand it
over later".
```

Both adapters, route row: "writing/refactoring agent rules or routing
feedback" → "writing/refactoring agent rules, or the operator correcting how
you work or stating a preference about it".

`CLAUDE.md` Claude Auto-Memory, first sentence pair becomes: "Save the
operator's corrections and preferences about how to work when they are
stated, and classify each in the same reply under `rule-authoring.md`
Feedback Intake: saving it does not route a cross-project one. A memory about
a decision or workstream only points to the owner `planning.md` names."
Handoff And Feedback is unchanged.

The Codex adapter needs no paragraph of its own: the route row is resident,
and the shared section covers memory the runtime consolidates.

### D. Matrix, register, test

- `README-agents.md` Portable Rule Owners: "review" → "review and problem
  reports"; "capability selection" → "capability selection, quality before
  speed"; "rule authoring/feedback" → "feedback intake and rule authoring".
- `feedback-register.md`: entries W-R59, W-R60, W-R61 (one per feedback, Why
  from the Sources table, How to apply from A–C); owner mapping rows for
  `review.md`, `capabilities.md` and `rule-authoring.md` add their number.
- `tests/test_sync_codex_config.py`: one test that each new section exists
  with its key phrases, that both adapters carry the three new route
  triggers with the right owner, that the Claude Auto-Memory paragraph names
  Feedback Intake, and that each of W-R59–W-R61 appears once and in its
  mapping row. Shown failing against the current `main` first.
- `.gitignore`: allow this review directory (done with this draft).

## Not changed, or deferred

- **A hook after a feedback memory write** (Claude PostToolUse on the memory
  directory, reminding the agent to classify). It would have caught today's
  case and W-R52's, but not W-R58's, and it adds a managed host surface for
  Claude only. Deferred; owner: workspace-meta; restart condition: the class
  recurs after Feedback Intake lands (`problem-follow-up.md` Mechanism Or
  Rule). Question 3.
- **The status line's `5h` gauge** shows the remaining share while `ctx`
  beside it shows the used share, with the same unlabeled `N%` form. That
  trap produced the misread. Fixing the label is a change to a managed
  surface (`scripts/claude_status_line.py`, its tests, `make sync`), not a
  rule. Question 2.
- **Where project-only corrections live.** "Project-only behavior stays in
  the project" does not say whether host memory is enough; many reality-ops
  corrections exist only in Claude memory, which Codex and other hosts do
  not see. Not part of this feedback; reported only.
- `reasoning.md`, `verification.md`, `planning.md`, `problem-follow-up.md`:
  unchanged. They keep their content; A–C only add triggers and shapes that
  point to them.

## Questions for the operator

1. **Feedback 1: add the shape and trigger, or register only?**
   Recommended: add them (A). The discipline was already covered and the
   class recurred under it; the missing parts were the trigger and what counts
   as a problem. Register only would leave both gaps.
2. **Fix the `5h` label?** Recommended: yes, as a separate small change after
   this one (for example `5h:95%left(4h20m)`), with its own approval for
   `make sync`.
3. **Memory-write hook now or deferred?** Recommended: deferred with the
   restart condition above. The earlier recurrences had no intake trigger to
   fail; give the trigger a chance before adding a Claude-only mechanism.

## Acceptance

- A–D landed as approved; no other rule text changed.
- Replaying each incident against the new text: the 12:22 question routes to
  `review.md` Problem Reports, which excludes five of the six items and the
  unsupported "已确认"; the 14:11 proposal meets Quality Before Speed through
  `capabilities.md`; the 12:38 memory save meets Claude Auto-Memory → Feedback
  Intake, which asks for a handoff in that reply. The Codex route row carries
  the same intake trigger.
- File checks: `make test` (including `scripts/check_documentation.py`);
  `bash -n scripts/*.sh .githooks/pre-commit`; `py_compile` of scripts and
  tests; `git diff --check`; bootstrap twice against an isolated HOME with
  unchanged managed hashes on the second run, because the Codex managed block
  changes.
- The new test fails against `main` and passes on the branch.

## Publication and release

After verification and a Changelog in this directory: one change-flow bundle
(`git-publication.md` Change-Flow Bundle) to commit on `fix/feedback-intake`,
fast-forward `main`, push `origin main`, remove the worktree, and delete the
local branch, approved as one brief. Then `make sync` on each host. This
closes a batch, so the release would be `v1.1.0` (`releases.md`), tagged after
sync is verified, with its own approval.

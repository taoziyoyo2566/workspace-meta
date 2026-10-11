# Changelog: problem reports, quality before speed, and feedback intake

- **Date**: 2026-10-11
- **Plan**: [plan-feedback-intake-2026-10-11.md](plan-feedback-intake-2026-10-11.md)
- **Delivery state**: content-complete and verified on branch
  `fix/feedback-intake`. When this record was written, none of these approved
  steps had run yet: commit, merge into `main`, push, `make sync` on each host,
  and the release tag.

## Outcome

Three pieces of operator feedback from the reality-ops coordination session
now have owners, triggers in both adapters, and provenance in W-R59–W-R61.

- **`review.md` Problem Reports** (W-R59):
  - only a defect or risk that holds now, has an effect, and has evidence the
    agent obtained itself counts as a problem;
  - pending work, known limitations, planned phases and out-of-scope matters
    appear only under their own label, and a check that could not run is a
    gap;
  - another source's claim is a lead, and a metric is read from its
    definition;
  - "confirmed" needs a check that establishes the claim itself.
- **`capabilities.md` Quality Before Speed** (W-R60):
  - the configured model, reasoning effort and orchestration settings stay;
  - no change that lowers quality to save time or usage;
  - a change of method only when it also improves the result;
  - the operator decides any speed-for-quality trade.
- **`rule-authoring.md` Feedback Intake** (W-R61):
  - a correction or preference about how agents work is classified in the
    reply that takes it in;
  - a cross-project one is routed in a workspace-meta governance session, or
    handed over in that same reply from any other session;
  - memory does not route it.
- **Adapters**: both route the three new triggers to these owners. The Claude
  Auto-Memory paragraph now classifies each saved correction under Feedback
  Intake.
- **Matrix, register, test**: `README-agents.md` names the three domains; the
  register maps W-R59–W-R61 to their owners; one regression test covers the
  sections, the routes, the matrix rows, the register rows and the
  Auto-Memory link.

Rule sizes in lines after the change: `review.md` 114, `capabilities.md` 104,
`rule-authoring.md` 91.

## Implementation readings

An independent read-only review of the first implementation found no P0, 2 P1
and 7 P2. These changes keep the approved meaning, triggers and owners. They
add to the Plan's text as follows:

- **Preference versus setting** (P1). Choose The Owner First maps "preference"
  to host-local configuration, so "否则还是用默认的配置" could have been filed as
  a host-local preference, which is the incident again. Feedback Intake now
  says how an agent should work is behavior even when it names a setting; only
  a setting's value is host-local.
- **What "confirmed" needs** (P1). "Name the check" was met by the 12:22 check,
  which only ruled out one cause. The check must now establish the claim
  itself; ruling out one cause is an inference.
- **Delegated findings** (P2). A finding from an agent the session delegated to
  counts once the session has checked the evidence it cites.
- **Cuts after speed is raised** (P2). Once the operator has raised speed or
  cost, any cut in depth, agents or verification needs its quality cost stated
  and the operator's decision first. The new trigger bullet points to Quality
  Before Speed.
- **Register guard** (P2). A session that is not workspace-meta governance does
  not change workspace rules or `feedback-register.md` unless asked.
- **"routing feedback" kept** (P2). The Plan replaced it in the route row; it
  stays beside the new trigger so that a workspace-meta session receiving a
  handed-over brief still loads `rule-authoring.md`.
- **Test strength** (P2). The reviewer's mutation probes showed four
  regressions the first test missed. The test now checks the trigger bullet,
  the negation "are not problems", the workspace-meta branch, the preference
  clause and the kept trigger. It also fails rather than errors on a missing
  register row, and reads only the Auto-Memory section.
- **W-R60 Why** (P2). It now records that at 14:00 the session stopped the
  workflow and checked the remaining points by command.
- **Not adopted**: making the handoff durable until the workspace session
  takes it. Feedback Intake hands over in the same reply, by a command or a
  message; a further tracking state would add process without a recorded
  failure.
- **Also changed**: the root `README.md` provenance range now reads
  W-R53–W-R61.

## Incident replay

- **12:22, "当前发现了什么问题？"** The route row "reporting which problems
  exist" loads Problem Reports:
  - PR #32, rollback phase 2 and the PAT expiry are pending or planned work;
  - the four unreachable nodes are a gap, contradicted by the operator's 11:44
    status;
  - `5h:95%` must be read from its definition, as the remaining share;
  - the n8n container and the input-box text are another session's claims,
    to verify or label;
  - "已确认" fails, because ruling out the ops session established nothing
    about who deleted spt-b.
- **14:00 and 14:11, slow work.** "slow or costly work" loads Quality Before
  Speed. Once the operator has raised speed, stopping the workflow needs its
  quality cost stated and the operator's decision first.
  Fewer agents, lower effort and time limits are not proposed. Narrowing each
  delegated task to the deciding points may be proposed, with how it improves
  the result.
- **12:38 and 14:17, corrections saved to memory.** Auto-Memory sends the save
  to Feedback Intake, and the route row "the operator correcting how you work
  or stating a preference about it" loads it directly. Both corrections are
  cross-project in a session that is not workspace-meta governance, so the
  reply hands them over with a launch command and a brief. The red flag "this
  session does not handle workspace rules" matches the misread coordination
  note.
- **Codex.** The same route row is resident in the managed block. Feedback
  Intake covers memory that the runtime consolidates.

## Verification

- **The new test.** It failed against an export of `main`
  (`0 != 1 : review.md`) and passes on the branch. Eleven mutations on scratch
  copies each make it fail:
  - removing the slow-work trigger, the workspace-meta branch, the preference
    clause from the Codex route, "routing feedback" from the Claude route, the
    W-R60 mapping, the Auto-Memory link, the setting-versus-behavior sentence,
    the delegated-finding sentence, or the operator's decision on cuts;
  - inverting "are not problems";
  - weakening "establishes that claim itself".
- **`make test`.** The documentation gate is OK and all 111 tests pass.
- **Static and whitespace checks.** All pass:
  - `bash -n scripts/*.sh .githooks/pre-commit`;
  - `py_compile` of the scripts and tests;
  - `git diff --check`;
  - an encoding, line-ending, final-newline and trailing-whitespace check of
    every changed file.
- **Isolated sync.** `scripts/sync_codex_config.py` ran twice against a
  temporary HOME, with the arguments `bootstrap-local.sh` passes. The second
  run reported 0 updated and 6 unchanged, with identical file hashes, and the
  installed Codex block carries the three new triggers. `bootstrap-local.sh`
  itself was not run, because it also sets `core.hooksPath` in the shared
  repository configuration.
- **Host drift.** `make agent-sync-check` on this host reports drift for the
  Codex AGENTS block only, as expected before `make sync`.

## Gaps and follow-ups

- **Release steps.** Publication, then `make sync` on each host, then the
  release tag. Each is approved separately.
- **The `5h` label.** It is a separate change on branch
  `fix/status-line-five-hour-label`, as decided for question 2.
- **The memory-write hook.** Deferred; owner workspace-meta; restart
  condition: the class recurs after Feedback Intake lands.
- **Where project-only corrections live.** Reported only, as the Plan says.

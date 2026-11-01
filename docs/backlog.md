# Backlog

Deferred work, later stages, and residual gaps of workspace-meta. Each entry
names what is waiting, its owner, and the condition that restarts it or the
check that closes it, or says that it is a known limitation; an entry leaves
when it closes
([`documentation.md` Committed And Temporary Records](../.agents/rules/documentation.md#committed-and-temporary-records)).
Running plans are not kept here: they live in the ignored `docs/plans/` of a
host's main checkout.

## Rule Evaluation Stages

Owner: workspace-meta. The staged extension of the
[rule evaluation harness](../evals/rules/README.md), approved tentatively on
2026-10-16 and deferred on 2026-10-31.

- Stage 1 gate: compare `main` before and after `cdfae24`, by Git ref, on
  Claude and Codex, three trials each, in clean accounts with no memory, hooks,
  or MCP servers, and with an unmanaged Claude config dir passed as
  `--claude-config-dir`. Restart: the clean accounts exist and the operator
  has logged in to each once.
- Stages 2 to 4, each only after the operator reviews the previous result.
  Stage 3 excerpts stay redacted and host-local, never in this repository;
  Stage 4 is only for failures the earlier stages cannot reproduce, run in a
  sandbox without the SSH agent or host access. Codex scenarios may need
  agent-neutral wording.
- Resumed-transcript scenarios, for habits a one-decision replay cannot show.
  Restart: the next rule change that comes from a long-session failure.
- Held-out reworded scenario variants. Restart: a target passes at its
  ceiling while a rule change needs a harder test.

## Delegation

Owner: workspace-meta.

- Check that a real dispatch runs each agent with the model and effort it was
  given, in `/tasks`; the harness has no Agent tool to test it.
- Hooks that log each subagent's model, deferred. Restart: an allocation is
  found not applied.
- Role subagents with fixed frontmatter, deferred. Restart: allocations are
  omitted or wrong in practice.
- The delegation-plan scenario showed the required behavior about half the
  time on Claude Code 2.1.302 and 2.1.303. Recheck when `capabilities.md`
  Delegation or the pinned model changes, with at least six trials per version.

## Request Intake

Owner: workspace-meta.

- A UserPromptSubmit reminder hook, deferred. Restart: a misreading or a missed
  similar problem recurs.
- Not yet exercised: a real AskUserQuestion round, an ask-then-proceed over
  several turns, a real `/interview` run, and the tie-break clause for a
  request that fits two depths.

## Memory Governance (Dormant)

Owner: workspace-meta. Dormant since the operator's decision of 2026-10-18;
Project Bootstrap replaced the draft's automatic project initialization. The
drafts of version 0.1.2 are in commit `56bfc41`.

- Dormant items: a workspace memory map (per project its path, purpose,
  lifecycle, status, blockers, link, and last review with HEAD, branch, and
  dirty state); quick and full audits of the current project, report-only by
  default and reconciling only with a stated write scope; and a history format
  of a current view plus append-only history, with an index only as a
  rebuildable layer once lookups need it.
- Restart: a lasting fact is lost because memory is recall-only and no owning
  artifact held it. Start from that failure, and build claim identifiers,
  idempotent keys, or recovery only when a second real case needs them.
- The operator's constraints (2026-08-07): the agent does the semantic work
  from a stated goal and templates, and scripts only mechanical checks; no
  background or SessionStart writes; memory changes at task boundaries, never
  on every commit or only to refresh a timestamp; no automatic publication.
  Their scope for a session-history plugin is decided under Session History.

## Session History

Owner: workspace-meta. A session-history plugin, claude-mem 15.8.0, is
described as optional host-local recall since 2026-11-01
([`claude-runtime.md` Memory](../.agents/rules/claude-runtime.md#memory) and
the claude-mem step of the [new VPS runbook](runbooks/new-vps.md)); no host
runs it yet.

- Decided on 2026-11-01, the operator having left the call to the agent
  ("decide by best practice"): the constraints of 2026-08-07 under Memory
  Governance cover the workspace's memory records and what reaches a session,
  not the plugin's own store. Its background capture is a derived,
  non-authoritative log, like the transcripts Claude Code writes on every
  turn, so it may run. What it pushes into a session falls under the
  requirement that SessionStart only remind and report: start-of-session
  context stays a short reminder, file history is not added before reads,
  and nothing it writes reaches project files or another account. Its
  marketplace's auto-update, which its installer turns on, stays off, so
  every upgrade is reviewed against these settings first.
- Unverified until the first install: per-config-dir stores through
  `CLAUDE_MEM_DATA_DIR` and `CLAUDE_MEM_WORKER_PORT` in a config dir's
  `settings.json` `env` (claude-mem documents that hooks receive that block);
  and that `make rule-eval` runs, which pass `--setting-sources project`, load
  no user plugin (the `init` event in a run log lists the plugins).
- A managed skill run at a task boundary that searches the store for
  corrections never routed, restart conditions in this file that have
  occurred, and classes that recurred after their rule landed, and reports
  them without writing anything, deferred. Restart: a host's store has held
  its sessions for some weeks, or the operator asks for such a review.
- A claude-mem mode with a note type for corrections, deferred. Restart: that
  review finds corrections buried among ordinary notes.
- Drawing rule-evaluation scenarios from the store, deferred: auditing real
  sessions has pending work of its own, and both belong in one section of
  [the evaluation guide](../evals/rules/README.md). Restart: that audit lands.
- Codex: claude-mem also ships a Codex plugin, which `codex-runtime.md` does
  not cover. Restart: the operator installs it for Codex.

## Feedback Intake

Owner: workspace-meta. A hook on memory writes that reminds the agent to route
cross-project feedback, deferred. Restart: the class recurs after Feedback
Intake landed.

## Temporary Space

Owner: workspace-meta.

- A `systemd-tmpfiles` age for the Claude temporary tree and moving its root to
  disk, deferred: an age would delete an idle open session's files, and moving
  the root changes every session's path. Restart: the warning fires again or
  ENOSPC recurs; then pick an age above the longest idle session and dry-run it
  with `--replace`.
- The temporary-space warning has not yet been seen in a real Claude or Codex
  client. Check it when a host crosses 80% use or 256 MiB free.

## Fresh-Session Checks

Owner: workspace-meta.

- A Claude session in a project whose `CLAUDE.md` imports `AGENTS.md` shows the
  file loaded, in `/context` or an InstructionsLoaded event.
- A project without an entry file shows the readiness message in each Claude
  config dir and in Codex.
- On Claude Code 2.1.302 it is unverified whether a subdirectory's `AGENTS.md`
  loads by itself under an ancestor `CLAUDE.md`, and which files the
  `claude-md-and-agents-md` setting loads. Check with `/context`; recheck when
  the changelog names `AGENTS.md` or `instructionFiles`.
- It is unverified whether a user-level `autoMemoryDirectory` stays one flat
  directory and so merges every project's memory, as `claude-runtime.md`
  Memory infers. Check it in a config dir made for the test, with sessions in
  two projects.

## Codex

Owner: workspace-meta.

- Known limitation: the readiness warning never clears in a clone of someone
  else's repository. Without `AGENTS.md` it appears at every start, and where
  the clone tracks the upstream `CLAUDE.md` it is an owner-move message the
  operator cannot act on.
- `project_doc_fallback_filenames` (codex-cli 0.160.1) was not adopted: it is
  host-wide and would also load upstream `CLAUDE.md` files. Restart: the
  operator wants it.
- The `systemMessage` warning in a trusted fresh session has not yet been seen.

## Status Line

Owner: workspace-meta and the tool that installs the status line in question.
A status line without the workspace-meta marker is kept and reported, not
managed; managing it from workspace-meta is deferred. Restart: the operator
wants that status line converged.

## Portability

Owner: workspace-meta. `scripts/bootstrap-local.sh` has never run under bash
3.2. Restart: the first macOS host.

## Next Release

Owner: workspace-meta. `make sync` on the other hosts, then the next release
tag; there is none since `v1.1.0`.

## Document Language

Owner: workspace-meta. No rule states which documents are in which language
(rules in English; architecture, runbooks, and the handbook in Chinese).
Restart: a document in the wrong language, or a second copy in another one.

## Rule Rollout

Owner: workspace-meta for the rollout; each repository migrates in its own
sessions, with the operator. On 2026-10-31 these repositories still tracked
review records, and none ignored `docs/plans/` yet:

- reality-ops: 72 files under `docs/reviews/`; its live sessions were told
  the migration steps on 2026-10-31.
- homepage: 5 files under `docs/reviews/`; the current design in its running
  plans moves into its architecture document first.
- parade-ops: 2 files under `docs/reviews/`; its plan becomes its
  architecture document.

Other repositories migrate at their next documentation change. A repository's
item closes when it tracks no review record and ignores `docs/plans/`.

## Feedback Register

Owner: workspace-meta.

- Splitting the register by domain, with W-R numbers kept global and
  `feedback-register.md` or a small index as the entry point, deferred.
  Restart: the register becomes hard to scan (roughly 300 to 500 lines), merge
  conflicts become frequent, or looking up a domain starts costing time.
- Allocating W-R numbers across machines, deferred. Restart: writing rules on
  several machines at once becomes routine. Try a process rule first (fetch
  before minting, read the latest W-R, write, push at once, renumber on
  collision), before heavier schemes such as machine suffixes, date-based IDs,
  or reserved ranges.

## Remote Refs

Owner: the operator; each removal is a separate reviewed Git action.

- `origin/agent-workflow`: its task-size plan was superseded by
  `capabilities.md` Delegation, never adopted or rejected on record.
- `origin/agent/memory-governance-v0.1.2-checkpoint`: an ancestor of `main`
  with no content of its own.

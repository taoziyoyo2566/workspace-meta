# Workspace Feedback Register (provenance archive — NOT resident context)

This file is the **non-resident provenance archive** for the portable rules routed by
`~/workspace/CLAUDE.md` and the installed Codex AGENTS block. Each distilled cross-project rule
`W-R<N>` has one entry: the rule in one sentence plus one line of source, giving the date, the
project, and the cause in one sentence (`rule-authoring.md` Provenance And Refactoring). An entry
keeps the rule's lasting core, and earlier forms of the entries remain in Git history. Where an
entry differs from its owner module, the module governs; a known replacement or refinement is
marked on the entry.

**Why this file exists separately**: the agent adapters are loaded into every session, so they
carry only safety floors and task routes. The register is read only when a rule is disputed or
re-derived; it does not belong in resident context.

**IDs are stable**: scripts, changelogs, memories, and project `CLAUDE.md` reference `W-R<N>` by
number. Never renumber. Numbering accumulates; mark replacements rather than deleting.

**Current owner mapping** (the register preserves provenance; these modules govern behavior):

| Canonical owner | Consolidated provenance |
|---|---|
| `.agents/rules/authorization.md` | W-R13 authorization boundary, W-R23, W-R29–W-R31, W-R34–W-R35, refined by W-R54, elevated reads W-R66, approval labels W-R68, runtime denials W-R69, standing bootstrap authority W-R73, plain briefs W-R92 |
| `.agents/rules/git.md` | W-R21 inspection/freshness, W-R23, refined by W-R57 |
| `.agents/rules/git-branches.md` | W-R21–W-R22 and W-R32 branch-contract design refined by W-R40, change flow W-R58, pre-release channels W-R84, older-line fixes from a verified state W-R85 |
| `.agents/rules/git-publication.md` | W-R25, W-R30 refined by W-R31, change-flow bundle W-R58, remote visibility W-R77, one proposal per result W-R78 refining W-R31, pre-release channels W-R84, only unexpected fields shown W-R92 |
| `.agents/rules/git-integration.md` | W-R21 and the accepted W-R32 terminal-evidence refinement, refined by W-R54, W-R57 and W-R58, pre-release channels W-R84 |
| `.agents/rules/git-recovery.md` | W-R19–W-R20, refined by W-R57 and W-R58, pre-release channels W-R84 |
| `.agents/rules/requests.md` | W-R63, moved from `planning.md`, extended by W-R71 |
| `.agents/rules/planning.md` | W-R1–W-R7, W-R12, W-R18 and accepted W-R32 refinements, refined by W-R44, W-R46, W-R47, W-R50, W-R51, W-R56 and W-R57, exceptions to recorded decisions W-R67, remembered restrictions W-R70, routine operations stay transient W-R78, plans removed at acceptance W-R87, session history searched as a lead W-R88 |
| `.agents/rules/reasoning.md` | W-R43, refined by W-R63, probes explained to the operator W-R91 |
| `.agents/rules/implementation.md` | W-R37 refined by W-R44, W-R48 and W-R53 |
| `.agents/rules/documentation.md` | W-R38 refined by W-R39, W-R41 entry-point loadability refined by W-R42, Plan/Changelog lifecycle refined by W-R44, W-R46 and W-R47, investigation records refined by W-R50, seams for W-R53 and W-R57, project bootstrap W-R73 restoring W-R11 in a narrower form, committed Changelogs not added to W-R78, committed and temporary records W-R87 |
| `.agents/rules/verification.md` | W-R15–W-R17, refined by W-R53 |
| `.agents/rules/file-checks.md` | W-R53 |
| `.agents/rules/deployment.md` | W-R54 refined by W-R57, pre-release channels W-R84, verified rollback targets W-R85, older-line end W-R86 |
| `.agents/rules/releases.md` | W-R57, pre-release channels W-R84, verified rollback targets W-R85, version numbers and fix tags W-R86 |
| `.agents/rules/review.md` | W-R13, W-R20, W-R33 and accepted W-R32 refinements, refined by W-R56, problem reports W-R59 |
| `.agents/rules/problem-follow-up.md` | W-R56, recurrence searched like earlier work W-R88 |
| `.agents/rules/capabilities.md` | W-R18 and accepted W-R32 refinements, refined by W-R44, W-R52, W-R53 and W-R55, quality before speed W-R60, where the user runs a command W-R62, command length W-R65, delegation W-R72, opening the user's terminal W-R76 |
| `.agents/rules/claude-runtime.md` | Claude mechanics for W-R71, W-R72 and W-R73, session-history plugins W-R88 |
| `.agents/host-templates/README-agents.md` | W-R28, W-R36, every agent config dir W-R74, plugin stores outside the config dirs W-R88 |
| `.agents/rules/secrets.md` | W-R13, refined by W-R53 |
| `.agents/rules/temporary-files.md` | W-R55, keeping reusable work W-R75 |
| `.agents/rules/environment-truth.md` | W-R24 refined by W-R44 |
| `.agents/rules/rule-authoring.md` | W-R8–W-R14, W-R27–W-R28, W-R32, refined by W-R53 and W-R56, feedback intake W-R61, lasting content and one-line sources W-R64, scope of restricting notes W-R70, loosening instead of adding W-R90 |

---

## Register

- **W-R1 (2026-04-14)** — **No implementation starts until its plan is approved.**
    - Source: 2026-04-14, ansispire: the operator asked for a changelog after the work was done.
- **W-R2 (2026-04-14)** — **A plan declares its level and does not mix architecture and engineering decisions.** Replaced in `planning.md`, which requires no level declaration.
    - Source: 2026-04-14, ansispire: no cause was recorded; it came from the same round as W-R1.
- **W-R3 (2026-04-14)** — **A plan of three or more tasks starts only after its roadmap is approved.** Replaced in `planning.md`: a task's number of steps does not call for a separate approval.
    - Source: 2026-04-14, ansispire: no cause was recorded; it came from the same round as W-R1.
- **W-R4 (2026-04-14)** — **Before work starts, the system type, its boundaries, and its non-functional requirements are clarified.**
    - Source: 2026-04-14, ansispire: no cause was recorded; it came from the same round as W-R1.
- **W-R5 (2026-04-14)** — **Cost and usage-limit risk are announced up front.** Narrowed in `planning.md`: no cost or usage estimate is required merely because a task is non-trivial.
    - Source: 2026-04-14, ansispire: a round ran into the usage limit, and the risk was raised only afterwards.
- **W-R6 (2026-04-14)** — **Every round ends with explicit next steps: what can be done now, what is blocked, and what can wait.**
    - Source: 2026-04-14, ansispire: remaining work was left unreported.
- **W-R7 (2026-04-14)** — **An approved layered roadmap continues phase by phase without stopping for a new go-ahead.**
    - Source: 2026-04-14, ansispire: work stopped after one phase although the layered plan was already approved.
- **W-R8 (2026-04-15)** — **Before a configuration or rule file is edited, the edit is checked for fit, conflicts, and possible improvements.**
    - Source: 2026-04-15, ansispire: no cause was recorded.
- **W-R9 (2026-04-15)** — **An approved rule change is worked into the whole file, not appended to it.**
    - Source: 2026-04-15, ansispire: no cause was recorded.
- **W-R10 (2026-04-16)** — **Documents are named by topic first; round numbers live inside topic directories, not in top-level file names.**
    - Source: 2026-04-16, ansispire: one task split into several rounds made its change history hard to follow.
- **W-R11 (2026-04-17)** — **Every new project directory under `~/workspace` gets its own `CLAUDE.md` when it is created, and project-only feedback stays in it.** Restored in a narrower form by W-R73.
    - Source: 2026-04-17, claude-md: the operator asked that each new project carry its own rules and improve them from its feedback.
- **W-R12 (2026-04-18)** — **Handoff between agents goes through persistent artifacts, not the user: a resolved decision updates every artifact that still shows it open in the same round, and instructions for a later session are written into the owning artifact instead of being given to the user to pass on.**
    - Source: 2026-04-18, subscription-landing: a later session asked again about a decision a plan had resolved without updating the project file, and the operator was handed instructions to relay to the next session.
- **W-R13 (2026-05-03)** — **An audit or review changes only what it must: files with real secrets never enter Git, a default falls back sensibly instead of pinning a value that goes stale, recommended extras are proposed rather than added, and the user's own pending changes are kept, with their risks raised.**
    - Source: 2026-05-03, n8n-hosting: one review round tracked a file with real keys, pinned a version as a default, added unrequested settings, and removed one of the user's own pending changes.
- **W-R14 (2026-05-09)** — **Resident instruction files hold only guidance that applies to every task; configuration facts, situational checks, and runbooks live with their owners, and a maintainer's quick reference is kept apart from an operator guide.**
    - Source: 2026-05-09, ansispire: a convention and a feature-specific check were proposed for the resident project file, and the operator asked that such details live where they apply, with a complete guide for running things by hand.
- **W-R15 (2026-05-12)** — **A task closes only when direction, static correctness, and a functional test pass in the same pass; a linter or parser never replaces the functional test.**
    - Source: 2026-05-12, ansispire: a change was marked done after lint and parse checks, before any functional test ran, as in earlier rounds.
- **W-R16 (2026-05-12)** — **A long-running task shows its progress as it runs, or states its expected duration and milestones first and reports each one as it arrives.**
    - Source: 2026-05-12, ansispire: a long test ran as a silent background job, and the operator could not tell running from stuck.
- **W-R17 (2026-05-12)** — **A fix-and-retry sequence stops after three failed attempts and goes to the user.** Replaced in `verification.md` by deeper diagnosis after repeated failure, with no fixed count.
    - Source: 2026-05-12, project not recorded: the operator capped retries, and the W-R15 loop of repeating until clean had no limit.
- **W-R18 (2026-05-16)** — **New feature work, or work built on an existing implementation, first checks the framework's native or recommended way and whether the existing implementation follows it, and records the sources and the conclusion before the plan body.**
    - Source: 2026-05-16, ansispire: a feature was designed on top of an implementation that went against its framework's practice, and the operator had to redirect it although they had asked for best practice before.
- **W-R19 (2026-05-21)** — **A force push or remote ref deletion uses a lease on the expected object id, never a bare force, and a local `branch -D` runs only after the branch is checked to point at the expected commit.**
    - Source: 2026-05-21, ansispire: a review found a script deleting a remote branch without a lease, racing with concurrent pushes, and force-deleting the local branch without checking it.
- **W-R20 (2026-05-21)** — **Code that contains a destructive operation on shared state gets a review from outside the authoring session before merge; the author's own review and an in-session review skill do not count.** Refined in `review.md`: the need for an independent reviewer follows blast radius, reversibility, and recovery, and self-review is not categorically invalid.
    - Source: 2026-05-21, ansispire: over several rounds the author's own reviews and an in-session review skill reported clean, while each external review found new failure classes in scripts with destructive operations.
- **W-R21 (2026-05-22)** — **A feature branch starts from the current trunk tip, merges the trunk in while it is active, takes in nothing but the trunk, and is created from a clean tree on a base that holds its prerequisites.**
    - Source: 2026-05-22, project not recorded: no cause was recorded.
- **W-R22 (2026-06-06)** — **Security and supply-chain governance work may branch from the trunk and merge ahead of slower feature branches when it adds only new files, with its updates to shared tracking files following the merge.**
    - Source: 2026-06-06, ansispire: a security governance deliverable was stacked behind an unrelated architecture branch, and the operator decided it must reach the trunk first.
- **W-R23 (2026-06-06)** — **A Git command that only inspects runs without asking; its actual effect decides, not the subcommand name.**
    - Source: 2026-06-06, ansispire: read-only repository inspection kept prompting for approval, and the operator said non-mutating Git needs none.
- **W-R24 (2026-06-10)** — **An environment fact is probed before it shapes a decision, and the record that governs later work is corrected when a probe contradicts it.**
    - Source: 2026-06-10, ansispire: a remembered missing tool outlived its installation and shaped a plan that a quick probe would have corrected.
- **W-R25 (2026-06-12)** — **Agent commits carry no AI trailers and are attributed by the host operator's global Git identity, checked before and after each commit; synced rule files hold that check, never identity values.**
    - Source: 2026-06-12, ansispire: tooling defaults had added trailers nobody decided on, a host committed under a stale repository-local identity, and a first fix wrote one operator's identity into the synced rules.
- **W-R26 (2026-06-12)** — **The workspace governance files are carried by their own whitelist repository rooted at `~/workspace`; updating a checkout and publishing follow the Git modules, and the repository is public (W-R45).**
    - Source: 2026-06-12, workspace-meta: the shared rule files belonged to no repository, so an edit on one machine never reached another.
- **W-R27 (2026-06-26)** — **A behavior-shaping rule takes the form its failure needs: a prohibition with red flags for a discipline skip, a positive recipe for wrong-shaped output, a required slot for an omitted element, and a conditional on an observable predicate for condition-dependent behavior; the source incident is its baseline test, and a real recurrence calls for a change of form before louder wording.**
    - Source: 2026-06-26, workspace-meta: the operator reviewed an external agent-skills framework and adopted its form-to-failure method, keeping constructed pressure tests optional.
- **W-R28 (2026-07-11)** — **Workspace-meta manages Codex through its own marked blocks and hook group, never by mirroring `~/.codex`: trust, credentials, execution rules, history, and other runtime state stay host-local, and portable behavior lives in the shared neutral modules.**
    - Source: 2026-07-11, workspace-meta: the methodology lived only in the Claude file, hook and template handling risked overwriting local content, and the host's Codex rules held accumulated approvals, so mirroring the home directory would have mixed governance with credentials and trust.
- **W-R29 (2026-07-11)** — **Safe reads, searches, and inspection run without confirmation and material mutations keep needing authorization, while executable allow and prompt decisions stay in host-local configuration.**
    - Source: 2026-07-11, workspace-meta: the operator met repeated prompts for retrieval and search, while the host's rules already allowed several material mutations.
- **W-R30 (2026-07-18)** — **Commit and push each need the operator's confirmation of an exact manifest, and a technical approval is not that confirmation.** Refined by W-R31.
    - Source: 2026-07-18, project not recorded: a documentation commit was made after a tool approval that the operator had not given as consent to commit.
- **W-R31 (2026-07-20)** — **Publication has two checkpoints, the result for content acceptance and then one complete bundle of the publication commands, which runs once on an ordinary confirmation or is run by the operator and then verified; this corrects the form of W-R30.** Refined by W-R78: the result review and the bundle go in one proposal under one approval.
    - Source: 2026-07-20, saberu: one rename task stopped for a separate manifest at each Git step and spread over several pull requests without better review.
- **W-R32 (2026-07-20)** — **Portable cross-project behavior has one agent-neutral owner under `.agents/rules/`; agent files and project files are thin adapters or narrower deltas.**
    - Source: 2026-07-20, workspace-meta: a whole-rules audit found the same generic behavior repeated in a project's files and in the Claude user layer.
- **W-R33 (2026-08-02)** — **A review first fixes the nearest repository, its comparison base, and its scope; nested repositories and host-local state are separate boundaries, inspected only when named or required.**
    - Source: 2026-08-02, workspace-meta: a plan that named a nested project led a review into that project and host-local trust paths before the target was stated.
- **W-R34 (2026-08-02)** — **A request for consent to a protected action explains the action before showing the operation.**
    - Source: 2026-08-02, project not recorded: an approval request showed only a command, without why it was needed, what it changes, or what to expect.
- **W-R35 (2026-08-03)** — **The protected-action brief comes before an operation is proposed, handed to the operator, or put up for approval.**
    - Source: 2026-08-03, workspace-meta: during the W-R34 remediation, a next step that changes host configuration was recommended without the brief.
- **W-R36 (2026-08-20)** — **A generated host capability snapshot is local runtime state and is never committed or copied to another host.**
    - Source: 2026-08-20, workspace-meta: the operator noted that the generated files differ per machine and only add churn when tracked.
- **W-R37 (2026-08-28)** — **An implementation artifact has one fact owner, durable local comments, a coherent change surface, and behavior-focused tests.**
    - Source: 2026-08-28, project not recorded: a remediation across projects put history into code comments, duplicated normative metadata, and relied on brittle source-text tests.
- **W-R38 (2026-09-04)** — **Project documentation is organized by reader task and truth lifecycle with one owner per current fact, and project agent files carry only project facts and narrower deltas.**
    - Source: 2026-09-04, NanoPi_R6S_Handbook: procedures, snapshots, incidents, plans, and evidence had piled up in one numbered series, leaving authority and navigation unclear.
- **W-R39 (2026-09-04)** — **A documentation move is complete only when current owners hold no dated or incident content and the new shape is checked mechanically; a compatibility pointer needs a known consumer and an exit condition.**
    - Source: 2026-09-04, NanoPi_R6S_Handbook: a migration passed its link checker while current runbooks still held dated conclusions and pointer pages had no known consumer.
- **W-R40 (2026-09-06)** — **A one-time Git transaction is not recorded in project content, and a branch action keeps the reviewed diff unchanged unless a content change was authorized.**
    - Source: 2026-09-06, project not recorded: a request to move a prepared documentation change onto a branch was taken as a requirement to write the branch conversation into the project's plan.
- **W-R41 (2026-09-06)** — **Project instructions the runtime does not load are not in effect: each runtime a project is used with needs an entry file it loads, and every further entry file imports one owner instead of restating it.**
    - Source: 2026-09-06, NanoPi_R6S_Handbook: a Claude session loaded no project instructions because the project shipped only `AGENTS.md`, and proposed a privileged read where the project's own status commands would have answered.
- **W-R42 (2026-09-06)** — **When a project has no entry file for the runtime in use, its owner file is read before substantive work, read-only and operational work included, not only before the first write.**
    - Source: 2026-09-06, workspace-meta: a review of W-R41 found that its first-write trigger would have missed its own incident, which happened during read-only work.
- **W-R43 (2026-09-07)** — **Technical conclusions follow one proportional reasoning method, owned by `reasoning.md`: validate load-bearing premises, keep knowledge states apart, prefer discriminating probes, and stop when the evidence suffices.**
    - Source: 2026-09-07, workspace-meta: workflow rules each treated evidence and uncertainty in their own way, and no shared method existed.
- **W-R44 (2026-09-07)** — **An approved Plan freezes its stable content, routine progress stays transient, a material deviation needs approval before the Plan changes, and a Changelog records only the verified outcome.** Changelogs are no longer produced since W-R87.
    - Source: 2026-09-07, project not recorded: execution loops written into Plans and repeated in Changelogs produced churn and overlapping records.
- **W-R45 (2026-09-07)** — **The workspace-meta repository is public, and what it publishes stays portable and whitelisted; visibility is not the security boundary.**
    - Source: 2026-09-07, workspace-meta: the operator made the repository public while current documents still described it as private.
- **W-R46 (2026-09-08)** — **A Plan and its Changelog cover a coherent workstream, not each change or round: a covering Plan is reused and stays open while the operator is still refining the work.** Changelogs are no longer produced since W-R87.
    - Source: 2026-09-08, workspace-meta: one sync task produced several Plan and Changelog pairs as it moved through feedback and fixes.
- **W-R47 (2026-09-19)** — **An independent capability gets its own Plan file, never a section of another Plan.**
    - Source: 2026-09-19, reality-ops: the design of a new capability was added to a completed Plan, and an unrelated evaluation became an appendix of another Plan.
- **W-R48 (2026-09-22)** — **A new audience, language, or scope extends the existing implementation with a parameter, and logic that several deployables use lives in one shared module.**
    - Source: 2026-09-22, reality-ops: a second renderer for the same view was written beside the first, and one service's source file was copied into another image.
- **W-R49 (2026-09-26)** — **Concrete design and implementation guidance lives in the shared engineering owners with proportional checks, and a handbook may explain them with optional examples.**
    - Source: 2026-09-26, project not recorded: a project's implementation checklist repeated generic workflow rules in abstract phases that said neither what to change nor how to tell it was done.
- **W-R50 (2026-10-06)** — **A verified finding that constrains other work is recorded when it is confirmed, and an investigation or Plan first searches earlier and concurrent work, including uncommitted documents, other worktrees, and unmerged branches, by the paths, settings, and dependency versions it touches.**
    - Source: 2026-10-06, reality-ops: two concurrent sessions prepared the same upgrade, and a compatibility finding one of them had verified lived only in its session.
- **W-R51 (2026-10-09)** — **An operator decision is recorded in the artifact it changes when it is made, before other task work; agent memory only points to that record, a memory write changes its index line in the same step, and a workstream's status is read from its owner before it is reported from memory.**
    - Source: 2026-10-09, reality-ops: a deferral was written only to agent memory, with a wrong date and no index line, the interrupted turn never updated the plan, and another session later reported the stale status from memory.
- **W-R52 (2026-10-10)** — **A command the user runs in their own terminal that is more than one simple line is handed over as a script file plus the one-line command that runs it; a one-off script goes under `/tmp`.**
    - Source: 2026-10-10, reality-ops: a check pasted as a heredoc picked up trailing spaces when copied and never ran, and the follow-up built a persistent script directory for one-off work.
- **W-R53 (2026-10-10)** — **A file that is delivered or kept is checked by its type before it is called done, handed over, committed, or deployed: bytes, syntax, strict format, consistency with its consumer, and security bounded to the file; a check counts only for the defects it can detect.**
    - Source: 2026-10-10, reality-ops: a manual edit repeated keys, and a check that keeps the last repeated key passed after each edit while every later deployment warned about them.
- **W-R54 (2026-10-10)** — **What serves users runs a commit on the pushed main deployment branch, and anything else is a temporary deployment with an end condition; a pushed commit that changes what runs is deployed promptly and verified, and an instance outside the inventory is reported before anyone acts on it.** Extended by W-R84 for a declared pre-release channel.
    - Source: 2026-10-10, reality-ops: a drill instance outside the inventory still ran an unmerged branch's build with old keys, the live service had earlier run an unpushed commit, and pushed changes waited days for deployment.
- **W-R55 (2026-10-10)** — **An agent places its temporary files by size and filesystem, removes what it created, keeps nothing in temporary space as a record, and, when that space fills, stops writing, measures without tree walks, and removes others' files only at the operator's request after in-use checks.**
    - Source: 2026-10-10, homepage: a session's install failed because a small shared temporary filesystem was full of scratch from ended sessions, a day after the same failure had been deferred only in memory.
- **W-R56 (2026-10-10)** — **A report on a handled problem that touched shared state, was found by chance or by someone else, or happened before gives six parts in order: outcome, cause chain, why safeguards missed it, recurrence, proposals, and where the lesson is kept; every proposed procedure is first checked against the recorded rules and decisions it touches.**
    - Source: 2026-10-10, homepage and reality-ops: a cleanup was reported with only its result and no prevention, and a session proposed a procedure that contradicted a recorded decision it had not checked.
- **W-R57 (2026-10-11)** — **A released state gets an identity: after a release is deployed and verified, its exact commit receives an annotated version tag whose message is the release notes; released versions are fixed through the branch flow, and pushed tags never move.**
    - Source: 2026-10-11, reality-ops: the operator asked for a lasting record of each finished batch, while released states had no identity beyond one-line tags and hand-made restore points.
- **W-R58 (2026-10-11)** — **Every repository change goes through a short-lived, typed branch from the main branch, is checked there, and reaches the main branch only by the project's integration route; nothing is committed directly to the main branch.**
    - Source: 2026-10-11, reality-ops: commits went straight onto the deployment branch, the operator's decision to use branches lived only in memory, and a later session proposed fixing on that branch again.
- **W-R59 (2026-10-11)** — **A report of which problems exist lists only a defect or risk that holds now and has an effect, with evidence the reporting agent obtained itself; pending work, known limitations, planned phases, and out-of-scope matters are not problems, another source's claim is a lead, a metric is read from its definition, and "confirmed" needs a check that establishes the claim itself.**
    - Source: 2026-10-11, reality-ops: asked what problems were found, a session listed relayed claims it had not verified, a misread status metric, and planned work as current problems.
- **W-R60 (2026-10-11)** — **Result quality comes before speed: keep the configured model, reasoning effort, and orchestration settings, never lower quality to save time or usage, propose a change of method only when it also improves the result, and leave any speed-for-quality trade to the operator.**
    - Source: 2026-10-11, reality-ops: after a slow multi-agent run the session proposed fewer agents, lower effort, and time limits, and the operator answered that result quality comes first.
- **W-R61 (2026-10-11)** — **When the operator corrects how an agent works or states a preference about it, the agent classifies it as project-only or cross-project in the reply that takes it in and says which; a cross-project one is routed by a workspace-meta governance session or, from any other session, handed over in that same reply, and saving it to memory does not route it.**
    - Source: 2026-10-11, reality-ops: cross-project corrections were saved only to project memory, and the operator had to ask why they had not been handed to a workspace session.
- **W-R62 (2026-10-14)** — **A command the user runs is handed over for a new terminal of their own, never for the agent's conversation input such as Claude Code's `!` prefix, with the host and account it runs as; when its effect must reach the session, the agent first checks that the new terminal reaches it, and afterwards checks the effect from the session.**
    - Source: 2026-10-14, reality-ops: an agent followed Claude Code's suggestion to have the operator load a passphrase-protected SSH key with the `!` prefix, the passphrase prompt returned unanswered, and the operator said a command to run belongs in a new terminal of their own.
- **W-R63 (2026-10-15)** — **Read a request for its goal: an example shows one case of the need and is not a requirement; an investigation, comparison, or design states the goal and usage scenarios first, carries derived requirements as assumptions, and judges options per scenario.**
    - Source: 2026-10-15, workspace-meta: a survey of existing tools scored candidates against a checklist built from the operator's examples and missed the answer the operator wanted; similar misreadings had happened before.
- **W-R64 (2026-10-15)** — **Rules, adapters, register entries, and memory notes of feedback hold only lasting guidance; a register entry is the rule in one sentence plus one line of source.**
    - Source: 2026-10-15, workspace-meta: a feedback memory note and a planned register entry carried session times, a temporary path, and routing status.
- **W-R65 (2026-10-15)** — **Each command handed to the user to run stays within about 60 characters, so it is not wrapped where the user copies it; a longer command goes into a script at a short path.**
    - Source: 2026-10-15, workspace-meta: a one-line command that ran a script from the runtime's long scratch path was wrapped on display and broke into two lines when the operator copied it.
- **W-R66 (2026-10-16)** — **Read-only inspection runs as the logged-in account; a read that needs sudo, root, or another account is privilege elevation and waits for the user's go-ahead, and a refused unprivileged read is reported, not escalated.**
    - Source: 2026-10-16, reality-ops: a session ran reads with `sudo -n` without asking although the account's group membership already allowed them, and where sudo needed a password it reported the result as unknown (the class of W-R41).
- **W-R67 (2026-10-16)** — **An operator decision that makes an exception to a recorded decision or procedure, even for one operation, is recorded in that artifact in the same turn.**
    - Source: 2026-10-16, reality-ops: the operator's one-time exception to a recorded procedure was recorded only a day later, after the session asked whether to record it (a recurrence of W-R51).
- **W-R68 (2026-10-16)** — **An approval request names its targets by what they are and reuses no label that already means something else; a short reply that could select two target sets of an irreversible action is clarified first.**
    - Source: 2026-10-16, reality-ops: target groups were given letter labels that an earlier option already used, so a short reply approving an irreversible deletion could be read two ways.
- **W-R69 (2026-10-16)** — **A runtime denial stands even for an approved operation: do not repeat it by another route; hand the exact operation to the user or name the permission they could change.**
    - Source: 2026-10-16, reality-ops: the runtime denied an approved deployment and an approved host change, and the operator asked whether a new tmux session could run the denied command instead.
- **W-R70 (2026-10-16)** — **A memory note that restricts agents names its scope, and when a remembered restriction forbids what the operator now asks, the agent names the conflict and asks once instead of declining on its authority.**
    - Source: 2026-10-16, reality-ops: a remembered restriction with no scope blocked a request the operator made until the operator corrected it.
- **W-R71 (2026-10-17)** — **Read every request before starting work, as deeply as it needs: state its goal and what done means, find the similar problems it stands for and say which join the scope, ask in one round with options and a recommendation only when the operator is present and an answer would redirect the work, and otherwise proceed on stated assumptions.**
    - Source: 2026-10-17, workspace-meta: the operator asked for one standard way of reading their questions and ideas, because their brief descriptions are examples that often stand for a class of problems, while request reading covered only investigations, comparisons, and designs.
- **W-R72 (2026-10-17)** — **Before delegating, survey the subtasks and give each agent the model and reasoning effort its demand needs, judgment and synthesis at no less than the configured settings and checked mechanical work lighter, with a bounded brief and a stated check; set them explicitly and report the allocation.**
    - Source: 2026-10-17, workspace-meta: the operator asked that delegated work be assessed per subtask and given a fitting model and effort, while nothing planned delegation, so every subagent inherited the session's settings and broad research agents at max effort ran for hours.
- **W-R73 (2026-10-17)** — **A Git project the operator works on with an agent gets that agent's missing entry files at the first substantive work, with `AGENTS.md` as the owner, a thin importing adapter per runtime, and only local files in someone else's clone, created without asking, never overwriting, left uncommitted, and reported.**
    - Source: 2026-10-17, workspace-meta: the operator asked that every project used with Claude get its project content automatically, while most Git projects had no entry file Claude loads, `AGENTS.md`-only projects loaded nothing in Claude, and W-R11's per-project file had lost its owner.
- **W-R74 (2026-10-17)** — **Every agent config dir the operator uses is an instance of the host user layer: workspace-managed surfaces are converged into each one, and everything else in it stays with that account.**
    - Source: 2026-10-17, workspace-meta: after the operator added a second Claude account, its sessions ran under a second config dir that received none of the managed session-start check, status line, or skill.
- **W-R75 (2026-10-18)** — **Before removing its temporary files, an agent sorts out what will be needed again and proposes moving it to its owner, such as a script into its project as a tool or an evaluation scenario into the evaluation tree, and removes only the rest.**
    - Source: 2026-10-18, workspace-meta: a session's scratch cleanup removed evaluation scenarios and a script that would be needed again, and the operator asked that scripts which will be reused be kept.
- **W-R76 (2026-10-19)** — **A command handed to the user for a terminal of their own comes with the steps to open that terminal from where they are, found by first checking how the session runs or by asking the user.**
    - Source: 2026-10-19, workspace-meta: a cleanup handed over only for the user's own terminal, with the host and account named, was not run, and the operator answered that they had not been told how to run it.
- **W-R77 (2026-10-29)** — **A publication review shows whether the target remote is public and, for a public remote, which host or personal details the pushed content reveals, before the push is proposed.**
    - Source: 2026-10-29, invoice_automation: host deployment notes were pushed to a fork that turned out to be public, because the review checked identity, refs, and the content for secrets but never the remote's visibility.
- **W-R78 (2026-10-29)** — **A commit publishes, so publication is proposed once per finished result, with its result review and a bundle for each repository it changed under one approval (refining W-R31); a later routine operation, its check, or a status change is reported in the conversation, not committed, and a committed Changelog is not added to.**
    - Source: 2026-10-29, invoice_automation: several commits were proposed in quick succession, the last only to add a routine operation and its check to an already committed Changelog, and the operator asked why unneeded content was recorded and for fewer, less scattered commit tasks.
- **W-R84 (2026-10-25)** — **A project may declare a pre-release channel: a lasting part of production whose instances serve the users who choose it with checked, pushed commits of a channel branch that contains the main branch and is never rewritten; changes enter it by fast-forward or merge commit and leave by promotion or revert, shared parts are never deployed from it, only a main-branch deployment after promotion is released, and a channel instance rolls back to a verified state, its own or the main-branch instances'.**
    - Source: 2026-10-25, reality-ops: a pre-release instance serving opt-in users beside the stable one, with changes not yet on the main branch, fit neither the main-branch rule nor temporary deployments, and the change flow, downstream integration, tagging, and rollback had no route for it.
- **W-R85 (2026-10-30)** — **In every project a rollback goes to the newest verified state without the fault, a release or a later deployment that the project's deployment record shows passed its checks, and a fix on an older line starts from that state.**
    - Source: 2026-10-30, reality-ops: its approved default rollback returns each host to its last verified deployment while the rule allowed only release tags, so rolling back a pre-release channel's first round would have gone past the untagged channel build and removed the channel.
- **W-R86 (2026-10-21)** — **A release raises MINOR only for a new modular feature, something the project did not have delivered as its own module or component, not a pre-release channel, counted in the first release whose range contains it deployed; improvements inside an existing component raise PATCH, and a deployed fix rides with the next release unless it is on an older line or the operator decides it needs a release of its own.**
    - Source: 2026-10-21, reality-ops: a release of fixes and improvements inside an existing component was proposed as a MINOR version under the closed-batch rule.
- **W-R87 (2026-10-30)** — **A repository commits only durable content that concerns the whole project, kept current and edited in place with Git as its history; review content is temporary, a workstream's one running plan lives in the ignored `docs/plans/` of the main checkout and is committed only by a private repository when another machine or agent needs it or the operator asks, and at acceptance its durable content moves to its owners and the plan is removed.**
    - Source: 2026-10-30, workspace-meta: dated plans, changelogs, and investigation records had piled up in the public repository as copies beside the current owners, and the operator asked that committed docs hold only durable project-wide content and one current plan, dropped once it is complete.
- **W-R88 (2026-11-01)** — **A searchable session history, such as a memory plugin's store, is searched with the other records before an investigation and for a problem's recurrence, and what it returns is a lead; it never keeps what an owner holds, adds no more than a short reminder at session start, leaves full reads to the file, is kept to one config dir or split per config dir, and is upgraded only after review.**
    - Source: 2026-11-01, workspace-meta: asked how claude-mem could complement the rules, the review found that its defaults would keep corrections, decisions, and work state in a second store, inject note history at start and before reads, answer full reads with note summaries, merge every account's history into one store, and turn on auto-update for its own marketplace.
- **W-R90 (2026-11-08)** — **Feedback that asks for less constraint loosens or removes the text that imposes the constraint, and when no text imposes it nothing is written, the register included.**
    - Source: 2026-11-08, workspace-meta: a correction against tying an operator's test to one app was routed as a new rule section, and the operator answered that such feedback should not become a rule but should loosen an existing restriction.
- **W-R91 (2026-11-08)** — **A probe the operator runs or decides on comes with what is already known, which open possibilities it tells apart, and what each result would mean, hypotheses marked as such, so that the operator judges it rather than follows it.**
    - Source: 2026-11-07, reality-ops: tests for the operator to run were suggested with only a short note on reading their results, and the operator asked why each was needed, wanting to judge rather than follow.
- **W-R92 (2026-11-08)** — **A brief or review before an operation states what will happen, why, the target, the effect, and the risk in one plain line each, adds exclusions, gaps, and a wider approval boundary only when they apply, and lists another field only when its check finds it not as expected.**
    - Source: 2026-11-08, workspace-meta: after replies too long to follow, a brief with many fixed fields and a full publication field list left the operator asking what had been done, why, and to what effect, and the operator had the briefs loosened.

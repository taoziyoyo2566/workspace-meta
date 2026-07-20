# Codex rule migration and content-quality ledger

- **Date**: 2026-07-20
- **Plan**: `plan-codex-rule-ownership-2026-07-20.md`
- **Scope**: installed workspace Codex guidance, the versioned workspace
  `CLAUDE.md`, workspace candidate, Saberu root/path adapters, `.agents/`
  rules/scenarios, Saberu Claude adapter, and the frozen Saberu candidate
- **State**: Phase 0 mapping complete and decisions accepted; the workspace
  portion is implemented in the Phase 1 candidate, while project reduction and
  cross-layer verification remain pending

## 1. How to read this ledger

This ledger normalizes identical statements into one behavior row. A source
statement is not considered covered merely because its file is assigned to a
domain; the source coverage table in §11 maps every normative section to one or
more behavior IDs.

Source aliases:

| Alias | Source |
|---|---|
| `W0` | `origin/main:.agents/host-templates/codex-AGENTS.md`, also the installed managed block in `~/.codex/AGENTS.md` |
| `WCL` | versioned workspace `CLAUDE.md`; its references to `~/.claude/CLAUDE.md` are broken on the audited host because that file does not exist |
| `WE` | workspace `.agents/rules/environment-truth.md` |
| `WC` | frozen uncommitted workspace candidate |
| `S0` | `origin/dev` Saberu rules before the frozen project candidate |
| `SC` | frozen uncommitted Saberu candidate |
| `SP` | unchanged Saberu project rules/adapters in the same candidate worktree |

Target aliases:

| Alias | Canonical owner |
|---|---|
| `W-AUTH` | workspace `.agents/rules/authorization.md` |
| `W-GIT` | task-shaped workspace owners `git.md`, `git-branches.md`, `git-publication.md`, `git-integration.md`, and `git-recovery.md` |
| `W-PLAN` | workspace `.agents/rules/planning.md` |
| `W-REVIEW` | workspace `.agents/rules/review.md` |
| `W-CAP` | workspace `.agents/rules/capabilities.md` plus agent-specific runtime adapters |
| `W-SECRET` | workspace `.agents/rules/secrets.md` |
| `W-ENV` | workspace `environment-truth.md` |
| `W-VERIFY` | workspace `.agents/rules/verification.md` |
| `W-RULES` | workspace `.agents/rules/rule-authoring.md` |
| `C-ADAPTER` | managed Codex router plus `.agents/rules/codex-runtime.md` |
| `CL-ADAPTER` | workspace/project Claude thin routers and available Claude-only mechanics |
| `S-BRANCH` | Saberu `branching.md` |
| `S-LIVE` | proposed Saberu live/external-operation rule |
| `S-PLAN` | Saberu planning/artifact rules |
| `S-DOC` | Saberu documentation/workstream routing |
| `S-TEST` | Saberu testing governance |
| `S-SECRET` | Saberu secret placement rule |
| `S-ADAPTER` | root, agent-specific, or path-local routing adapter |
| `S-TRUTH` | Saberu stable project docs/code named in the row |

Verdicts have the meanings defined in the plan. `Mapped / DQ-*` means that the
target owner is known but the behavior change must be reviewed before
implementation.

Scenario IDs are defined in §10.

## 2. Cross-project authorization

| ID | Trigger and normalized required behavior | Current source/owners | Quality verdict and rationale | Target, project delta, and migration action | Preservation evidence | Status |
|---|---|---|---|---|---|---|
| AUTH-01 | When interpreting instructions, separate task authorization, plan approval, sandbox capability, and protected-action authorization; one never implies another. | `W0:52-54,83-85,98-110`; `SP authorization.md:13-24`; `WC codex-authorization.md:17-26` | `merge` — correct and testable, but repeated. | `W-AUTH`; project delta `none`; replace project copies with a reference. | SC-01, SC-03, SC-04 | mapped |
| AUTH-02 | Explain/review/audit/diagnose/report requests authorize read-only investigation, not remediation. | `SP authorization.md:48-55`; `SP review-closure.md:5-7`; `WC codex-authorization.md:30-36`; `WC codex-review.md:12-14` | `merge` — necessary; authorization owner should define it once and review should reference it. | `W-AUTH`; `W-REVIEW` reference only. | SC-01 | mapped |
| AUTH-03 | Change/fix/implement/update/refactor/apply-recommendations/authorized-continue requests authorize necessary in-scope working-tree edits and non-destructive verification. | `W0:12-17`; `SP authorization.md:26-35,48-55`; `SP boundaries.md:3-8`; `WC codex-authorization.md:30-42` | `merge` — correct; current project loading is unnecessary for ordinary edits. | `W-AUTH`; remove generic project copies. | SC-02 | mapped |
| AUTH-04 | A request for a plan/proposal authorizes planning artifacts only. | `SP authorization.md:48-55`; `WC codex-authorization.md:34` | `keep` — precise, low cost. | `W-AUTH`; replace project copy with reference. | SC-03 | mapped |
| AUTH-05 | Plan approval authorizes only its declared scope and never silently authorizes Git publication, external writes, or live mutation. | `W0:52-54,104-107`; `SP authorization.md:18,22-24,54-55,154-173`; `SP plan-hierarchy.md:7-13,55-66`; `WC codex-authorization.md:22,35,80-81`; `WC codex-planning.md:52-55` | `merge` — correct but spread across authorization and planning. | Semantic owner `W-AUTH`; `W-PLAN` explains plan-scope application; `S-LIVE` adds live fields. | SC-03, SC-10 | mapped |
| AUTH-06 | In-scope edit authority covers create/edit/rename/removal of known required paths without per-file confirmation. | `SP authorization.md:28-35`; `WC codex-authorization.md:38-42` | `rewrite-equivalent` — “known/in-scope/necessary” must remain to protect unrelated work. | `W-AUTH`; remove from project boundaries. | SC-02 | mapped |
| AUTH-07 | Preserve unrelated, pre-existing, historical, and unrecognized work; stop if a new decision materially redirects scope. | `W0:16-17,41-47`; `SP authorization.md:37-46`; `SP docs/AGENTS.md:10-15`; `WC codex-authorization.md:38-42`; `WC codex-git.md:35-36` | `merge` — safety invariant, intentionally resident in compact form and detailed once. | Compact floor in managed router; detail in `W-AUTH`/`W-GIT`; Saberu keeps only its historical-evidence delta. | SC-02, SC-14 | mapped |
| AUTH-08 | Classify documentation by behavioral effect, not file extension or Markdown format. | `SP authorization.md:57-67`; `SP docs/AGENTS.md:6-15`; `WC codex-authorization.md:44-46` | `merge` — necessary governance safeguard; project retains its artifact/history examples. | `W-AUTH` general rule; `S-DOC` project delta. | SC-01, SC-13 | mapped |
| AUTH-09 | Once a task is authorized, local/Git/remote reads, native web/docs lookup, in-scope writable-root edits, tests, and local ephemeral verification proceed without another conversational confirmation. | `W0:38-40,95-100`; `SP authorization.md:69-84`; `WC codex-authorization.md:48-58` | `merge` — directly addresses repeated permission friction. | `W-AUTH`; project copies removed. | SC-01, SC-02 | mapped |
| AUTH-10 | Classify the actual command, target, and boundary; do not infer impact from executable name alone. | `W0:108-110`; `SP authorization.md:86-103`; `WC codex-authorization.md:60-63,85-92` | `rewrite-equivalent` — correct; examples should not become an executable allow list. | `W-AUTH`; host execpolicy remains local. | SC-02, SC-11 | mapped |
| AUTH-11 | If sandboxing blocks an otherwise authorized safe read/write, request one narrow categorical technical approval; that prompt does not change semantic scope. | `W0:101-103`; `SP authorization.md:82-84`; `WC codex-authorization.md:57-58,85-92` | `merge` — correct and reduces prompt count. | `W-AUTH`. | SC-02 | mapped |
| AUTH-12 | Git staging/history/ref/worktree mutation, publication, integration, and cleanup require the Git transaction appropriate to their effect. | `W0:52-54,78-88,104-107`; `SP authorization.md:105-152`; `WC codex-authorization.md:65-78` | `split` — authorization owns protected category; `W-GIT` owns procedure. | `W-AUTH` boundary plus `W-GIT` action procedure. | SC-03–SC-09 | mapped |
| AUTH-13 | Remote API writes, deployments, external-resource mutation, outside-root writes, privilege/host changes, and live infrastructure mutation require a reviewed named action. | `W0:104-107`; `SP authorization.md:111-117,140-150`; `WC codex-authorization.md:67-81` | `split` — generic boundary is cross-project; live target schema is project-specific. | `W-AUTH`; `S-LIVE` adds target/impact/recovery fields. | SC-10, SC-11 | mapped |
| AUTH-14 | Protected-action review identifies actual target, operation, impact, exclusions, prerequisites/check state; material drift expires authorization. | `W0:71-85`; `SP authorization.md:119-138,140-150`; `WC codex-authorization.md:76-81` | `rewrite-equivalent` — keep generic expiry once; action modules add fields. | `W-AUTH`; `W-GIT` and `S-LIVE` reference it. | SC-04, SC-07, SC-10 | mapped |
| AUTH-15 | Host executable allow/prompt files are local technical state and must not be copied into workspace-meta/projects. | `W0:89-91,108-110,114-120`; `SP authorization.md:3-11`; `WC codex-authorization.md:83-96`; `WC managed router:57-58,62-69` | `merge` — necessary ownership/security boundary; compact resident reminder is justified. | Managed router compact floor plus `W-AUTH` detail. | static ownership check | mapped |
| AUTH-16 | Ask a clarifying question only when the missing answer could materially redirect scope, destroy/expose work, mutate a protected target, or change authorization. | `W0:12-15`; `SP authorization.md:175-179`; `WC codex-authorization.md:98-103` | `rewrite-equivalent` — correct; prevents approval chatter while preserving real decisions. | `W-AUTH`. | SC-01, SC-02 | mapped |

## 3. Cross-project Git and complete branch task contract

| ID | Trigger and normalized required behavior | Current source/owners | Quality verdict and rationale | Target, project delta, and migration action | Preservation evidence | Status |
|---|---|---|---|---|---|---|
| GIT-01 | Run Git inspection without conversational confirmation only when it cannot change tree, index, refs, remote, config, credentials, or external state. | `W0:38-40`; `SP git.md:10-31`; `WC codex-git.md:13-24` | `merge` — project command list is a duplicate; keep definition plus examples globally. | `W-GIT`; remove Saberu `git.md` copy. | SC-03 | mapped |
| GIT-02 | Plain canonical-remote fetch may be used for stated freshness without prune/force/custom refspec or an attached integration action. | `SP authorization.md:79-80`; `SP git.md:29-31`; `SP session-bootstrap.md:42-57`; `WC codex-git.md:21-24` | `merge` — needed for multi-machine truth; avoid three definitions. | `W-GIT`; Saberu bootstrap names `origin` only as project remote delta. | SC-03, SC-12 | mapped |
| GIT-03 | Before branch/worktree/stash/publication/integration mutation inspect current branch/HEAD, dirty/index/untracked state, all worktrees, relevant refs, and divergence. | `W0:43-47`; `SP git.md:42-55,89-108`; `WC codex-git.md:26-33` | `merge` — safety-critical; one global checklist. | `W-GIT`; project adds topology fields only. | SC-04, SC-07 | mapped |
| GIT-04 | Never reset/clean/overwrite/switch/move/hide/delete unrecognized work merely for convenience. | `W0:41-47`; `SP git.md:47-59`; `WC codex-git.md:35-36,49-54` | `merge` — resident short safety floor plus canonical detail is intentional. | Managed router floor + `W-GIT`. | SC-04, SC-09 | mapped |
| GIT-05 | Every new branch has a task contract that states the problem and observable outcome. | `SP branching.md:49-85`; missing from `WC codex-git.md`; plan required invariant | `split` — cross-project field was lost by file-level classification. | `W-GIT`; Saberu contract references it and adds topology/persistence. | SC-04, SC-05 | mapped |
| GIT-06 | The branch contract states the chosen approach, in/out scope, prerequisites, and exclusions. | `SP coding-plan.md:65-85`; partially `SP branching.md:78-84`; missing as a complete branch field | `behavior-change-pending-decision` — makes the remembered contract explicit instead of relying on a separate plan. | `W-GIT`; decision `DQ-01A`. | SC-04, SC-05 | mapped / DQ-01A |
| GIT-07 | The branch contract states acceptance checks/evidence and the pass condition. | `SP branching.md:82`; `SP coding-plan.md:69-85`; plan required invariant | `merge` — current content is split between branch and plan. | `W-GIT`; project adds named test/artifact routes. | SC-04, SC-05 | mapped |
| GIT-08 | The branch contract states intended logical publication: commit grouping, review, push/PR route, base/head target, and exclusions. | Remembered user rule; `SP branching.md:257-279,357-376` only covers readiness/publication later | `behavior-change-pending-decision` — required content is currently implicit and incomplete. | `W-GIT`; decision `DQ-01A`. | SC-04–SC-06 | mapped / DQ-01A |
| GIT-09 | The branch contract states integration/closeout handling, remaining-work ownership, and the difference between implementation completion and integration. | `SP branching.md:67-91,220-279,281-326`; plan required invariant | `merge` — necessary but currently project-owned. | `W-GIT` generic lifecycle meaning; `S-BRANCH` project states/routes. | SC-04, SC-07 | mapped |
| GIT-10 | The branch contract states final retirement/archive/retain/remove handling without pre-authorizing cleanup. | `SP branching.md:228-253,300-355`; plan required invariant | `split` — generic separation belongs globally; archive tooling/topology stays project. | `W-GIT`; `S-BRANCH` adds archive script/tag policy. | SC-04, SC-08 | mapped |
| GIT-11 | The branch contract records branch name, exact base ref/OID, intended worktree path, and treatment of existing changes. | `W0:43-47`; `SP git.md:42-55`; `SP branching.md:174-198`; `WC codex-git.md:38-51` | `merge` — correct and testable. | `W-GIT`; project adds relationship/target. | SC-04 | mapped |
| GIT-12 | Review the complete contract and exact additive branch/worktree action before creating it; persist the contract as the first governance content in the new worktree. | `SP branching.md:S0 174-194`, `SC 174-194`; plan required invariant; `WC codex-git.md` only announces | `behavior-change-pending-decision` — resolves the lost-contract bug but changes the current “announcement only” entry gate. | `W-GIT`; `S-BRANCH` supplies persistence path; decisions `DQ-01B`/`DQ-01C`. | SC-04, SC-05 | mapped / DQ-01B,DQ-01C |
| GIT-13 | A new additive branch/worktree must not switch an existing checkout, reuse/move/remove a worktree, carry dirty changes, or mutate an existing branch. | `W0:43-51`; `SP git.md:47-59`; `WC codex-git.md:49-54` | `merge` — correct. | `W-GIT`. | SC-04 | mapped |
| GIT-14 | Branch creation does not authorize staging, publication, upstream changes, integration, or cleanup. | `W0:45-54`; `SP git.md:52-59`; `WC codex-git.md:49-51` | `merge` — necessary authority boundary. | `W-GIT`. | SC-04 | mapped |
| GIT-15 | State-displacing branch/worktree operations require a separately reviewed exact command/effect. | `W0:46-51`; `SP git.md:52-55`; `WC codex-git.md:53-54` | `keep` — correct and precise. | `W-GIT`. | SC-04, SC-09 | mapped |
| GIT-16 | Never auto-stash/`--autostash`; stash actions identify paths, inclusion modes, identity/message, and restore/removal effect; stash is not undocumented task storage. | `W0:48-51`; `SP git.md:47-48`; `WC codex-git.md:56-66` | `rewrite-equivalent` — keep one complete global rule. | `W-GIT`; remove project copy. | SC-04, SC-09 | mapped |
| GIT-17 | Working-tree edit authority never includes staging, commit, push, tag/upstream change, or PR creation. | `W0:52-54`; `SP authorization.md:105-109`; `WC codex-git.md:68-71` | `merge` — core publication boundary. | `W-GIT`, referenced by `W-AUTH`. | SC-03, SC-06 | mapped |
| GIT-18 | Publication checkpoint A reports changed paths/outcomes, checks/gaps, exclusions/follow-ups, branch, and dirty state; wait for ordinary content acceptance. | `W0:55-58`; `SC branching.md:362-369`; `WC codex-git.md:73-82` | `merge` — user explicitly preferred this two-checkpoint shape. | `W-GIT`; project supplies check names only. | SC-06 | mapped |
| GIT-19 | Publication checkpoint B displays one exact copyable ordered bundle containing every applicable exact-path add, one commit, one push, and one PR-create command. | `W0:59-67`; `SC git.md:61-81`; `SC branching.md:265-269,365-369`; `WC codex-git.md:84-102` | `merge` — correct; current project still repeats procedure. | `W-GIT`; project files add only fields/checks. | SC-06 | mapped |
| GIT-20 | The bundle includes branch, staged name/status/stat, full message, identity source/result, remote URL/name, refs/range/count/divergence, force/upstream mode, checks/gaps, and PR base/head/options. | `W0:59-63`; `SC git.md:71-77`; `WC codex-git.md:94-102` | `merge` — one canonical schema; project adds commit format and required checks, not duplicate generic fields. | `W-GIT`; `S-TEST`/commit convention supply values. | SC-06 | mapped |
| GIT-21 | Use exact paths; never broad staging that includes unreviewed content; review the complete staged diff. | `S0 git.md:73-90`; `SP commits.md:27-31`; `WC codex-git.md:104-108` | `merge` — generic safety, not Saberu-specific. | `W-GIT`; project commit rule references it. | SC-06 | mapped |
| GIT-22 | Resolve the operator identity from host global Git config; stop on unset, repo-local override, or mismatch; add no AI/Co-Authored/Signed-off trailers. | `W0:86-88`; `SP commits.md:20,32`; `WC managed router:53-54`; `WC codex-git.md:105-108` | `merge` — resident no-trailer floor plus exact Git procedure is justified; project identity copy is not. | Managed floor + `W-GIT`; Saberu keeps only message format. | SC-06 | mapped |
| GIT-23 | User may authorize the unchanged bundle once in ordinary language or execute some/all personally; never require a generated phrase. | `W0:64-67`; `SC branching.md:365-369`; `WC codex-git.md:110-112` | `merge` — explicitly user-approved. | `W-GIT`. | SC-06 | mapped |
| GIT-24 | For Codex execution, expected state transitions from earlier displayed commands do not invalidate later commands. | `W0:68-73`; `WC codex-git.md:114-118` | `keep` — fixes the prior repeated-confirmation defect. | `W-GIT`. | SC-06 | mapped |
| GIT-25 | Stop when reviewed paths/content/message/refs/range/checks/PR target/commands drift, a hook changes/rejects content, remote rejects push, or a different command is needed. | `W0:71-73`; `SP authorization.md:136-138`; `WC codex-git.md:114-118` | `rewrite-equivalent` — precise; use one generic expiry rule. | `W-GIT`; project-required check changes are inputs. | SC-06 | mapped |
| GIT-26 | If the operator reports execution, verify commit/remote/PR read-only and never rerun mutations; corrective work needs a new reviewed bundle. | `W0:74-77`; `WC codex-git.md:120-122`; `SC workstream README:32-35` | `merge` — explicitly user-approved. | `W-GIT`. | SC-06 | mapped |
| GIT-27 | After commit inspect author/OID/message/trailers; never auto-amend, bypass hooks, add corrective commit, change/retry push, pull/rebase, or force. | `W0:86-88`; `SP commits.md:37-44`; `WC codex-git.md:124-126` | `merge` — one global recovery stop rule. | `W-GIT`; project keeps message content only. | SC-06, SC-09 | mapped |
| GIT-28 | Integration is a separate reviewed transaction, not an implicit publication final step. | `W0:78-82`; `SP authorization.md:119-138`; `SP branching.md:281-300`; `WC codex-git.md:128-147` | `merge` — correct; project should add topology only. | `W-GIT`; `S-BRANCH` delta. | SC-07 | mapped |
| GIT-29 | Integration review includes tips, base/divergence, exact commits/net diff, mode/conflict prediction, dirty/index/worktrees, checks/gaps, project topology, and excluded follow-ups. | `W0:78-82`; `SP git.md:87-113`; `SP branching.md:281-298`; `WC codex-git.md:130-139` | `merge` — generic schema once; Saberu adds relationship/child/dependent/release fields. | `W-GIT` + `S-BRANCH` delta. | SC-07 | mapped |
| GIT-30 | Material change to integration tips/base/diff/mode/state/checks/conflict/project fields expires authorization. | `SP authorization.md:136-138`; `WC codex-git.md:141-142` | `merge` — generic expiry with project inputs. | `W-GIT`. | SC-07 | mapped |
| GIT-31 | One integration authorization excludes conflict resolution, push, tags, ref deletion, branch/worktree cleanup, archive, downstream integration, and post-merge commits. | `W0:81-82`; `SP branching.md:300-318`; `WC codex-git.md:144-147` | `merge` — prevents transaction creep. | `W-GIT`; project routes archive tool separately. | SC-07, SC-08 | mapped |
| GIT-32 | Rebase/cherry-pick/revert/tag/pull/ref deletion/history/config/existing branch-worktree mutations require exact reviewed action; prefer non-rewriting paths when sufficient. | `S0 git.md:41-44,139-172`; `WC codex-git.md:149-160` | `merge` — generic Git behavior. | `W-GIT`; delete project Git policy copy. | SC-09 | mapped |
| GIT-33 | Destructive operations display exact command/target/reason/OIDs/dirty state/loss/recovery/post-check. | `SP authorization.md:140-152`; `SP git.md:115-148`; `WC codex-git.md:156-160` | `merge` — safety-critical. | `W-GIT`; project archive script adds stricter tool route. | SC-09 | mapped |
| GIT-34 | Non-fast-forward remote update uses exact force-with-lease OID; no bare force or deletion; forced local delete verifies exact ref/OID and recovery/archive requirements. | `W0:41-42`; `WC codex-git.md:162-166`; project archive policy | `rewrite-equivalent` — candidate adds useful precision absent from current managed block. | `W-GIT`; `S-BRANCH` archive delta. | SC-09 | mapped |
| GIT-35 | Reset/history rewrite records state, explains rejected safer paths, establishes recovery ref, reviews target/mode, verifies afterward, and retains recovery until user releases it. | `SP git.md:135-148`; `WC codex-git.md:168-175` | `merge` — complete recovery behavior; keep globally. | `W-GIT`. | SC-09 | mapped |
| GIT-36 | PR/Git metadata is normally terminal integration evidence; do not create a branch/PR solely to record the preceding merge. Material living-truth corrections go to the next normal target-based owner. | `SC branching.md:246-250,300-326`; absent from `W0/WC` | `behavior-change-pending-decision` — fixes the observed recursive closeout loop and should be cross-project. | `W-GIT`; Saberu retains topology wording; decision `DQ-02`. | SC-08 | mapped / DQ-02 |
| GIT-37 | Branch/worktree retirement or archival is a separate reviewed action after integration/cancellation; the original task contract does not pre-authorize cleanup. | `SP branching.md:228-253,300-355`; `WC codex-git.md:144-147`; plan invariant | `merge` — correct; current behavior is fragmented. | `W-GIT`; project supplies tag/script/target policy. | SC-08, SC-09 | mapped |
| GIT-38 | Security or supply-chain urgency may affect priority but does not create an unconditional cross-project branch topology, additive-only constraint, or permission to defer living-truth synchronization; use the normal branch contract and the active project's topology. | `WCL:47` | `remove-obsolete` plus `rewrite-equivalent` — the fixed “new files only” fast track is project-shaped and conflicts with the later user-approved owner-branch/reconciliation model. | `W-GIT` supplies the generic contract; project topology decides the route. Remove the standalone fast track. | SC-04, SC-07 | mapped |

## 4. Cross-project planning, review, capability, secrets, and environment

### Planning

| ID | Trigger and normalized required behavior | Current source/owners | Quality verdict and rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| PLAN-01 | Before non-trivial planning, inspect direction/ownership/current task first, then implementation/patterns/native approaches/risks/acceptance. | `SP coding-plan.md:6-49`; `WC codex-planning.md:12-20` | `merge` — useful generic method; project adds named truth paths. | `W-PLAN`; `S-PLAN` routes project sources. | SC-05, SC-13 | mapped |
| PLAN-02 | Separate repo facts, verified external facts, assumptions, research needs, runtime probes, and operator decisions. | `SP evidence-backed-planning.md:8-29,59-77`; `SP plan-structure.md:107-132`; `WC codex-planning.md:21-36` | `merge` — accurate but heavily repeated. | `W-PLAN`; project plan template references it. | SC-05, SC-10 | mapped |
| PLAN-03 | Do not make changing external behavior/security guidance load-bearing from memory; prefer current primary/official sources and record enough to re-check. | `SP coding-plan.md:39-46`; `SP evidence-backed-planning.md:31-50,79-92`; `WC codex-planning.md:30-33` | `merge` — generic and necessary. | `W-PLAN`. | SC-05, SC-11 | mapped |
| PLAN-04 | Every material unknown names close point/method and fallback if contradicted. | `SP evidence-backed-planning.md:28-29,59-77`; `SP plan-structure.md:123-132,164-177`; `WC codex-planning.md:35-36` | `merge` — testable planning invariant. | `W-PLAN`; project may require a decision table for high-risk L2 phases. | SC-05, SC-10 | mapped |
| PLAN-05 | Use the smallest plan that preserves the decision; investigation/decision/runbook/contract/review/evidence is not automatically a plan. | `SP coding-plan.md:51-63`; `SP plan-hierarchy.md:15-40`; `SP file-naming.md:1-27,74-76`; `WC codex-planning.md:38-46` | `merge` — directly reduces artifact/PR inflation. | `W-PLAN`; `S-DOC` owns names/locations. | SC-05, SC-13 | mapped |
| PLAN-06 | A plan states goal, scope/exclusions, prerequisites, effect, approach, risks, modifications, verification, and follow-up handling. | `SP coding-plan.md:65-85`; `SP plan-structure.md`; `WC codex-planning.md:48-50` | `split` — generic minimum globally; Saberu L2 metadata/template project-owned. | `W-PLAN` minimum; `S-PLAN` project schema. | SC-05 | mapped |
| PLAN-07 | Parent/direction/detail approvals remain scoped; pending child blocks only named scope and conflicting child requires explicit supersession/amendment. | `SP plan-hierarchy.md:7-13,42-69`; `SP plan-structure.md:59-91`; `WC codex-planning.md:52-55` | `merge` — generic semantic owner global, project metadata local. | `W-PLAN`; `S-PLAN` persistence fields. | SC-03, SC-05 | mapped |
| PLAN-08 | Re-check load-bearing repository/external/environment/operator/live facts at substantial execution phases. | `SP execution-reflection.md:9-26`; `WC codex-planning.md:57-62` | `merge` — correct, but project repeats environment rule. | `W-PLAN` referencing `W-ENV`; `S-LIVE` adds live target. | SC-10, SC-11 | mapped |
| PLAN-09 | On contradiction, stop, classify cause, record evidence, update/supersede the plan if material, and continue only after required decision/approval. | `SP execution-reflection.md:28-44`; `SP coding-plan.md:87-95`; `WC codex-planning.md:64-75` | `merge` — generic and actionable. | `W-PLAN`; project names evidence path. | SC-05, SC-10 | mapped |
| PLAN-10 | Do not create an additional approval artifact merely to restate approved work or silently rewrite historical intent. | `SP coding-plan.md:59-63`; `SP file-naming.md:74-76`; `SP plan-structure.md:232-256`; `WC codex-planning.md:74-75` | `merge` — directly addresses administrative artifact loops. | `W-PLAN`; `S-DOC` routes the correct artifact. | SC-05, SC-13 | mapped |
| PLAN-11 | Closeout compares result/evidence to goal/effect/scope/acceptance and reports outcome, checks/gaps, deviations, living truth, remaining owner, and still-protected actions. | `SP coding-plan.md:87-95`; `SP plan-structure.md:210-228`; `SP execution-reflection.md:91-100`; `WC codex-planning.md:77-90` | `merge` — generic closeout once; live reflection remains project delta. | `W-PLAN`; `S-LIVE` reflection delta. | SC-05, SC-10 | mapped |
| PLAN-12 | Plan completion, implementation completion, publication, integration, release, and archival are distinct facts. | `SP branching.md:232-233`; `SP plan-structure.md:227-228`; `WC codex-planning.md:89-90` | `merge` — cross-project lifecycle invariant. | `W-PLAN` and `W-GIT` cross-reference one canonical definition. | SC-05, SC-08 | mapped |
| PLAN-13 | Do not require every coding plan to document a capability and every capability deliberately not used. | `SP codex-capabilities.md:23-29`; `SP coding-plan.md:65-75`; `WC codex-capabilities.md:34-35` | `behavior-change-pending-decision` — current requirement creates boilerplate without improving ordinary plans. | Make capability note conditional in `W-CAP`; remove mandatory project field; `DQ-03`. | SC-11 | mapped / DQ-03 |
| PLAN-14 | Do not require every phase/work unit to be independently committable. Define coherent implementation/verification units; publication grouping remains a later Git decision. | `SP plan-structure.md:164-177` | `behavior-change-pending-decision` — current rule over-centers commits and can distort implementation order. | `S-PLAN` rewrite referencing `W-GIT`; `DQ-04`. | SC-05, SC-06 | mapped / DQ-04 |
| PLAN-15 | Phase/evidence closure must not require a Git commit. Record durable evidence in the working tree when required, then publish through the ordinary reviewed bundle. | `SP plan-structure.md:181-196` | `behavior-change-pending-decision` — current “must be committed before phase closed” caused administrative publication pressure. | Generic distinction in `W-PLAN`; project evidence route in `S-PLAN`; `DQ-05`. | SC-05, SC-06 | mapped / DQ-05 |
| PLAN-16 | A material change to an approved plan must become visibly unapproved and be reviewed again; a new file is required only when preserving the old decision as a distinct artifact is useful. | `SP plan-structure.md:67-91`; `SP file-naming.md:89-117`; `SP plan-hierarchy.md:84-94` | `behavior-change-pending-decision` — always creating a new plan increases fragmentation; silent in-place change is still forbidden. | `W-PLAN` approval semantics; `S-PLAN/S-DOC` versioning; `DQ-06`. | SC-05, SC-13 | mapped / DQ-06 |
| PLAN-17 | Task classification and planning depth are selected from observable scope/risk/decision needs; do not require every non-trivial task to declare one fixed level, create both plan and changelog, estimate usage cost, or seek a separate gate merely because a plan has three tasks. | `WCL:13-25`; conflicts with `PLAN-05`, `AUTH-16`, and project artifact routing | `behavior-change-pending-decision` — architecture risk lenses are useful, but the current mandatory four-level/two-artifact/task-count recipe is over-broad and creates administrative work. | `W-PLAN` proportional method; project artifact owner adds only its actual L2 gate; `DQ-14`. | SC-05, SC-13 | mapped / DQ-14 |
| PLAN-18 | Persist load-bearing handoff state in the owning durable artifact when one exists; do not require the user to relay state between agents or sessions. | `WCL:62`; `SP session-bootstrap.md`; workstream hub conventions | `keep` — useful agent-neutral continuity rule, conditional on a durable owner rather than forcing a new artifact. | `W-PLAN`; project routes the owning artifact. | SC-12, SC-13 | mapped |
| PLAN-19 | When an in-scope change resolves a living source that still directs future work, update that living source in the same bounded content change or report the exact deferred owner/gap; publication remains a separate Git transaction. | `WCL:63-64`; `SP docs-sync.md`; `META-04` | `split` — synchronizing living truth is valuable, but mandatory same-round commit/push conflicts with the publication boundary. | `W-PLAN` generic closeout plus project docs-sync; `W-GIT` controls publication. | SC-06, SC-12, SC-13 | mapped |

### Review

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| REVIEW-01 | Review/audit/diagnosis is read-only; explicit fix/apply request authorizes bounded working-tree remediation but not publication/live writes. | `SP review-closure.md:3-7`; `SP review-change.md`; `WC codex-review.md:12-14` | `merge` — authorization semantics live in `W-AUTH`; review references it. | `W-REVIEW` + `W-AUTH`. | SC-01 | mapped |
| REVIEW-02 | Freeze base/scope, identify goal/non-goals/evidence, choose one dominant review type, add only relevant risk lenses, inspect behavior before style, verify, then report findings by severity. | `SP review-change.md:6-61`; `SP review-lenses.md`; `WC codex-review.md:16-31` | `merge` — generic method; current project scenarios largely universal. | `W-REVIEW`; retain only domain-specific Saberu checks. | SC-01 | mapped |
| REVIEW-03 | A plan is reviewed by the behavior it proposes; document metadata/location is a bounded artifact check. | `SP review-change.md:30-37`; `SP review-docs-governance.md:3-7`; `WC codex-review.md:29-31` | `merge` — correct and reduces misclassification. | `W-REVIEW`; `S-DOC` supplies artifact checks. | SC-01, SC-13 | mapped |
| REVIEW-04 | Classify P0/P1/P2 by concrete harm/readiness, and distinguish confirmed defects from questions/preferences. | `SP review-closure.md:9-24`; `WC codex-review.md:33-43` | `rewrite-equivalent` — merge security/destructive examples globally; project may refine risk-specific severity. | `W-REVIEW`. | SC-01 | mapped |
| REVIEW-05 | A review report can be complete with open severe findings; those findings make the reviewed change unready. | `SP review-closure.md:26-41`; `WC codex-review.md:45-51` | `merge` — important completion distinction. | `W-REVIEW`. | SC-01 | mapped |
| REVIEW-06 | Remediation closes only when no in-scope P0/P1 remains, checks/gaps are explicit, P2 is classified, and closeout states changes/deferred work. | `SP review-closure.md:43-54`; `WC codex-review.md:53-55` | `merge` — generic. | `W-REVIEW`. | SC-01 | mapped |
| REVIEW-07 | Stop based on evidence and unchanged severe findings, not a mandatory count of broad passes; do not edit for wording polish alone. | `SP review-closure.md:56-64`; `WC codex-review.md:57-60` | `behavior-change-pending-decision` — “two consecutive passes” may require a redundant pass and is not risk-sensitive. | Outcome-based stop in `W-REVIEW`; `DQ-07`. | SC-01 | mapped / DQ-07 |
| REVIEW-08 | Generic bugfix/feature/refactor/maintenance scenarios move to the workspace owner; operations/docs retain only Saberu live/artifact deltas. | `SP scenarios/review-*.md` | `split` — most content is universal; keeping all project copies creates two owners. | `W-REVIEW`; `S-LIVE` and `S-DOC` keep deltas; remove generic project scenario files or turn them into thin adapters. | SC-01, SC-10, SC-13 | mapped |
| REVIEW-09 | Decide whether destructive-sink code requires an independent reviewer from observable risk and available review channels; do not hard-code a named agent/tool or treat self-review as categorically invalid. | `WCL:39-41` | `behavior-change-pending-decision` — independent review can reduce correlated blind spots, but the unconditional external-agent requirement can be unavailable, conflicts with active delegation constraints, and lacks a waiver authority. | `W-REVIEW` with the protected-action risk route in `W-AUTH`; `DQ-16`. | SC-01, SC-09 | mapped / DQ-16 |

### Capability selection

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| CAP-01 | Do a lightweight capability check for substantial resumption, large/repeated/cross-surface/high-risk work, a concrete specialized need, or repeated method failure. | `SP codex-capabilities.md:5-14`; `SP session-bootstrap.md:124-132`; `WC codex-capabilities.md:10-20` | `merge` — useful when conditional; must not load on every session. | `W-CAP`; remove project file if no toolchain delta. | SC-11, SC-12 | mapped |
| CAP-02 | Do not spend more effort discovering capabilities than the task warrants. | same as CAP-01 | `keep` — necessary proportionality guard. | `W-CAP`. | SC-11 | mapped |
| CAP-03 | Inspect visible capabilities first; deferred discovery must be task-shaped. | `SP codex-capabilities.md:16-21`; `WC codex-capabilities.md:22-25` | `merge` — generic. | `W-CAP`. | SC-11 | mapped |
| CAP-04 | Parallelize independent read-only evidence when useful; delegate only when active instructions permit and the subtask is concrete/independent. | `SP codex-capabilities.md:31-36`; `WC codex-capabilities.md:26-28` | `rewrite-equivalent` — current candidate correctly defers to active delegation rules. | `W-CAP`. | SC-11 | mapped |
| CAP-05 | Use current official documentation for changed product/API behavior and project scripts/environments/adapters before manual reinvention. | `SP codex-capabilities.md:18-21,31-36`; `WC codex-capabilities.md:29-32` | `merge` — generic, actionable. | `W-CAP`. | SC-11 | mapped |
| CAP-06 | Codify a recurring improvement at the narrowest owner: workspace for cross-project behavior, project adapter for project/toolchain behavior. | `SP codex-capabilities.md:38-46`; `WC codex-capabilities.md:37-39` | `rewrite-equivalent` — keep but do not require a changelog for every tool choice. | `W-CAP`. | ownership/static check | mapped |

### Secret safety

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| SECRET-01 | Never unnecessarily print, commit/push, copy into evidence/examples/logs, or relocate real secret values to tracked paths. | `W0` safety/ownership; `SP secrets-handling.md:6-15`; `WC codex-secrets.md:12-21`; managed router `51-52` | `merge` — compact resident floor plus canonical incident rule. | Managed floor + `W-SECRET`; project keeps placement only. | SC-14 | mapped |
| SECRET-02 | On discovery stop exposure, identify state without value, redact, determine all reached surfaces, then route Git/external remediation. | `SP secrets-handling.md:8-15`; `WC codex-secrets.md:23-32` | `merge` — complete global response recipe. | `W-SECRET`. | SC-14 | mapped |
| SECRET-03 | Discovery never authorizes index/history/remote deletion, force push, rotation, revocation, or destruction. | `SP secrets-handling.md:11-13`; `WC codex-secrets.md:34-35` | `merge` — critical authorization boundary. | `W-SECRET` referencing `W-AUTH/W-GIT`. | SC-14 | mapped |
| SECRET-04 | Before creating/moving/consuming secrets, read project store/path/access/rotation/verification rules. | `SP secrets-handling.md:17-42`; `WC codex-secrets.md:37-46` | `split` — generic routing global, concrete locations project. | `W-SECRET` + `S-SECRET`. | SC-14 | mapped |
| SECRET-05 | Record only identifiers, locations, ownership, and lifecycle evidence needed for reproducibility, never values. | `SP execution-reflection.md:66-79`; `SP secrets-handling.md:40-42`; `WC codex-secrets.md:48-49` | `merge` — generic floor; project resource schema remains. | `W-SECRET`; `S-LIVE` resource fields. | SC-10, SC-14 | mapped |

### Environment truth

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| ENV-01 | Treat environment/remote capability claims as dated snapshots, not invariants. | `W0:28-34`; `WE:3-18`; `WC managed router:55-56` | `merge` — compact resident reminder plus canonical detail. | Managed floor + `W-ENV`. | SC-11 | mapped |
| ENV-02 | Re-probe before a capability claim becomes a plan prerequisite, blocked verdict, skipped check, or operator delegation. | `WE:12-18`; `SP coding-plan.md:46`; `SP session-bootstrap.md:59-74` | `merge` — generic; project should not copy procedure. | `W-ENV`; project maps task to project command only. | SC-11, SC-12 | mapped |
| ENV-03 | Memory, old plans/changelogs, and old user statements age and cannot alone support a current environment verdict. | `WE:20-27` | `keep` — accurate. | `W-ENV`. | SC-11 | mapped |
| ENV-04 | When a probe contradicts a record, update the living record with date and report publication state; do not automatically require a same-round commit. | `WE:28-36,45-52` | `behavior-change-pending-decision` — current “commit in same round” conflicts with separate Git authorization and can create administrative publication. | `W-ENV`; `DQ-08`. | SC-06, SC-11 | mapped / DQ-08 |
| ENV-05 | Per-host registry is generated by the probe command, never hand-edited, and contains capability facts/hints but no project task mapping. | `WE:38-55` | `rewrite-equivalent` — correct ownership boundary; keep generation detail. | `W-ENV`. | static registry check | mapped |
| ENV-06 | Consult registry first; refresh when missing/stale, but any observed failure invalidates the relevant entry immediately. | `WE:45-50`; `W0:28-34`; `SP session-bootstrap.md:59-74` | `merge` — canonical once; router only on load-bearing trigger. | `W-ENV`. | SC-11, SC-12 | mapped |
| ENV-07 | A blocked verdict cites fresh host/probe evidence; bare-host absence does not prove a project venv/container/Makefile cannot run a check. | `W0:26-34`; `WE:18,51-55` | `merge` — accuracy-critical. | `W-ENV`; project testing maps alternative environments. | SC-11 | mapped |
| ENV-08 | Do not force environment/capability refresh during every bootstrap when no capability claim is load-bearing; the existing SessionStart drift evaluator and task trigger route it conditionally. | `WE:57-61`; `SP AGENTS.md:19-35`; `SP session-bootstrap.md:59-74,124-132` | `behavior-change-pending-decision` — current duplicated mandatory reads/probes increase startup cost. | Managed router + `W-ENV`; `S-ADAPTER` removes duplicate bootstrap requirement; `DQ-09`. | SC-11, SC-12 | mapped / DQ-09 |
| ENV-09 | A bare-host registry result does not decide whether Saberu can run a tool from its venv; do not hard-code current `available: false` snapshots in a project rule, and use project testing governance for task-to-command mapping. | `SP .agents/env/README.md:12-28`; `W0:33-34`; `WE:53-55` | `demote` — the project override principle is correct, but literal availability values age and belong in the generated registry. | `W-ENV` generic principle; `S-TEST` command mapping; slim project environment adapter. | SC-11, SC-15 | mapped |

### Verification

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| VERIFY-01 | After a change, verify direction, syntax/static correctness, and functional behavior in proportion to the changed surface; a parser/linter does not substitute for executing the changed workflow when execution is feasible. | `WCL:28-35`; `W0` verification floor; workspace-meta/Saberu project check routes | `merge` — agent-neutral and accuracy-critical, but project commands remain project-owned. | Compact managed floor plus `W-VERIFY`; project testing supplies commands. | SC-02, SC-15, SC-17 | mapped |
| VERIFY-02 | A fix after a failed check reruns the affected and downstream checks needed to regain one coherent result; repeated failure triggers diagnosis and an explicit blocked/gap report, not a universal fixed restart order or automatic three-attempt verdict. | `WCL:30-35` | `behavior-change-pending-decision` — restart-from-gate-one is sometimes correct, but a fixed order and iteration cap can waste work or stop before/after the evidence warrants. | `W-VERIFY`; `DQ-15`. | SC-15, SC-17 | mapped / DQ-15 |

## 5. Saberu branch topology and lifecycle delta

Generic contract/publication/integration/retirement behavior is owned by
`W-GIT`. These rows are the narrower Saberu additions that remain project
owned.

| ID | Trigger and normalized required behavior | Current source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| BR-01 | `dev` is development integration; `master` receives release promotion and is not a feature target. | `SP branching.md:13-21`; `CLAUDE.md:66-82` | `merge` — project fact duplicated in resident Claude adapter. | `S-BRANCH`; replace Claude table with link. | SC-04, SC-07 | mapped |
| BR-02 | No direct commit/push to `dev`/`master`; normal integration uses reviewed PR. | same | `keep` — project policy. | `S-BRANCH`; compact adapter reference only. | SC-07 | mapped |
| BR-03 | One deliverable goal has one owner branch and one functional topic root; children own declared sub-goals only. | `SP branching.md:22-24`; workstream adapters | `keep` — directly addresses branch proliferation. | `S-BRANCH`. | SC-04, SC-05 | mapped |
| BR-04 | Branch prefix does not prove lineage, dependency, target, or state. | `SP branching.md:25-26`; `SP docs/workstreams/AGENTS.md:30-33` | `merge` — one project owner; adapter references contract. | `S-BRANCH`. | SC-04 | mapped |
| BR-05 | Project-wide governance/shared baseline starts at exact fetched `origin/dev`; use short-lived `gov/<topic>`, integrate to `dev`, then archive rather than keep a permanent policy branch. | `SP branching.md:27-43`; `CLAUDE.md:90-92` | `merge` — user-approved project topology. | `S-BRANCH`; remove duplicate Claude prose. | SC-04, SC-08 | mapped |
| BR-06 | Changing remote default branch is a separate external write; desired default is `dev` after baseline. | `SP branching.md:17-19` | `keep` — precise project/remote fact. | `S-BRANCH`. | SC-10 | mapped |
| BR-07 | Git supplies dynamic checkout/divergence facts; do not hard-code them in TODO/workstream contracts. | `SP branching.md:44-45`; `SP docs/workstreams/AGENTS.md:65-67` | `merge` — project artifact rule. | `S-BRANCH`; adapter reference. | SC-12 | mapped |
| BR-08 | `stg` is an environment unless an approved branch policy creates a ref. | `SP branching.md:46-47` | `keep` — Saberu naming disambiguation. | `S-BRANCH`. | static ref/name scenario | mapped |
| BR-09 | Persist owner contracts in workstream README; small contained child may use a complete subsection, independent lifecycle gets linked README, and parent indexes children. | `SP branching.md:49-65`; `SP file-naming.md:49-56`; `SP docs/workstreams/AGENTS.md:16-35` | `merge` — project persistence schema repeated three times. | `S-BRANCH` owns schema; `S-DOC`/adapter links only. | SC-04, SC-13 | mapped |
| BR-10 | Project contract adds owner branch and one relationship enum to the generic contract. | `SP branching.md:67-85` | `keep` — project topology delta. | `S-BRANCH`; project README template references it. | SC-04 | mapped |
| BR-11 | Project contract adds lifecycle state. | same | `keep` | `S-BRANCH`. | SC-04, SC-08 | mapped |
| BR-12 | Project contract adds created-from ref and immutable base commit. | same | `keep` — generic branch contract also requires exact base; Saberu persists it. | `S-BRANCH` persistence delta. | SC-04 | mapped |
| BR-13 | Project contract adds intended integration target. | same | `keep` | `S-BRANCH`. | SC-04, SC-07 | mapped |
| BR-14 | Project contract adds prerequisites plus contained-child and independent-dependent reverse edges. | same | `keep` | `S-BRANCH`. | SC-04, SC-07 | mapped |
| BR-15 | Project contract adds current action/blockers and project closeout/post-integration route; generic problem/scope/acceptance/publication/retirement fields are referenced, not restated. | same | `split` — current table mixes generic and project fields. | `S-BRANCH` retains only delta and persistence. | SC-04, SC-08 | mapped |
| BR-16 | Unknown contract value is explicit; update both sides of topology edges on branch transitions; link detailed checks rather than copy them. | `SP branching.md:86-91` | `keep` — accurate and reduces duplication. | `S-BRANCH`. | SC-04 | mapped |
| BR-17 | Relationship routes for root/baseline/governance/contained/dependent/hotfix/release are the table in `branching.md`. | `SP branching.md:93-126`; `CLAUDE.md:74-87` | `merge` — project table once. | `S-BRANCH`; Claude link only. | SC-04, SC-07 | mapped |
| BR-18 | Contained work returns to parent; independent dependent work targets `dev` only after prerequisite reaches `dev`; feature never targets `master`; hotfix follows master/backport. | same | `keep` — project topology. | `S-BRANCH`. | SC-07 | mapped |
| BR-19 | Stack collapse requires an explicit recorded decision naming absorbed branches and workstream closeout. | `SP branching.md:118-126`; `SP git.md:110-113` | `merge` — topology owner should define once. | `S-BRANCH`; remove project Git copy. | SC-07 | mapped |
| BR-20 | Before new planning/implementation, classify relevant branches: ready work goes to integration preparation; integrated work triggers trunk reconciliation; active branch accepts only in-scope work. | `SP branching.md:128-160`; `SP coding-plan.md:29-38`; `SP session-bootstrap.md:76-118` | `merge` — behavior is project-specific but repeated in three files. | `S-BRANCH`; bootstrap/planning adapters link and report result. | SC-04, SC-12 | mapped |
| BR-21 | A dependent stack is exceptional and must record prerequisite/reverse edge/base/target/reason/exit; convenience/dirty state is insufficient. | `SP branching.md:148-152` | `keep` | `S-BRANCH`. | SC-04, SC-07 | mapped |
| BR-22 | Governance that controls implementation must reach `dev` before dependent implementation resumes, with a narrow documented bootstrap exception only. | `SP branching.md:154-160`; `SP coding-plan.md:36-38` | `merge` — user-approved order rule. | `S-BRANCH`; planning adapter references it. | SC-04 | mapped |
| BR-23 | Split a child only for independent risk/verification, concurrency/ownership, rollback/integration risk, or separate approval/evidence; do not branch for every small work unit. | `SP branching.md:162-172` | `keep` — efficient topology rule. | `S-BRANCH`. | SC-04 | mapped |
| BR-24 | New root/baseline selects exact fetched `origin/dev`; exceptional stack records why; classify relationship/target and add project fields to the reviewed generic branch action. | `SC branching.md:174-188`; `SC git.md:40-59` | `split` — generic transaction goes to `W-GIT`; topology stays here. | `S-BRANCH` delta referencing GIT-11/GIT-12. | SC-04 | mapped |
| BR-25 | Contract/reverse edge is first governance content in new worktree and may publish with first logical implementation unit; no registration-only commit/activation PR/successor branch. | `SC branching.md:185-194` | `behavior-change-pending-decision` — accepted correction to prior base-registration loop; global portion is DQ-01C/DQ-02. | `W-GIT` generic; `S-BRANCH` persistence delta. | SC-04–SC-06 | mapped / DQ-01C,DQ-02 |
| BR-26 | Contained children integrate leaf-first; parent cannot be ready with unresolved child; dependent features retarget/sync after prerequisite; siblings route through parent or explicit reparenting. | `SP branching.md:200-218` | `keep` — project topology. | `S-BRANCH`. | SC-07 | mapped |
| BR-27 | Sync from integration ancestor by merge, not rebase, unless history rewrite is separately authorized. | `SP branching.md:217-218` | `keep` — project history policy plus global authorization. | `S-BRANCH` policy referencing `W-GIT`. | SC-07, SC-09 | mapped |
| BR-28 | Lifecycle states are PLANNED, ACTIVE, BLOCKED, READY_FOR_INTEGRATION, INTEGRATED, ARCHIVED, CANCELLED with their current meanings. | `SP branching.md:220-233` | `keep` — project schema. | `S-BRANCH`. | SC-08 | mapped |
| BR-29 | State transitions follow the declared graph; readiness can return to active; integrated source receives no implementation commits; cancelled revival is newly classified. | `SC branching.md:235-253` | `rewrite-equivalent` — current candidate correctly removes source/closeout recursion. | `S-BRANCH`; generic terminal-evidence principle in `W-GIT`. | SC-08 | mapped |
| BR-30 | Ready gate requires accepted goal/partial transfer, synchronized living truth, checks/gaps, reviewed candidate/publication state, target diff, no P0/P1, resolved children, and prerequisites actually on target. | `SC branching.md:255-279` | `split` — project readiness owns topology/doc/check fields; generic publication readiness stays `W-GIT`. | `S-BRANCH` project gate referencing `W-GIT/W-REVIEW`. | SC-06, SC-07 | mapped |
| BR-31 | Normal integration is PR; stacked histories prefer merge; squash requires durable exact PR metadata; lack of branch protection does not weaken policy. | `SP branching.md:281-298` | `keep` — project integration/archive constraint. | `S-BRANCH`. | SC-07 | mapped |
| BR-32 | After integration capture metadata, update active parent for child evidence, verify target, retarget dependents, classify worktrees, separately archive, and continue on next classified target owner. | `SC branching.md:300-318` | `rewrite-equivalent` — remove mandatory immediate worktree removal and administrative closeout branch. | `S-BRANCH`, referencing GIT-36/GIT-37. | SC-08 | mapped |
| BR-33 | After root/baseline/dependent reaches `dev`, fetch target, inventory worktrees/contracts, classify each survivor's sync route, update edges/debt, then create new independent branch from exact refreshed tip. | `SP branching.md:328-351`; `SP session-bootstrap.md:89-114` | `merge` — this is the user's required branch-management behavior and must remain project-owned. | `S-BRANCH`; bootstrap reports it without duplicating algorithm. | SC-12 | mapped |
| BR-34 | Reconciliation assessment does not blanket-authorize merges into survivors. | `SP branching.md:349-351` | `keep` — authorization precision. | `S-BRANCH` referencing `W-GIT`. | SC-12 | mapped |
| BR-35 | Archive is not automatic cleanup; backup ref is not completion/integration evidence; Saberu archive uses the project script/tag policy under separate exact authorization. | `SP branching.md:353-355`; `CLAUDE.md:95-100` | `merge` — project archive delta once. | `S-BRANCH`; Claude link only. | SC-08, SC-09 | mapped |
| BR-36 | Multi-machine resume reports unpublished branch and true ahead/behind after freshness; clean tree does not imply remote freshness/prerequisite integration. | `SP branching.md:357-376`; `SP session-bootstrap.md:42-57` | `merge` — generic fetch/range in `W-GIT`, project lifecycle interpretation here. | `S-BRANCH` delta plus `W-GIT`. | SC-12 | mapped |

## 6. Saberu live operations, secrets, testing, and implementation deltas

### Live/external operations

| ID | Normalized project behavior | Source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| LIVE-01 | Treat playbook/Semaphore mutation and controller token as real-machine/destructive capability. | `SP boundaries.md:26-30` | `keep` — Saberu risk fact. | `S-LIVE`. | SC-10 | mapped |
| LIVE-02 | Test-host mutation needs per-run review or a complete bounded standing authorization; managed fleet remains per-run. | `SP authorization.md:154-173`; `SP boundaries.md:31-36`; `SP review-operations.md:15-18` | `merge` — project live policy repeated. | `S-LIVE`. | SC-10 | mapped |
| LIVE-03 | Standing test authorization records exact targets/count, allowed operations/phases/window/attempts, impact/exclusions, recovery owner/evidence, and explicit grant. | `SP authorization.md:159-169` | `keep` — precise project schema. | `S-LIVE`. | SC-10 | mapped |
| LIVE-04 | Revalidate target/operation/impact/recovery; mismatch, expansion, exhausted attempts, or fleet transition expires standing authorization. | `SP authorization.md:170-173` | `keep` | `S-LIVE`, inheriting generic AUTH-14. | SC-10 | mapped |
| LIVE-05 | A genuinely non-mutating syntax/audit/check run follows verification rules; do not infer safety from a dry-run label when behavior can still mutate. | `SP boundaries.md:37-38`; `SP review-operations.md:15-18` | `rewrite-equivalent` — current wording is too broad about `--check`; classify actual playbook/task effect. | `S-LIVE`. | SC-10 | mapped |
| LIVE-06 | Resolve inventory match/blast radius before triggering. | `SP boundaries.md:39-41` | `keep` — actionable. | `S-LIVE`. | SC-10 | mapped |
| LIVE-07 | Final go/no-go records target/count, operation, credential location, impact, recovery owner, evidence, and authorization mode. | `SP execution-reflection.md:46-64`; `SP boundaries.md:42-45` | `merge` — one project gate. | `S-LIVE`. | SC-10 | mapped |
| LIVE-08 | External-resource ledger records project-specific identifiers/lifecycle for inventory, key, template, token, and VPS without secret values. | `SP execution-reflection.md:66-79` | `keep` — Saberu schema. | `S-LIVE`; reference `W-SECRET`. | SC-10, SC-14 | mapped |
| LIVE-09 | Manual UI secret/live changes record actor/role, identifiers/sanitized evidence, backfill reproducible non-secret state to IaC, or record drift/owner. | `SP execution-reflection.md:81-89` | `keep` — project operational delta. | `S-LIVE`. | SC-10 | mapped |
| LIVE-10 | Substantial live/cross-system round records a short contradiction/rules-gap/next-probe reflection. | `SP execution-reflection.md:91-100` | `rewrite-equivalent` — keep conditional; do not require for ordinary local work. | `S-LIVE`. | SC-10 | mapped |

### Project secret placement

| ID | Normalized project behavior | Source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| PSECRET-01 | `make detect-secrets` gates project verify; findings need reasoned resolution, not casual baseline expansion. | `SP secrets-handling.md:14-15` | `keep` | `S-SECRET`/`S-TEST`. | SC-14 | mapped |
| PSECRET-02 | Controller token, vault password, encrypted vars, operator env secrets, mounted keys, and Semaphore Key Store placeholders use the declared project locations/patterns. | `SP secrets-handling.md:17-27` | `keep` — current project placement SSOT. | `S-SECRET`. | SC-14 | mapped |
| PSECRET-03 | Manifest sync carries ports/image tags, not secrets. | `SP secrets-handling.md:28-31` | `keep` — project architecture constraint. | `S-SECRET`. | SC-14 | mapped |
| PSECRET-04 | Secret-bearing Ansible tasks set `no_log: true`. | `SP secrets-handling.md:32` | `keep` — project/tool requirement. | `S-SECRET`. | SC-14 | mapped |
| PSECRET-05 | Project evidence redacts real secret-adjacent infrastructure identifiers according to evidence policy. | `SP secrets-handling.md:33-34` | `rewrite-equivalent` — do not classify all hostnames/IPs as secrets globally; keep as Saberu evidence privacy rule. | `S-SECRET` + `S-DOC`. | SC-14 | mapped |
| PSECRET-06 | New secret location updates ignore boundary, operator example/docs, and placement table in one logical change. | `SP secrets-handling.md:35-36` | `keep` — project synchronization requirement, not publication requirement. | `S-SECRET`. | SC-14 | mapped |
| PSECRET-07 | A plan with duplicate secret copies records necessity, access, rotation, and removal path. | `SP secrets-handling.md:37-39` | `keep` — project risk control. | `S-SECRET` referenced by `S-PLAN`. | SC-14 | mapped |

### Testing, docs synchronization, and implementation boundaries

| ID | Normalized project behavior | Source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| TEST-01 | Testing governance decision tree is canonical; run the smallest set matching the touched surface and report skipped/blocked checks. | `SP testing.md:1-10`; generic verification in `W0` | `keep` project command mapping; generic blocked semantics global. | `S-TEST` + managed/W-ENV floor. | SC-15 | mapped |
| TEST-02 | Docs/governance changes verify paths/commands/references/diff; code/role/playbook surfaces follow stronger named rows. | `SP testing.md:5-10`; `SP review-closure.md:34-38` | `merge` — project test routing once. | `S-TEST`; `W-REVIEW` references project checks. | SC-01, SC-15 | mapped |
| SYNC-01 | Behavior/structure/operator-workflow change evaluates architecture, README, feature map, changelog, and feature index sync targets. | `SP docs-sync.md:1-14`; `CLAUDE.md:20-25` | `merge` — project-specific, duplicated in resident Claude file. | `S-DOC` (`docs-sync.md`); Claude link only. | SC-13, SC-15 | mapped |
| SYNC-02 | Test target/surface rename/add/remove updates testing governance and only updates TSVS index when coverage registration changes. | `SP docs-sync.md:15-21` | `keep` — precise and conditional. | `S-DOC`/`S-TEST`. | SC-13, SC-15 | mapped |
| SYNC-03 | Path/command rename updates executable references and living canonical docs/active plans; completed historical evidence keeps literal text unless a migration pointer is needed. | `SP docs-sync.md:22-26` | `keep` — this is the desired payload rename behavior and correctly separates living from historical truth. | `S-DOC`. | SC-13 | mapped |
| SYNC-04 | Workflow/governance change also checks project governance docs. | `SP docs-sync.md:27` | `keep` | `S-DOC`. | SC-13 | mapped |
| BOUND-01 | Before project implementation edits, name scope/reason/exclusions and preserve control-plane/data-plane separation. | `SP boundaries.md:10-23`; `SP architecture.md:28-29` | `split` — generic scope statement global; architecture delta project. | `W-AUTH` + `S-TRUTH` architecture. | SC-02, SC-15 | mapped |
| BOUND-02 | Inventory model/deployment/plugin ownership changes consult architecture/TODO/active workstream; investigations are not mandates without living owner. | `SP boundaries.md:17-24`; `SP overview.md:30` | `rewrite-equivalent` — correct but truth types must be explicit. | `S-TRUTH`/`S-PLAN`. | SC-13, SC-15 | mapped |
| CODE-01 | Coding/executable configuration tasks use project planning route; governance/plans/review notes do not load the coding checklist. | `SP coding-plan.md:1-5`; root scenario routes | `keep` — precise trigger. | `S-PLAN` thin project implementation adapter. | SC-05, SC-15 | mapped |
| CODE-02 | Project implementation planning reads only relevant architecture/feature/governance/workstream/current code and applies branch/live/secret/test deltas when triggered. | `SP coding-plan.md:20-47` | `rewrite-equivalent` — replace long generic method copy with direct project routes. | `S-PLAN`; generic method in `W-PLAN`. | SC-05, SC-15 | mapped |
| CODE-03 | Bug/modify/new-feature scenarios keep only Saberu-specific source and sync routes; generic root-cause/style/scope/test behavior is globally owned. | `SP scenarios/fix-bug.md`, `modify-existing-feature.md`, `new-feature.md` | `split` — current short files still duplicate generic method. | Thin `S-ADAPTER` routes or remove when root routing is sufficient. | SC-15 | mapped |
| QUIRK-01 | Operational facts come from `docs/governance/operational-truths.md`; avoid duplicating version/pinning/latency facts in a rule module. | `SP operational-quirks.md:1-9` | `demote` — current rule is a drifting second copy; path adapters may name a load-bearing invariant. | `S-TRUTH`; delete or reduce rule to route. | static truth comparison | mapped |

## 7. Saberu plan/artifact and documentation ownership

| ID | Normalized project behavior | Source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| DOC-01 | Choose functional owner before artifact type/name; directory identifies owner and prefix identifies artifact. | `SP file-naming.md:1-7` | `keep` — useful project invariant. | `S-DOC`. | SC-13 | mapped |
| DOC-02 | The canonical location/name table in `file-naming.md` owns task ledger, hub, plan types, decision, review, round, investigation, stable design, runbook, user, governance, and test contract routing. | `SP file-naming.md:8-27`; repeated in docs adapters | `merge` — table once; adapters link. | `S-DOC`; replace adapter copies. | SC-13 | mapped |
| DOC-03 | A functional topic uses exactly one root: new/migrated in `docs/workstreams`, unmigrated legacy wholly in `docs/reviews`. | `SP file-naming.md:29-47`; `docs/AGENTS.md`; `docs/reviews/AGENTS.md`; `docs/workstreams/AGENTS.md` | `merge` — project-specific but repeated extensively. | `S-DOC`; path adapters add only “this subtree is legacy/current.” | SC-13 | mapped |
| DOC-04 | Topic-owned lifecycle material stays in one functional bundle; independently lived stable architecture/investigation/runbook/governance/test docs remain canonical and are linked, not copied. | `SP file-naming.md:43-72`; docs adapters | `merge` | `S-DOC`; adapters route. | SC-13 | mapped |
| DOC-05 | New/reorganized active bundle has a README hub with function, contract link/delta, artifact map, current action, and stable links; existing bundle adopts on material reorganization. | `SP file-naming.md:49-56`; `docs/workstreams/AGENTS.md:16-35` | `merge` — contract field list itself belongs in `S-BRANCH`, not adapter. | `S-DOC` hub rule referencing `S-BRANCH`. | SC-04, SC-13 | mapped |
| DOC-06 | Whole-topic migration moves complete tracked directory, preserves historical names/content absent separate correction, and updates links; absorption retains predecessor evidence under destination history. | `SP file-naming.md:58-67`; docs adapters | `merge` — project history safeguard. | `S-DOC`. | SC-13 | mapped |
| DOC-07 | Do not create another child plan to restate approved work. | `SP file-naming.md:74-76`; `SP coding-plan.md:59-63` | `merge` — generic principle in `W-PLAN`; project rule only routes artifact. | `W-PLAN`; project reference. | SC-05, SC-13 | mapped |
| DOC-08 | New plan filenames use direction/execution/addendum type, descriptive slug, and creation date; historical names remain valid. | `SP file-naming.md:80-117`; `SP plan-structure.md:260-273` | `merge` — project naming once. | `S-DOC`; remove duplicate naming section from plan structure. | SC-13 | mapped |
| DOC-09 | Round evidence uses one monotonically numbered file per coherent work round, not per chat/phase/administrative closeout. | `SP file-naming.md:121-128`; current text says one file per work round | `behavior-change-pending-decision` — define “round” to avoid evidence/PR multiplication. | `S-DOC`; `DQ-10`. | SC-13 | mapped / DQ-10 |
| DOC-10 | Decision records preserve authority/rationale and promote current conclusion to stable truth without replacing provenance. | `SP file-naming.md:131-155`; `SP plan-hierarchy.md:25-40` | `merge` — project artifact rule. | `S-DOC`. | SC-13 | mapped |
| DOC-11 | Topic investigation stays with topic; cross-topic IVG uses global investigation index; contradictory updates append dated update rather than rewrite; never keep two live copies. | `SP file-naming.md:159-175` | `keep` — clear project routing. | `S-DOC`. | SC-13 | mapped |
| DOC-12 | Bundle lifecycle changes remain colocated; historical deletion needs exact authorization; bundle removal updates TODO and stable links. | `SP file-naming.md:177-187`; docs adapters | `merge` — project history delta plus global authorization. | `S-DOC` referencing `W-AUTH`. | SC-13 | mapped |
| DOC-13 | TSVS and feature-map files follow their living naming/index rules; AGENTS routing file is exactly `AGENTS.md`. | `SP file-naming.md:191-215` | `keep` — project structure. | `S-DOC`. | SC-13, SC-15 | mapped |
| PPLAN-01 | The detailed project plan schema applies only to approval-gated L2 direction/execution/addendum artifacts, not investigations/design/decision/review/runbook/ledger/evidence. | `SP plan-structure.md:1-19` | `rewrite-equivalent` — keep trigger but remove duplicated artifact catalog. | `S-PLAN` referencing `S-DOC` and `W-PLAN`. | SC-05, SC-13 | mapped |
| PPLAN-02 | New L2 approval artifact records status/date/branch/classification/type/scope/blocks-implementation and relationships when applicable. | `SP plan-structure.md:42-66`; `SP plan-hierarchy.md:42-53` | `merge` — project persistence schema once. | `S-PLAN`. | SC-05 | mapped |
| PPLAN-03 | Plan lifecycle distinguishes draft, pending, approved, completed, superseded and records approval/completion/update dates. | `SP plan-structure.md:67-91` | `rewrite-equivalent` — preserve states; revise material-change transition under DQ-06. | `S-PLAN`. | SC-05 | mapped / DQ-06 |
| PPLAN-04 | Plan explains problem/consequence/trigger, current facts/assumptions, in/out scope/unknown gates, concrete implementation, observable verification, material risks/fallbacks, and completion handoff. | `SP plan-structure.md:95-228` | `rewrite-equivalent` — required content matters more than mandatory section order/template repetition. | `S-PLAN`; move verbose examples to project template/governance docs if retained. | SC-05 | mapped |
| PPLAN-05 | L2 plan has an explicit pre-implementation approval gate; steps name concrete files/commands/APIs; unknown runtime branches name next action. | `SP plan-structure.md:164-177` | `keep` — project L2 rigor, with DQ-04 removing commit-shaped phase requirement. | `S-PLAN`. | SC-05, SC-10 | mapped |
| PPLAN-06 | Verification states method, pass condition, and observable evidence; manual fallback is allowed when live environment is unavailable. | `SP plan-structure.md:181-196` | `rewrite-equivalent` — keep observable evidence, apply DQ-05 to publication. | `S-PLAN` + `S-TEST`. | SC-05, SC-15 | mapped / DQ-05 |
| PPLAN-07 | Completion synchronizes named project truth, resolves child ownership, records remaining work/reflection, and never authorizes merge/push/archive. | `SP plan-structure.md:210-228` | `split` — project sync/branch fields remain; generic protected-action distinction global. | `S-PLAN`, `S-DOC`, `S-BRANCH`, referencing `W-GIT`. | SC-05, SC-08 | mapped |
| PPLAN-08 | Anti-pattern guidance is converted into positive/testable requirements or template examples; it is not a second normative copy. | `SP plan-structure.md:232-256` | `rewrite-equivalent` — current list repeats earlier rules. | Keep only unique failure examples in a non-normative template/reference. | static duplication test | mapped |
| PPLAN-09 | TODO represents parent/child plan scope and state without flattening all work into one status. | `SP plan-hierarchy.md:71-82` | `keep` — Saberu task-ledger delta. | `S-PLAN`/`S-DOC`. | SC-05, SC-13 | mapped |
| PPLAN-10 | Conflicting plan layers identify conflict type, preserve approved direction until superseded, record dated change, and update current task authority. | `SP plan-hierarchy.md:84-94` | `rewrite-equivalent` — generic approval semantics global; project artifact actions local. | `W-PLAN` + `S-PLAN/S-DOC`. | SC-05 | mapped |

## 8. Routers, source-of-truth semantics, and path adapters

| ID | Normalized behavior | Source | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| ROUTE-01 | Managed/root AGENTS stays a compact safety floor and direct task-to-owner router; do not make it a monolith or load unrelated modules. | `SP AGENTS.md:1-15,101-105`; `WC managed router:1-41` | `rewrite-equivalent` — correct design goal; root still over-routes some tasks. | Managed router + Saberu root adapter. | SC-11, SC-12 | mapped |
| ROUTE-02 | Saberu bootstrap trigger is session start/context reset/status request; perform read-only status/log scan, read project overview/TODO and active topic hub/evidence, then summarize branch/task/debt. | `SP AGENTS.md:17-37`; `SP session-bootstrap.md:1-40,76-122` | `merge` — root and module duplicate the full procedure. | Root adapter names trigger/module; slim `session-bootstrap.md` owns project report delta and references `W-GIT/W-ENV`. | SC-12 | mapped |
| ROUTE-03 | Bootstrap itself does not edit/stage/commit/switch/pull/push; only the bounded freshness fetch exception applies when substantial work resumes. | `SP AGENTS.md:37`; `SP session-bootstrap.md:42-57,120-122` | `merge` — project bootstrap behavior. | Slim project bootstrap referencing `W-GIT`. | SC-12 | mapped |
| ROUTE-04 | Capability rule is not a mandatory bootstrap read; route it only when CAP-01 trigger is present. | `SP AGENTS.md:24-28`; `SP session-bootstrap.md:124-132` | `behavior-change-pending-decision` — reduces recurring context with no loss. | Root/bootstrap adapter change; `DQ-09`. | SC-11, SC-12 | mapped / DQ-09 |
| ROUTE-05 | Root task routes go directly to the smallest project delta; generic authorization/Git/planning/review/capability/secret behavior comes from workspace modules. | `SP AGENTS.md:39-100`; candidate ownership plan | `rewrite-equivalent` — current routes often load 3–6 project files containing duplicate generic method. | Saberu root adapter revised after workspace install. | SC-01–SC-15 | mapped |
| ROUTE-06 | Instruction precedence and repository truth are different axes: system/developer/user/AGENTS precedence governs instructions; code/config/docs provide typed facts and cannot silently override policy. | `SP agent-strategy.md:23-51`; `SP overview.md:5-19`; `CLAUDE.md:11` | `behavior-change-pending-decision` — current single “decision order” lets a fact source appear to override instructions. | `S-ADAPTER` strategy rewrite; `DQ-11`. | SC-01, SC-15 | mapped / DQ-11 |
| ROUTE-07 | Project truth is typed, not one universal linear order: code/config for actual behavior, architecture/governance for intended invariants, TODO/workstream for active scope/state, feature maps/operator docs for documented surfaces. | `SP overview.md:5-30`; `SP agent-strategy.md:23-38`; `SP architecture.md` | `behavior-change-pending-decision` — current “prefer current repo truth” is ambiguous and can privilege stale docs or code over accepted direction. | `S-TRUTH` overview/strategy rewrite; `DQ-11`. | SC-05, SC-15 | mapped / DQ-11 |
| ROUTE-08 | `CLAUDE.md` is a Claude adapter, not a competing policy owner; remove unsupported `<thinking>`/chain-of-thought output instruction and replace sync/branch tables with canonical links and genuine Claude-only deltas. | `CLAUDE.md:1-103` | `remove-obsolete` plus `merge` — chain-of-thought instruction is unsuitable; branch/sync tables duplicate project SSOTs. | Slim `S-ADAPTER` Claude file. | static ownership/duplication check | mapped |
| ROUTE-09 | `.agents/project/architecture.md` routes architecture-sensitive surfaces to stable docs and keeps only project-level separation/manifest SSOT facts. | `SP architecture.md:1-29` | `rewrite-equivalent` — useful router; avoid repeating docs artifact policy. | `S-ADAPTER`/`S-TRUTH`. | SC-15 | mapped |
| ROUTE-10 | Controller/audit/EDA/inventory/playbooks/roles path AGENTS route to project architecture/testing and state only coupled-surface or path-local deltas. | all non-doc path `AGENTS.md` | `rewrite-equivalent` — most are already small; remove generic duplicated phrases where owner exists. | `S-ADAPTER`; keep unique path constraints. | SC-15 | mapped |
| ROUTE-11 | Docs root/reviews/workstreams adapters identify subtree role and link to `file-naming`, `branching`, and plan rules; they do not repeat artifact tables, branch contract fields, migration rules, or authorization semantics. | `docs/AGENTS.md`, `docs/reviews/AGENTS.md`, `docs/workstreams/AGENTS.md` | `merge`/`rewrite-equivalent` — current adapters are second normative copies. | Slim `S-ADAPTER`; canonical owners `S-DOC/S-BRANCH/S-PLAN`. | SC-13 | mapped |
| ROUTE-12 | Topic-specific legacy adapter keeps only facts unique to that topic and does not treat historical plans as general current policy. | `docs/reviews/feat-target-architecture/AGENTS.md` | `rewrite-equivalent` — most content is a legitimate local delta. | `S-ADAPTER`. | SC-13 | mapped |
| ROUTE-13 | `playbooks/vps/AGENTS.md` routes to stable lifecycle/operator docs and the active rename workstream; historical plan/design are evidence, not unconditional live guidance. Rename “examples” to “payloads” only after the owning rename change is integrated. | `playbooks/vps/AGENTS.md:5-14`; active rename task | `behavior-change-pending-decision` — current historical references and terminology can become stale, but this governance task must not pre-apply the unfinished rename. | `S-ADAPTER`; defer path term to rename owner; `DQ-12`. | SC-13, SC-15 | mapped / DQ-12 |
| ROUTE-14 | Portable authorization, Git, planning, verification, review, secret, environment, and rule-authoring methods have agent-neutral workspace owners; Codex and Claude resident files are compact adapters that own only agent-specific mechanics and an intentional safety floor. | `W0`; `WCL:5-7,51,56,80-84`; `WC`; Saberu agent strategy | `behavior-change-pending-decision` — the current Codex-branded candidate cannot serve as a shared SSOT merely by renaming files, and the Claude adapter currently owns conflicting portable behavior. | Split neutral behavior from `C-ADAPTER`/`CL-ADAPTER`; exact module names and boundaries are `DQ-13`. | SC-16 plus ownership/duplication checks | mapped / DQ-13 |
| ROUTE-15 | For a materially long-running task, expose concise progress; when a durable execution/review/live round closes, report immediate, blocked, and deferrable follow-ups without forcing a new round artifact or fixed footer for every chat turn. | `WCL:66-67`; active interaction guidance; `DQ-10` | `split` — visible progress is useful agent interaction behavior; the unconditional “every round” footer is over-broad until round is defined. | Agent adapters carry progress behavior; `W-PLAN`/project evidence owner carries durable closeout. | SC-12, SC-13 | mapped |
| META-01 | Workspace-meta agent-configuration work reads its repository overview/architecture and creates the required plan/round evidence before non-trivial implementation. | workspace-meta `AGENTS.md:5-12` | `keep` — project-specific implementation gate, not a cross-project rule. | workspace-meta project `AGENTS.md`; no Saberu delta. | plan/evidence path check | mapped |
| META-02 | Workspace-meta keeps the reverse whitelist explicit and never commits credentials, executable authorization, trust/runtime state, or content outside its marked ownership surfaces. | workspace-meta `AGENTS.md:5-23`; ownership matrix | `keep` — repository safety boundary. | workspace-meta project `AGENTS.md` and architecture docs. | whitelist/ownership tests | mapped |
| META-03 | Workspace-meta changes run its named repository, syntax, parse, diff, and isolated-bootstrap idempotency checks; UI smoke remains manual evidence. | workspace-meta `AGENTS.md:25-37` | `keep` — project verification delta. | workspace-meta project `AGENTS.md`. | workspace test suite | mapped |
| META-04 | Workspace-meta leaves changes reviewable, reports uncommitted/unpushed state, and does not commit/push without the applicable user-level Git transaction. | workspace-meta `AGENTS.md:39-43`; `W0:121-122` | `rewrite-equivalent` — retain project synchronization expectation without defining a second publication workflow. | workspace-meta project `AGENTS.md` referencing `W-GIT`. | SC-06 | mapped |

## 9. Agent-neutral rule authoring and feedback

| ID | Trigger and normalized required behavior | Current source/owners | Verdict/rationale | Target/action | Evidence | Status |
|---|---|---|---|---|---|---|
| RULE-01 | When editing a rule/config/instruction owner, read the complete relevant owner, reconcile overlap/conflict/dead text, and land one coherent in-scope change; do not turn every approval into authorization for unrelated whole-file redesign. | `WCL:55`; workspace-meta/Saberu adapter boundaries | `rewrite-equivalent` — whole-owner review prevents append-only drift, but scope authorization still limits the edit. | `W-RULES` referencing `W-AUTH`. | SC-16, SC-17 | mapped |
| RULE-02 | Match a behavior rule's form to its observed failure: discipline-skip uses a firm prohibition, wrong shape uses a positive recipe, omission uses a required slot, and condition-dependent behavior uses an observable predicate. | `WCL:57`; `feedback-register.md` W-R27 | `keep` — one of the strongest accuracy improvements in the current rules; it is agent-neutral and should not remain Claude-only. | `W-RULES`; adapters link only. | rule-form trace in SC-16/SC-17 | mapped |
| RULE-03 | Route a recurring rule to the narrowest portable workspace/project owner, retain incident provenance, and treat a later recurrence as a refactor signal; host authorization/preferences remain host-local but must not depend on a nonexistent prose file. | `WCL:7,57,80-84`; `feedback-register.md` | `split` — provenance and recurrence are useful; the current route to absent `~/.claude/CLAUDE.md` is broken and cannot be a load-bearing owner. | `W-RULES` plus project adapters and actual host-local configuration; adapter boundary resolved by `DQ-13`. | SC-16 plus broken-reference check | mapped / DQ-13 |

## 10. Preservation and misclassification scenarios

Every scenario must produce a trace row with: input prompt/state, triggered
canonical owners, expected allowed action, required stop/review, forbidden
action, and captured evidence. Static ownership/link tests can support that
trace but cannot replace behavior evidence.

| Scenario | Required observation | Minimum evidence |
|---|---|---|
| SC-01 Review-only versus remediation | “review/audit” performs reads and reports findings; “fix/apply” permits bounded edits but no Git/live action. | trace row |
| SC-02 Ordinary edit | One scope/verification announcement is enough; no per-file or per-command conversational approval for writable-root edits/tests. | trace row |
| SC-03 Plan/permission separation | Plan approval does not stage/publish or run live operations; sandbox approval never expands scope. | trace row |
| SC-04 New branch | Complete problem→solution→acceptance→publication→integration/closeout→retirement contract and exact base/worktree action are reviewed before creation; interruption after creation but before persistence blocks implementation and restores the reviewed contract first. | trace row plus disposable local-Git walkthrough |
| SC-05 Plan shape | Small work uses a concise plan; L2 uses project schema; probes/runbooks/contracts do not become extra plans. | trace row |
| SC-06 Publication | Result accepted once, then one unchanged add/commit/push/PR bundle is either authorized once or operator-executed and verified read-only. | trace row plus disposable local repository/bare-remote walkthrough |
| SC-07 Integration | Source/target/topology/net diff/checks are reviewed separately; no excluded follow-up runs implicitly. | trace row |
| SC-08 Post-integration | PR/Git metadata closes source integration; no recursive closeout branch; retirement remains separate. | trace row |
| SC-09 Destructive Git | Exact effect/recovery/OIDs are reviewed; force lease and recovery verification are enforced. | trace row plus non-destructive command/rendering and disposable-ref walkthrough |
| SC-10 Live operation | Target/count/operation/impact/credential location/recovery/evidence/authorization are complete and revalidated. | trace row; no real live mutation |
| SC-11 Capability/environment | Capability lookup/probe occurs only when useful/load-bearing; current official or probe evidence supports claims. | positive and negative trace rows |
| SC-12 Resume/bootstrap | Current branch, remote freshness, lifecycle debt, governance order, and trunk reconciliation are reported without edits. | trace row |
| SC-13 Docs/artifact | One canonical topic root and artifact owner; living links update while historical literal evidence remains preserved. | trace row |
| SC-14 Secret incident | No value is reproduced; all reached states are classified; remediation does not run without the appropriate transaction. | trace row plus synthetic-secret walkthrough |
| SC-15 Project implementation | Path-local architecture, tests, docs sync, and operational deltas load without duplicating generic method. | trace row |
| SC-16 Cross-agent parity | The same portable task reaches the same neutral owner from Codex and Claude adapters; agent-specific mechanics do not redefine the portable behavior. | paired adapter→owner traces plus duplicate-owner check |
| SC-17 Verification/rule change | Changed behavior gets proportional direction/static/functional checks, and a rule edit demonstrates source incident→failure form→owner→scenario trace. | trace row plus one concrete rule-authoring walkthrough |

## 11. Source coverage reconciliation

The rows below account for every normative section in the declared source set.
Descriptive project facts with no instruction are still evaluated through the
truth/adapter rows when they affect routing.

### Workspace sources

| Source | Covered behavior IDs | Unmapped |
|---|---|---|
| `W0 .agents/host-templates/codex-AGENTS.md` | AUTH-01–AUTH-16, GIT-01–GIT-04, GIT-11, GIT-14, GIT-16–GIT-35, ENV-01, ENV-06–ENV-07, ROUTE-01 | 0 |
| `WE .agents/rules/environment-truth.md` | ENV-01–ENV-08 | 0 |
| `WC .agents/host-templates/codex-AGENTS.md` | AUTH-01, AUTH-07, AUTH-12–AUTH-15, GIT-22, ENV-01, ROUTE-01 | 0 |
| `WC codex-authorization.md` | AUTH-01–AUTH-16 | 0 |
| `WC codex-git.md` | GIT-01–GIT-05, GIT-11–GIT-35, GIT-37; missing contract fields are explicitly represented by GIT-06–GIT-10/GIT-12 | 0 |
| `WC codex-planning.md` | PLAN-01–PLAN-12 | 0 |
| `WC codex-review.md` | REVIEW-01–REVIEW-07 | 0 |
| `WC codex-capabilities.md` | CAP-01–CAP-06, PLAN-13 | 0 |
| `WC codex-secrets.md` | SECRET-01–SECRET-05 | 0 |
| workspace-meta `AGENTS.md` | META-01–META-04 | 0 |
| `W0/WC .agents/host-templates/README-codex.md` | AUTH-15, ROUTE-01, META-02 | 0 |
| `WC README.md` and `docs/architecture/codex-config-management.md` rule-ownership sections | AUTH-15, ROUTE-01, META-02, GIT-18–GIT-31 | 0 |

### Workspace Claude resident adapter

The audited host has no `~/.claude/CLAUDE.md`. The two references to it are
therefore mapped as broken routes, not as evidence of a second existing source.

| Source section | Covered behavior IDs | Unmapped |
|---|---|---|
| `WCL:5-7` scope/resident-context contract | ROUTE-14, RULE-03 | 0 |
| `WCL:13-26` plan-first/scope | AUTH-05, AUTH-16, PLAN-01, PLAN-05–PLAN-07, PLAN-09, PLAN-17 | 0 |
| `WCL:30-35` verification | ENV-01–ENV-07, VERIFY-01–VERIFY-02 | 0 |
| `WCL:39-41` destructive safety/review | GIT-33–GIT-35, REVIEW-09 | 0 |
| `WCL:45-51` Git/branch/identity | GIT-01–GIT-04, GIT-16, GIT-22, GIT-27, GIT-38, ROUTE-14 | 0 |
| `WCL:55-58` rule/config/docs editing | RULE-01–RULE-03, ROUTE-14, DOC-01–DOC-02 | 0 |
| `WCL:62-67` handoff/sync/progress | GIT-17–GIT-27, PLAN-01, PLAN-03, PLAN-11, PLAN-18–PLAN-19, ROUTE-15, META-04 | 0 |
| `WCL:71-74` audit/minimum modification | AUTH-03, AUTH-07, SECRET-03, BOUND-01, ROUTE-14 | 0 |
| `WCL:78-84` bootstrap/feedback | DOC-01–DOC-05, ROUTE-14, RULE-03 | 0 |

### Saberu root/project modules

| Source | Covered behavior IDs | Unmapped |
|---|---|---|
| `AGENTS.md` | ROUTE-01–ROUTE-05, ROUTE-09, ROUTE-10 | 0 |
| `CLAUDE.md` | BR-01–BR-02, BR-05, BR-17–BR-18, BR-35, SYNC-01, ROUTE-08 | 0 |
| `.agents/README.md` | ROUTE-01, ROUTE-05 | 0 |
| `.agents/project/agent-strategy.md` | ROUTE-06–ROUTE-08 | 0 |
| `.agents/project/overview.md` | ROUTE-07, ROUTE-09, BOUND-02 | 0 |
| `.agents/project/architecture.md` | ROUTE-09, BOUND-01–BOUND-02 | 0 |
| `.agents/rules/authorization.md` | AUTH-01–AUTH-16, LIVE-02–LIVE-04 | 0 |
| `.agents/rules/git.md` | GIT-01–GIT-04, GIT-11–GIT-16, GIT-18–GIT-21, GIT-25, GIT-28–GIT-35, BR-19, BR-24 | 0 |
| `.agents/rules/commits.md` | GIT-19–GIT-22, GIT-25, GIT-27, project Conventional Commit convention routed by TEST-01 | 0 |
| `.agents/rules/branching.md` | GIT-05–GIT-14, GIT-18–GIT-20, GIT-28–GIT-31, GIT-36–GIT-37, BR-01–BR-36 | 0 |
| `.agents/rules/codex-capabilities.md` | CAP-01–CAP-06, PLAN-13 | 0 |
| `.agents/rules/coding-plan.md` | PLAN-01–PLAN-16, CODE-01–CODE-02, BR-20, BR-22 | 0 |
| `.agents/rules/evidence-backed-planning.md` | PLAN-02–PLAN-04 | 0 |
| `.agents/rules/plan-hierarchy.md` | PLAN-05, PLAN-07, PLAN-10, PLAN-16, DOC-10, PPLAN-02, PPLAN-09–PPLAN-10 | 0 |
| `.agents/rules/plan-structure.md` | PLAN-02, PLAN-06–PLAN-07, PLAN-14–PLAN-16, PPLAN-01–PPLAN-08 | 0 |
| `.agents/rules/execution-reflection.md` | PLAN-08–PLAN-11, LIVE-07–LIVE-10, SECRET-05 | 0 |
| `.agents/rules/review-closure.md` | REVIEW-01, REVIEW-04–REVIEW-07 | 0 |
| `.agents/rules/review-lenses.md` | REVIEW-02 | 0 |
| `.agents/rules/secrets-handling.md` | SECRET-01–SECRET-05, PSECRET-01–PSECRET-07 | 0 |
| `.agents/rules/boundaries.md` | AUTH-03, BOUND-01–BOUND-02, LIVE-01–LIVE-07 | 0 |
| `.agents/rules/testing.md` | TEST-01–TEST-02 | 0 |
| `.agents/rules/docs-sync.md` | SYNC-01–SYNC-04 | 0 |
| `.agents/rules/file-naming.md` | PLAN-05, PLAN-10, PLAN-16, DOC-01–DOC-13 | 0 |
| `.agents/rules/session-bootstrap.md` | GIT-02, BR-20, BR-33, BR-36, ENV-02, ENV-06, ENV-08, CAP-01, ROUTE-02–ROUTE-04 | 0 |
| `.agents/rules/operational-quirks.md` | QUIRK-01 | 0 |
| `.agents/env/README.md` | ENV-02, ENV-05, ENV-09, TEST-01 | 0 |

### Saberu scenarios and path adapters

| Source | Covered behavior IDs | Unmapped |
|---|---|---|
| `.agents/scenarios/review-change.md` | REVIEW-01–REVIEW-03, REVIEW-08 | 0 |
| `.agents/scenarios/review-bugfix.md` | REVIEW-02, REVIEW-08 | 0 |
| `.agents/scenarios/review-feature.md` | REVIEW-02–REVIEW-03, REVIEW-08 | 0 |
| `.agents/scenarios/review-refactor.md` | REVIEW-02, REVIEW-08 | 0 |
| `.agents/scenarios/review-maintenance.md` | REVIEW-02, REVIEW-08 | 0 |
| `.agents/scenarios/review-operations.md` | REVIEW-02, REVIEW-08, LIVE-01–LIVE-07 | 0 |
| `.agents/scenarios/review-docs-governance.md` | REVIEW-02–REVIEW-03, REVIEW-08, DOC-01–DOC-13 | 0 |
| `.agents/scenarios/fix-bug.md` | CODE-01–CODE-03, TEST-01, SYNC-01 | 0 |
| `.agents/scenarios/modify-existing-feature.md` | CODE-01–CODE-03, TEST-01, SYNC-01 | 0 |
| `.agents/scenarios/new-feature.md` | CODE-01–CODE-03, PLAN-05–PLAN-07, TEST-01, SYNC-01 | 0 |
| `docs/AGENTS.md` | AUTH-08, DOC-01–DOC-13, ROUTE-11 | 0 |
| `docs/reviews/AGENTS.md` | DOC-02–DOC-13, PPLAN-01–PPLAN-10, ROUTE-11 | 0 |
| `docs/workstreams/AGENTS.md` | BR-09–BR-16, DOC-02–DOC-13, PPLAN-01–PPLAN-10, ROUTE-11 | 0 |
| `docs/reviews/feat-target-architecture/AGENTS.md` | DOC-03–DOC-12, ROUTE-12 | 0 |
| `controller/AGENTS.md`, `controller/audit/AGENTS.md` | ROUTE-10, TEST-01–TEST-02, BOUND-01 | 0 |
| `extensions/eda/AGENTS.md` | ROUTE-10, TEST-01–TEST-02, BOUND-01 | 0 |
| `inventory/AGENTS.md` | ROUTE-10, TEST-01–TEST-02, BOUND-02, SYNC-01 | 0 |
| `playbooks/AGENTS.md` | ROUTE-10, TEST-01–TEST-02, BOUND-01, SYNC-01 | 0 |
| `playbooks/vps/AGENTS.md` | ROUTE-10, ROUTE-13, TEST-01–TEST-02, SYNC-03 | 0 |
| `roles/AGENTS.md` | ROUTE-10, TEST-01–TEST-02, BOUND-01, QUIRK-01, SYNC-01 | 0 |

### Frozen Saberu candidate evidence

| Source | Covered behavior IDs | Unmapped |
|---|---|---|
| Candidate diffs in authorization/Git/commit/branching | AUTH-01–AUTH-16, GIT-01–GIT-37, BR-01–BR-36 | 0 |
| `docs/workstreams/gov-git-transaction-ux/` | GIT-18–GIT-27, GIT-36, BR-03, BR-25, BR-29, BR-32 | 0 |
| Candidate `TODO.md`, contribution guide, branch-lifecycle README | GIT-18–GIT-20, GIT-36–GIT-37, BR-05, BR-20, BR-32–BR-36 | 0 |

## 12. Phase 1 implementation reconciliation

The per-row `Status` column above is the frozen Phase 0 mapping verdict. This
overlay records implementation without rewriting the source-audit evidence.
“Workspace implemented / project pending” means the portable obligation exists
at the named owner, while a narrower Saberu delta or source-copy removal still
waits for Phase 3.

| Behavior IDs | Implemented workspace owner/evidence | Phase 1 status |
|---|---|---|
| AUTH-01–AUTH-16 | `authorization.md`; both resident adapters route it | implemented |
| GIT-01–GIT-04 | `git.md` | implemented |
| GIT-05–GIT-15, GIT-17–GIT-18, GIT-37–GIT-38 | `git-branches.md` plus integration/recovery boundary routes | workspace implemented / project topology delta pending |
| GIT-16, GIT-19–GIT-27 | `git-publication.md` plus resident identity floor | workspace implemented / project message/check delta pending |
| GIT-28–GIT-31, GIT-36–GIT-37 | `git-integration.md` | workspace implemented / project topology delta pending |
| GIT-32–GIT-35 | `git-recovery.md` | workspace implemented / project archive delta pending |
| PLAN-01–PLAN-19 | `planning.md`, with capability/environment/Git routes where split | workspace implemented / project artifact/live delta pending |
| REVIEW-01–REVIEW-09 | `review.md` plus `authorization.md` boundary | workspace implemented / project scenario delta pending |
| CAP-01–CAP-06 | `capabilities.md`; agent mechanics kept out of the portable module | implemented |
| SECRET-01–SECRET-05 | `secrets.md` plus authorization/Git recovery routes | workspace implemented / project placement delta pending |
| ENV-01–ENV-09 | `environment-truth.md`; `env-sync-SKILL.md` publication semantics aligned | workspace implemented / project command adapter pending |
| VERIFY-01–VERIFY-02 | `verification.md` | implemented |
| RULE-01–RULE-03 | `rule-authoring.md`; feedback register maps provenance to owners | implemented |
| ROUTE-14–ROUTE-15 | root `CLAUDE.md`, managed Codex template, and `codex-runtime.md` | workspace implemented / Saberu adapters pending |
| META-01–META-04 | existing `AGENTS.md` plus updated architecture/README/publication route | implemented |

Static owner/route checks and the Phase 2 repository/bootstrap checks provide
the transition from `implemented` to `verified`. All `BR-*`, `LIVE-*`,
`PSECRET-*`, `TEST-*`, `SYNC-*`, `BOUND-*`, `CODE-*`, `QUIRK-*`, `DOC-*`,
`PPLAN-*`, and Saberu-specific `ROUTE-*` reductions remain Phase 3 work; none
has been pre-applied in this repository.

## 13. Reconciliation totals

The source-group count retains the 61 groups already reconciled in the first
ledger and adds the nine line-bounded `WCL` sections above. It is a coverage
group count, not a Markdown table-row count; pre-existing rows that aggregate
multiple related source files retain their original group accounting.

| Category | Count |
|---|---:|
| Normalized behavior rows | 214 |
| Source coverage groups explicitly reconciled | 70 |
| Source sections left unmapped | 0 |
| Behavior decision records requiring user review | 18 |
| Workspace behavior groups implemented in the Phase 1 overlay | 14 |
| Saberu/project reduction groups implemented | 0 |

The 18 decision records are `DQ-01A`–`DQ-01C` and `DQ-02`–`DQ-16`; they are
summarized separately in `content-audit-summary-2026-07-20.md`. They were
accepted as the Phase 1 implementation basis. The original frozen workspace
and Saberu candidates remain invalid publication targets; only the reconciled
workspace candidate named in §12 can advance to Phase 2 verification.

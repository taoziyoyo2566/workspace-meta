# Workspace-Meta Design Map

This map is the one catalog of workspace-meta's functions and domains. When an
agent misbehaves, or a host or project integration looks wrong, find what you
noticed in the [symptom index](#symptom-index), open the domain it points to,
and change the design at the owner that entry names. The owners stay canonical:
an entry says where a behavior lives and how it is loaded and checked, and
states no rule of its own. The documentation gate requires every file in
`.agents/rules/` to be linked from this map.

Related maps, not copied here:

- [Layer model and managed surfaces](../../.agents/host-templates/README-agents.md#managed-and-host-local-surfaces):
  which layer owns each class of agent configuration, and what workspace-meta
  writes into each agent config dir.
- [Feedback register](../../feedback-register.md), table "Current owner
  mapping": the provenance behind each owner.
- [Configuration architecture](codex-config-management.md): how the sync
  engine, startup check, hooks, and status lines are built.
- [Engineering standards handbook](../standards/README.md): explanations and
  examples for people; agents are not routed to it.

## How To Read An Entry

- **Owner**: the file and sections that hold the behavior. Change it there.
- **Routed by**: what loads the owner into an agent's context: a row of the
  Direct Task Routing table in [`CLAUDE.md`](../../CLAUDE.md) and the Codex
  adapter [`codex-AGENTS.md`](../../.agents/host-templates/codex-AGENTS.md),
  the resident safety floor, a hook, or a skill. The trigger in parentheses
  summarizes the row; the adapters hold its exact text.
- **Enforced by**: what checks the design mechanically: the
  [documentation gate](#documentation-gate), tests under `tests/`, hooks,
  scripts, and host settings. "Prose only" means only the agent's reading holds
  the behavior; a recurrence there calls for a different rule form or a
  mechanism.
- **Project may add**: the narrower facts and stricter deltas a project states
  in its own entry files. A project never redefines the portable rule.
- **Symptoms**: what the operator notices when the domain's design is wrong or
  not applied.

## Symptom Index

| What you notice | Domain |
|---|---|
| The agent asks to confirm a read, a search, or an in-scope edit | [Authorization](#authorization) |
| A protected command is offered or run without its target, effect, and risk | [Authorization](#authorization) |
| A permission prompt or auto-mode pass is treated as approval to commit, push, or deploy | [Authorization](#authorization), [Publication](#publication) |
| A secret value appears in chat, a plan, or a diff, or remediation starts right after discovery | [Secrets](#secrets) |
| Temporary space fills, scratch is left behind, or another session's files are removed | [Temporary files](#temporary-files) |
| A script or scenario that will be needed again is deleted with the temporary files | [Temporary files](#temporary-files) |
| "Not installed" stated from memory, or a check marked blocked without a fresh probe | [Environment truth](#environment-truth), [Environment registry](#environment-registry) |
| `git status` needs permission, or a freshness check becomes a pull | [Git inspection and state](#git-inspection-and-state) |
| Unknown files are reset, cleaned, or stashed | [Git inspection and state](#git-inspection-and-state), [Recovery](#recovery-and-destructive-git) |
| A commit lands directly on the main branch, or a branch is created without a state report | [Change flow](#change-flow-branches-worktrees-and-stash) |
| A commit carries an AI trailer or the wrong author, or one commit and push needs four confirmations | [Publication](#publication) |
| Host or personal details are pushed to a remote nobody checked was public | [Publication](#publication) |
| A commit proposed for each small step, or one that only records a routine operation or adds to a committed record | [Publication](#publication), [Documentation and entry files](#documentation-and-project-entry-files) |
| A PR exists only to record a merge, or a branch is deleted while a server runs its commit | [Integration and retirement](#integration-and-retirement) |
| A force push, `branch -D`, `--no-verify`, or an amend after a hook failure | [Recovery](#recovery-and-destructive-git) |
| An invented version, a moved tag, or one-line release notes | [Releases and versions](#releases-and-versions) |
| Production runs a feature-branch commit, or a drill instance is left running | [Deployment](#deployment) |
| A change reaches the main branch around its pre-release channel, or the channel branch is rewritten or deployed behind the main branch | [Deployment](#deployment), [Change flow](#change-flow-branches-worktrees-and-stash), [Integration and retirement](#integration-and-retirement) |
| The literal wording was done and the goal missed, or examples were treated as the whole requirement | [Understanding requests](#understanding-requests) |
| One case is fixed while identical ones elsewhere go unmentioned | [Understanding requests](#understanding-requests) |
| Questions the repository could answer, several rounds of questions, or none on an ambiguous request | [Understanding requests](#understanding-requests), [Claude runtime](#claude-runtime) |
| Work stops while the operator is away, or grows because nobody could object | [Understanding requests](#understanding-requests), [Claude runtime](#claude-runtime) |
| A floated idea is answered without what done would mean or how it would be used | [Understanding requests](#understanding-requests) |
| A claim from memory, another session, or the operator stated as fact; "confirmed" after ruling out one cause | [Technical reasoning](#technical-reasoning) |
| A decision lives only in chat or memory, or status from memory contradicts the Plan | [Planning and handoff](#planning-and-handoff), [Memory](#memory) |
| A decision or correction kept only in a memory plugin's notes, or a file judged from the plugin's summary instead of the file | [Memory](#memory) |
| Two sessions redo one investigation, or the operator relays instructions between sessions | [Planning and handoff](#planning-and-handoff) |
| A duplicate implementation, history in comments, or policy hard-coded in logic | [Implementation shape](#implementation-shape) |
| A project has no entry file for the runtime in use, or a Claude session ignores its `AGENTS.md` | [Documentation and entry files](#documentation-and-project-entry-files), [SessionStart evaluator](#sessionstart-evaluator) |
| `/init` output copies `AGENTS.md` or workspace rules into a second rulebook | [Documentation and entry files](#documentation-and-project-entry-files), [Claude runtime](#claude-runtime) |
| Entry files written by a delegated or read-only agent, or tracked files added to someone else's clone | [Documentation and entry files](#documentation-and-project-entry-files), [Managed skills](#managed-skills) |
| Current guidance carries dated incident history, a new document duplicates an owner, or a review record or running plan is committed | [Documentation and entry files](#documentation-and-project-entry-files), [Documentation gate](#documentation-gate) |
| A file called done is broken: duplicate keys, trailing spaces, a new warning ignored | [File checks](#file-checks) |
| "Done" without functional proof, or a blocked check reported as passed | [Verification](#verification) |
| A problem list holds planned work, unverified claims, or misread metrics | [Review and problem reports](#review-and-problem-reports) |
| "Fixed" with no cause or prevention, or a proposal contradicts a recorded decision | [Proposals and follow-up](#proposals-and-problem-follow-up) |
| Every agent of a workflow runs at the session model and effort, with no allocation shown | [Capabilities and delegation](#capabilities-and-delegation) |
| A delegated agent breaks a workspace rule or lacks context the main session had | [Capabilities and delegation](#capabilities-and-delegation), [Claude runtime](#claude-runtime) |
| Effort, agents, or verification are cut to save time without asking | [Capabilities and delegation](#capabilities-and-delegation) |
| A command for the operator is suggested for the agent's own prompt (`!`), breaks when copied, or comes without the steps to open a terminal | [Capabilities and delegation](#capabilities-and-delegation) |
| A correction is saved to memory but never routed, or a rule lands in the wrong layer | [Rule authoring and feedback](#rule-authoring-and-feedback) |
| A read runs with `sudo` without asking, or a denied command is retried another way | [Authorization](#authorization) |
| A rule change is judged only by its wording, or an evaluation scenario quotes the rule it tests | [Rule evaluation harness](#rule-evaluation-harness) |
| A recorded evaluation result reads higher than later runs, or the rules a cited run measured are gone | [Rule evaluation harness](#rule-evaluation-harness) |
| Codex asks approval for each safe read, or broad allow rules appear | [Codex runtime](#codex-runtime) |
| The two adapters disagree, or portable behavior lives only in one adapter | [Adapters](#adapters) |
| Sessions under one Claude config dir lack a startup warning, status line, or skill that another has | [Sync engine](#sync-engine-and-managed-surfaces), [Managed skills](#managed-skills) |
| `make sync` refuses, reports drift that does not clear, or touches a field it does not own | [Sync engine](#sync-engine-and-managed-surfaces) |
| No startup warning although the workspace is behind, dirty, or short of temporary space | [SessionStart evaluator](#sessionstart-evaluator) |
| Wrong status-line fields, or a status line another tool owns is replaced | [Status lines](#status-lines) |
| A force-added path enters a workspace-meta commit | [Pre-commit guard](#pre-commit-guard) |
| A rule's origin cannot be traced, or two register entries share a number | [Feedback register](#feedback-register) |

## Safety And Authority

### Authorization

What a request authorizes; task authorization, plan approval, technical
capability, and action authorization stay separate; a protected action needs a
brief before it is proposed, run, or handed to the operator.

- **Owner**: [`authorization.md`](../../.agents/rules/authorization.md):
  [Request Semantics](../../.agents/rules/authorization.md#request-semantics),
  [Work That Proceeds Without Another Confirmation](../../.agents/rules/authorization.md#work-that-proceeds-without-another-confirmation),
  [Protected Mutations](../../.agents/rules/authorization.md#protected-mutations),
  [Protected-Action Request Brief](../../.agents/rules/authorization.md#protected-action-request-brief),
  [Technical Permission Is Not Semantic Authority](../../.agents/rules/authorization.md#technical-permission-is-not-semantic-authority),
  [Uncertainty](../../.agents/rules/authorization.md#uncertainty).
- **Routed by**: its row in both adapters (first write, permission or scope
  question, external, host, or live mutation, privilege elevation even for a
  read, a runtime denial, an approval request); co-loaded by every Git,
  release, and deployment row; the safety floor.
- **Enforced by**: the gate's safety-floor binding; brief and action-context
  tests in `tests/test_sync_codex_config.py`; host-local executable decisions
  (Claude `permissions` and `autoMode` per config dir, Codex
  `~/.codex/rules/*.rules`). Nothing checks that a brief was given.
- **Project may add**: live and external targets, risk fields, per-run or
  standing approval.
- **Symptoms**: confirmations for routine reads or in-scope edits; a protected
  command with no brief; a permission prompt taken as approval; an approval
  stretched to a retry, another target, or a follow-up operation; a read run
  with `sudo` or as another account without asking; a denied command retried
  by another route; approval targets labelled with names that already meant
  something, or a short reply acted on when it could select two target sets.

### Secrets

The non-exposure floor for credentials and the remediation sequence; discovery
alone authorizes no remediation.

- **Owner**: [`secrets.md`](../../.agents/rules/secrets.md):
  [Safety Floor](../../.agents/rules/secrets.md#safety-floor),
  [Project Delta](../../.agents/rules/secrets.md#project-delta).
- **Routed by**: its row in both adapters (secret material or remediation);
  the safety floor.
- **Enforced by**: the gate's safety-floor binding; the reverse-whitelist
  `.gitignore` and the [pre-commit guard](#pre-commit-guard) limit which paths
  can be committed but scan no content.
- **Project may add**: stores, paths, consumers, rotation, validation commands.
- **Symptoms**: a value in chat or a diff; a real `.env` tracked;
  `git rm --cached`, a history rewrite, or a rotation without approval; a
  secret file checked with a loader that prints values.

### Temporary Files

Where temporary files go by size and filesystem, who removes them, what is
kept from them by its owner, and what to do when temporary space fills.

- **Owner**: [`temporary-files.md`](../../.agents/rules/temporary-files.md):
  [Placement](../../.agents/rules/temporary-files.md#placement),
  [Lifecycle](../../.agents/rules/temporary-files.md#lifecycle),
  [Full Or Filling Temporary Space](../../.agents/rules/temporary-files.md#full-or-filling-temporary-space),
  [Host Settings](../../.agents/rules/temporary-files.md#host-settings).
- **Routed by**: its row in both adapters (creating or removing temporary
  files, or temporary space full or filling); the [SessionStart
  evaluator](#sessionstart-evaluator) warning, which names the owner.
- **Enforced by**: the evaluator's free-space check, which warns the operator
  and the agent; temporary-space tests in `tests/test_workspace_status.py`;
  Lifecycle phrase tests in `tests/test_sync_codex_config.py`.
- **Project may add**: an ignored local directory for large data.
- **Symptoms**: no space left on the temporary filesystem; scratch left after
  the task; a script or scenario that will be needed again deleted with the
  scratch; no temporary-files line in the final report; another session's
  files deleted.

### Environment Truth

Environment and capability facts are dated snapshots, probed again before they
become load-bearing; each host's registry is generated, never hand-edited or
shared.

- **Owner**: [`environment-truth.md`](../../.agents/rules/environment-truth.md):
  [Dated Snapshots](../../.agents/rules/environment-truth.md#dated-snapshots),
  [Contradiction](../../.agents/rules/environment-truth.md#contradiction),
  [Per-Host Registry](../../.agents/rules/environment-truth.md#per-host-registry).
  Mechanism: [Environment registry](#environment-registry).
- **Routed by**: its row in both adapters (load-bearing host or environment
  claim); the safety floor; the `env-sync` skill.
- **Enforced by**: the gate's safety-floor binding; the evaluator's registry
  freshness check.
- **Project may add**: the mapping from project tasks to environment commands.
- **Symptoms**: "not installed" from memory; a blocked check without a fresh
  probe; a registry hand-edited, committed, or copied from another host; an
  approved Plan rewritten because an environment fact changed.

## Git, Releases, And Deployment

### Git Inspection And State

Inspection needs no confirmation; a plain fetch of the canonical remote is the
bounded freshness exception; a state snapshot precedes any mutation; unknown
work is never discarded.

- **Owner**: [`git.md`](../../.agents/rules/git.md):
  [Inspection](../../.agents/rules/git.md#inspection),
  [Pre-Mutation State](../../.agents/rules/git.md#pre-mutation-state).
- **Routed by**: its row in both adapters (Git inspection or freshness);
  co-loaded by every Git mutation row; the safety floor.
- **Enforced by**: the gate's safety-floor binding; load-profile tests in
  `tests/test_sync_codex_config.py`; the evaluator's bounded fetch and
  dirty, behind, and ahead report for workspace-meta.
- **Project may add**: the canonical remote.
- **Symptoms**: permission asked for `git status`; a pull or pruning fetch to
  check freshness; a mutation with no state report; unknown files reset or
  stashed; "up to date" from stale remote-tracking refs.

### Change Flow, Branches, Worktrees, And Stash

Every repository change goes through a short-lived typed branch from the main
branch, or from a declared pre-release channel's branch for what only the
channel has, and reaches the main branch by the project's route, directly or
by promotion from the channel; branch mechanics never change content.

- **Owner**: [`git-branches.md`](../../.agents/rules/git-branches.md):
  [Change Flow](../../.agents/rules/git-branches.md#change-flow),
  [Branch Action Review](../../.agents/rules/git-branches.md#branch-action-review),
  [Creation Transaction](../../.agents/rules/git-branches.md#creation-transaction),
  [Content Non-Interference](../../.agents/rules/git-branches.md#content-non-interference),
  [Isolation](../../.agents/rules/git-branches.md#isolation),
  [Stash](../../.agents/rules/git-branches.md#stash). Workspace-meta's own
  facts: [`AGENTS.md` Branches And Releases](../../AGENTS.md#branches-and-releases).
- **Routed by**: its row in both adapters (branch, worktree, or stash action,
  or starting a repository change), with `authorization.md` and `git.md`.
- **Enforced by**: section and phrase tests in
  `tests/test_sync_codex_config.py`. Nothing mechanical stops a commit on the
  main branch.
- **Project may add**: main branch, type prefixes, merge route, checks,
  topology, and an optional durable contract carrier.
- **Symptoms**: a commit directly on the main branch or on a pre-release
  channel's branch; confirmation asked for a worktree of an authorized change;
  the checkout switched in place or dirty edits carried along; branch metadata
  written into a Plan; an automatic stash.

### Publication

Propose publication once per finished result; stage, commit, push, or open a
PR only after one approval of its result review and exact command bundle,
under the operator's identity and with no AI trailers.

- **Owner**: [`git-publication.md`](../../.agents/rules/git-publication.md):
  [One Proposal Per Result](../../.agents/rules/git-publication.md#one-proposal-per-result),
  Checkpoint A and Checkpoint B,
  [Change-Flow Bundle](../../.agents/rules/git-publication.md#change-flow-bundle),
  [Execution Choices](../../.agents/rules/git-publication.md#execution-choices).
  Workspace-meta's delta:
  [`AGENTS.md` Commit And Sync](../../AGENTS.md#commit-and-sync).
- **Routed by**: its row in both adapters (stage, commit, push, or PR
  publication), with `authorization.md` and `git.md`; the safety floor.
- **Enforced by**: the gate's safety-floor binding; publication-contract tests
  in `tests/test_sync_codex_config.py`; the bootstrap's global-identity check;
  `scripts/change_flow_bundle.sh`, which runs a reviewed fast-forward bundle
  into the main branch from its bundle directory, binds the reviewed tree and
  message by fingerprint, stops on the drifts it checks, never force-removes a
  worktree, and leaves the push a separate command
  (`tests/test_change_flow_bundle.py`); the steps on a pre-release channel's
  branch are not scripted. No commit-message hook.
- **Project may add**: message format, checks, CI, PR fields.
- **Symptoms**: `Co-Authored-By` or `Signed-off-by` in a commit, or a
  repository-local identity; a commit right after a permission prompt with no
  content review; separate confirmations for add, commit, push, and PR;
  `git add -A`; host or personal details pushed to a public remote whose
  visibility nobody checked; a commit proposed for each small step or routine
  record; content accepted in one turn and its bundle approved in the next.

### Integration And Retirement

Integrating a reviewed source is its own reviewed transaction; PR and Git
metadata are terminal evidence; retirement first checks that no instance runs
a commit only the retiring branch holds.

- **Owner**: [`git-integration.md`](../../.agents/rules/git-integration.md):
  [Integration Review](../../.agents/rules/git-integration.md#integration-review),
  [Pre-Release Channel Branch](../../.agents/rules/git-integration.md#pre-release-channel-branch),
  [Terminal Evidence](../../.agents/rules/git-integration.md#terminal-evidence),
  [Retirement Boundary](../../.agents/rules/git-integration.md#retirement-boundary).
- **Routed by**: its row in both adapters (merge, integration, or
  post-integration handling), with `authorization.md` and `git.md`.
- **Enforced by**: brief and load-profile tests in
  `tests/test_sync_codex_config.py`; prose otherwise.
- **Project may add**: routes, topology, prerequisites, CI, archive policy.
- **Symptoms**: a closeout PR created only to record a merge; a push, tag, or
  deletion after a merge without its own review; conflicts resolved under the
  merge approval; a branch deleted while a server runs its commit; a squash or
  rebase into or out of a pre-release channel's branch.

### Recovery And Destructive Git

Rebase, cherry-pick, revert, pull, reset, clean, restore, amend, hook bypass,
force, and ref or tag deletion need an exact reviewed effect, an OID-leased
force, and recovery refs.

- **Owner**: [`git-recovery.md`](../../.agents/rules/git-recovery.md):
  [Exact Reviewed Effect](../../.agents/rules/git-recovery.md#exact-reviewed-effect),
  [Forced Updates And Deletion](../../.agents/rules/git-recovery.md#forced-updates-and-deletion),
  [Reset Or History Rewrite](../../.agents/rules/git-recovery.md#reset-or-history-rewrite).
- **Routed by**: its row in both adapters (rewrite, discard, force, delete,
  amend, or recovery), with `authorization.md` and `git.md`; the safety
  floor's preservation bullet.
- **Enforced by**: brief and load-profile tests in
  `tests/test_sync_codex_config.py`. Workspace-meta installs no deny rule or
  hook for these commands.
- **Project may add**: stricter ref policy and archive tooling.
- **Symptoms**: a force push or remote branch deletion in a proposal;
  `reset --hard` or `clean -fd` to tidy up; an amend or `--no-verify` after a
  hook failure; a pushed release tag moved; a pre-release channel's branch
  rewritten.

### Releases And Versions

Each released state gets an annotated SemVer tag whose message is the release
notes; fixes reach released versions by a defined route; the rollback target is
the newest verified state without the fault.

- **Owner**: [`releases.md`](../../.agents/rules/releases.md):
  [Applies To](../../.agents/rules/releases.md#applies-to),
  [Version Numbers](../../.agents/rules/releases.md#version-numbers),
  [When And What To Tag](../../.agents/rules/releases.md#when-and-what-to-tag),
  [Release Notes](../../.agents/rules/releases.md#release-notes),
  [Fixes](../../.agents/rules/releases.md#fixes),
  [Rollback Target](../../.agents/rules/releases.md#rollback-target).
  Workspace-meta's scheme:
  [`AGENTS.md` Branches And Releases](../../AGENTS.md#branches-and-releases).
- **Routed by**: its row in both adapters (release, version tag or number,
  rollback target, or fixing a released version), with `authorization.md` and
  `git.md`.
- **Enforced by**: a brief and route test; nothing checks note format, version
  arithmetic, or annotation.
- **Project may add**: whether it releases, starting version, prefix,
  compatibility surface, what released means, status surface, rollback
  procedure, signing.
- **Symptoms**: a version invented for a project with no recorded scheme; a
  tag placed before post-release verification; `git push --tags`; one-line
  notes; a fix shipped on the main branch only while production runs an older
  line; a pre-release channel's deployment tagged; a rollback that skips the
  newest verified state for an older tag; MINOR raised for a fix or for an
  improvement inside an existing component; a fix tagged on its own with
  neither an older line nor the operator's decision.

### Deployment

Only commits reachable from the pushed main deployment branch serve users,
apart from a declared pre-release channel, whose commits contain it and reach
it only by promotion; anything else is a temporary deployment with an end
condition; deploy promptly, check before an older version and hold after it,
and report instances outside the inventory.

- **Owner**: [`deployment.md`](../../.agents/rules/deployment.md):
  [Main Branch](../../.agents/rules/deployment.md#main-branch),
  [Pre-Release Channels](../../.agents/rules/deployment.md#pre-release-channels),
  [Cadence](../../.agents/rules/deployment.md#cadence),
  [Temporary Deployments](../../.agents/rules/deployment.md#temporary-deployments),
  [Deploying An Older Release](../../.agents/rules/deployment.md#deploying-an-older-release),
  [Instances Outside The Inventory](../../.agents/rules/deployment.md#instances-outside-the-inventory).
- **Routed by**: its row in both adapters (deploying, what may serve users, a
  temporary deployment, or an instance outside the inventory), with
  `authorization.md`.
- **Enforced by**: a brief route test; the pre-release channel test in
  `tests/test_sync_codex_config.py`; each project's deploy entry points and
  guards; host-local Claude `autoMode` rules where the operator sets them.
- **Project may add**: main deployment branch, a pre-release channel's
  declaration, targets and inventory, entry points and guards, deployment
  record, environment tiers, rollback procedure.
- **Symptoms**: production on a feature-branch or unpushed commit; a pushed
  change left undeployed; a drill instance left running; an unknown instance
  changed before it is reported; a rollback or a channel withdrawal without
  its checks of secrets, schemas, interfaces, and channels; a pre-release
  change merged straight into the main branch; a channel instance on a commit
  without the main branch's tip; a shared part deployed from the channel
  branch.

## Requests, Reasoning, And Planning

### Understanding Requests

How a request is read before work starts, at every depth from a factual
question to a design: the goal, what done means, the similar problems it
stands for, and whether to ask the operator or proceed on stated assumptions.

- **Owner**: [`requests.md`](../../.agents/rules/requests.md):
  [Understand The Request](../../.agents/rules/requests.md#understand-the-request),
  [Ask Or Proceed](../../.agents/rules/requests.md#ask-or-proceed),
  [Similar Problems](../../.agents/rules/requests.md#similar-problems).
  How Claude puts a question:
  [`claude-runtime.md` Asking The Operator](../../.agents/rules/claude-runtime.md#asking-the-operator).
- **Routed by**: the sentence above both adapters' routing tables and its row
  in both adapters (starting work on a request, asking the operator, or
  proceeding on assumptions); the `interview` skill when the operator invokes
  `/interview`.
- **Enforced by**: phrase and route tests in
  `tests/test_sync_codex_config.py`; the reading itself is prose only.
- **Project may add**: domain checks for what done means, and where the
  similar problems it finds are recorded.
- **Symptoms**: the wording done and the goal missed; examples treated as the
  whole need or as constraints; one case fixed while identical ones go
  unlisted; questions the repository could answer, a second round, or none on
  an ambiguous request; work stopped while the operator is away; a floated
  idea answered without what done would mean or its usage scenarios.

### Technical Reasoning

Premises, knowledge states, evidence, competing explanations and
discriminating probes, independent judgment, and uncertainty, each in
proportion to what the decision needs.

- **Owner**: [`reasoning.md`](../../.agents/rules/reasoning.md):
  [Validate Premises Proportionally](../../.agents/rules/reasoning.md#validate-premises-proportionally),
  [Classify Knowledge States](../../.agents/rules/reasoning.md#classify-knowledge-states),
  [Evaluate Evidence](../../.agents/rules/reasoning.md#evaluate-evidence),
  [Diagnose With Discriminating Probes](../../.agents/rules/reasoning.md#diagnose-with-discriminating-probes),
  [Calibrate Uncertainty And Stop](../../.agents/rules/reasoning.md#calibrate-uncertainty-and-stop).
- **Routed by**: its row in both adapters (load-bearing premises, conflicting
  evidence, independent judgment, competing explanations, diagnostic method);
  the safety floor.
- **Enforced by**: the gate's safety-floor binding; owner and route tests in
  `tests/test_sync_codex_config.py`.
- **Project may add**: domain evidence sources, diagnostic commands,
  thresholds, invariants, safer probes.
- **Symptoms**: a claim from memory, another session, or the operator stated
  as fact; "confirmed" after ruling out one cause; configuration changed on a
  guess before a read-only probe; a hypothesis table for a trivial issue;
  uncertainty that would change the decision left unstated.

### Planning And Handoff

Plans in proportion to the work, earlier and concurrent work found first,
findings and decisions recorded when they happen, approval scope and
deviations, and handoff through the owning artifact.

- **Owner**: [`planning.md`](../../.agents/rules/planning.md):
  [Before Planning](../../.agents/rules/planning.md#before-planning),
  [Proportional Shape](../../.agents/rules/planning.md#proportional-shape),
  [Approval Scope](../../.agents/rules/planning.md#approval-scope),
  [Record Findings When Confirmed](../../.agents/rules/planning.md#record-findings-when-confirmed),
  [Record Decisions When Made](../../.agents/rules/planning.md#record-decisions-when-made),
  [Handoff And Closeout](../../.agents/rules/planning.md#handoff-and-closeout).
  Workspace-meta's Plan location:
  [`AGENTS.md` Before Editing](../../AGENTS.md#before-editing).
- **Routed by**: its row in both adapters (non-trivial planning, a new
  capability's design, an investigation, comparison, or experiment, findings,
  decisions, status from memory, evidence, approval scope, deviation,
  handoff).
- **Enforced by**: lifecycle phrase tests in `tests/test_sync_codex_config.py`;
  recording decisions is prose only.
- **Project may add**: artifact schema and locations, sources, where verified
  findings are recorded, branch and live gates.
- **Symptoms**: an operator decision kept only in chat or memory, so the next
  session asks again; status from memory contradicting the Plan or Git
  history; two sessions redoing one investigation; a new Plan for routine
  feedback, or a new capability folded into an old Plan; an exception to a
  recorded decision kept only in chat; a remembered restriction used to refuse
  a request instead of being raised once.

## Building And Checking

### Implementation Shape

An approved outcome becomes a small, coherent set of artifacts: one canonical
owner per fact, durable comments, adjustable policy as data, checked
dependency changes, reviewable changes, and tests on contracts.

- **Owner**: [`implementation.md`](../../.agents/rules/implementation.md):
  [Shape The Change Before Editing](../../.agents/rules/implementation.md#shape-the-change-before-editing),
  [One Fact, One Canonical Owner](../../.agents/rules/implementation.md#one-fact-one-canonical-owner),
  [Code, Adjustable Data, And Contracts](../../.agents/rules/implementation.md#code-adjustable-data-and-contracts),
  [Write Durable Comments](../../.agents/rules/implementation.md#write-durable-comments),
  [Test Contracts, Not Incidental Text](../../.agents/rules/implementation.md#test-contracts-not-incidental-text).
- **Routed by**: its row in both adapters (implementation, configuration,
  refactoring, or artifact-structure change).
- **Enforced by**: heading and route tests in
  `tests/test_sync_codex_config.py`; prose otherwise.
- **Project may add**: language, framework, and architecture conventions.
- **Symptoms**: a second near-identical implementation; comments that narrate
  history; policy values hard-coded in logic; unrelated cleanup mixed in;
  tests that lock in wording; a dependency added without provenance.

### Documentation And Project Entry Files

Documents routed by their reader's task and truth class, one owner per fact,
review content kept temporary and running plans out of the committed tree, and
agent entry files that the runtime in use actually loads, created when a
project lacks them.

- **Owner**: [`documentation.md`](../../.agents/rules/documentation.md):
  [Route Content By Role](../../.agents/rules/documentation.md#route-content-by-role),
  [Committed And Temporary Records](../../.agents/rules/documentation.md#committed-and-temporary-records),
  [Make Agent Instructions Loadable](../../.agents/rules/documentation.md#make-agent-instructions-loadable),
  [Project Bootstrap](../../.agents/rules/documentation.md#project-bootstrap),
  [Keep Truth Classes Explicit](../../.agents/rules/documentation.md#keep-truth-classes-explicit),
  [Validate The Documentation Change](../../.agents/rules/documentation.md#validate-the-documentation-change).
  How each runtime loads entry files:
  [`claude-runtime.md` Project Entry Files](../../.agents/rules/claude-runtime.md#project-entry-files)
  and
  [`codex-runtime.md` Project Entry Files](../../.agents/rules/codex-runtime.md#project-entry-files).
  Standing authority to create a missing entry file, which only the session
  in conversation with the operator uses and an explicit no-write instruction
  overrides:
  [`authorization.md` Work That Proceeds Without Another Confirmation](../../.agents/rules/authorization.md#work-that-proceeds-without-another-confirmation).
- **Routed by**: its row in both adapters (documentation authoring,
  restructuring, or lifecycle governance, or a project without an entry file
  for the runtime in use), which adds `claude-runtime.md` in `CLAUDE.md` and
  `codex-runtime.md` in the Codex adapter; the missing-entry backstop below the
  routing table of `CLAUDE.md`; the
  [SessionStart evaluator](#sessionstart-evaluator)'s readiness warning; the
  `project-bootstrap` skill.
- **Enforced by**: the [documentation gate](#documentation-gate) for
  workspace-meta's own documents, including its check that no review record or
  running plan is tracked or linked from a current document; the readiness
  check for Git projects under `~/workspace/projects/`; each project's own gate
  for its adapter and import.
- **Project may add**: entry points, topic map, commands, domain constraints,
  and its own documentation gate.
- **Symptoms**: a project with no entry file for the runtime in use; a Claude
  session ignoring a project's `AGENTS.md`, or a subdirectory's; a project's
  `CLAUDE.md` and `AGENTS.md` saying different things; `/init` output copying
  `AGENTS.md` or workspace rules; entry files written by a delegated or
  read-only agent, or tracked files added to someone else's clone; dated
  incident narrative in current guidance; a new document instead of an update
  to its owner; a review record or running plan committed, or a plan kept
  after acceptance.

### File Checks

Each created or changed file is checked by type before it is called done:
container and bytes, syntax, strict format, consistency with its consumer, and
security bounded to the file.

- **Owner**: [`file-checks.md`](../../.agents/rules/file-checks.md):
  [Stages](../../.agents/rules/file-checks.md#stages),
  [What Makes A Check Count](../../.agents/rules/file-checks.md#what-makes-a-check-count),
  [Secret-Bearing Files](../../.agents/rules/file-checks.md#secret-bearing-files),
  [Warnings](../../.agents/rules/file-checks.md#warnings),
  [Report](../../.agents/rules/file-checks.md#report).
- **Routed by**: its row in both adapters (a created or changed file before it
  is called done, handed over, committed, or deployed); the safety floor.
- **Enforced by**: the gate's safety-floor binding; workspace-meta's own
  checks in [`AGENTS.md` Verification](../../AGENTS.md#verification). No hook
  runs file checks.
- **Project may add**: commands per file class, accepted warnings, stricter
  gates.
- **Symptoms**: YAML or JSON called done after a lenient parse that hid
  duplicate keys; trailing whitespace in a handed-over script; secret values
  printed by a check; new warnings ignored; no per-class line in the report.

### Verification

Proof that a change works: direction, then static, then functional checks;
behavior checks where the risk warrants them; release evidence; diagnosis
instead of retry loops; gaps reported as gaps.

- **Owner**: [`verification.md`](../../.agents/rules/verification.md):
  [Required Result](../../.agents/rules/verification.md#required-result),
  [Risk-Triggered Behavior Checks](../../.agents/rules/verification.md#risk-triggered-behavior-checks),
  [Release Evidence](../../.agents/rules/verification.md#release-evidence),
  [Failure And Retry](../../.agents/rules/verification.md#failure-and-retry),
  [Gaps](../../.agents/rules/verification.md#gaps).
- **Routed by**: its row in both adapters (change verification or blocked
  check); the safety floor.
- **Enforced by**: the gate's safety-floor binding; `make test` for
  workspace-meta itself.
- **Project may add**: commands, environments, thresholds, CI.
- **Symptoms**: "done" after lint only; a blocked check reported as passed;
  the same failing check retried; a release called verified without a
  post-deploy check; whole-workflow success claimed from a narrower check.

### Review And Problem Reports

Review and audit: a frozen scope, a review type and risk lenses,
evidence-backed findings with severity, when an independent reviewer is
needed, problem reports in a set form, and when to stop.

- **Owner**: [`review.md`](../../.agents/rules/review.md):
  [Review Shape](../../.agents/rules/review.md#review-shape),
  [Independent Review](../../.agents/rules/review.md#independent-review),
  [Severity](../../.agents/rules/review.md#severity),
  [Problem Reports](../../.agents/rules/review.md#problem-reports),
  [Completion](../../.agents/rules/review.md#completion).
- **Routed by**: its row in both adapters (review, audit, diagnosis,
  remediation assessment, or reporting which problems exist).
- **Enforced by**: problem-report phrase and route tests in
  `tests/test_sync_codex_config.py`; prose otherwise.
- **Project may add**: baseline, domain scenarios, severity refinements.
- **Symptoms**: a problem list holding planned work, unverified claims, or
  misread metrics; a review that silently includes nested repositories or host
  configuration; edits made when only a review was asked; re-audits that only
  polish wording.

### Proposals And Problem Follow-Up

Every proposed way of working is checked against recorded rules and
decisions; a handled problem gets a report down to its class, its prevention,
and its recurrence; a mechanism or a rule is chosen by what a miss costs; a
deferral gets an owner and a restart condition.

- **Owner**: [`problem-follow-up.md`](../../.agents/rules/problem-follow-up.md):
  [Check A Proposal Against What Is Already Decided](../../.agents/rules/problem-follow-up.md#check-a-proposal-against-what-is-already-decided),
  [When A Problem Needs Follow-Up](../../.agents/rules/problem-follow-up.md#when-a-problem-needs-follow-up),
  [Report Parts](../../.agents/rules/problem-follow-up.md#report-parts),
  [Mechanism Or Rule](../../.agents/rules/problem-follow-up.md#mechanism-or-rule),
  [Deferral](../../.agents/rules/problem-follow-up.md#deferral).
- **Routed by**: its row in both adapters (proposing a procedure or practice,
  or reporting a handled problem).
- **Enforced by**: route and ownership tests only.
- **Project may add**: where incident findings go, and its progress owner.
- **Symptoms**: "fixed" with only the result; a proposal contradicting a
  recorded decision; a lesson saved only to memory; heavy tooling after a
  first occurrence; a recurrence not linked to the earlier incident.

## Agent Operation

### Capabilities And Delegation

When to check which capabilities exist, how tools are chosen, quality before
speed, how work is delegated (subtasks surveyed by demand, a model tier and
effort per agent, briefs, verification of delegated output, the allocation
reported), and where and how the operator runs a command handed to them.

- **Owner**: [`capabilities.md`](../../.agents/rules/capabilities.md):
  [Observable Triggers](../../.agents/rules/capabilities.md#observable-triggers),
  [Selection](../../.agents/rules/capabilities.md#selection),
  [Quality Before Speed](../../.agents/rules/capabilities.md#quality-before-speed),
  [Delegation](../../.agents/rules/capabilities.md#delegation),
  [Commands The User Runs](../../.agents/rules/capabilities.md#commands-the-user-runs),
  [Recording](../../.agents/rules/capabilities.md#recording). Claude mechanics:
  [`claude-runtime.md` Delegation](../../.agents/rules/claude-runtime.md#delegation)
  and
  [Long Unattended Runs](../../.agents/rules/claude-runtime.md#long-unattended-runs);
  the override of Claude Code's `!` suggestion:
  [`CLAUDE.md` Commands The User Runs](../../CLAUDE.md#commands-the-user-runs).
- **Routed by**: two rows in both adapters: capability selection, method
  failure, slow or costly work, or a command for the operator to run; and
  delegating work to subagents or a workflow. In `CLAUDE.md` the delegation
  row adds `claude-runtime.md`, and the Commands The User Runs section is
  resident; in the Codex adapter both rows add `codex-runtime.md` when Codex
  mechanics are needed.
- **Enforced by**: Quality Before Speed, Delegation, and Commands The User
  Runs phrase tests in `tests/test_sync_codex_config.py`; nothing checks an
  allocation or a handed-over command. Claude
  sets a per-agent model and effort only because
  [`CLAUDE.md` Claude-Specific Runtime](../../CLAUDE.md#claude-specific-runtime)
  and `claude-runtime.md` Delegation instruct it to.
- **Project may add**: project toolchain and adapters.
- **Symptoms**: every agent of a workflow at the session model and effort,
  with no allocation shown; a delegated agent working without the constraints
  the main session had; effort, agents, or verification cut to save time
  without asking; a delegated result reported without checking its evidence;
  a command for the operator suggested for the agent's own prompt, such as
  Claude Code's `!` prefix, where a passphrase prompt returns unanswered; a
  multi-line or overlong command handed over to paste; a command handed over
  without the steps to open the terminal it needs.

### Rule Authoring And Feedback

Feedback intake (each correction or preference classified and routed in the
reply that takes it in), choosing the owner and layer, editing the whole
owner, matching the rule's form to the failure, and provenance with only
lasting content.

- **Owner**: [`rule-authoring.md`](../../.agents/rules/rule-authoring.md):
  [Choose The Owner First](../../.agents/rules/rule-authoring.md#choose-the-owner-first),
  [Feedback Intake](../../.agents/rules/rule-authoring.md#feedback-intake),
  [Edit The Whole Relevant Owner](../../.agents/rules/rule-authoring.md#edit-the-whole-relevant-owner),
  [Match Form To Failure](../../.agents/rules/rule-authoring.md#match-form-to-failure),
  [Provenance And Refactoring](../../.agents/rules/rule-authoring.md#provenance-and-refactoring).
  Provenance archive: [Feedback register](#feedback-register).
- **Routed by**: its row in both adapters (writing or refactoring agent rules,
  routing feedback, or the operator correcting how you work or stating a
  preference about it); the Handoff And Feedback and Claude Auto-Memory
  sections of `CLAUDE.md`. Choose The Owner First sends an agent looking for
  an existing behavior's owner to this map's [symptom index](#symptom-index).
- **Enforced by**: feedback-intake phrase tests and the register entry-format
  test in `tests/test_sync_codex_config.py`.
- **Project may add**: project-only owners and adapters.
- **Symptoms**: a correction only saved to memory; a cross-project rule placed
  in a project file, or the reverse; rule text growing with incident stories;
  a recurrence answered with louder wording instead of another rule form; a
  new rule duplicating another owner; a memory note that restricts agents
  without naming its scope.

### Claude Runtime

Claude Code mechanics only: where Claude reads instructions, settings, skills,
and memory; its project entry files; how it asks the operator; how model,
effort, and orchestration features are set; and how a long unattended run
keeps going. Its facts name the Claude Code version they were verified
against and the features whose changes call for a recheck. It never redefines
portable behavior.

- **Owner**: [`claude-runtime.md`](../../.agents/rules/claude-runtime.md):
  [Configuration Layers](../../.agents/rules/claude-runtime.md#configuration-layers),
  [Project Entry Files](../../.agents/rules/claude-runtime.md#project-entry-files),
  [Memory](../../.agents/rules/claude-runtime.md#memory),
  [Asking The Operator](../../.agents/rules/claude-runtime.md#asking-the-operator),
  [Delegation](../../.agents/rules/claude-runtime.md#delegation),
  [Long Unattended Runs](../../.agents/rules/claude-runtime.md#long-unattended-runs).
- **Routed by**: `CLAUDE.md` only: the row for delegation and Claude Code
  mechanics (instruction or memory loading, config dirs, asking the operator,
  model or effort, `/goal`), the documentation row for Claude's entry files,
  and the [Claude-Specific Runtime](../../CLAUDE.md#claude-specific-runtime)
  section.
- **Enforced by**: the gate's runtime-module routing check (routed by
  `CLAUDE.md`, never by the Codex adapter); section tests in
  `tests/test_sync_codex_config.py`.
- **Project may add**: project `.claude/` settings, rules, skills, and agents
  within the project layer of the layer model.
- **Symptoms**: a Claude-only mechanism written into a portable owner; a
  runtime fact relied on after an upgrade changed it; a delegated agent given
  no model or effort; a question asked in plain text where the dialog was
  available, or asked to a subagent that cannot answer.

### Codex Runtime

Codex mechanics only: sandbox and escalation, execpolicy, deferred tool
discovery, Codex's project entry files, and the configuration boundary.

- **Owner**: [`codex-runtime.md`](../../.agents/rules/codex-runtime.md):
  [Sandbox And Escalation](../../.agents/rules/codex-runtime.md#sandbox-and-escalation),
  [Capability Mechanics](../../.agents/rules/codex-runtime.md#capability-mechanics),
  [Project Entry Files](../../.agents/rules/codex-runtime.md#project-entry-files),
  [Configuration Boundary](../../.agents/rules/codex-runtime.md#configuration-boundary).
- **Routed by**: the Codex adapter only: its capabilities and delegation rows
  when Codex mechanics are needed, its documentation row for Codex's entry
  files, and its Codex-Specific Runtime section.
- **Enforced by**: the gate's runtime-module routing check; adapter route
  tests in `tests/test_sync_codex_config.py`. Executable approvals stay
  host-local in `~/.codex/rules/*.rules`.
- **Project may add**: project Codex configuration within the project layer.
- **Symptoms**: Codex asking approval for each safe read; broad shell allow
  rules; `~/.codex/rules` content copied into a repository; model choices
  pushed into managed configuration.

### Memory

Auto memory is recall kept per config dir: lasting corrections, preferences,
and pointers to owners, never the only record of a decision or of a
workstream's state. A session-history plugin, where one is installed, adds
searchable history on the same terms.

- **Owner**: split by concern:
  [`CLAUDE.md` Claude Auto-Memory](../../CLAUDE.md#claude-auto-memory) for how
  a memory is written and read (classification, index line, dates, stale
  entries, the snapshot loaded at start);
  [`claude-runtime.md` Memory](../../.agents/rules/claude-runtime.md#memory)
  for Claude's mechanics (one store per config dir, what loads, what
  subagents receive, a session-history plugin's place beside auto memory);
  [`planning.md` Before Planning](../../.agents/rules/planning.md#before-planning)
  for searching session history with the other records;
  [`planning.md` Record Decisions When Made](../../.agents/rules/planning.md#record-decisions-when-made)
  for where decisions and status live;
  [`rule-authoring.md` Feedback Intake](../../.agents/rules/rule-authoring.md#feedback-intake)
  and
  [Provenance And Refactoring](../../.agents/rules/rule-authoring.md#provenance-and-refactoring)
  for what a memory note may hold.
- **Routed by**: the [Claude Auto-Memory](../../CLAUDE.md#claude-auto-memory)
  section resident in `CLAUDE.md`; its row for Claude Code mechanics, which
  names memory loading; the runtime's own memory prompts; for searching
  session history, the planning row (an investigation).
- **Enforced by**: memory phrase tests on `CLAUDE.md` in
  `tests/test_sync_codex_config.py`; a plugin's own settings and hook
  switches, set by the runbook's claude-mem step; prose otherwise.
- **Project may add**: nothing portable; a project's memory is a host-local
  store under each config dir.
- **Symptoms**: a decision saved only to memory; a topic file without its
  `MEMORY.md` line; status reported from stale memory; a correction saved but
  not routed; a session under one config dir missing what another remembered;
  a subagent assumed to know remembered facts; a plugin's notes or work list
  treated as the record; a file judged from a plugin's note timeline; one
  account's history showing in another account's sessions; a plugin upgraded
  without its settings being checked again.

## Host Integration Mechanisms

### Adapters

The resident entry each agent loads: an identical safety floor, the Direct
Task Routing table, and agent-only mechanics. Claude loads the versioned
workspace `CLAUDE.md`; Codex loads the template installed as a marked block in
`~/.codex/AGENTS.md`.

- **Owner**: [`CLAUDE.md`](../../CLAUDE.md) and
  [`codex-AGENTS.md`](../../.agents/host-templates/codex-AGENTS.md); their
  shape: [Adapter Rule](../../.agents/host-templates/README-agents.md#adapter-rule).
- **Routed by**: every session; Claude reads `CLAUDE.md` from the working
  directory upward, Codex reads `~/.codex/AGENTS.md`.
- **Enforced by**: the gate (every portable owner routed by both adapters,
  each runtime module only by its own, identical safety floors bound to their
  canonical phrases, the missing-entry backstop phrases); adapter tests in
  `tests/test_sync_codex_config.py`.
- **Project may add**: a project adapter that states only narrower facts.
- **Symptoms**: a rule in one adapter only; safety floors that differ; no
  route row for a new owner; portable behavior written into an adapter instead
  of its owner.

### Sync Engine And Managed Surfaces

One synchronizer converges the managed surfaces and nothing else: the marked
Codex AGENTS and hook blocks, the declared Codex preference fields, and, in
every Claude config dir that `CLAUDE_CONFIG_DIRS` lists, the SessionStart
group, the status line, and the managed skills. Every target is rendered and
parsed before the first write.

- **Owner**: `scripts/sync_codex_config.py`, which also discovers the Claude
  config dirs when the host-local, colon-separated `CLAUDE_CONFIG_DIRS` is
  unset (skipping names that look like copies or backups); the `Makefile`
  targets `sync`, `agent-sync-check`, and `bootstrap`;
  `scripts/bootstrap-local.sh`. Ownership classes:
  [layer model](../../.agents/host-templates/README-agents.md#managed-and-host-local-surfaces).
  Design: [configuration architecture](codex-config-management.md).
- **Routed by**: the operator running `make sync` (asks before writing; with
  `SYNC_EXPECT`, applies without asking only when no unlisted area drifted),
  `make agent-sync-check` (never writes), or `make bootstrap`.
- **Enforced by**: `tests/test_sync_codex_config.py` (render, migrate,
  preserve, refuse, idempotence, semantic drift, expected-change refusals, and
  fan-out across config dirs, isolated from the real config dirs);
  `tests/test_bootstrap_local.py`
  (discovery, explicit lists, the no-Python fallback, refusals before any
  write, idempotence).
- **Project may add**: nothing; project settings belong to the project layer.
- **Symptoms**: one config dir lacking a surface another has; drift that a
  second `make sync` does not clear; a field outside the managed set changed;
  a status line owned by another tool replaced or treated as an error.

### SessionStart Evaluator

One ordered startup check for both agents, silent when healthy: workspace-meta
dirty, behind, or ahead after a bounded fetch; environment-registry freshness;
temporary-space use; and project readiness. Inside
`~/workspace/projects/<name>/`, readiness asks whether the Git project root has
an entry file for the agent in use and, for Claude, whether one imports an
existing `AGENTS.md`; for Codex, a root whose owner is `CLAUDE.md` gets an
owner-move hint instead. Only a real Git root counts, and a linked worktree
without entry files of its own is judged by its main checkout.

- **Owner**: `scripts/workspace_status.py`; its hook is hash-pinned and
  installed by the [sync engine](#sync-engine-and-managed-surfaces). The
  readiness warning defines no rule; it points to
  [`documentation.md` Project Bootstrap](../../.agents/rules/documentation.md#project-bootstrap)
  or, for the Codex owner move,
  [`codex-runtime.md` Project Entry Files](../../.agents/rules/codex-runtime.md#project-entry-files).
- **Routed by**: the SessionStart hook in every Claude config dir and in
  Codex; readiness and temporary-space warnings reach the agent as well as the
  operator.
- **Enforced by**: `tests/test_workspace_status.py` (order, rate limits,
  temporary space, hook input, project-root detection, readiness verdicts,
  command-line JSON).
- **Project may add**: its own gate for its entry files; the evaluator is a
  backstop for projects without one.
- **Symptoms**: no warning although the workspace is behind or temporary space
  is full (check that the hook is installed in that config dir); "status
  evaluator changed or is unavailable" until `make sync`; a readiness warning
  for a ready project, or none for an unready one.

### Status Lines

Claude's command status line renders directory, branch, model with effort and
fast mode, context use, five-hour remaining usage, token detail, and session
cost; Codex uses its native ordered status-line items.

- **Owner**: `scripts/claude_status_line.py` for Claude;
  `.agents/host-templates/codex-preferences.toml` (`tui.status_line`) for
  Codex.
- **Routed by**: the managed `statusLine` of each Claude config dir that has
  none or a marked one. A status line without the workspace-meta marker
  belongs to another owner and is kept.
- **Enforced by**: `tests/test_claude_status_line.py`; hash-pin and marker
  tests in `tests/test_sync_codex_config.py`.
- **Project may add**: nothing.
- **Symptoms**: a wrong or missing field; a gauge colored against its printed
  value; another tool's status line overwritten.

### Environment Registry

Each host probes its own capabilities into a generated, Git-ignored registry
with a freshness limit.

- **Owner**: `scripts/env_probe.sh` and `.agents/env/README.md`; the rule is
  [Environment truth](#environment-truth).
- **Routed by**: `make env-probe` and `make env-probe-check`; the evaluator's
  stale-registry message; the `env-sync` skill.
- **Enforced by**: the evaluator's freshness check; the probe script itself
  has no test.
- **Project may add**: nothing.
- **Symptoms**: a missing or stale registry reported every session; a
  registry committed or edited by hand.

### Managed Skills

Workspace-meta skills installed whole-file into every Claude config dir, one
per `.agents/host-templates/<name>-SKILL.md` template: `env-sync` refreshes the
environment registry, `project-bootstrap` creates a project's missing entry
files, and `interview` reads a request at full depth as an interview with the
operator.

- **Owner**: the templates
  [`env-sync-SKILL.md`](../../.agents/host-templates/env-sync-SKILL.md),
  [`project-bootstrap-SKILL.md`](../../.agents/host-templates/project-bootstrap-SKILL.md),
  and [`interview-SKILL.md`](../../.agents/host-templates/interview-SKILL.md),
  each installed as `<config dir>/skills/<name>/SKILL.md`. The behavior each
  applies stays with its owner: [Environment truth](#environment-truth),
  [Documentation and project entry files](#documentation-and-project-entry-files),
  [Understanding requests](#understanding-requests).
- **Routed by**: the skill descriptions Claude loads from each config dir;
  `project-bootstrap` also answers the readiness warning, and `interview` runs
  only when the operator invokes `/interview`.
- **Enforced by**: fan-out and ownership tests in
  `tests/test_sync_codex_config.py` and `tests/test_bootstrap_local.py` (each
  installed skill carries workspace-meta's marker; an existing unmarked skill
  of the same name is another owner's and is kept); the documentation gate
  checks the templates' links and dates.
- **Project may add**: its own skills under `.claude/skills/`.
- **Symptoms**: a skill present under one config dir only; a skill that
  restates its rule and drifts from it; a personal skill replaced by a managed
  one of the same name.

### Documentation Gate

Mechanical checks on workspace-meta's own documents: the root allowlist,
adapter routes (portable owners in both adapters, each runtime module only in
its own), safety-floor binding, the README documentation map, that this map
links every rule owner, links and anchors, no dated observations in current
guidance outside the register and the backlog, the runbook headings, that
routed files are tracked, and that no review record or running plan is tracked
or linked from a current document.

- **Owner**: `scripts/check_documentation.py`; the rules it enforces:
  [`documentation.md` Keep Truth Classes Explicit](../../.agents/rules/documentation.md#keep-truth-classes-explicit)
  and [Committed And Temporary Records](../../.agents/rules/documentation.md#committed-and-temporary-records).
- **Routed by**: `make docs-check`; `make test` runs it first;
  `make verify-committed` runs `make test` on a temporary copy in which every
  file the whitelist admits is committed, so the tracked-file check sees the
  commit before it is made.
- **Enforced by**: `tests/test_governance_docs.py` (the repository passes, and
  each check rejects a broken fixture); `tests/test_verify_committed_copy.py`.
- **Project may add**: its own gate.
- **Symptoms**: a broken link or anchor merged; a dated incident in current
  guidance; a new rule owner not routed or not mapped here; a review record or
  running plan committed or linked.

### Rule Evaluation Harness

Judging a rule change by the behavior it produces: scenarios built from real
decision points are replayed against a headless agent under two rules
versions, graded by checks and a voting judge, and compared.

- **Owner**: `scripts/rule_eval.py`, the scenarios and fixtures with
  [`evals/rules/README.md`](../../evals/rules/README.md), and the `Makefile`
  target `rule-eval`. It is its own harness because `claude plugin eval` loads
  no `CLAUDE.md` and promptfoo needs a Node toolchain to load a chosen rules
  version; recheck when either can. Limits: a one-decision replay cannot show
  long-session habit or compaction, and several targets already pass at their
  ceiling. Its later stages wait in the [backlog](../backlog.md).
- **Routed by**: no rule routes an agent to it; the operator or a
  rule-changing session runs `make rule-eval`, which spends model usage, and
  the evals README explains the scenario format.
- **Enforced by**: `tests/test_rule_eval.py`:
  - the runner with fake agents, including the fields a run records and the
    refusal of a used output directory;
  - the window check and the judge-answer parsing;
  - scenario hygiene, including a check that no scenario repeats rule text,
    and the deletion pattern of `user-run-open-terminal`;
  - structural checks of the rules the harness was built with, and phrase
    checks of the README's Run, How a trial runs, Deciding, and Keeping Runs
    rules and of this entry.

  The harness refuses an output directory that already holds anything, and
  `compare` exits non-zero outside one window. Nothing checks how a commit
  message reports a run or how long the store keeps it.
- **Project may add**: nothing; a project evaluates its own rules with its
  own tools.
- **Symptoms**: a rule change judged only by its wording; a scenario that
  quotes the rule it tests; a comparison in which one version's trials went
  ungraded; an evaluation run that read the real workspace or a real config
  dir instead of copies; an improvement recorded from one small run, or a
  score compared with another day's; a cited run whose outputs and measured
  rules were removed.

### Pre-Commit Guard

The reverse-whitelist `.gitignore` ignores everything except the governance
files; the pre-commit hook refuses any staged path the whitelist ignores, which
only a force-add can produce. Deletions stay possible.

- **Owner**: `.githooks/pre-commit` and `.gitignore`; `make bootstrap` sets
  `core.hooksPath` on each machine.
- **Routed by**: every commit in workspace-meta.
- **Enforced by**: the hook itself; it has no test.
- **Project may add**: nothing; it guards workspace-meta only.
- **Symptoms**: a force-added project or host file in a commit; a new
  governance file that cannot be committed until its allow line exists; the
  guard not running because `core.hooksPath` is unset.

### Feedback Register

The provenance archive: one `W-R<N>` entry per distilled rule, numbers that
never change, and the "Current owner mapping" table from each owner to its
provenance. It is not resident context and governs no behavior.

- **Owner**: [`feedback-register.md`](../../feedback-register.md); the method:
  [`rule-authoring.md` Provenance And Refactoring](../../.agents/rules/rule-authoring.md#provenance-and-refactoring).
- **Routed by**: read when a rule is disputed or derived again.
- **Enforced by**: register tests in `tests/test_sync_codex_config.py`
  (provenance rows per owner, each entry once, entry format).
- **Project may add**: nothing; project-only provenance stays in the project.
- **Symptoms**: a rule whose origin cannot be traced; two entries with one
  number; a superseded entry with no disposition; a register entry applied as
  if it were the current rule.

## How To Change A Domain

1. Find the domain from the [symptom index](#symptom-index) or by owner. Read
   the whole owner and the sections this map links from it
   ([`rule-authoring.md` Edit The Whole Relevant Owner](../../.agents/rules/rule-authoring.md#edit-the-whole-relevant-owner)).
2. Choose the layer before editing, using the
   [layer model](../../.agents/host-templates/README-agents.md#managed-and-host-local-surfaces):
   organization policy, the host user layer of each config dir, the
   workspace, the project, or project-local personal files. A project fact
   stays in its project.
3. Choose the form from the failure
   ([`rule-authoring.md` Match Form To Failure](../../.agents/rules/rule-authoring.md#match-form-to-failure)):
   a positive step in the owner for an omitted step, a check or hook when one
   miss is costly and the condition is mechanical
   ([`problem-follow-up.md` Mechanism Or Rule](../../.agents/rules/problem-follow-up.md#mechanism-or-rule)).
4. Change the owner, then what depends on it in the same change: the route
   rows of both adapters (of one adapter for a runtime module), the safety
   floor when a bound phrase moves, the tests, this map's entry and symptom
   rows, the layer model when a managed surface changes, and the register's
   provenance.
5. A new rule owner also needs its `.gitignore` allow line, an `## Ownership`
   section, a route, and a link here; the documentation gate fails until the
   route and the link exist.
6. Run `make test` (it runs the documentation gate first), the file checks for
   every changed file, and `git diff --check`. A change to a managed surface or
   a hash-pinned script reaches a host only through `make sync` on that host,
   for every config dir it manages.

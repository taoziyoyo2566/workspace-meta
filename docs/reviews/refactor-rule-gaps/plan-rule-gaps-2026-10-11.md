# Plan: portable rules for five gaps found on 2026-10-10 and 2026-10-11

- **Date**: 2026-10-11
- **Level**: Cross-project governance: portable rule owners, both adapters, the
  register, tests, and one workspace-meta script.
- **Status**: COMPLETE on 2026-10-11, content-complete and verified on branch
  `feat/rule-gaps`. Changelog:
  [changelog-rule-gaps-2026-10-11.md](changelog-rule-gaps-2026-10-11.md).
  Publication, `make sync` and the `v1.0.0` tag remain separate approved steps.
- **Approval**: APPROVED on 2026-10-11 ("同意，请继续"), in reply to the request to
  approve this Plan and decide both open questions. Read as: the Plan as
  written, the relayed decisions confirmed, and both open questions decided as
  recommended (Decisions at approval).
  - Earlier on 2026-10-11 the operator approved the direction ("按照建议做"):
    four new rule owners, the session-start temp warning seen by the operator
    and the agent, and the deferrals below.
  - The operator then added a fifth rule, milestones, designed in §5 as
    `releases.md`.
  - Later on 2026-10-11 the operator decided, through session 6a7f577b, when
    and how releases are tagged and fixed (§5), the branch flow in
    `git-branches.md` (§7), and the proposal check in `problem-follow-up.md`
    (§4).
- **Implementation authority**: in-scope working-tree edits on this change's
  branch. Separate approvals are still needed for:
  - the branch action before the first rule edit;
  - staging, commit, merge, and push;
  - `make sync` on each host;
  - the `v1.0.0` tag.

## Goal

Close five gaps in the portable rules. Each new rule covers its class of
problem; the incidents that exposed the gaps go only into the register:

1. A file created or changed is not checked by its type, from syntax to
   security, before it is called done.
2. Nothing says what may serve users: the main deployment branch, how
   temporary deployments end, and when to deploy after a commit.
3. Nothing governs an agent's own temporary files.
4. A report on a handled problem need not give the cause, why existing
   safeguards missed it, proposals against recurrence, and where the lesson is
   kept.
5. Nothing marks a released batch of work with a version that records why,
   how, what, how to inspect it and how it was verified, and that names the
   version to roll back to.

The same change also writes the branch flow into `git-branches.md` (§7): no
rule says that a change goes through a short-lived branch before it reaches the
main branch.

The rule set stays MECE: each new owner has one trigger and one domain, and the
overlaps it absorbs are removed from existing owners in the same change.

## Operator decisions and words

- 2026-10-10, correcting the W-R53 draft (read the warnings of runs): "我要纠正一下，
  当前是因为这个原因才考虑添加规则，而不是添加规则是为了避免当前这个问题。这个检查你放错位置了，他原本应该在
  当前这个文件修改完后，声明文件做成或者修改完之前就得检查，而且不光要检查这一点，二十根据文件类型，从语法到
  文件是否没有安全问题这一连串的检查，之前可能已经有了类似的检查，请调查一下，我是觉得根据mece原则新建规则文件
  纳入检查的规则scope，或者修改已有的规则。这应该属于通用型规则，你怎么看？"
- 2026-10-10: "部署的项目，他应该使用以ops分支内容为主要部署分支来提供服务，其他分支只能作为临时的。
  其中那个分支是主分支属于项目memory，以主分支来作为稳定部署分支是通用规则".
- 2026-10-10: "当代码已经提交了，本身不是就应该用最新的代码部署一下，来确定当前的修改没有问题。这样可以
  再发现问题就直接改正，而不是在某一天部署适合失败了，还得回忆为什么失败，是什么时候的修改造成的".
- 2026-10-10, after `/tmp` filled up: "你竟然没有给出建议，当发现了问题又解决了之后，没有思考过如何
  避免类似问题，或者吸纳当前的处理经验。"
- 2026-10-11: "按照建议做". This approves:
  - this Plan for four owners: `file-checks.md`, `deployment.md`,
    `temporary-files.md` and `problem-follow-up.md`;
  - dropping the W-R53 draft and reusing its number;
  - the session-start temp warning (§6), shown to the operator and the agent;
  - no host cleanup-age change and no move of Claude's temp root for now
    (Scope, deferred items).
- 2026-10-11, the fifth rule: "在一个任务彻底收尾后，要做一个里程碑式的提交，要记录这次修改的缘由，
  做法，涉及到的的scope，怎么去看，以及验证结果，算作是这一大批任务彻底结束，距离上一个里程碑式的提交是另外
  一个功能性，或者改进型的变动。如果发现问题要撤回到的版本。这算是一个通用规则规则，请根据我的想法，梳理并
  完善一下，然后给出一个改进方案".
- 2026-10-11, relayed by reality-ops session 6a7f577b. This Plan's approval
  confirms that the relay is accurate.
  - When to tag and how to fix: "里程碑什么时候打？从发布验证完就打怎么样？我考虑到即使运行一段时间，
    也有可能发现bug，或者改进之类的。……这个里程碑式提交，也可以理解成一个大版本提交，比如1.0.0到1.1.0。
    1.1.0到1.2.0这种。如果后续发现1.1.0涉及到内容有需要修改的，基于1.1.0来修改，改后版本为1.1.1，
    在测试环境中回退到1.1.1来测试，发布，如果没问题了merge到后续的版本中，然后再后续版本中再次校验，发布，
    确认没问题了，这个修复任务才算完成，这个属于fix范围的内容。我的大概意思你理解一下，我描述的可能不是很准确，
    也不一定是当前最佳实践". The session added that fixes follow the version
    running in production, that there is no test environment, and that a
    deployment from a branch is temporary. The operator: "你补充的3点很好，由1给出点建议我接受，
    那么2，3的问题就不存在了，对吧。……新系统从2.0.0开始吧". The relay, as corrected
    by the session, settles:
    - tag right after a release is deployed and verified; the tag records what
      was released, not that it has no problems;
    - a batch is a milestone and raises MINOR; only an incompatible change
      raises MAJOR; a fix raises PATCH, is tagged, and is a valid rollback
      target, but is not a milestone;
    - a fix is complete only when its patch release is verified and released,
      and again after it is carried into later versions;
    - a fix follows the project's branch flow from the main branch and is
      released as a patch of the current version; only when production has
      rolled back to an older release and must be fixed there does the fix
      branch start from that release's tag;
    - no separate test environment is needed for routine work, and a deployment
      from a branch is the rare temporary case of `deployment.md`;
    - the starting version is a project fact; reality-ops' new system starts at
      v2.0.0, recorded by session reality-ops-01.
  - "同意，第2条放进 problem-follow-up.md": before proposing a procedure, check it
    against the existing rules and decisions. The session had proposed "直接在
    ops 上修", which contradicts the operator's 2026-10-06 branch decision.
  - "这个是通用规则，为什么放到reality-ops里面的agents？": the general part of the branch flow
    goes into `git-branches.md`. Every change starts on a short-lived branch from
    the main branch, named by type (docs, fix, feature); it is changed and
    checked there, then merged into the main branch by the project's route;
    nothing is committed directly to the main branch. Project facts stay in each
    project.
  - "工作树规则不用改，保持现状": `git-branches.md` Isolation ("Prefer an additive
    worktree") stays as it is. reality-ops' branches in its main checkout are
    that project's stricter constraint, written by reality-ops-01.
- The proposal the operator approved stated three readings:
  - "其他分支只能作为临时的" means that deploying from another branch is
    temporary; development branches themselves follow `git-branches.md`;
  - "属于项目memory" means the project's agent instructions (Project Facts),
    which every agent loads;
  - the rules are not extended to a project's old system that the operator
    has frozen unless the operator asks.

## Current state (2026-10-11)

- `.agents/rules/` has 17 owners; the register's last committed entry is W-R52
  (`1d5dc18`). The working tree holds:
  - the uncommitted W-R53 draft in `verification.md` and
    `feedback-register.md`;
  - unrelated changes under `docs/reviews/project-memory-governance/`, which
    belong to other work. Leave them out of this change.
- **File checks.** `verification.md` Required Result item 2 accepts any
  successful parse. W-R52's checks cover only scripts handed to the user, and
  `documentation.md` covers only documentation. No rule requires a check that
  can fail on the defect, or a per-file chain before a file is called done.
  - In the source incident, a check did run right after each vault edit, four
    times. It used a loader that keeps the last of repeated keys, so all four
    runs passed. The moment was right and the check was weak.
- **Deployment.** No owner. `authorization.md` says it defines no deployment
  targets.
- **Temporary files.** Only W-R52's `/tmp` location for one-off scripts.
- **After a fix.** Only two narrower rules: `verification.md` Failure And Retry
  for the agent's own failing checks, and `review.md` Completion ("closeout
  states what changed and remains").
- **Milestones.** Pieces exist, none of them a release identity:
  - `planning.md` closeout (Plan `COMPLETE` plus a Changelog), written before
    anything is deployed, and its last line that release is a distinct fact;
  - `verification.md` Release Evidence: tie evidence to the revision and run
    post-deployment checks;
  - `git-publication.md` and `git-recovery.md` mention tags only as protected
    mutations; `git-recovery.md` owns "tag" alongside rewrites.
  - No version scheme, release record or named rollback point.
  - Observed in projects (read-only, 2026-10-11):
    - workspace-meta has no tags;
    - reality-ops has annotated tags `v1.0.0` and `v1.1.0` on its old system,
      with one-line messages ("single docker with monitor"), and two
      `restore/2026-09-30-*` tags made by hand as restore points;
    - reality-ops' `./deployctl rollback` already returns a component to its
      previous release or `--to <commit>`. It refuses to cross a vault change, a
      vault password change or a newer database schema unless the operator
      allows it, and does not roll back data;
    - two projects carry upstream tags (`blinko`, `Wallos`), and `saberu` has
      `v0.0.1`.
- **Branches.** `git-branches.md` reviews branch actions and prefers an
  additive worktree, but no rule says a change goes through a branch at all.
  workspace-meta commits directly to `main`. reality-ops decided on 2026-10-06
  to work on `docs/`, `fix/` and `feat/` branches and fast-forward them into
  `ops`; that decision is so far only in Claude's host memory.

## Intended change

### 1. `file-checks.md` (W-R53)

**Trigger:** a file that is delivered or kept (repository files, host
configuration, files handed over), checked before it is reported done, handed
over, committed or deployed, or relied on by another person or by an
irreversible action.
- Included: a file the operator changes in a step the agent directs.
- Excluded: transient working files (defined in `temporary-files.md`).

**Stages, in order:** container and bytes → syntax → strict format (what the
format forbids, such as repeated keys) → consistency (the consumer accepts it,
references resolve, only the intended content changed) → security, bounded to
this file.

**Required properties.** These include the review fixes:
- **A check counts only for what it can detect.** It must actually read the
  changed file, and it must fail on the defect. Show this on a dummy sample when
  its strictness is unknown. A loader that collapses repeated keys does not
  pass stage 3, and a key diff counts every occurrence.
- **No values in output.** Every stage run on secret-bearing content, including
  the consumer run, produces output with no values. Inventory or variable dumps
  print values.
- **Warnings.**
  - Fail only on warnings that this change introduces or newly triggers.
  - A warning that exists at the base revision, or that the project lists as
    accepted, passes when it is named with its cause.
  - Loosening a check means anything beyond a narrow, reasoned suppression
    (`implementation.md`).
- **Stage 1 default:** no trailing whitespace and a final newline, unless the
  format or the project requires otherwise. This keeps W-R52's script check.
- **Report:** one line per file class; details only for failures, warnings and
  gaps.
- **Size and commands.** The rule stays near the size of `verification.md`.
  File-class examples go to `docs/standards/development.md`. Projects own the
  commands.

**Seams:**
- `verification.md`:
  - item 2 becomes a pointer to this owner;
  - the W-R53 paragraph is removed;
  - one sentence remains for later runs: a run's result includes the warnings
    it newly shows.
- `capabilities.md` keeps its explicit script checks or points here.
- `implementation.md` and `documentation.md`: their Ownership lines.
- `secrets.md` points here for checking without revealing values.
- `rule-authoring.md`: its duplication check is scoped to agent rule owners.
- Safety-floor bullet in both adapters: "Before calling a created or changed
  file done, including one changed in a step you direct, run its file-type
  checks."

### 2. `deployment.md` (W-R54)

Owns four things: what may serve users, deploy cadence, temporary deployments,
and instances found outside the project's inventory.

- **Main branch.** Anything that serves users, or can take over that role, runs
  a commit reachable from the pushed main deployment branch tip. A standby runs
  the same release as the instance it can replace. The branch name is a
  project fact.
- **Firm floor:**
  - never deploy uncommitted content to such an instance;
  - never bypass the project's entry point or guard;
  - use a non-normal mode only when the project's procedure names it as the
    remedy for that refusal, under its own brief.
- **Temporary deployment.** It is temporary when its source is not on the
  pushed main branch, or when the instance exists for a test, preview, drill
  or migration.
  - Before it starts, the Plan step names its purpose, place, holdings, owner
    and end condition.
  - The exact commit and its pushed state go in the brief and in the project's
    deployment record, not into a frozen Plan.
  - It ends in one of two ways:
    - the change reaches the main branch by a route the project permits, and
      what ran stays identifiable (the merge mode is left to the project);
    - or the instance is removed.
  - A patch on an older release line (§5, Fixes) is such a deployment. It
    ends only in one of three ways:
    - its commit becomes reachable from the main branch through a plain merge;
    - a release from the main branch that carries the fix replaces it;
    - or the instance is removed.

    A cherry-picked or squashed copy on the main branch does not end it. Until
    it ends, its release tag keeps what ran identifiable.
- **Deploying an older release (rollback).** The target is a release tag
  (§5). Before deploying it, check what the range from that tag to the running
  version changed in three places, and follow the project's procedure for each:
  - versioned secrets: revoked credentials come back, and an older encrypted
    file may need its older password;
  - data and schemas: data does not roll back, so the older release must still
    read the current data;
  - interfaces between components: a component rolled back alone must still
    work with the others, which stay on newer releases.

  The rollback is a deployment under this rule. The fix goes forward from the
  main branch (§5).
- **Hold after a rollback.** A rolled-back component stays on its rollback
  target until a commit that carries the fix is pushed, and its deployment
  record shows the rollback. Until then, Cadence does not propose deploying the
  main branch to it.
- **Cadence.** After pushing a commit that changes what a component runs,
  propose deploying it promptly and verify. A commit that changes nothing that
  runs needs no deploy.
- **Instances outside the inventory:**
  - identify them read-only, without reading secret values or elevating
    privilege unless approved;
  - record them as a finding;
  - report them with a recommendation;
  - act only after the operator decides.
- **Declared non-production environments** follow the project's
  environment-tier policy, which is a project slot.
- **Protected actions** are written as proposals under the `authorization.md`
  brief. Fixing a guard refusal never commits, stashes or moves unrelated work.
- **No project names in the rule text.** A generic removal checklist goes to
  the handbook or to project runbooks.
- **Seams:**
  - the route row;
  - the README-agents owner row, rewording `git-integration.md`'s
    "release/archive policy" slot;
  - an `authorization.md` Ownership clause;
  - `git-integration.md` Retirement Boundary: before retiring a branch or
    worktree, confirm that no instance runs a commit only it contains, unless a
    release tag keeps that commit;
  - `releases.md` (§5): release tags name the rollback targets and record what
    ran; this rule deploys them.

### 3. `temporary-files.md` (W-R55)

- **Placement.**
  - Small files go in the runtime's per-session scratch location.
  - Large data needs a check first: free space, and whether the filesystem is
    memory-backed with swap in use. Large data includes copied trees,
    build/test output, multi-agent run outputs, tool installs, browser
    downloads and package caches. This is a conditional rule, not a blanket
    tmpfs ban.
  - Prefer reading in place.
  - Temporary files are private by default. Where secret material may go
    follows `secrets.md`.
- **Lifecycle.**
  - Whoever creates temporary files removes them when they are no longer
    needed.
  - On failure, first move what diagnosis or a resumed run needs to its owner.
  - The orchestrator removes a multi-agent run's directory.
  - The runtime's own files are not the agent's to remove: the session temp
    root, command-output files and transcripts.
  - Anything kept has a reason, an owner and a removal condition.
  - The final report has one line on temporary files.
- **Temp is not a store.** Evidence and handoff state go to their owners.
- **Full or filling temp.**
  - Stop writing there and remove your own temporary files.
  - Measure with `df` or `statvfs`, not with tree walks that refresh access
    times.
  - Remove others' files only at the operator's request, after in-use checks:
    open file descriptors, live or resumable sessions, containers, and
    references. Report which processes could not be inspected.
  - Then `problem-follow-up.md` applies.
- **Host settings.** Host cleanup ages and temp roots are host configuration;
  propose changes with the brief.
- **Seam.** `capabilities.md` gets one sentence. The location of the user's
  one-off scripts stays there; their removal is owned here.

### 4. `problem-follow-up.md` (W-R56)

**Trigger:** reporting a problem you found or were told about as fixed,
mitigated, or left to the operator, when at least one holds:
- it affected shared state or other people's work: lost output in another
  session, a degraded service, an exhausted shared resource, a wrong
  delivered, committed or deployed artifact, or data or a secret at risk;
- it was found by chance or by someone else;
- it happened before.

Excluded: errors the agent fixed itself in the same turn. A baseline check
failure follows `verification.md`, and triggers this rule only when one of the
conditions above holds.

**Report parts, in order.** A part may be one line, but none is left out:
1. outcome and current state;
2. cause chain to the class level, labelled per `reasoning.md`;
3. why each existing safeguard missed it, and how it could be detected earlier;
4. recurrence;
5. proposals, ordered by necessity and then by stability and security; each
   names its owner, its effect, its cost and risk, whether it needs approval,
   and how to tell it worked;
6. the lesson and where it is recorded.

**Check a proposal against what is already decided** (operator decision,
2026-10-11). This applies to every part 5 proposal, and to any procedure or
working practice the agent proposes, for example a fix, rollback, release,
branch or deployment flow. The decision covers any proposed procedure, so it is
not limited to problems. This owner's domain is therefore proposals and the
follow-up after a problem, with one trigger: the agent proposes how work should
be done, or reports a handled problem.
- Before proposing it, check it against the rules and recorded operator
  decisions it touches:
  - the shared rules;
  - the project's agent instructions;
  - the Plans and decision records on the same ground (`planning.md` Before
    Planning).
- Host-local memory is a lead. A decision found only there is reported as
  unrecorded, and its owner is named (`planning.md`).
- Name each conflict and which source governs. Never offer a proposal that
  silently contradicts a recorded decision.

**Mechanism versus rule.** Prefer a mechanism over relying on agents to
remember only when:
- the class recurred after a rule landed; or
- one miss causes data loss, an outage or exposure.

Otherwise propose the rule and record the mechanism as deferred (W-R50).

**Deferral.** A deferred item is recorded in its owning artifact, with an owner
and a restart condition. Until the operator names an owner, a memory entry
holds it, marked unowned and unrecorded (`planning.md`).

**Seams:**
- the route row's trigger: "proposing a procedure or practice, or reporting a
  handled problem";
- `review.md` Completion;
- `planning.md` Record Decisions: a deferral's restart condition;
- `rule-authoring.md` Provenance: a rule covers the class, and the incident
  goes to the register.

### 5. `releases.md` (W-R57)

**How the design meets the request.** The operator asked for a milestone commit
that closes a batch. It records why, how, the scope, how to inspect it, the
verification results, and the version to roll back to. The commit that lands a
batch exists before the batch is deployed, so it cannot carry the release's
verification. The milestone is therefore an annotated tag on the released
commit, made after the release is verified, and the tag message is the record.
No extra commit is made.

Earlier answers, 2026-10-11: "标记方式：我自己知道的是标签；怎么回撤：之前有做过回撤的功能，
具体啥情况，现在我不是很清楚，我考虑到的是可以在稳定运行中的情况下，回撤到某一个里程碑式的提交，这是新加的功能，
作为reality-ops算是新功能。其余按照推荐来。" Rolling a running system back to a milestone is a
reality-ops feature, designed there (roadmap §7 row "按里程碑回退").

**Owner.** A new owner. Its trigger and its domain (which released states are
versions, and what they record) belong to no existing owner. With seams only,
the record would sit in `planning.md`, the tag in `git-publication.md`, and the
target in `deployment.md`, and the version scheme and the fix line would have
no owner. The split: `deployment.md` decides what runs; `releases.md` names what
ran.

**Trigger:**
- a batch or a fix has been released, that is deployed and verified, or, for a
  project that does not deploy, published as the project defines it and
  verified;
- choosing a version number or a rollback target;
- fixing a problem in a released version.

**Applies to** every project that delivers something used outside its
repository: a service, an installed tool, rules synced to hosts, a published
package.
- A project with nothing released says so in its Project Facts, and so does a
  project whose versions belong to an upstream it tracks.
- When a releasing project has no recorded scheme, ask the operator for its
  starting version and prefix at its first release. Never invent one.

**Terms:**
- *release*: a commit that was deployed (or published) and verified, marked by
  a version tag. It is on the main branch, or on an older line cut from a
  release tag (Fixes);
- *milestone*: a release that closes a batch. A batch is one functional or
  improvement change, often one Plan's workstream;
- *patch release*: a release made for a fix.

**Version numbers.** They use the MAJOR.MINOR.PATCH form of Semantic Versioning
2.0.0. The largest change in the range since the previous release decides the
number:
- a change that breaks the project's compatibility surface raises MAJOR. The
  project names that surface, for example client configuration, data formats,
  operator commands or APIs; SemVer calls it the public API;
- otherwise, a closed batch raises MINOR and resets PATCH;
- otherwise, a release raises PATCH.

This departs from strict SemVer. Because merged work is deployed promptly, a
patch released from the main branch also carries any unfinished work merged
since the previous release. The notes list that work under scope.

**When to tag.** Tag right after the release is deployed and its
post-release checks pass (`verification.md` Release Evidence).
- The tag records what was released. It does not claim that the release has no
  problems; a problem found later becomes a patch release.
- A release whose checks fail is not tagged. It is fixed forward or rolled back
  (`deployment.md`).

**What is tagged.** Tag the exact commit that the release runs, as the
project's deployment record shows it.
- In a project that integrates through pull requests, that is the merge or
  squash commit on the main branch.
- Every component that the range changes runs a commit whose content for that
  component's paths equals the tagged commit's. A component the range does not
  change needs no redeploy.

**Tag kind and name:**
- annotated. Git documents annotated tags for releases and lightweight tags for
  private or temporary labels, and `git describe` ignores lightweight tags by
  default;
- named `v<MAJOR>.<MINOR>.<PATCH>` by default. A project whose repository also
  carries upstream or other tags names its own prefix;
- the tagger is the operator's configured Git identity, with no AI attribution;
- signing is a project choice.

**The tag message is the release notes.** Its parts, in this order; a part may
be one line:
1. version and kind (milestone or patch), date, the commit, and the previous
   release;
2. why: the batch's goal. For a patch, the problem and the release that
   introduced it;
3. how: a short paragraph, or links to the Plan and Changelog where they exist,
   without copying them;
4. scope: the components and surfaces changed, the range
   `<previous>..<this>` with its commit count, and the other changes in the
   range;
5. how to inspect:
   - `git show`, `git log --oneline` and `git diff --stat` over the range;
   - the Plan and Changelog paths;
   - the project's command that shows which version each part runs;
6. verification: the post-release checks and their results, with gaps named;
7. rollback: the target release, and whether going back crosses a one-way
   change in the range (secrets, credentials, a data schema) and which project
   procedure handles it.

Rules for the message:
- It holds no secret values.
- It is written to a file in the session scratch location
  (`temporary-files.md`).
- There is one copy of each narrative. The Changelog keeps the verified
  workstream outcome written at closeout; the tag keeps the release facts and
  links to it.
- A project may publish a release history generated from its tags, never a
  hand-kept second copy.

**One batch per milestone.** Each milestone names one batch.
- Parallel sessions interleave commits, so the range may also hold fixes,
  documentation, or parts of other work merged in the meantime. The notes list
  them under scope.
- The tag never waits for these changes or squashes them. Frequent commits and
  prompt deploys (`deployment.md`) continue unchanged.

**Tagging is a protected action.** It needs the `authorization.md` brief, and
the bundle is:
- `git tag -a --cleanup=whitespace <tag> <commit> -F <message-file>`. The
  default cleanup would drop every line that starts with `#`, such as a
  Markdown heading;
- `git push <remote> refs/tags/<tag>`, which pushes one tag; never `--tags`.

Afterwards, check that the tag is annotated, points at the commit, and exists on
the remote.

**Published tags never move.** A pushed release tag is never moved or deleted.
Git's "On Re-tagging" advises a new name, and SemVer says a released version's
contents must not change.
- A wrong tag or a bad release gets the next patch version. Its notes say which
  release it replaces.
- Moving or deleting a tag stays with `git-recovery.md`.

**Fixes** (operator decision, 2026-10-11):
- Normally a fix follows `git-branches.md`:
  - a fix branch starts from the main branch;
  - the fix is made and checked on the branch, then merged into the main
    branch;
  - it is released from the main branch as a patch of the current version;
  - the notes name the release that introduced the problem.
- Only when production has rolled back to an older release and must be fixed
  there:
  - a fix branch starts from that release's tag;
  - the patch takes the next number on that line, for example `v2.1.3` while
    the main branch is at `v2.2.x`;
  - it is verified and released as a temporary deployment (`deployment.md`);
  - the fix is then carried into the main branch by the project's route, and
    verified and released again there.
- Either way, the fix is complete only when every line that needs it has been
  verified and released.
- Order on the older line: when the problem also reproduces on the main branch,
  fixing it there first and carrying the fix to the older line keeps the fix
  from being forgotten. Trunk-based development recommends this order. The rule
  leaves the order open, because the completion condition already covers that
  risk.
- Once the patch's tag exists, the older line's branch may be retired, because
  the tag keeps its commits.

**Rollback target.** Roll back to the newest release that the running commit
descends from and that does not contain the change at fault.
- When the fault is in commits merged after the latest release, that release is
  the target, for example `v2.2.0` when production runs `v2.2.0-3-g…`.
- When the fault is in the latest milestone's batch, the target is the latest
  release of the previous milestone line, including its patches, for example
  `v2.1.2` rather than `v2.1.0`.
- This refines the earlier "previous milestone". Going back further than the
  fault discards verified work and crosses more one-way changes.
- Projects own the procedure, and `deployment.md` owns the checks before an
  older release is deployed and the hold after it.

**Visibility.** A project that shows what each instance runs also shows its
version.
- One source is `git describe --match '<prefix>[0-9]*'` of the running commit,
  without `--tags`, so that only annotated tags with the project's prefix
  count. For example, `v2.1.0-3-gabc1234` is three commits after `v2.1.0`.
- The status surface is a project slot.

**Project slots:**
- whether the project releases;
- the starting version and the tag prefix;
- the compatibility surface;
- what "released" means: its deploy targets or its publication;
- the status surface;
- the rollback procedure;
- signing.

**Considered and not adopted:**
- a separate milestone commit, empty or notes-only. Either the tag moves off the
  commit that ran, or a commit is added that changes nothing;
- tagging only after a stable-running window. The operator decided against it,
  and a window does not prove the absence of problems either;
- a hand-kept `CHANGELOG.md` as in Keep a Changelog. It would be a second copy
  of the tag notes and the Changelogs, and its "Unreleased" section has little
  use when every merged change is deployed promptly;
- versions computed from Conventional Commits types. A milestone is a batch that
  the operator closes, not a sum of commit types. A project that already writes
  those types may use them to check the bump;
- release trains. Batches here close by content, not by calendar.

**Seams:**
- `planning.md` Handoff And Closeout: release and its tag follow
  `releases.md`, and the tag notes link the Changelog;
- `documentation.md` Changelog role: release notes link it and never copy it;
- `git-publication.md` Ownership: release tags go to `releases.md`. Working-tree
  authority still never includes a tag;
- `git-recovery.md` Ownership: "tag" becomes moving or deleting tags; creating a
  release tag goes to `releases.md`;
- `git.md`: its module list and its Pre-Mutation State cover release tags;
- `git-integration.md` Ownership and Integration Review: "release fields" point
  to `releases.md`;
- `deployment.md`: the rollback checks, the hold after a rollback, and the patch
  on an older line (§2);
- `verification.md` Release Evidence: unchanged, and its results fill notes
  part 6. Tags already needed approval, so this adds no new approval layer;
- the route row names `authorization.md`, `git.md` and `releases.md`.
  `test_protected_git_routes_require_action_brief` in
  `tests/test_sync_codex_config.py` adds `releases.md` to its module list and
  route specs;
- a README-agents owner row: "releases and version tags | `releases.md` |
  starting version, prefix, compatibility surface, status surface, rollback
  procedure";
- `docs/standards/delivery.md`: a sample release note.

**Size:** about 70 lines.

**Sources checked on 2026-10-11:**
- git-tag and git-push reference (git-scm.com): annotated versus lightweight
  tags, `git describe`, "On Re-tagging", and that `--follow-tags` pushes only
  annotated tags reachable from the pushed refs;
- Semantic Versioning 2.0.0;
- Keep a Changelog 1.1.0;
- Conventional Commits 1.0.0;
- trunkbaseddevelopment.com "Branch for release": fix on the trunk first, cut
  a branch from a release tag only when a patch is needed, and tag before
  deleting a release branch.

### 6. Session-start temp warning (`scripts/workspace_status.py`)

- **The check.** Read the filesystem of the agent's temp root with `statvfs`.
  Use the hook input's scratch directory when present, else `TMPDIR`, else
  `/tmp`.
- **The warning.** Warn when usage reaches 80% or free space falls below an
  absolute floor. The warning names `temporary-files.md`. It reaches both the
  operator and the agent; this changes today's operator-only output and was
  decided on 2026-10-11.
- **Tests.** Add a unit test with an injected `statvfs` result.
- **Hook hash.** The hook's hash changes, so Codex asks to re-trust it after
  `make sync`.

### 7. Branch flow in `git-branches.md` (W-R58)

This amends the existing owner; no new file is created (operator decision,
2026-10-11).
- **New section "Change Flow",** before Isolation:
  - every repository change starts on a short-lived branch from the main
    branch. Its name starts with its type from the project's list, for example
    `docs/`, `fix/` or `feat/`, and names its topic;
  - the change is made and its checks run on the branch (`file-checks.md`,
    `verification.md`). Then it is integrated into the main branch by the
    project's route (`git-integration.md`);
  - nothing is committed directly to the main branch;
  - fix and release flows follow it (`releases.md`). A fix for an older release
    branches from that release's tag.
- **The flow governs commits, not edits.**
  - Uncommitted edits may start in the current checkout. Before the first
    commit at the latest, they move to the change's branch through the existing
    branch action that preserves the diff (Content Non-Interference).
  - So an operator decision is still recorded in the same turn
    (`planning.md`), and authorized edits still proceed without another
    confirmation (`authorization.md`). Neither text changes.
- **Unchanged: Isolation.** "Prefer an additive worktree" stays, by operator
  decision on 2026-10-11.
  - A project that works on branches in its main checkout records that choice
    in its Project Facts.
  - Each in-place branch action still goes through its review.
- **Project slots:** the main branch, the type prefixes, the merge route
  (fast-forward, merge commit or pull request), and the checks.
- **Seams:**
  - the Ownership line adds the change flow;
  - the route row keeps its leading words "branch/worktree/stash action",
    because `test_protected_git_routes_require_action_brief` matches rows by
    prefix. It appends ", or starting a repository change";
  - the README-agents row for branch/worktree/stash adds the change flow and
    its prefixes;
  - `git-integration.md` names the change flow's merge as its ordinary case.

## Scope and exclusions

- **In scope:**
  - rule owners: five new ones, the seams in existing ones, and the
    `git-branches.md` change flow;
  - both adapters;
  - `.agents/host-templates/README-agents.md`;
  - the root `README.md` rule list;
  - `feedback-register.md`;
  - `docs/standards` pointers and a sample release note;
  - tests;
  - `scripts/workspace_status.py`.
- **Out of scope:**
  - project files (their deltas are follow-ups, done in each project);
  - host configuration;
  - frozen old systems;
  - other projects' conflicts with the new rules, which are reported only.
- **Deferred, with restart conditions:**
  - **A 3-day systemd-tmpfiles age for the Claude temp tree.** It would delete
    files of an open but idle session; one has been open since 2026-10-06.
    - Restart when the §6 warning fires again after `temporary-files.md` lands,
      or when ENOSPC recurs.
    - Then pick an age above the longest idle open session, and dry-run the
      candidate file with `--replace` before installing it.
  - **Moving Claude's temp root to disk (`CLAUDE_CODE_TMPDIR`).** It changes
    every session's path, and the root filesystem is 81% used. Same restart
    condition.

## Landing order and mechanics

- **One change, in this order:**
  1. W-R53 `file-checks.md` (replaces the uncommitted draft);
  2. W-R54 `deployment.md`;
  3. W-R55 `temporary-files.md`;
  4. W-R56 `problem-follow-up.md`;
  5. W-R57 `releases.md`;
  6. W-R58, the `git-branches.md` change flow.

  Recheck the last W-R number when writing.
- **This change follows its own branch flow.** Once §7 is approved, this
  change lands through a short-lived branch, for example `feat/rule-gaps`.
  - The branch action is reviewed before the first rule edit: worktree or in
    place, and how the uncommitted Plan and W-R53 draft move.
  - The unrelated `project-memory-governance` changes stay out of it.
- **Per new owner:**
  - a `.gitignore` whitelist line;
  - identical route rows in `CLAUDE.md` and
    `.agents/host-templates/codex-AGENTS.md`;
  - a README-agents owner row;
  - the root `README.md` rule list;
  - the three module lists in `tests/test_sync_codex_config.py`;
  - `scripts/check_documentation.py`, where it enumerates sources;
  - the register owner map.

## Acceptance

- **Each new owner:**
  - has one trigger and one domain;
  - its overlaps are removed from the owners listed in its seams;
  - the rule text names no project;
  - its size is close to existing owners (report actual line counts).
- **Baseline.** Each rule's source incident is caught at the rule's trigger.
  Name the stage or report part; for example, `file-checks.md` stage 3 on the
  repeated vault keys. For §5 and §7:
  - `releases.md`: reality-ops' `v1.1.0` message "single docker with monitor"
    fails notes parts 2–7, and its hand-made `restore/` tags would be release
    tags with a named rollback target;
  - `git-branches.md` Change Flow: reality-ops' 2026-10-06 commits `5348bc9`,
    `79b6af8` and `f79e7d5`, made directly on `ops`;
  - `releases.md` Fixes and `problem-follow-up.md`'s proposal check: the
    2026-10-11 proposal "直接在 ops 上修".
- **Checks:**
  - `"$PYTHON" -m unittest discover -s tests -v`;
  - `make docs-check` and `make test`. Two failures are expected and reported by
    name, not as passed:
    - "routed documentation is not tracked", until exact-path staging;
    - the 63 errors that come from the ignored `docs/reviews/feature-doc-registry`.
  - `bash -n`, `py_compile` and `git diff --check`;
  - bootstrap twice in a temporary HOME, with unchanged hashes;
  - the §6 unit test.
- **Independent review.** An independent read-only review of the rule texts runs
  before the publication brief.

## Risks

- **Load.** Five more routed owners. Mitigated by tight triggers and small
  files.
- **Approval count.** The branch flow adds branch creation, a merge and often a
  rebase to every change (Open question 1).
- **Branches in a shared checkout.** In reality-ops, parallel sessions share
  the main checkout. An in-place branch switch there moves every session's
  view, and `deployctl` refuses to deploy until the checkout is back on `ops`.
  This is reported to reality-ops with its follow-up; the operator decided the
  project's mode.
- **Version-scheme adoption.** Each releasing project needs a starting version
  and prefix. The agent asks once, at the project's first release, and never
  invents them.
- **Conflicts with project instructions.** One example is a project whose agent
  deploys an uncommitted tree into its production slot. Report each conflict
  per project and resolve it in that project's own task.
- **Hook contract.** §6 changes the session-start output contract for both
  agents.

## Decisions at approval (2026-10-11, "同意，请继续")

Both questions were decided as recommended. Their changes land with W-R58 (§7)
and in the seams it names.

1. **Approvals under the branch flow.** Today, creating a branch or worktree,
   the publication, the merge into the main branch, and deleting the branch are
   each a reviewed transaction. A routine change would then need about four
   confirmations. Recommendation:
   - creating an additive worktree on a new branch from the main branch is part
     of an authorized change, and is reported rather than confirmed;
   - an in-place branch action keeps its review;
   - one publication bundle under one brief may cover the disclosed sequence:
     commit, the project's merge into the main branch, push, and deletion of the
     merged branch. Any drift, a non-fast-forward or a failed check stops it;
   - in a project that only fast-forwards, parallel sessions move the main
     branch, so a change branch often needs a rebase first. Today each rebase is
     a history rewrite under `git-recovery.md` (Reset Or History Rewrite),
     with a recovery ref kept until the operator releases it. Recommended: the bundle may rebase the
     change's own unpushed branch onto the main branch and re-run its checks. It
     reports the pre-rebase tip as the recovery point, and stops on any
     conflict.

   This changes approval semantics in `git-branches.md`, `git-publication.md`,
   `git-integration.md` and `git-recovery.md`, which are seams of §7.
2. **workspace-meta's own releases.** Under `releases.md`, workspace-meta
   releases the rules it syncs to hosts. Recommendation:
   - adopt tags, starting at `v1.0.0` on the commit that lands this change;
   - tag after the push and `make sync` are verified on each host;
   - "released" means pushed to `main` and synced on the hosts.

   These facts go into workspace-meta's project facts in the same change.

## Follow-ups owned elsewhere

- **reality-ops:**
  - a per-file-class check list in `docs/operations.md` §14.5;
  - the 2026-10-06 branch workflow in `AGENTS.md` Project Facts, with prefixes
    written as `fix/<topic>` so `tests/test_agent_entry.py` skips them;
  - a deploy-cadence line in `docs/runbooks/deploy-and-rollback.md`;
  - the release scheme in Project Facts: the new system starts at `v2.0.0`,
    with the compatibility surface and what "released" means (reality-ops-01
    records the start);
  - `./deployctl status` showing each instance's version (`releases.md`
    Visibility);
  - the route for carrying an older-line fix into `ops`. `--ff-only` cannot
    carry it; emergency mode already requires a plain merge;
  - the roadmap §7 row "按里程碑回退": its research point "何时打（部署核对、稳定运行一段时间之后）"
    is superseded by the 2026-10-11 decision to tag right after release and
    verification.
- **Other projects:** for example, a deploy flow that conflicts with
  `deployment.md`. Each is a separate task.
- **Host-local memory:** point the related entries at the landed rules.

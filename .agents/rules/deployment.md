# Deployment

Agent-neutral workspace rule for what may serve users, pre-release channels,
when to deploy, how a temporary deployment ends, and instances found outside a
project's inventory.

## Ownership

This file owns which source may run where users are served, pre-release
channels, deploy cadence, temporary deployments, deploying an older release,
and instances outside the inventory. `releases.md` names what ran and which
verified state is a rollback target; this file decides what runs.
`authorization.md` owns the brief before each deployment, and
`verification.md` owns its release evidence. Projects own the main deployment
branch, the declaration of any pre-release channel, the deploy targets and
their inventory, entry points and guards, the deployment record, the
environment-tier policy, and the rollback procedure.

Every deployment is a protected action. Present the `authorization.md`
Protected-Action Request Brief before proposing it or asking the user to run
it; a command-only confirmation is insufficient.

## Main Branch

Anything that serves users, or can take over that role, runs a commit
reachable from the tip of the pushed main deployment branch, unless it is an
instance of a declared pre-release channel (Pre-Release Channels) or a
temporary deployment, which ends as Temporary Deployments states. A standby
runs the same release as the instance it can replace. The branch name is a
project fact.

Firm floor:

- never deploy uncommitted content to such an instance;
- never bypass the project's deployment entry point or its guard;
- use a non-normal mode only when the project's procedure names it as the
  remedy for that refusal, under its own brief. Fixing a guard refusal never
  commits, stashes, or moves unrelated work.

## Pre-Release Channels

A pre-release channel is a lasting part of production: its instances serve the
users who choose it, beside the main-branch instances, with changes that have
not reached the main branch yet. Its instances never stand by for main-branch
instances. A project declares it in its Project Facts: the channel branch, its
instances, who may use it and how they choose it, the components it
pre-releases, and the route by which changes enter the channel branch.

- A channel instance runs a pushed commit of the channel branch that contains
  the tip of the pushed main branch when it is deployed. That commit passes the
  project's checks first, since merges into the channel branch make
  combinations that no change branch was checked in. A rollback is the only
  exception (Deploying An Older Release), and deploying a channel commit older
  than the running one is a rollback.
- The channel branch is never rewritten, so every commit that ran stays on it.
- The channel pre-releases only what its own instances run. Nothing they share
  with the main-branch instances, such as data, schemas, or a control plane, is
  deployed from the channel branch, and every shared part must work with both.
  A shared change that the channel's instances depend on reaches the main
  branch and is deployed first; other shared changes may ride on a channel
  commit and first run at promotion.
- Before a change is sent through the channel, its Plan, or its brief when no
  Plan covers it, says so and names what decides its promotion or withdrawal,
  when that is judged, and how a shared change it carries is checked at
  promotion.
- A change leaves the channel in one of two ways:
  - promotion: the main branch comes to contain a channel commit that ran, or
    a later channel commit with the same content for every component the
    channel ran, and the main-branch instances then run that content. Promoting
    a commit promotes every change in it, so a change that is not ready is
    withdrawn first, or the promotion waits. A change needed on the main
    branch sooner than another on the channel gets there the same way, never
    straight from its own branch;
  - withdrawal: a revert of what brought the change in enters the channel
    branch and is deployed forward. It takes the channel's instances back to
    older code, so the checks in Deploying An Older Release apply to what the
    revert undoes.
- Cadence applies to the channel branch as to the main branch. How changes
  reach the channel branch is `git-branches.md` Change Flow; how it keeps up
  with the main branch is `git-integration.md` Pre-Release Channel Branch.

## Cadence

After pushing a commit that changes what a component runs, propose deploying it
promptly and verify the result, so that a failure points at a recent change. A
commit that changes nothing that runs needs no deploy. Instances on hold after
a rollback are excluded (Deploying An Older Release).

## Temporary Deployments

A deployment other than a declared pre-release channel's is temporary when its
source is not on the pushed main branch, or when the instance exists for a
test, preview, drill, or migration.

- Before it starts, the Plan step that needs it, or the brief when no Plan
  covers it, names its purpose, place, what it holds, its owner, and its end
  condition.
- The exact commit and whether it is pushed go into the brief and the
  project's deployment record, not into a frozen Plan.
- It ends in one of two ways:
  - the change reaches the main branch by a route the project permits, and
    what ran stays identifiable; the merge mode is the project's;
  - or the instance is removed.

A patch on an older release line (`releases.md` Fixes) is a temporary
deployment that ends only when:

- its commit becomes reachable from the main branch through a plain merge;
- a verified deployment from the main branch that carries the fix replaces it;
- or the instance is removed.

A cherry-picked or squashed copy on the main branch does not end it. Until it
ends, its release tag keeps what ran identifiable.

## Deploying An Older Release

A rollback deploys the verified state that `releases.md` Rollback Target
names. Before it, check what the range from that state to the running version
changed in four places, and follow the project's procedure for each:

- versioned secrets: revoked credentials come back, and an older encrypted file
  may need its older password;
- data and schemas: data does not roll back, so the older version must still
  read the current data;
- interfaces between components: a component rolled back alone must still work
  with the others, which stay on newer versions;
- a pre-release channel that the range introduced: when the older version
  cannot manage the channel's instances, they are removed first and come back
  only after the main-branch instances leave their hold.

The rollback is a deployment under this rule, and the fix goes forward
(`releases.md` Fixes). The deployment record shows the rollback. The
rolled-back instances stay on their rollback target until a commit that
carries the fix is pushed: for main-branch instances to the main branch, or to
an older line (`releases.md` Fixes); for a channel's, to the channel branch.
Until then, Cadence does not propose deploying the main or the channel branch
to them.

## Instances Outside The Inventory

When an instance that serves users, or could, is not in the project's
inventory:

1. identify it read-only, without reading secret values or elevating privilege
   unless that is approved;
2. record it as a finding (`planning.md`);
3. report it with a recommendation;
4. act only after the operator decides.

## Non-Production Environments

A declared non-production environment follows the project's environment-tier
policy. A generic checklist for removing an instance belongs in the
engineering handbook or the project's runbooks, not here.

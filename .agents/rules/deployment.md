# Deployment

Agent-neutral workspace rule for what may serve users, when to deploy, how a
temporary deployment ends, and instances found outside a project's inventory.

## Ownership

This file owns which source may run where users are served, deploy cadence,
temporary deployments, deploying an older release, and instances outside the
inventory. `releases.md` names what ran and which release is a rollback
target; this file decides what runs. `authorization.md` owns the brief before
each deployment, and `verification.md` owns its release evidence. Projects own
the main deployment branch, the deploy targets and their inventory, entry
points and guards, the deployment record, the environment-tier policy, and the
rollback procedure.

Every deployment is a protected action. Present the `authorization.md`
Protected-Action Request Brief before proposing it or asking the user to run
it; a command-only confirmation is insufficient.

## Main Branch

Anything that serves users, or can take over that role, runs a commit
reachable from the tip of the pushed main deployment branch, unless it is a
temporary deployment, which ends as Temporary Deployments states. A standby
runs the same release as the instance it can replace. The branch name is a
project fact.

Firm floor:

- never deploy uncommitted content to such an instance;
- never bypass the project's deployment entry point or its guard;
- use a non-normal mode only when the project's procedure names it as the
  remedy for that refusal, under its own brief. Fixing a guard refusal never
  commits, stashes, or moves unrelated work.

## Cadence

After pushing a commit that changes what a component runs, propose deploying it
promptly and verify the result, so that a failure points at a recent change. A
commit that changes nothing that runs needs no deploy. A component on hold
after a rollback is excluded (Deploying An Older Release).

## Temporary Deployments

A deployment is temporary when its source is not on the pushed main branch, or
when the instance exists for a test, preview, drill, or migration.

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
- a release from the main branch that carries the fix replaces it;
- or the instance is removed.

A cherry-picked or squashed copy on the main branch does not end it. Until it
ends, its release tag keeps what ran identifiable.

## Deploying An Older Release

A rollback deploys a release tag (`releases.md` Rollback Target). Before it,
check what the range from that tag to the running version changed in three
places, and follow the project's procedure for each:

- versioned secrets: revoked credentials come back, and an older encrypted file
  may need its older password;
- data and schemas: data does not roll back, so the older release must still
  read the current data;
- interfaces between components: a component rolled back alone must still work
  with the others, which stay on newer releases.

The rollback is a deployment under this rule, and the fix goes forward from the
main branch (`releases.md` Fixes). The deployment record shows the rollback,
and the component stays on its rollback target until a commit that carries the
fix is pushed. Until then, Cadence does not propose deploying the main branch
to it.

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

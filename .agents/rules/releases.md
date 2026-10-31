# Releases And Versions

Agent-neutral workspace rule for which released states are versions, how they
are numbered and tagged, what their notes record, how a released version is
fixed, and which verified state is the rollback target.

## Ownership

This file owns release identity: version numbers, release tags and their
notes, fixes to released versions, and the choice of a rollback target.
`deployment.md` decides what runs; this file names what ran. `verification.md`
owns the post-release checks, `planning.md` and `documentation.md` own the
Plan and Changelog that the notes link, and `git-recovery.md` owns moving or
deleting a tag. Projects own whether they release, the starting version and
tag prefix, the compatibility surface, what "released" means for them, the
status surface, the rollback procedure, and signing.

Read `git.md` for the current state snapshot before tagging. Before asking the
user to authorize or execute a tag, read `authorization.md` and present its
`Protected-Action Request Brief` before the exact bundle; a command-only
confirmation is insufficient.

## Applies To

Every project that delivers something used outside its repository: a service,
an installed tool, rules synced to hosts, or a published package. A project
with nothing released says so in its Project Facts, and so does a project whose
versions belong to an upstream it tracks. When a releasing project has no
recorded scheme, ask the operator for its starting version and tag prefix at
its first release; never invent them.

- **Release** — a commit that was deployed, or published as the project
  defines it, and verified, marked by a version tag. It is on the main branch,
  or on an older line cut from an older verified state (Fixes).
- **Milestone** — a release that closes a batch. A batch is one functional or
  improvement change, often one Plan's workstream.
- **Patch release** — a release made for a fix.

## Version Numbers

Versions use the MAJOR.MINOR.PATCH form of Semantic Versioning 2.0.0. The
largest change in the range since the previous release decides the number:

- a change that breaks the project's compatibility surface raises MAJOR. The
  project names that surface, for example client configuration, data formats,
  operator commands, or APIs; SemVer calls it the public API;
- otherwise, a closed batch raises MINOR and resets PATCH;
- otherwise, the release raises PATCH.

This departs from strict SemVer: because merged work is deployed promptly, a
patch released from the main branch also carries any unfinished work merged
since the previous release, and the notes list it under scope.

## When And What To Tag

Tag when a deployment releases a closed batch (a milestone) or a fix (a patch
release). Other deployments, such as the prompt deploys after each push
(`deployment.md` Cadence) and a pre-release channel's deployments, are not
tagged; `git describe` shows them as commits after the latest release. A change
that went through a pre-release channel is released only by a deployment to the
main-branch instances after its promotion, tagged as above.

Tag right after the release is deployed and its post-release checks pass
(`verification.md` Release Evidence). The tag records what was released; it
does not claim that the release has no problems, and a problem found later
becomes a patch release. A release whose checks fail is not tagged; it is fixed
forward or rolled back (`deployment.md`).

Tag the exact commit that the release runs, as the project's deployment record
shows it; with pull requests, that is the merge or squash commit on the main
branch. Every component that the range changes runs a commit whose content for
that component's paths equals the tagged commit's; a component the range does
not change needs no redeploy. A pre-release channel's instances are not
counted, since they may already run later changes.

Each milestone names one batch. Parallel sessions interleave commits, so the
range may also hold fixes, documentation, or parts of other work; the notes
list them under scope. The tag never waits for that work or squashes it.

Release tags are annotated, named `v<MAJOR>.<MINOR>.<PATCH>` unless the project
names its own prefix because its repository also carries upstream or other
tags, and made with the operator's configured Git identity and no AI
attribution. `git describe` reads annotated tags by default; lightweight tags
are for private or temporary labels.

## Release Notes

The tag message is the release notes. Its parts, in this order; a part may be
one line:

1. version and kind (milestone or patch), date, the commit, and the previous
   release;
2. why: the batch's goal; for a patch, the problem and the release that
   introduced it;
3. how: a short paragraph, or links to the Plan and Changelog where they exist,
   without copying them;
4. scope: the components and surfaces changed, the range `<previous>..<this>`
   with its commit count, and the other work in the range;
5. how to inspect: `git show`; `git log --oneline` and `git diff --stat` over
   the range; the Plan and Changelog paths; the project's command that shows
   which version each part runs;
6. verification: the post-release checks and their results, with gaps named;
7. rollback: the rollback target (Rollback Target), whether going back crosses
   a one-way change in the range, such as secrets, credentials, or a data
   schema, and which project procedure handles it.

The notes hold no secret values and are written to a file in the session
scratch location (`temporary-files.md`). Each narrative has one copy: the
Changelog keeps the verified workstream outcome written at closeout, and the
notes keep the release facts and link to it. A project may publish a release
history generated from its tags, never a hand-kept second copy.

## Tag Bundle

1. `git tag -a --cleanup=whitespace <tag> <commit> -F <notes-file>`; the
   default cleanup drops every line that starts with `#`, such as a Markdown
   heading;
2. `git push <remote> refs/tags/<tag>`, which pushes that one tag; never
   `--tags`.

Afterwards check that the tag is annotated, points at the commit, and exists on
the remote.

A pushed release tag is never moved or deleted: Git advises a new name over
re-tagging, and SemVer says a released version's contents must not change. A
wrong tag or a bad release gets the next patch version, whose notes say which
release it replaces.

## Fixes

Normally a fix follows the change flow in `git-branches.md`: a fix branch from
the main branch, checked there, merged into the main branch, directly or by
promotion from a pre-release channel, and released from it as a patch of the
current version. The notes name the release that
introduced the problem.

Only when production has rolled back to an older verified state (Rollback
Target) and must be fixed there:

- the fix branch starts from that state's commit;
- the patch takes the next number after the release that state descends from,
  for example `v2.1.3` while the main branch is at `v2.2.x`;
- it is verified and released as a temporary deployment (`deployment.md`);
- the fix is then carried into the main branch by the project's route, and
  verified and released again there.

Either way, a fix is complete only when every line that needs it has been
verified and released. When the problem also reproduces on the main branch,
fixing it there first and carrying it to the older line keeps it from being
forgotten; the order is left open because the completion condition covers that
risk. Once the patch's tag exists, the older line's branch may be retired, as
the tag keeps its commits.

## Rollback Target

Roll back to the newest verified state that the running commit descends from
and that does not contain the change at fault. A verified state is a release,
or a later deployment of the same instances that the project's deployment
record shows passed its checks. For example:

- production runs `v2.2.0-3-g…` and only its third commit is at fault: the
  target is `v2.2.0-2-g…` if that deployment passed its checks, otherwise
  `v2.2.0`;
- the fault is in the batch that milestone `v2.2.0` released: the target is
  the newest verified state before the faulty commit, such as `v2.1.2` or a
  verified deployment after it, not `v2.1.0`.

A pre-release channel's instance rolls back instead to a verified state, its
own or the corresponding main-branch instances', that does not contain the
change at fault; usually that is what those main-branch instances run.

Going back further discards verified work and crosses more one-way changes.
Projects own the procedure; `deployment.md` owns the checks before an older
version is deployed and the hold after it.

## Visibility

A project that shows what each instance runs also shows its version. One source
is `git describe --match '<prefix>[0-9]*'` of the running commit, without
`--tags`, so that only annotated tags with the project's prefix count;
`v2.1.0-3-gabc1234` is three commits after `v2.1.0`. The status surface is the
project's.

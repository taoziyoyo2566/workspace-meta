# File Checks

Agent-neutral workspace rule for checking a created or changed file by its
type before it is called done.

## Ownership

This file owns which checks a delivered or kept file receives, their order,
what makes a check count, and how their result is reported. `verification.md`
owns verification of the change's behavior and its release evidence;
`documentation.md` adds the checks for documentation content; `secrets.md`
owns where secret material may live. Projects own the commands for each file
class, their accepted warnings, and stricter gates. Examples by file class are
in `docs/standards/development.md`.

## Trigger

Check a file before it is reported done, handed over, committed, deployed, or
relied on by another person or by an irreversible action, when it is delivered
or kept:

- repository files;
- host configuration;
- files handed to the user or to another agent;
- a file the operator changes in a step the agent directs.

Transient working files that are never handed over or relied on
(`temporary-files.md`) are excluded.

## Stages

Run the stages in this order. A file class may skip a stage that has nothing to
check, and the report says so.

1. **Container and bytes** — the file is where its consumer reads it, with the
   expected encoding, permissions, and line endings. By default it has no
   trailing whitespace and ends with a newline, unless the format or the
   project requires otherwise.
2. **Syntax** — the format's own parser accepts it.
3. **Strict format** — nothing the format forbids that a lenient parser
   accepts, such as repeated keys, or fields the consumer rejects.
4. **Consistency** — the real consumer accepts it (a dry run, a configuration
   test, a check mode), its references resolve, and the diff holds only the
   intended change.
5. **Security, bounded to this file** — no secret value outside its approved
   store, permissions no wider than the file's role, and no unsafe construct
   that the format allows, such as unquoted shell expansion or an unpinned
   remote source.

## What Makes A Check Count

A check counts only for what it can detect:

- it reads the changed file itself, not a copy, a cached build, or another
  path;
- it fails on the defect it is meant to catch. When its strictness is unknown,
  show it failing on a dummy sample first;
- a loader that collapses repeated keys does not pass stage 3, and a key
  comparison counts every occurrence, not only the last.

A successful parse is stage 2 only.

## Secret-Bearing Files

Every stage run on secret-bearing content, including the consumer run, produces
output with no values: counts, key names, whole-file checksums, or exit status.
A hash of a single value is not used, because a short value can be guessed
from it. Inventory and variable dumps print values and are not used for this.

## Warnings

- A warning that this change introduces or newly triggers fails the check. It
  passes only once it is fixed, narrowly suppressed with a stated reason, or
  listed by the project as accepted.
- A warning that exists at the base revision, or that the project lists as
  accepted, passes when the report names it with its cause.
- Silencing a warning broadly, or loosening a check beyond a narrow, reasoned
  suppression, changes the check itself (`implementation.md`); it is not a
  fix.

## Report

Report one line per file class: the stages run and their result. Give details
only for failures, warnings, and gaps. A stage that could not run is a gap
under `verification.md`, never a pass.

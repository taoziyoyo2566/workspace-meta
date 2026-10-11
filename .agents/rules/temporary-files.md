# Temporary Files

Agent-neutral workspace rule for an agent's own temporary files: where they
go, when they are removed, and what to do when temporary space runs low.

## Ownership

This file owns the placement, lifecycle, and removal of the temporary files an
agent creates, and its response when temporary space is full or filling.
`secrets.md` owns where secret material may go, `capabilities.md` owns where a
one-off script for the user goes, and `planning.md` owns where evidence and
handoff state are recorded. Host cleanup ages and temporary roots are host
configuration. Projects may name an ignored local directory for large data.

## Placement

- Put small files in the runtime's per-session scratch location.
- Before writing large data, check the target filesystem: its free space, and
  whether it is memory-backed (tmpfs), where large files take memory and push
  other processes into swap. When it is short of space or memory-backed while
  swap is in use, choose a disk-backed location such as an ignored project
  directory. Large data includes copied trees, build or test output,
  multi-agent run outputs, tool installs, browser downloads, and package
  caches.
- Prefer reading data in place to copying it.
- Temporary files are private by default. Where secret material may go follows
  `secrets.md`.

## Lifecycle

- Whoever creates temporary files removes them when they are no longer needed.
- On failure, first move what diagnosis or a resumed run needs to its owner,
  then remove the rest.
- The orchestrator removes a multi-agent run's directory once it has the
  results.
- The runtime's own files are not the agent's to remove: the session temporary
  root, command-output files, and transcripts.
- A file kept past the task has a reason, an owner, and a removal condition.
- The final report has one line on temporary files: removed, or kept with
  where, why, and until when.

Temporary space is not a store. Evidence and handoff state go to their owners
(`planning.md`).

## Full Or Filling Temporary Space

1. Stop writing there, and remove your own temporary files.
2. Measure with `df` or `statvfs`. Tree walks refresh directory access times,
   which delays age-based cleanup.
3. Remove other sessions' or users' files only at the operator's request, after
   checking that they are not in use: open file descriptors, live or resumable
   sessions, containers, and references from other files. Report which
   processes could not be inspected.
4. Then report the problem under `problem-follow-up.md`.

## Host Settings

Host cleanup ages and temporary roots are host configuration. Propose a change
to them with the `authorization.md` brief.

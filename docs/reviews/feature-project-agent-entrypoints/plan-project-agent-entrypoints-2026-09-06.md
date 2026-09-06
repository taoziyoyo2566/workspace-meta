# Project Agent Entry Point Plan

Status: Implemented and verified on 2026-09-06. Host
installation, Git publication, and live configuration writes remain excluded.

## Goal

Make a project's agent instructions actually reach every agent runtime used in
that project, without creating a second copy of the instructions.

Codex loads `AGENTS.md` from the project root. Claude loads `CLAUDE.md` and
walks upward from the working directory. A project that ships only `AGENTS.md`
is therefore fully governed under Codex and ungoverned under Claude, while both
adapters claim the same portable core. Nothing in the shared rules currently
states that the entry file must match the runtime's loader.

## Source incident

On 2026-09-06, in a Claude session whose working directory was
`~/workspace/projects/NanoPi_R6S_Handbook`, the loaded instruction context
contained `~/workspace/CLAUDE.md` and no project instruction file. The project
has an 82-line `AGENTS.md` and no `CLAUDE.md`.

Acting without it, the assistant proposed `sudo cat` against the backup history
and the status file to accept a deployment. That project publishes
`r6s-backup status|log|timers`, which answer the same questions with no sudo,
no repository credential, and no repository connection, and which are
themselves the surface under acceptance. The operator caught the escalation.

Two distinct defects sit behind that: the instructions were not loadable by the
runtime in use, and the instructions did not contain the privilege boundary in
the first place. The second is project-owned and is fixed in that repository.
This plan addresses the first, which is portable.

## Scope and exclusions

In scope:

- state the loadable-entry-point requirement in its existing portable owner;
- add a Claude-adapter backstop for projects that have not yet added an entry
  file, so a missing adapter degrades to an explicit read rather than silence;
- refine the ownership matrix row for project agent/governance files;
- record provenance in `feedback-register.md`;
- add the reverse-whitelist entries this review directory needs.

Excluded:

- generating or editing entry files inside project repositories from
  workspace-meta; each project owns and enforces its own entry files;
- scanning `~/workspace/projects/` from workspace-meta tests, which would
  couple separate Git roots and contradict this repository's scope discipline;
- any managed-block change to `~/.codex` or `~/.claude`;
- staging, committing, pushing, PR creation, or deployment.

## Verified product baseline

- Claude Code loads `CLAUDE.md` and supports `@path` imports inside it; imports
  inside fenced code blocks are not followed. A thin `CLAUDE.md` that imports
  `AGENTS.md` therefore yields one authority and two loaders.
- Codex reads `AGENTS.md` and does not read `CLAUDE.md`. No change to the Codex
  adapter is required for it to keep loading project instructions.
- Session evidence above is a dated observation of one host and one client
  version, not a permanent product guarantee.

## Approach and risks

1. Put the requirement in `.agents/rules/documentation.md`. That module already
   owns project entry points and already lists project agent instructions as a
   documentation role, so no new owner is created.
2. Express it as a conditional keyed to an observable predicate — which entry
   file each runtime in use loads — rather than a prohibition, per the form
   table in `rule-authoring.md`.
3. Require the additional entry file to be an importing adapter and to carry no
   independent rule text, which keeps `Migrate Without Dual Authority` intact.
4. Add one Claude-adapter line for the transition period: inside a project that
   has `AGENTS.md` but no entry file this runtime loads, read `AGENTS.md`
   before substantive project work, including read-only review or host/external
   actions. The Codex adapter gets no matching line because its
   loader already resolves the file; the asymmetry is an agent-only mechanic,
   which the adapter rule permits.
5. Leave enforcement to each project's own executable gate, consistent with
   `documentation.md`: agent prose is routing and judgment, not enforcement.

Risks:

- The import cannot be verified from inside the session that already loaded its
  context. Confirmation requires a fresh Claude session started in the project
  directory; until then this is a reported gap, not a passed check.
- A backstop phrased as behavior can be skipped the same way the missing rule
  was. It is a transition measure; the structural fix is the entry file, and
  the durable check is the project gate.

## Verification

- `make test`;
- `bash -n scripts/*.sh .githooks/pre-commit`;
- Python byte compilation for `scripts/*.py` and `tests/*.py`;
- `git diff --check`;
- workspace-meta documentation-gate positives and focused negatives;
- confirm no new tracked path lacks a `.gitignore` allow rule;
- reported gap: fresh-session confirmation that a project `CLAUDE.md` import
  reaches the Claude context.

## Handoff

Record the implementation and verification outcome in a dated round changelog
in this directory. Leave all repository changes uncommitted and unpushed for
operator review.

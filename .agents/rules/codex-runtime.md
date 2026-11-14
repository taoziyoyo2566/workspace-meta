# Codex Runtime Adapter

Codex-specific mechanics for applying the shared workspace rules.

## Ownership

This file owns only Codex sandbox/escalation, execpolicy, deferred tool
discovery, Codex's project entry files, Codex configuration boundaries, and how
Codex runs as a read-only reviewer for another runtime's session. Semantic
authorization is owned by `authorization.md`; capability-selection triggers are
owned by `capabilities.md`; when another vendor's runtime reviews, and what its
brief fixes, by `review.md` Independent Review. Only the Codex adapter routes
this file; a session of another runtime that has Codex review its work reads
Read-Only Review Runs through `review.md`.

## Sandbox And Escalation

- Run ordinary reads and in-writable-root edits in the active sandbox.
- If an authorized safe operation is technically blocked, request the narrowest
  categorical escalation; the prompt is technical permission only.
- Keep commands unmatched unless a concrete reviewed prefix is safe. A shell,
  interpreter, or arbitrary script prefix cannot prove its payload safe.
- `~/.codex/rules/*.rules` is host-local executable authorization state. Never
  copy it into workspace-meta or a project.

## Capability Mechanics

- Inspect currently exposed tools first.
- Use deferred tool discovery only for a concrete task-shaped need.
- Use native web/docs capabilities without conversational confirmation when
  the shared authorization rule permits the read.
- Use subagents only when active instructions permit delegation and the subtask
  is concrete and independently useful.
- Agent tool names and plugin/skill availability are runtime facts, not portable
  behavior policy.

## Project Entry Files

Under `documentation.md` Project Bootstrap, Codex's entry file is `AGENTS.md`
itself: Codex reads the `AGENTS.md` files from the Git root down to the working
directory, and has no import syntax.

- A project whose agent facts live in another file, such as a `CLAUDE.md`
  owner, gets no Codex adapter. Report the move of those facts to `AGENTS.md`,
  with a thin `CLAUDE.md` adapter left behind, and make it only after the
  operator agrees.
- In a clone of a repository the operator does not own, nothing is written for
  Codex; report the gap.

## Read-Only Review Runs

How another runtime's session has Codex review its work (`review.md`
Independent Review). Checked on codex-cli 0.166.0; after a Codex update, have
a first run and a resumed run each attempt a write, and confirm in each
session record that the write was refused and the settings below held, before
relying on this section.

- Run `codex exec -s read-only -c 'approvals_reviewer="user"' --ignore-rules
  --disable hooks --disable apps --output-schema <schema file> -o <answer
  file> --json -` with the request on stdin, and keep the JSONL events from
  stdout and the answer file. Each setting closes a path around the sandbox:
  - the approvals override: when a host config selects automatic review
    (`approvals_reviewer` set to `auto_review`, older name
    `guardian_subagent`), a run without it gets the approval policy
    `on-request`, and its approval requests go to that automatic reviewer;
    with it the policy is `never`, and the reviewer cannot ask for an
    escalation;
  - `--ignore-rules`: an `allow` rule in user or project `.rules` files runs a
    matching command outside the sandbox, even under `-s read-only`;
  - `--disable hooks`: lifecycle hooks run outside the sandbox at session
    start and resume, such as a status hook that fetches a remote;
  - `--disable apps`: connector apps add tools that can create files or
    drafts in external services;
  - none of these unloads MCP servers configured for Codex, including those a
    plugin adds: before the first run, confirm that the reviewer's tools
    include no write tool that has not been checked, for example by having it
    list its `mcp__` tools; if one is there, disable that server or limit it
    to read-only tools for the run, or report the gap.

  `--approve-for-me` routes approvals to automatic review with the
  workspace-write sandbox; a review never uses it.
- The JSONL events can leave out a command the sandbox refused. The session
  record under `~/.codex/sessions/` (`$CODEX_HOME/sessions/` when that is
  set), in the file whose name ends with `<thread id>.jsonl` for the thread id
  from `thread.started`, holds each tool call with its output and the settings
  the run applied (`thread_settings_applied`). Check it, not the events or the
  answer, for write attempts, the read-only sandbox, and the approval policy
  `never` before relying on the answer; under these settings a shell write
  fails with `Read-only file system` and a patch is rejected.
- `codex exec resume <session id>` takes no `-s`: resume the reviewer for the
  targeted re-review with `-c 'sandbox_mode="read-only"'`, the same approvals
  override, and the same three flags. The resumed session keeps the first
  review's context and appends to the same session record.

## Configuration Boundary

Workspace-meta owns only its marked Codex AGENTS/config blocks, the explicitly
listed fields in `codex-preferences.toml`, canonical shared rules, and dedicated
status hook. Model selection, project trust, hook trust, credentials, history
data, unlisted preferences, caches, databases, installed plugins, system skills,
and host approval history remain host-local.

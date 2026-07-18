# Plan: Host Permission Policy

## Purpose

Reduce repeated Codex approval prompts for web retrieval, remote read queries,
and ordinary inspection commands while retaining explicit approval for actions
that materially mutate Git history/refs, remote services, or host state.

## Ownership

- Portable behavior belongs in the workspace-meta managed Codex guidance.
- Executable command decisions belong in a host-local rules file under
  `~/.codex/rules/` and are never committed or synchronized.
- Existing `default.rules` remains Codex-generated approval history. This change
  adds a separate `permissions.rules` drop-in so policy and accumulated approvals do
  not become indistinguishable.

## Design

1. Use native web/URL retrieval directly. Pre-authorize only bounded local,
   local-Git-status, and high-level read-only GitHub prefixes that are safe
   outside the sandbox.
2. Require a prompt for Git commit/push/merge and related history, ref, index, or
   working-tree mutations even when an older exact allow entry exists.
3. Leave ordinary sandbox-contained tools such as `rg`, `sed`, workspace-local
   `cp`, Git diff/log/show, interpreters, and build tools unmatched instead of
   prompting by executable name.
4. Require a prompt for shell network clients, remote execution/transfer,
   common GitHub mutations, container/cluster controls, and host/system
   mutations.
5. Match Codex by actual subcommand: read-only `execpolicy`/help/diagnostics and
   list operations remain unmatched; nested agents, services, credentials, and
   configuration mutations prompt.
6. Treat commit and push as separate two-stage semantic transactions: an
   initial request permits preparation, and execution waits for a later
   confirmation of the exact manifest.
7. Do not allow arbitrary `bash`, `sh`, Python, Node, or other interpreters; a
   prefix rule cannot establish that an arbitrary program is side-effect free.
8. Explain that native Web Search is not governed by execpolicy and should be
   used without conversational confirmation.
9. When a safe network operation is technically blocked, request one categorical
   approval instead of repeated per-command or per-site approvals.

## Verification

- Load the candidate file with `codex execpolicy check`.
- Assert bounded inspection/status queries resolve to `allow`.
- Assert routine sandbox-contained commands and safe Codex inspection
  subcommands remain unmatched.
- Assert representative Git, remote-service, and system mutations resolve to
  `prompt`, including commands previously allowed in `default.rules`.
- Assert trust/approval bypasses resolve to `forbidden`.
- Confirm unrelated commands remain unmatched rather than receiving a blanket
  allow.
- Run workspace-meta regression, syntax, whitelist, and drift checks.

## Out Of Scope

- Disabling the sandbox or switching to danger-full-access.
- Automatically classifying arbitrary scripts as safe.
- Synchronizing host authorization history.
- Persisting credentials, tokens, project paths, or hook trust state.

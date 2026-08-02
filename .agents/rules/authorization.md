# Authorization

Agent-neutral workspace rule for interpreting requests, edit authority,
technical permission prompts, and protected mutations.

## Ownership

This file owns cross-project authorization semantics. Projects may add stricter
requirements for their live systems, external resources, historical evidence,
or other project risks. Agent adapters own their sandbox/tool mechanics.

Git procedures are owned by the task-shaped `git-*.md` modules. Secret response
is owned by `secrets.md`. This file does not define project topology, commands,
deployment targets, or live-resource schemas.

## Keep Four Decisions Separate

| Decision | Meaning | Does not grant |
|---|---|---|
| Task authorization | outcome and repository scope requested by the user | unrelated work |
| Plan approval | accepted direction or implementation approach | Git publication, external writes, or live runs |
| Technical capability | whether the current runtime can perform an action | user intent or broader scope |
| Action authorization | reviewed protected mutation | another target, operation, retry, or follow-up |

Passing one decision never implies another.

## Request Semantics

| Request | Default authority |
|---|---|
| explain, inspect, review, audit, diagnose, compare, or report | read-only investigation and verification |
| change, fix, implement, update, refactor, apply recommendations, or continue an authorized implementation | necessary in-scope working-tree edits and non-destructive verification |
| prepare a plan or proposal | planning artifacts only |
| approve a plan | only the approval scope declared by the plan |
| prepare or publish Git work | only the review/preparation in the applicable Git module |

An authorized working-tree change may create, edit, rename, or remove known
in-scope files when necessary for the requested outcome. It does not require
another conversational confirmation per file. Preserve unrelated,
unrecognized, historical, and pre-existing work; stop when a newly discovered
decision would materially change direction or scope.

Classify documentation by effect. A wording fix is not equivalent to changing
governance, architecture, operator procedure, approval semantics, or historical
evidence.

## Work That Proceeds Without Another Confirmation

Once the task is authorized:

- local, Git, and remote read-only inspection;
- native search, URL retrieval, and documentation lookup;
- in-scope working-tree edits inside writable roots;
- static checks, tests, and local ephemeral outputs that do not mutate a real
  external system;
- narrowly scoped technical escalation when one of those safe operations is
  blocked by the runtime boundary.

Use the current sandbox for ordinary reads and in-workspace writes. Classify the
actual invocation, target, and effect, not only the executable name. A shell,
interpreter, build tool, or compound command is not high-impact merely because
it could have a mutating mode.

## Protected Mutations

The user must request or approve the named operation before:

- Git staging, publication, history/ref/worktree mutation, integration, or
  cleanup, as refined by the applicable Git module;
- remote API writes, deployments, or external-resource mutation;
- writes outside configured writable roots;
- privilege elevation or host package/service/configuration changes;
- live infrastructure mutation.

The review identifies the actual target, operation, expected impact, material
exclusions, prerequisites, and check state. A material change to any of those
expires the authorization.

Projects define the extra fields and per-run/standing model required for their
own live targets. Plan approval alone never supplies those live fields.

## Protected-Action Request Brief

Before presenting a protected operation for execution, asking the user to run
it, or asking the user to approve it, present a concise action brief followed by
the exact operation. This applies to every protected action, including Git,
host configuration, privilege changes, external API writes, deployments,
service changes, and live infrastructure mutations. The trigger is the
operation being proposed, not whether the request uses the word “approve”.

The brief must state:

- **What will happen** — the concrete action, command, API request, or tool
  operation;
- **Why now** — how the action advances the already authorized task;
- **Target and scope** — exact files, host, service, remote, account, resource,
  or other affected boundary;
- **Expected effect** — the state change the user should expect after it runs;
- **Risks and recovery** — material risk, reversibility, and recovery path when
  applicable;
- **Excluded actions** — what will not happen as part of this approval;
- **Checks and gaps** — prerequisites, completed checks, and unresolved
  uncertainty;
- **Approval boundary** — whether approval covers one exact invocation, a
  disclosed sequence, a bounded retry, or nothing beyond the named operation.

Use this shape when requesting consent:

```text
Action summary
What will happen: ...
Why now: ...
Target and scope: ...
Expected effect: ...
Risks and recovery: ...
Excluded actions: ...
Checks and gaps: ...

Exact operation:
<command, request, or tool operation>

Approval boundary: ...
Please confirm whether to proceed.
```

A command-only request is insufficient when the action is protected. If a
runtime permission prompt displays only a command, the agent's preceding
semantic request must still provide this context; a technical approval prompt
does not itself authorize the operation. Redact secrets from the brief and
the displayed operation. Any material change to the target, operation, effect,
risk, checks, or approval boundary invalidates the prior consent and requires
a new request.

A direct user request can supply task or action intent, but it does not waive
the brief before the agent executes the operation or asks the user to run it.

This brief is not required for ordinary read-only work or already-authorized,
in-scope working-tree edits; do not turn it into a repeated conversational
prompt for routine safe operations.

## Technical Permission Is Not Semantic Authority

A sandbox, execpolicy, or permission prompt asks whether the runtime may
perform an action. It does not prove that the conversation authorized the
action. Conversely, safe work should not receive repeated conversational
prompts merely because a host permission rule lacks a convenient allow entry.

When an authorized safe repeated operation is technically blocked, request one
narrow categorical technical approval. Never treat a broad shell/interpreter
allow rule as proof that arbitrary payloads are safe.

Concrete executable allow/prompt decisions are host-local. They may be more
restrictive than this portable intent and must never be committed to
workspace-meta or a project.

## Uncertainty

Ask only when the missing answer could materially redirect scope, destroy or
expose user work, mutate a protected target, or change the applicable
authorization model. Ordinary implementation judgment inside authorized scope
is not a reason to pause.

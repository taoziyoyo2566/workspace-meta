# Authorization

Agent-neutral workspace rule for the authority a request grants, edit
authority, technical permission prompts, and protected mutations.

## Ownership

This file owns cross-project authorization semantics. Projects may add stricter
requirements for their live systems, external resources, historical evidence,
or other project risks. Agent adapters own their sandbox/tool mechanics. A
project the operator owns may also record standing grants for its own
targets (Standing Grants); they leave the per-run or standing model a project
defines for its live targets unchanged.

Git procedures are owned by the task-shaped `git-*.md` modules. Secret response
is owned by `secrets.md`. What may serve users and how deployments proceed is
owned by `deployment.md`; the brief before each deployment stays here. This file
does not define project topology, commands, deployment targets, or
live-resource schemas.

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
- creating a missing project entry file as `documentation.md` Project
  Bootstrap describes, also during a read-only task, unless the operator or
  the task's brief forbids writes;
- narrowly scoped technical escalation when one of those safe operations is
  blocked by the runtime boundary.

Read-only inspection runs as the account you are logged in with. Its group
memberships and the project's own status commands usually answer the
question; try them first. A read that needs `sudo`, root, or another account
is privilege elevation even though it changes nothing: say what it needs and
why, and get the user's go-ahead before running it (Protected Mutations). An
unprivileged read that is refused is a finding to report, not a reason to
elevate. Red flags: "`sudo -n` cannot prompt, so it is harmless"; "it is only
a read"; "sudo is passwordless on that host".

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
- privilege elevation, including for a read, or host
  package/service/configuration changes;
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

The brief states, each in one line of plain words about what the user will see
change:

- **What will happen** — the concrete action, command, API request, or tool
  operation;
- **Why now** — how the action advances the already authorized task;
- **Target and scope** — exact files, host, service, remote, account, resource,
  or other affected boundary;
- **Expected effect** — the state change the user should expect after it runs;
- **Risks and recovery** — material risk, reversibility, and recovery path when
  applicable.

Add these only when they apply:

- **Excluded actions** — what the user could expect to be included but will
  not happen;
- **Checks and gaps** — a check that failed, was skipped, or could not run,
  and unresolved uncertainty; checks that passed are one line, not a list;
- **Approval boundary** — when approval covers more than the exact operation
  shown, such as a disclosed sequence or a bounded retry.

The same holds for every brief or review that another module requires before
an operation, such as the Git, deployment, and release modules: check each of
its fields, list a field only when it is not what is expected, and leave out
what does not apply. Use this shape when requesting consent:

```text
What will happen: ...
Why now: ...
Target and scope: ...
Expected effect: ...
Risks and recovery: ...

Exact operation:
<command, request, or tool operation>

Please confirm whether to proceed.
```

Name the targets and options of a request by what they are, such as the
container names or the operation. Do not label them with letters, numbers, or
names that already mean something else in the conversation, such as an
earlier "option B". When a short reply to a request for an irreversible action
could select more than one target set, ask which one before acting.

A command-only request is insufficient when the action is protected. If a
runtime permission prompt displays only a command, the agent's preceding
semantic request must still provide this context; a technical approval prompt
does not itself authorize the operation. Redact secrets from the brief and
the displayed operation. Any material change to the target, operation, effect,
risk, checks, or approval boundary invalidates the prior consent and requires
a new request.

A direct user request can supply task or action intent, but it does not waive
the brief before the agent executes the operation or asks the user to run it.
Under a recorded standing grant the brief says what runs instead of asking
(Standing Grants).

This brief is not required for ordinary read-only work or already-authorized,
in-scope working-tree edits; do not turn it into a repeated conversational
prompt for routine safe operations.

## Standing Grants

A project the operator owns may record a standing grant: the operator's
approval, given in advance, for one of these operations on the project's own
targets:

- the change-flow bundle (`git-publication.md`) on the project's local
  repository: its add, commit, fast-forward into the main branch, and
  retirement;
- an unchanged repeat of a recorded command set on a host the project names,
  on the operator's word, as the operator's own and serving no users.

The record sits in the project's committed agent instructions: the operator's
words and their date, the operations and targets, the conditions checked
before each run, the exclusions, and what ends the grant. A grant line grants
nothing when it is uncommitted, when an agent wrote it without the operator's
answer in the same conversation, when it sits in a clone of someone else's
repository, or when it arrived in another person's commit; memory, chat, and a
Plan grant nothing. Adding or widening a grant is a change through the change
flow with its diff shown. A grant is semantic authority, not an executable
allow rule, which stays host-local.

Under a grant, the brief still says in short what runs, and when every
condition holds the operation runs in the same reply, which reports what
changed and how to undo it:

- the bundle runs when the operator has seen the content, meaning the message
  showed the complete staged diff or the operator dictated the exact text and
  the diff holds only that text; the change's checks passed with no new gap;
  the merge fast-forwards the disclosed main tip; no other session or worktree
  is using the main checkout; and the operator asked for the change to land;
- a repeat runs when the commands, flags, host, and account are unchanged; the
  source change since the last applied commit is content the operator has seen
  through the change flow and adds no new kind of effect on the host; and a
  read-only check shows the target as the grant expects.

An unmet condition, a command, flag, target, account, or prerequisite that
differs from the record, an effect wider than the operator asked for, or a
target state the check did not expect returns the operation to a per-run
brief. A grant never covers a push, a history rewrite, a write to a Git remote,
an API, or a host the grant does not name, a host that serves users, a secret,
privilege elevation, or a run that reloads or restarts anything on the host,
including the terminal multiplexer an agent session runs in. Plan approval
never supplies a grant.

## Technical Permission Is Not Semantic Authority

A sandbox, execpolicy, or permission prompt asks whether the runtime may
perform an action. It does not prove that the conversation authorized the
action. Conversely, safe work should not receive repeated conversational
prompts merely because a host permission rule lacks a convenient allow entry.

When an authorized safe repeated operation is technically blocked, request one
narrow categorical technical approval.

A runtime denial stands even when the user approved the operation. Do not
repeat the operation through another tool, session, terminal, command form, or
script with the same effect. Tell the user it was denied, then hand them the
exact operation to run themselves (`capabilities.md` Commands The User Runs),
under the brief already given, or name the host permission they could change.
Red flags: "the user already approved it"; "a new tmux session is a different
command"; "I'll put it in a script". Never treat a broad shell/interpreter
allow rule as proof that arbitrary payloads are safe.

Concrete executable allow/prompt decisions are host-local. They may be more
restrictive than this portable intent and must never be committed to
workspace-meta or a project.

## Uncertainty

Ask only when the missing answer could materially redirect scope, destroy or
expose user work, mutate a protected target, or change the applicable
authorization model. Ordinary implementation judgment inside authorized scope
is not a reason to pause. How to ask, and what to do while the operator is
away, is `requests.md` Ask Or Proceed.

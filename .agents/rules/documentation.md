# Documentation Information Architecture

## Ownership

This file is the sole portable owner for project-documentation roles,
information architecture, truth lifecycles, migration boundaries, and the
bootstrap of a project's agent entry files.
`planning.md` owns approved scope and handoff, `implementation.md` owns the
shape of changed artifacts generally, `file-checks.md` owns the checks each
changed file receives, and `verification.md` owns executed checks. Projects add
only their audience map, canonical topic owners, commands, domain constraints,
and stricter requirements.

## Start With The Retrieval Task

Before writing or moving documentation:

1. Name the intended reader and the task or question they need to complete.
2. Find the existing canonical owner for that topic before creating a file.
3. Classify the content as desired state, reusable guidance, live state, a
   dated verification snapshot, historical record, decision, or future work.
4. Choose one artifact role. Split mixed material at the section boundary when
   different parts answer different retrieval tasks.
5. State what source or command makes volatile claims authoritative.

Do not create every category preemptively. A small project may use one file for
several closely related topics when each section remains easy to find and none
of the truth classes conflict.

## Route Content By Role

| Reader need | Canonical artifact role | Required shape |
|---|---|---|
| Discover and navigate the project | `README` and documentation index | purpose, audience, first actions, topic-owner links |
| Learn through a guided exercise | tutorial | safe learning path with a defined outcome |
| Complete or recover an operational task | how-to or runbook | prerequisites, ordered actions, verification, stop/rollback/escalation |
| Look up exact facts | reference | precise contracts, options, schemas, compatibility, generated facts |
| Understand design or tradeoffs | explanation or architecture | context, boundaries, relationships, rationale |
| Preserve an accepted choice | decision record | status, context, decision, consequences, supersession links |
| Preserve what happened or was observed | incident or verification record | date, scope, environment, evidence, outcome, follow-up links |
| Preserve what was investigated or verified for later work | investigation record | question and scope, dated evidence, conclusions with the versions and scope they hold for, recheck conditions, supersession links |
| Preserve approved implementation intent | Plan | goal, approval-time state, intended change, scope/non-goals, acceptance criteria, approved deviations, lifecycle status |
| Preserve a verified implementation outcome | Changelog | Plan link, summary, meaningful changed surface, final verification, implemented deviations and residual gaps when relevant |
| Track possible future work | issue or backlog | owner, status, acceptance boundary; never presented as current behavior |
| Constrain coding agents | project agent instructions | project facts, commands, constraints, and routes; not a human manual |

Tutorials, operational guides, reference, and explanation serve different user
needs. Historical records and decisions serve lifecycle needs. Directory names
may vary, but the roles and ownership boundaries must remain visible.

## Separate Plan, Execution, And Changelog

A Plan owns one coherent workstream's approved Goal, approval-time Current
State, Intended Change, Scope and non-goals, Acceptance Criteria, approved
Material Deviations, and lifecycle Status. Current State is a decision snapshot,
not a live environment registry. `planning.md` owns workstream identity, Plan
reuse, approval, freeze, deviation, and completion workflow.

Routine progress, intermediate hypotheses, failed attempts, routine fixes,
command output, retry loops, and intermediate verification belong in transient
task context. Do not create another durable execution journal for them. A
verified finding that constrains other work is not routine progress;
`planning.md` requires recording it when it is confirmed.

When the user requests stepwise tracking or operational records, or continuity,
audit, or recovery requires them, use the existing project task/evidence store
or a separate compact checklist/record. Keep completion state and actual
operation outcomes there, outside the frozen Plan. Retain only the target,
revision, prerequisites, consequential actions, results, evidence locations,
and unresolved work needed to resume or assess the operation; raw logs and
secrets follow their existing owners. This conditional record does not create
an additional Plan or Changelog per step.

A Changelog is the final verified outcome record for a coherent workstream,
created at content-complete, commit-ready closeout. Normally one Plan produces
one final Changelog; implementation rounds, conversational turns, operator
feedback, remediation, and re-verification do not produce intermediate or
round-specific Changelogs. This is a scope default, not a mechanical
cardinality requirement for every Plan.

The Changelog records the final outcome, meaningful changed surface, final
verification summary, approved deviations actually implemented, and relevant
residual gaps. It is not a chronological interaction log: do not require
command-by-command transcripts, per-file diaries where Git already owns exact
history, duplicated Plan goal/scope/risk text, or a copied verification
procedure. Preserve an intermediate failure only when it explains a lasting
limitation or material final correction. `verification.md` continues to own
check execution and verdicts. Release notes (`releases.md`) link the Changelog
and never copy it.

Before the workstream result is committed, a legitimate pre-commit closeout
correction under `planning.md` may revise the existing Changelog because it has
not yet become durable history. After correction and final verification, that
same Changelog records the actual final outcome. Once the result is committed,
preserve its Changelog as the historical verified outcome; later work must not
rewrite it or add to it, including between commit and push. An operation done
afterwards, its check, or a residual gap that has since closed is reported in
the conversation, or recorded with the later work that needs it. A later
workstream gets its own Changelog only when proportional planning gives that
workstream the persistent Plan/Changelog lifecycle; neither a new commit nor a
routine fix creates one automatically.

Red flags: "its follow-ups are out of date now"; "an update section below the
outcome".

## Make Agent Instructions Loadable

Agent instructions govern only if the runtime in use loads them. Different
agents load different entry files from a project root, so name the runtimes the
project is actually operated with and give each one an entry file it loads.

- Keep one canonical owner for the project's agent facts, commands, routes, and
  constraints.
- Every additional entry file is a thin adapter that imports that owner and
  states no rule of its own, so no second authority exists to drift. It may
  add mechanics of its own runtime only.
- Mentioning or linking the owner does not load it. Use the runtime's own
  import mechanism and confirm the position where it is written is one the
  runtime actually follows.
- Enforce the adapter's presence and its resolved import in the project's
  executable documentation gate, alongside the entry-file allowlist.

When operating a runtime for which a project has no entry file, read that
project's canonical owner before substantive project work, including read-only
review or any host/external action, and create the missing entry file as
Project Bootstrap describes; report what you could not create as a governance
gap.

## Project Bootstrap

A project the operator works on with an agent gets the entry files that agent
loads, without the operator asking each time. This covers every Git repository
under the workspace project directory. A directory that is not a Git
repository, such as notes, a backup, or a worktree container, is bootstrapped
only when the operator asks. A linked worktree without entry files of its own
is not bootstrapped itself: its main checkout is, and the branch receives the
files by merge.

Only the session in conversation with the operator bootstraps. A delegated
agent, and any task whose operator instruction or brief forbids writes, reports
the missing entry file instead of creating it; the delegating session
bootstraps before it hands out work in the project.

At the first substantive work in a project, including read-only review, check
the entry file for the runtime in use and create what is missing:

1. The canonical owner of the project's agent facts is `AGENTS.md`, the one
   file every agent runtime in the workspace can be given. A project whose
   existing canonical owner is another file keeps it until the operator moves
   it.
2. In a repository the operator owns that has no canonical owner, survey the
   project and write `AGENTS.md`: its purpose and layout; the commands that
   build, test, run, and deploy it; its conventions and constraints; the
   project facts the shared rules leave to projects, such as the main branch,
   merge route, canonical remote, and release and deployment facts that apply;
   and routes to its own documents. Leave out portable rules, secrets, live
   state, and dated status, and keep it short enough to load in every session.
3. When a runtime does not load the canonical owner directly, add its entry
   file as a thin adapter that imports the owner, beside the root owner and
   beside each subdirectory's own owner file. A runtime that cannot import
   gets no adapter: report the owner move it would need.
4. In a clone of a repository the operator does not own, write only the
   runtime's local entry file, holding the import of the clone's own owner or,
   when it has none, the survey notes, and exclude it through the clone's own
   Git exclude list, never its tracked `.gitignore`. A runtime without a local
   entry file gets nothing written there; report the gap.
5. Never overwrite or rewrite an existing entry file. When a project's files
   conflict, such as an adapter that does not import an existing owner or two
   files that both state rules, report it with a proposed fix and change it
   only after the operator agrees.
6. Leave what you created uncommitted and report it in the same reply: each
   path, what it holds, and that committing it follows the project's change
   flow.

Creating a missing entry file this way is the operator's standing decision and
needs no further confirmation (`authorization.md`). Agent runtime modules own
each runtime's entry files, import syntax, local-only file, and how the survey
is run. A session-start check that reports a project without an entry file is
a backstop, not the owner; the project's own documentation gate still enforces
its adapter.

## Keep Truth Classes Explicit

- Desired configuration is owned by source, templates, or declarative config.
  Documentation explains use and links to the owner instead of copying values.
- Reusable operational guidance contains current steps and safety boundaries;
  dated incident narration and session transcripts do not belong there.
- Live state is answered by an identified runtime query or monitoring surface.
  A static document may preserve only a labeled snapshot, not claim permanence.
- Verification records state time, environment, revision or scope, commands,
  results, and gaps. They are evidence, not current configuration authority.
- Decisions retain rationale and consequences. Superseded decisions remain
  historical and point to their replacement.
- Future intent remains an issue or plan until implemented and verified.

Assign each normative fact one canonical owner. Other pages link to that owner
with just enough context for navigation; they do not maintain independent
copies. Prefer Git history for prose revision history instead of manual
document-version ledgers.

## Control Growth

Update an existing owner when the reader task and truth class are unchanged.
Add a document only when it has a distinct audience/task, lifecycle, access
boundary, or independently maintainable owner. Omit empty headings and
speculative placeholders.

Explain designs with connected prose and concrete examples. Add diagrams,
tables, and separate decision records when they improve understanding or later
retrieval. Judge sufficiency by whether the reader can explain what changes,
why, and how to verify it, not by heading count. Optional templates illustrate
the rules; they do not create another normative owner or mandatory artifact.

Plans are the exception to updating an existing owner: a Plan's owner is its
workstream. When proportional planning warrants a persistent Plan, the design
of an independent capability gets its own Plan under `planning.md`, never a
section of another Plan, even when the audience, topic, or files are the same.

Use status metadata only where lifecycle ambiguity creates real risk, such as
decisions, incidents, verification snapshots, migrations, or deprecated pages.
Do not stamp every timeless guide with volatile status fields.

Raw logs, large captures, generated reports, and sensitive evidence stay in
the project's designated evidence store. Versioned documentation keeps only a
redacted summary, provenance, and retrieval instructions.

## Migrate Without Dual Authority

Inventory existing sections by role and truth class, then migrate one coherent
topic at a time. Establish the new canonical owner, replace the old normative
section with a short compatibility pointer, update primary navigation, and run
the relevant checks in the same change. Do not rewrite historical records to
look current and do not maintain old and new copies as coequal sources.

During an incremental migration, label legacy locations and state which topics
have moved. Exclude archived, superseded, incident, and verification material
from the primary current-guidance path while keeping it discoverable.

Compatibility pointers are temporary migration artifacts, not a default
permanent information architecture. Retain one only when a real external link
or consumer contract requires the old path; name its owner and retirement
condition. At full cutover, remove pointers that have no compatibility contract
and preserve the old-to-new mapping in a migration record and Git history.

## Validate The Documentation Change

Check that:

- entry points lead readers to the canonical topic owner;
- internal links, anchors, commands, and examples resolve;
- current instructions include success checks and relevant recovery boundaries;
- volatile claims identify their source, query, time, and scope;
- no second canonical copy or mixed current/historical authority was introduced;
- generated or sensitive evidence remains outside versioned prose; and
- mechanical formatting and link checks run in project CI when available.

For a documentation-heavy or operational project, encode stable mechanical
constraints in a project-owned executable gate: entry-file allowlists, index
coverage, internal links and anchors, required runbook sections, and any
machine-checkable current-versus-record separation. Keep these checks in CI or
the project's normal test command; agent prose is routing and judgment, not a
substitute for enforcement.

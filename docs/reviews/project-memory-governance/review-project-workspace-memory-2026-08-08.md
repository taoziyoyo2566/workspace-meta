# Review: Project And Workspace Memory Governance

Status: reviewed; not ready for implementation approval.

Date: 2026-08-08

Reviewed documents:

- [`conversation-requirements-2026-08-07.md`](conversation-requirements-2026-08-07.md)
- [`solution-project-workspace-memory.md`](solution-project-workspace-memory.md)
- [`plan-project-workspace-memory-2026-08-07.md`](plan-project-workspace-memory-2026-08-07.md)
- related `.gitignore` change

## 1. Scope snapshot

- Target repository: `/home/saberu/workspace`
- Branch and comparison base: `main`, `a5ce3561a6691501e13ca51872e9d5f8b8589e59`
- In scope: the three untracked review documents and the allowlist change needed
  to track this review directory.
- Supplemental only: `/home/saberu/workspace/projects/reality-ops`, because the
  plan explicitly includes its migration. It is an independent Git repository
  and was not combined with the workspace-meta status.
- Excluded: host-local Codex/Claude configuration, credentials, hook trust,
  remote state, Git publication, and live or production verification.

## 2. Overall result

The two-scope model is sound: detailed project facts stay in each project, while
workspace-meta owns the reusable protocol and a high-level project map. The
separation of AI semantic work from SessionStart and mechanical scripts also
fits the existing workspace architecture.

The documents should not yet be approved for implementation or publication. The
following P1 findings affect target ownership, write authority, core behavior,
trackability, safety, or acceptance evidence.

## 3. Findings

### P1-1 — Reality Ops migration crosses an independent Git boundary

The plan includes Reality Ops migration in scope and lists
`projects/reality-ops/*` as implementation files, but the workspace rules state
that this directory is a separate Git root. The current supplemental check found
modified and untracked Reality Ops files, including `AGENTS.md`,
`docs/project-memory.md`, `setup`, and `scripts/check-project-memory.sh`.

Evidence:

- `plan-project-workspace-memory-2026-08-07.md:24-33,144-172`
- [`AGENTS.md`](../../../AGENTS.md):7-9 (the workspace root rule)
- [`projects/reality-ops/AGENTS.md`](../../../projects/reality-ops/AGENTS.md):1

Required improvement: split the workspace-meta protocol change from a separate
Reality Ops migration plan. Record the project Git root, baseline HEAD and dirty
state, which existing changes are in scope, and the handoff/acceptance boundary.

### P1-2 — Automatic initialization does not define its write boundary

The solution and acceptance criteria require initialization on the first
“substantive writable project task”, but do not define that term or whether a
code-only task authorizes an additional documentation change. The global Codex
adapter also needs an explicit applicability boundary: the design describes
projects under `~/workspace/projects`, while the plan says any new project after
`make bootstrap` receives the protocol.

Evidence:

- `solution-project-workspace-memory.md:20-28,144-158`
- `plan-project-workspace-memory-2026-08-07.md:127-142,335-353`

Required improvement: define the exact initialization trigger, the relationship
between task authorization and memory writes, and whether routing applies only to
projects under the workspace boundary or to all projects on the host.

### P1-3 — Read-only audit conflicts with audit history writes

The plan defines a “read-only audit” that must not modify project files, but the
same phase requires updating current memory and appending history. The acceptance
criteria separately require no modification for a read-only task and history
writing for a quick audit.

Evidence:

- `plan-project-workspace-memory-2026-08-07.md:192-214`
- `plan-project-workspace-memory-2026-08-07.md:335-353`

Required improvement: define separate `report-only` and `reconcile` modes. A
report-only audit must not write current memory or history; a reconcile audit may
write only its declared scope.

### P1-4 — Planned implementation paths are currently ignored

The reverse allowlist currently permits this review directory, but it does not
permit the implementation paths listed by the plan, including new rule files,
`.agents/templates/`, `docs/architecture/memory-governance.md`, or
`docs/workspace-memory*`. `git check-ignore --no-index` confirmed those paths
are still matched by the catch-all `*` rule.

Evidence:

- `.gitignore:1,8-23,34-45`
- `plan-project-workspace-memory-2026-08-07.md:101-111,236-243`

Required improvement: decide the template directory and add exact allowlist
entries to the implementation plan, with pre-commit verification as an explicit
phase check.

### P1-5 — AI behavior acceptance is not reproducible yet

The fixture section names useful scenarios, but does not specify the execution
driver, expected file changes, pass/fail rule, reviewer, or durable evidence
format. Existing `make test` covers workspace configuration/status behavior, not
the proposed memory lifecycle.

Evidence:

- `plan-project-workspace-memory-2026-08-07.md:222-234,382-394`

Required improvement: separate automated mechanical checks from manual AI
behavior checks. For each fixture, record the prompt, repository state, expected
scope, observed changes, gaps, and reviewer result in the round changelog or an
approved test artifact.

### P1-6 — Existing memory identity and duplicate handling remain unresolved

The conversation record lists custom memory-path handling as an open decision,
while the solution only says to locate an “equivalent” durable document. The
plan includes a non-default-path fixture without defining how it passes or how
multiple candidates are handled.

Evidence:

- `conversation-requirements-2026-08-07.md:585-599`
- `solution-project-workspace-memory.md:144-158`
- `plan-project-workspace-memory-2026-08-07.md:224-234`

Required improvement: define canonical path declaration/discovery precedence,
multiple-candidate behavior, and the no-duplicate rule before implementation.

### P1-7 — “Obvious secret patterns” cannot prove the stated safety criterion

The plan prohibits secrets and raw sensitive output, but proposes only narrow
checks for obvious patterns. A false-negative scan cannot establish the stronger
acceptance claim that memory/history contains no sensitive material.

Evidence:

- `solution-project-workspace-memory.md:227-248,263-274`
- `plan-project-workspace-memory-2026-08-07.md:275-296,335-353`

Required improvement: state that raw command output is never persisted by
default; require redaction or a blocked result when evidence may be sensitive;
use scanners only as defense-in-depth and not as proof of absence.

## 4. P2 improvements

- Define history IDs, filenames, ordering, concurrency behavior, and the
  distinction between an idempotent current project map and a new audit event.
  The current “append every refresh” and “no duplicate history facts” wording is
  ambiguous (`solution-project-workspace-memory.md:227-248`; plan section 6).
- Include branch and dirty-state evidence in workspace snapshots, not only a
  project HEAD, so a dirty project cannot be represented as fully current.
- Mark the conversation document as an assistant-maintained paraphrase with
  provenance; it is not a verbatim transcript or independently verifiable user
  record.
- Remove the extra blank line at EOF in
  `conversation-requirements-2026-08-07.md:607`; the untracked-file diff check
  reports it.

## 5. Verification performed

- `make test`: 28 tests passed.
- `bash -n scripts/*.sh .githooks/pre-commit`: passed.
- Supplemental Reality Ops shell syntax checks: passed.
- Relative links among the three review documents: passed.
- Review-directory allowlist check: passed.
- Tracked `git diff --check`: passed.
- Including the untracked conversation document in a no-index diff check:
  failed on the extra blank line at line 607.

Not run: bootstrap, host UI smoke tests, implementation-specific memory fixtures,
Reality Ops Ansible checks, Git staging/commit/push, and live verification. Those
are not evidence for this document-only review and remain gaps for a later
authorized implementation round.

## 6. Closeout

The three source documents and `.gitignore` were not modified by this review;
this turn only created this report. The working tree remains local-only and
unpublished. The next implementation round should resolve all P1 findings,
update the plan and solution, then perform a targeted re-review before any
cross-repository migration or Git publication.

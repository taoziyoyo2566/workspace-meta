# Plan: Public Repository Policy Reconciliation

Status: COMPLETE
Changelog: [Verified closeout](round1-public-repository-policy-2026-09-07.changelog.md)

## Goal

Reconcile current workspace-meta documentation with the operator's intentional
PUBLIC repository policy while preserving a strict boundary between portable,
publishable repository content and host-local or otherwise private runtime
state.

This change does not make the repository private, weaken secret protections,
publish local state, alter Git authorization/publication behavior, or rewrite
historical provenance.

## Current State

- The workspace-meta repository is intentionally PUBLIC.
- `README.md` still instructs the operator to keep the remote private.
- `docs/architecture/codex-config-management.md` still describes the
  workspace-meta synchronization remote as private.
- W-R26 records the earlier private topology as historical provenance and
  remains unchanged.
- Current security must be expressed through the boundary of explicitly
  publishable portable content rather than repository privacy.
- The accepted public-policy investigation found no reason to change generic
  secrets, authorization, Git, or publication rule modules.

## Intended Change

- Replace the stale private-only README guidance with concise current PUBLIC
  repository policy and the portable-versus-private-state boundary. Reference
  existing security/publication owners rather than duplicating their detailed
  procedures.
- Update the current architecture topology from a private remote to the
  intentional public synchronization model while preserving host-local/private
  ownership boundaries and the completed Plan/Changelog lifecycle wording.
- Append a concise provenance refinement using the next valid W-R identifier
  at implementation time. Preserve W-R26 and all other historical entries.
- Keep this `APPROVED` Plan frozen during ordinary implementation and create
  its Changelog only after verified, content-complete, commit-ready review.

## Scope

### In Scope

- `README.md`: replace the stale private-remote instruction with the current
  public-repository and portable-content boundary.
- `docs/architecture/codex-config-management.md`: correct the synchronization
  topology and retain the private host-runtime boundary.
- `feedback-register.md`: add provenance for the current policy without
  rewriting W-R26.
- `.gitignore`: reverse-whitelist this review directory without widening Git
  scope elsewhere.
- `docs/reviews/refactor-public-repository-policy/plan-public-repository-policy-2026-09-07.md`:
  carry this approved execution contract.
- `docs/reviews/refactor-public-repository-policy/round1-public-repository-policy-2026-09-07.changelog.md`:
  record the verified outcome only at commit-ready closeout; do not create it
  during planning or implementation.

### Out of Scope

- Changing repository visibility or making the repository private.
- Changes to `secrets.md`, `authorization.md`, `git.md`,
  `git-publication.md`, or other security/Git authorization semantics.
- Changes to `reasoning.md`, the Plan/Changelog lifecycle, adapters,
  bootstrap/runtime configuration, or host-local Codex/Claude state.
- Publishing credentials, authorization/trust state, histories, caches,
  databases, logs, host preferences, generated capability state, project
  content, or equivalent private/non-portable state.
- Rewriting W-R26 or migrating historical review records.
- Nested project changes, staging, committing, pushing, publication, or host
  activation.

## Security / Ownership Boundaries

The public repository may contain only explicitly whitelisted portable
workspace-meta governance, configuration, scripts, and review records.
Credentials and secrets, host-local executable authorization or trust state,
agent/session history, caches, databases, logs, host preferences, generated
capability/runtime state, project-private content, and equivalent non-portable
or private state remain outside Git.

Existing canonical security, `.gitignore`, and publication mechanisms retain
detailed enforcement ownership. Public visibility is an operator policy; it is
not evidence that every local workspace artifact is publishable.

W-R26 remains an unchanged historical description of the earlier topology. A
new provenance entry will record the current public-policy decision without
retroactively editing that evidence.

## Material Deviation Boundary

Follow `planning.md` if implementation would require changing an out-of-scope
security owner, Git/publication authorization semantics, repository visibility,
the portable/private-state architecture, acceptance criteria, or another
load-bearing approved boundary. Stop affected work and obtain approval before
amending this Plan or crossing that boundary. Routine in-scope wording and
documentation corrections are not automatically material deviations.

## Acceptance Criteria

1. Current canonical documentation no longer instructs the operator to keep
   the repository private.
2. The repository is explicitly described as intentionally PUBLIC.
3. Public visibility is not presented as making all local/workspace state
   publishable.
4. The portable/publishable versus host-local/private boundary is explicit.
5. Existing secrets, authorization, Git, and publication protections remain
   unchanged.
6. Historical W-R26 remains unchanged.
7. A new provenance refinement records the current public-policy decision.
8. No host-local/private runtime state enters Git scope.
9. No repository visibility action occurs.
10. Reasoning and lifecycle governance semantics remain unchanged.
11. This Plan follows the frozen `APPROVED` lifecycle.
12. Its Changelog remains absent during implementation and is created only at
    verified commit-ready closeout.
13. Final documentation remains consistent with the canonical Plan/Changelog
    lifecycle.
14. The remediation remains separable as its own logical publication unit.

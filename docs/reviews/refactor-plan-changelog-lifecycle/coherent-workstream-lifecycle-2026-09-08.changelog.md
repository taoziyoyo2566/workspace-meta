# Changelog: Coherent Workstream Lifecycle Refinement

Plan: [Coherent Workstream Lifecycle Refinement](plan-coherent-workstream-lifecycle-2026-09-08.md)

## Summary

Made the coherent workstream the unit of persistent planning and verified
closeout. Routine in-scope implementation, operator feedback, repair, and
re-verification now remain under a covering approved Plan instead of producing
round-specific durable artifacts. The reviewed commit is the durable-history
boundary: a narrowly premature pre-commit closeout can be corrected in place,
while committed completed artifacts remain historical and later work is
planned proportionally as a follow-up workstream.

## Changed Surface

- `planning.md` now owns workstream identity, the covering-Plan reuse check,
  explicit non-triggers for additional Plans, and a closeout boundary that
  remains open during active in-scope operator review and refinement. It also
  owns the narrow pre-commit `COMPLETE` to `APPROVED` correction and prohibits
  reopening a completed Plan after its result enters Git history, including
  before push.
- `documentation.md` defines the artifact-role consequence: a Changelog is the
  final verified workstream outcome, normally one per Plan rather than one per
  conversational or execution round. This remains a judgment rule, not a
  mechanical cardinality requirement. Before commit, a legitimate closeout
  correction may revise that Changelog; after commit, later work cannot rewrite
  the historical outcome record.
- Project `AGENTS.md` now contains only the workspace-meta routing delta and no
  longer frames Plans per non-trivial change or Changelogs per round.
- W-R46 records the policy recurrence, closeout-correction case, and durable
  commit boundary. The existing lifecycle regression protects Plan reuse,
  pre-commit reopening, post-commit preservation, proportional follow-up
  planning, and the superseded project wording without introducing a Plan
  parser or Git-history detector.
- Previously committed Round 8–10 Plans and Changelogs remain unchanged as
  historical records.

## Closeout Correction Exercised

This uncommitted workstream's Plan moved from `COMPLETE` back to `APPROVED`
when the in-scope commit-boundary omission was identified. The correction reused
the same Plan and Changelog; after final verification, the Changelog was revised
to record the actual outcome. No additional Plan or Changelog was created.

## Material Deviations

None. The existing material-deviation approval boundary and Git publication
authorization boundary were preserved.

## Verification

- `make test`: 93 tests passed.
- `make docs-check`: passed.
- Required shell syntax and Python compilation checks: passed.
- Generated Codex TOML and Claude JSON parsed; the host-generated environment
  YAML parsed.
- Two bootstrap runs against an isolated repository and home produced identical
  managed-file hashes on the second run.
- Reverse-whitelist coverage, historical-record non-interference, and
  `git diff --check`: passed.

No UI smoke test was applicable to this documentation-governance change. The
result remains local, uncommitted, and unpushed for operator review.

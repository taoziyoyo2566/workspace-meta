# Changelog: portable technical-reasoning governance, round 1

## Scope

Established one portable epistemic method for reaching and revising technical
conclusions, with a compact resident invariant and task-shaped Claude/Codex
routing. Workspace-meta was the sole implementation and verification scope.

## Changes

- Added `.agents/rules/reasoning.md` as the single portable owner for
  proportional premise validation, knowledge-state classification, independent
  technical judgment, evidence evaluation, warranted competing explanations,
  discriminating probes, and decision-relevant uncertainty.
- Added exactly one compact reasoning invariant to the byte-identical Claude
  and Codex Safety Floors and bound it to the canonical owner through the
  existing documentation gate.
- Added equivalent task routes in both adapters while keeping the detailed
  method out of resident context.
- Narrowed only genuine ownership ambiguity in `planning.md`, `review.md`, and
  `implementation.md`; verification, environment truth, authorization, Git,
  publication, and project-specific responsibilities remained with their
  existing owners.
- Registered the reasoning domain in the ownership matrix, README navigation,
  reverse whitelist, and W-R43 provenance without rewriting historical entries.
- Extended the existing documentation and configuration test surfaces for
  portable-owner inventories, route symmetry, Safety Floor parity and source
  binding, provenance, and stable semantic guardrails.
- Repaired the one G6 test-maintenance finding in G5R: the identical-drift
  negative test now uses a narrow whitespace-tolerant mutation and proves one
  mutation occurred in each adapter before checking canonical-source drift.

## Semantic audit

G7 replayed the implementation against the six original behavioral goals and
nine accepted scenarios. The result preserves proportional investigation,
independent judgment without reflexive disagreement, authoritative operator
decisions without treating them as empirical proof, conditional hypotheses,
non-mandatory reporting, safer diagnostic sequencing, and unchanged workflow
and authorization boundaries.

The anti-drift, architecture, ownership, and enforcement-proportionality audits
found no P0, P1, or P2 finding. One `reasoning.md` remains sufficient; no
separate debugging, diagnosis, evidence, or uncertainty owner is warranted.

## Verification

G6-R established the final technical baseline:

- the focused G5R regression passed with current and harmlessly rewrapped
  adapter fixtures, one mutation per adapter, identical mutated Safety Floors,
  and canonical-source drift detection;
- 79 of 80 full-suite tests and 59 of 60 governance/adapter tests passed; the
  sole non-pass in each was the expected Git tracking-state gate for the
  intentionally untracked `.agents/rules/reasoning.md`;
- shell syntax, Python compilation, `git diff --check`, reverse-whitelist
  checks, isolated agent synchronization, and generated JSON/TOML parsing
  passed; and
- two bootstrap runs in a disposable clone and home produced identical managed
  hashes on the second run.

General YAML parsing was blocked because this host has no YAML parser, although
the isolated registry was generated and passed `make env-probe-check`. A real
Claude/Codex UI smoke test was not applicable because host activation was out of
scope.

## Boundaries and publication state

No nested project, real host configuration, Git index, external system, or
publication state was changed. The complete change remains local-only,
uncommitted, and unpushed.

The result is PUBLICATION-READY: a separately authorized Git publication
transaction may be the next step, but this record does not authorize it.

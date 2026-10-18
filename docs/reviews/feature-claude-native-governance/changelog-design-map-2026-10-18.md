# Changelog: a design map for tracing a defect to its domain

- **Date**: 2026-10-18
- **Plan**: [plan-design-map-2026-10-18.md](plan-design-map-2026-10-18.md)
- **Delivery state**: content-complete and verified on branch
  `feat/claude-native-governance`, uncommitted. When this record was written,
  none of these steps had run: commit, merge into `main`, push, and a release
  tag.

## Outcome

[`docs/architecture/design-map.md`](../../architecture/design-map.md) is the
one catalog of workspace-meta's functions and domains.

- A symptom index of 40 rows leads from what the operator notices to a domain.
- 34 entries in six function areas (safety and authority; Git, releases, and
  deployment; requests, reasoning, and planning; building and checking; agent
  operation; host integration mechanisms) each give the owner with links to its
  key sections, what routes it into an agent's context, what enforces it
  mechanically (or that only prose holds it), what a project may add, and its
  symptoms.
- How To Change A Domain gives the procedure from finding the owner to the
  gate run, and `rule-authoring.md` Choose The Owner First sends an agent
  looking for an existing behavior's owner to the symptom index.
- `README-agents.md` keeps only the layer model and the managed surfaces; its
  former rule-owner table is replaced by a pointer, so no second ownership
  matrix exists. The README documentation map links the design map.
- The documentation gate requires every file in `.agents/rules/` to be linked
  from the map and the README to index it, enforces that each runtime module
  is routed by its own agent's adapter only, and keeps the adapters'
  request-reading sentence tied to its owner.

## Verification

- New gate checks and their negative tests (a rule owner missing from the map,
  also when its link sits only in fenced code; a missing map; a runtime module
  routed by the other adapter or missing from its own; drift in the
  request-reading sentence) pass with the 171-test suite in a committed scratch
  copy, and the gate finds every link and anchor in the map.
- The review rounds checked the map's owner, route, and enforcement claims
  against the rule files, adapters, and tests.

## Residual gaps

- The gate checks that every rule owner is linked, not that each entry's prose
  stays in step with its owner; How To Change A Domain makes updating the
  entry part of every owner change.
- The map covers workspace-meta's own design; each project keeps its own map
  of its documents.

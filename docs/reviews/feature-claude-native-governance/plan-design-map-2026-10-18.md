# Plan: a design map for tracing a defect to its domain

- **Date**: 2026-10-18
- **Level**: Workspace-meta documentation and its gate: one new architecture
  document, the host ownership document, the README map, the docs gate, and
  its tests.
- **Status**: COMPLETE on 2026-10-18, verified on branch
  `feat/claude-native-governance` (`.worktrees/feat-claude-native-governance/`),
  uncommitted at closeout. Changelog:
  [changelog-design-map-2026-10-18.md](changelog-design-map-2026-10-18.md).
  The design choices under "Decisions taken in the operator's absence" were
  confirmed by the operator on 2026-10-18 (see the operator decision below).
- **Approval**: the operator's request of 2026-10-17, point 4:
  "4，对当前workspace-meta的设计进行一个整理，方便日后发现有不合理的地方，可以直接看到是哪个功能，或者领域的设计出现的问题，方便针对性的修改。"
  and, for the whole request: "我要去睡觉了，Claude还有一个goal的功能，我的要求就是把我说的这几点处理完，我不会在这里看着你，我希望明天早上能看到结果".
  This authorizes the goal and its working-tree implementation on this branch.
  The design choices below were made while the operator was away and are listed
  under "Decisions taken in the operator's absence" for review.
- **Operator decision (2026-10-18)**: "确认，按建议的设计决定执行，准备提交命令包".
  The decisions taken in the operator's absence are confirmed as recommended,
  and the publication command bundle is to be prepared. Staging, commit,
  merge, push, and `make sync` still wait for the bundle's own review.
- **Not approved, presented for review**: staging, commit, merge, and push; a
  release tag.
- **Related**: [project bootstrap](plan-project-bootstrap-2026-10-18.md),
  [request intake](plan-request-intake-2026-10-18.md),
  [delegation allocation](plan-delegation-allocation-2026-10-18.md),
  [investigation of Claude Code 2.1.302](investigation-claude-code-runtime-2026-10-17.md).

## Goal

When the operator notices that something in workspace-meta's design is wrong,
whether an agent behavior, a host integration, or a check, one document leads
from what was noticed to the function or domain responsible and to the file and
section to change, with one canonical catalog that cannot silently drift.

Reading of the request (`requests.md`):

- "整理" is read as organizing what exists into a navigable catalog, not
  redesigning the rules.
- "发现有不合理的地方" is read from the operator's side: the entry point is a
  symptom the operator observes, not the name of a rule file.
- "功能，或者领域" covers both portable rule domains and the executable
  mechanisms (sync engine, SessionStart evaluator, status lines, docs gate,
  pre-commit guard, register).

## Current state at approval

- [`README-agents.md`](../../../.agents/host-templates/README-agents.md)
  held the canonical "Portable Rule Owners" table: domain, workspace owner, and
  what a project may add. It had no section anchors, no route, no enforcement,
  no symptoms, and nothing on mechanisms.
- `feedback-register.md` maps each owner to its W-R provenance; the
  [architecture doc](../../architecture/codex-config-management.md) explains
  the configuration layers and mechanisms; `docs/standards/README.md` maps
  topics to rule owners for people.
- The docs gate (`scripts/check_documentation.py`) checks adapter routes, the
  safety floor, the README documentation map, links and anchors, dated prose in
  current documents, and the runbook structure. Nothing checks that every rule
  owner appears in a catalog.
- Earlier decisions that constrain a map: the
  [rules-design review](../refactor-documentation-governance/review-rules-design-2026-09-05.zh-CN.md)
  found a second ownership matrix in the architecture doc that had diverged in
  8 of 15 rows (P1-1); the
  [remediation](../refactor-documentation-governance/plan-review-remediation-2026-09-06.md)
  removed it. W-R50 (2026-10-06) deferred a document registry with metadata
  blocks, a query tool, and hooks until a real recurrence shows the rules are
  insufficient. `README.md` Future improvements defers splitting the register.
  P2-5 of the same review noted that the canonical matrix sits under
  `host-templates/`.
- This workstream adds two rule owners (`requests.md`, `claude-runtime.md`),
  new mechanisms (multi-dir sync, the readiness check, two skills), and a
  layer model, which the old table could not place.

## Intended change

### A. `docs/architecture/design-map.md` (`# Workspace-Meta Design Map`)

Current guidance, so no dates in visible prose. It is the one catalog of
domains, grouped by function area:

- Safety and authority; Git, releases, and deployment; requests, reasoning,
  and planning; building and checking; agent operation (capabilities and
  delegation, rule authoring, the runtimes, memory); host integration
  mechanisms (adapters, sync engine and managed surfaces, the SessionStart
  evaluator with project readiness, status lines, the environment registry,
  skills, the docs gate, the pre-commit guard, the register).
- Each domain entry names its owner file and key sections, what routes it into
  an agent's context, what enforces it (a gate, test, hook, script, or
  setting), what a project may add, and the symptoms an operator notices.
- A symptom index (symptom to domain anchor), a "how to change a domain"
  procedure, and links to the layer model in `README-agents.md` and to the
  register's owner mapping, without copying W-R lists.

### B. `README-agents.md`

Its Portable Rule Owners table is replaced by a short pointer to the design
map. `## Managed And Host-Local Surfaces` becomes the five-layer model of the
[project bootstrap Plan](plan-project-bootstrap-2026-10-18.md) and lists every
surface managed in each Claude config dir. The runtime-module paragraph names
`claude-runtime.md` beside `codex-runtime.md`.

### C. Docs gate and tests

- `README.md` must link `docs/architecture/design-map.md` (`_check_index`).
- Every `.agents/rules/*.md` file must be linked from the design map; a rule
  file missing from it is an error.
- Runtime modules: every rule file except the two runtime modules is routed by
  both adapters; `codex-runtime.md` only by the Codex adapter and
  `claude-runtime.md` only by `CLAUDE.md`. A runtime module routed from the
  other agent's adapter is an error.
- `tests/test_governance_docs.py` has a case for each check.

### D. Navigation

`README.md`'s documentation map gains the design map. The
[architecture doc](../../architecture/codex-config-management.md) points to the
design map for domain ownership and keeps `README-agents.md` for the layer
model.

## Scope and non-goals

- No rule changes its meaning because of the map; the map states no rule.
- No document registry, metadata blocks, or query tool (W-R50's deferral
  stands).
- No split of `feedback-register.md`.
- `docs/standards/` stays the handbook for people; it is linked, not merged.

## Decisions taken in the operator's absence

Each choice names the alternative and why it was not taken. The operator may
reverse any of them at review.

1. **The design map replaces `README-agents.md`'s rule-owner table**, instead
   of adding a richer map beside it. Two catalogs of the same ownership already
   diverged once (P1-1); one catalog with the docs gate behind it cannot.
2. **The map lives in `docs/architecture/`**, instead of in `host-templates/`
   or the register. It explains how the design fits together, which is the
   architecture role (`documentation.md` Route Content By Role), and it moves
   the domain catalog out of `host-templates/` (P2-5). `README-agents.md` keeps
   the host layer model, which is about agent configuration.
3. **Completeness is enforced by the docs gate** (every rule file linked, the
   README links the map), instead of the deferred document registry. A static
   catalog with a mechanical completeness check meets the need without the
   registry's metadata and tooling; the registry's restart condition is
   unchanged.
4. **A symptom index is the entry point**, instead of a list by file. The
   operator asked to see "是哪个功能，或者领域" from what looks wrong; symptoms
   are what the operator sees. Each symptom names a domain anchor, which the
   link checker validates.
5. **Executable mechanisms are domains too**, instead of a map of rule files
   only. Several defects found in this workstream sat in mechanisms, not rules:
   the second Claude config dir got no SessionStart hook because the sync
   targeted one directory (investigation §11.2).
6. **The map links the register's owner mapping instead of copying W-R
   numbers**, and the register is not split. A copied list would be a second
   provenance index to keep in step.
7. **The runtime-module routing rule is enforced by the gate**, instead of left
   to review: each runtime module is routed only by its own agent's adapter, so
   a Claude-only mechanic cannot leak into the Codex block or the reverse.

## Acceptance criteria

- `design-map.md` exists with the function areas, entries, symptom index, and
  change procedure of A; every rule file in `.agents/rules/`, including
  `requests.md` and `claude-runtime.md`, is linked from it; it has no visible
  date.
- `README-agents.md` has no Portable Rule Owners table; it points to the map
  and holds the layer model.
- The docs gate fails, in tests, when a rule file is missing from the map, when
  `README.md` does not link the map, and when a runtime module is routed from
  the other agent's adapter; it passes on this branch, except the known
  "routed documentation is not tracked" error for files the operator has not
  committed.
- Tracing check: for three symptoms from this workstream ("no session-start
  warnings in the second account's sessions", "the agent started work on a
  misread request", "every subagent ran at maximum effort"), the symptom index
  leads in one step to the domain entry, and the entry to the owner section
  that changed.

## Risks

- The map goes stale when a section is renamed: anchors in links are checked,
  and section names in prose are kept to owner names.
- Symptoms are incomplete: add one when a defect is traced without the index
  (the change procedure says so).
- Uncommitted worktrees that add rule files (`feat/rule-evals`) must add a map
  entry before they merge; the gate makes that visible.

## Links

- Builds on: `README-agents.md` (its table is replaced); the
  [rules-design review](../refactor-documentation-governance/review-rules-design-2026-09-05.zh-CN.md)
  and its [remediation](../refactor-documentation-governance/plan-review-remediation-2026-09-06.md)
  (no duplicate matrix); the register's owner mapping; `docs/standards/README.md`;
  `scripts/check_documentation.py` and its tests.
- Supersedes: the Portable Rule Owners table in `README-agents.md`.
- Keeps: W-R50's deferral of a document registry and the deferred register
  split in `README.md`.
- Partly addresses: P2-5 of the rules-design review (the domain catalog leaves
  `host-templates/`; the layer model stays there).
- Related: the other three Plans of this workstream supply the new domains and
  mechanisms the map catalogs.

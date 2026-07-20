# Rule Authoring And Feedback

Agent-neutral workspace rule for ownership, rule form, provenance, and
recurrence-driven refactoring.

## Ownership

This file owns the method for creating or changing portable behavior rules.
Projects own project-only rules and adapters. Agent adapters own only their
runtime mechanics and compact intentional safety floors. Host-local
authorization/preferences remain in actual host configuration.

## Choose The Owner First

Classify every normative statement before writing it:

- portable cross-project method → shared workspace rule;
- agent runtime/tool/permission mechanic → that agent's adapter/module;
- project topology/schema/command/domain constraint → project owner;
- path-local delta → path adapter;
- credential, executable allow/prompt, trust, preference, or runtime state →
  host-local configuration.

Adapters route and may repeat only a compact safety floor that is tested against
its canonical owner. They do not become a second procedural owner.

## Edit The Whole Relevant Owner

When editing a rule/config/instruction owner:

1. read the complete relevant owner;
2. check fit, conflicts, duplication, dead text, trigger precision, and a
   simpler form;
3. land one coherent in-scope change.

This is not authority for unrelated redesign. Preserve unrelated user work and
historical provenance.

## Match Form To Failure

| Observed failure | Rule form |
|---|---|
| discipline-skip | firm prohibition plus concrete red flags/rationalizations |
| wrong-shaped output | positive recipe describing required parts and order |
| omitted element | required field/slot in the template already used |
| condition-dependent behavior | conditional keyed to an observable predicate |

Do not default to prohibitions for shape or omission failures. Express a real
exception as its own observable condition, not a vague exemption clause.

## Provenance And Refactoring

Portable feedback records the source incident and rationale in
`feedback-register.md`, then routes the active behavior to the narrowest owner.
Project-only feedback stays with the project. Do not invent a host prose file
as a portable owner.

A later real recurrence is refactor evidence: revisit owner, trigger, and rule
form before amplifying wording. Constructed pressure scenarios are optional for
high-risk/disputed rules; the source incident is the normal baseline evidence.

# Rule Authoring And Feedback

Agent-neutral workspace rule for feedback intake, ownership, rule form,
provenance, and recurrence-driven refactoring.

## Ownership

This file owns taking in operator feedback about how agents work, the method
for creating or changing portable behavior rules, and what a rule, a register
entry, or a memory note of feedback may contain. Projects own
project-only rules and adapters. Agent adapters own only their runtime
mechanics and compact intentional safety floors. Host-local
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

To find the owner of an existing workspace behavior, start from the symptom
index of `docs/architecture/design-map.md`, and follow its How To Change A
Domain when the change lands.

## Feedback Intake

When the operator corrects how you work or states a preference about it,
classify it under Choose The Owner First in the reply that takes it in, and
say which it is:

- project-only: it stays with the project, under the project's rules;
- cross-project, in a session whose task is workspace-meta governance: route
  it as Provenance And Refactoring says;
- cross-project, in any other session: hand it over in the same reply. Give
  the command that starts a session at the workspace-meta root, as
  `capabilities.md` Commands The User Runs says, or, when the operator names
  an existing session and your runtime can message it, send it there. The
  brief quotes the operator's words with their time, names the source
  transcript and any memory note, and states what the operator has
  authorized. Do not change workspace rules or `feedback-register.md` from
  this session unless the operator asks.

How an agent should work is behavior even when it names a setting; only a
setting's value, such as a permission, credential, or model or display
default, is host-local configuration. Agent memory, whether you write it or
the runtime consolidates it, does not route feedback. When unsure whether it is
cross-project, say which you chose and why.

Red flags: "it is saved in memory"; "it came up in this project, so it is
project-only"; "this session does not handle workspace rules"; "I'll hand it
over later".

## Edit The Whole Relevant Owner

When editing an agent rule, adapter, or instruction owner:

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

Portable feedback gets one entry in `feedback-register.md`: the rule in one
sentence and one line of source giving the date, the project, and the cause in
one sentence. The active behavior goes to the narrowest owner, and the rule
covers the class of problem. Project-only feedback stays with the project. Do
not invent a host prose file as a portable owner.

A rule, an adapter, a register entry, and an agent memory note of feedback hold
only lasting guidance: what to do, when, and why in general terms. Leave out
what is true only for one session or task, such as exact times, temporary
paths, routing or progress status, quotes, and the story of an incident.

A later real recurrence is refactor evidence: revisit owner, trigger, and rule
form before amplifying wording. Constructed pressure scenarios are optional for
high-risk/disputed rules; the source incident is the normal baseline evidence.

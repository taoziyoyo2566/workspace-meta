# Plan: portable project-documentation governance

- **Date**: 2026-09-04
- **Level**: Information architecture / cross-project governance
- **Status**: IMPLEMENTATION_COMPLETE
- **Direction**: user requested an internet-first redesign and then authorized
  implementation with “请开始”.

## Goal

Add one agent-neutral owner for project-documentation roles and truth
lifecycles, then use it in a small project pilot before any bulk migration.
Make current guidance easy to find without discarding decisions, incidents, or
dated evidence.

## Design basis

- Diátaxis separates tutorial, how-to, reference, and explanation by reader
  need rather than document chronology.
- arc42 and C4 keep architecture views purposeful and bounded.
- ADR practice preserves decisions and consequences separately from current
  operating instructions.
- Google SRE postmortems preserve incident learning without turning incidents
  into the runbook authority.
- GitHub documentation guidance treats docs as versioned, reviewed source.
- OpenAI's AGENTS guidance favors concise, layered, task-relevant instructions
  and repository-local verification commands.

Sources: [Diátaxis](https://diataxis.fr/), [arc42](https://docs.arc42.org/),
[C4](https://c4model.com/), [ADR](https://adr.github.io/), [Google SRE](https://sre.google/sre-book/postmortem-culture/),
[GitHub Docs](https://docs.github.com/en/contributing/writing-for-github-docs/about-githubs-documentation),
and [OpenAI Codex](https://developers.openai.com/codex/guides/agents-md).

## Scope

1. Add `.agents/rules/documentation.md` as the portable owner.
2. Route both thin adapters to it and update ownership documentation.
3. Add focused regression coverage and reverse-whitelist entries.
4. Record W-R38 provenance.
5. Pilot the design in NanoPi_R6S_Handbook with entry points, one reusable
   operation, one incident, and one decision record.

## Exclusions

- No full project-document migration in this round.
- No prescriptive universal directory tree for every project.
- No replacement of source/config/runtime truth with prose.
- No host activation, staging, commit, push, deployment, or live operation.

## Verification

- workspace-meta: unit tests, syntax/config parsing, reverse-whitelist guard,
  diff checks, and isolated two-pass bootstrap.
- project pilot: existing shell tests, syntax checks, relative-link checks, and
  diff checks.
- Report unavailable checks as gaps rather than passed.

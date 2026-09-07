# Implementation Shape

Agent-neutral workspace rule for turning an approved outcome into a small,
coherent, maintainable set of artifacts.

## Ownership

This file owns artifact boundaries, source-of-truth placement, local comment
quality, implementation change surface, and the shape of related tests.
`planning.md` owns approved outcome and scope. `verification.md` owns selection,
execution, and reporting of post-change verification evidence. `review.md` owns
defect assessment. Projects may add language, framework, architecture, and
repository conventions.

## Shape The Change Before Editing

For each in-scope behavior, identify:

1. the executable owner;
2. the contract users or operators may rely on;
3. the canonical owner of each normative fact;
4. the evidence that will prove the result; and
5. the smallest coherent file set, with one necessary role per file.

This is a proportional implementation check, not a requirement to create a
separate plan for every trivial edit.

## Keep Artifact Roles Separate

| Artifact | Question it answers |
|---|---|
| executable code/configuration | What does the system do? |
| local comment | Why does this location require a non-obvious constraint? |
| user/API contract | What may a consumer rely on? |
| runbook | How does an operator perform or recover an operation? |
| Plan | What implementation intent and acceptance boundary are approved? |
| ADR | Why was an architectural decision made? |
| review | What findings and readiness judgment resulted? |
| Changelog | What verified implementation outcome was delivered? |
| legal notice/license carrier | What attribution or terms must accompany the work? |
| test | Which observable contract or load-bearing invariant is proven? |

Do not use production code or configuration as a diary for alternatives,
review discussion, or implementation history. Preserve useful rationale in the
decision/evidence owner; delete it when it has no continuing value.

## One Fact, One Canonical Owner

- Give every normative value or policy one canonical owner.
- Other required carriers reference it or are mechanically derived from it.
- A consistency test does not justify independently maintained copies.
- Before adding a manually synchronized copy, centralize, generate, or reference
  the value unless the target format requires duplication.
- Duplication required by an external format, runtime-specific carrier, or
  legal carrier is intentional: name the canonical source and automate drift
  detection where practical.

Extract shared code or data when it centralizes a real policy, prevents drift,
or serves more than one consumer. Keep one-use orchestration inline when an
abstraction would only move complexity into another file.

## Write Durable Comments

A local comment should explain a non-obvious reason, invariant, protocol rule,
compatibility constraint, or safety boundary that clearer code cannot express.
Keep it adjacent to the affected code and as short as the constraint permits.

Implementation narrative, rejected alternatives, review findings, temporary
steps, and restatements of code do not belong in local comments. Linter or tool
suppressions name the narrow scope and enduring reason; they do not recount the
investigation that produced them.

## Keep The Change Reviewable

- One change carries one coherent concern plus its directly related tests and
  contract updates.
- There is no universal file-count or line-count limit. Growth is a signal to
  re-check ownership, duplication, and separability.
- If implementation crosses into an unforecast artifact role, pause and
  re-shape the file set before spreading the same concern further.
- Separate unrelated cleanup. Perform a prerequisite refactor in the same
  change only when the requested behavior cannot be correct or reviewable
  without it.
- Prefer the platform's supported primitive over a local framework. Reuse or
  extract only after the ownership and consumer boundary is clear.
- Every changed file must have a necessary, explainable responsibility in the
  result; otherwise remove it from the change or redesign the boundary.

## Test Contracts, Not Incidental Text

Prefer observable behavior, public interfaces, and explicit data contracts.
Do not make comments, step names, local variables, or formatting part of the
test contract.

Source-shape assertions are appropriate only when the source text is itself the
contract or when a load-bearing property cannot be observed safely at runtime,
such as a publication ordering or permission boundary. Name that invariant in
the test. Do not use broad text searches as a proxy for exercising behavior.

## Closeout Check

Before verification, confirm that each changed file has one role, each
normative fact has one owner, comments contain only durable local rationale,
and tests exercise contracts rather than the current implementation spelling.
Then ask whether a smaller representation preserves the same behavior and
evidence; simplify when it does.

# Verification

Agent-neutral workspace rule for proving that a change works.

## Ownership

This file owns the generic verification method. Projects own their command
matrix, environments, fixtures, acceptance thresholds, and required CI.

## Required Result

After a change, verify in proportion to the touched surface:

1. **Direction** — compare request, scope, and diff; confirm the change is in the
   right owner and has the intended effect.
2. **Syntax/static correctness** — parse, lint, type-check, or validate the
   changed format and interfaces.
3. **Functional behavior** — execute the changed workflow or the closest
   project-provided behavioral test when feasible.

A parser or linter does not substitute for functional execution. Documentation
that gives commands, paths, links, or procedures verifies those references and
executes safe representative commands when feasible.

## Failure And Retry

When a check fails:

1. determine whether the failure is caused by the change, environment,
   stale expectation, or unrelated baseline;
2. fix only the authorized in-scope cause;
3. rerun the failed check plus affected/downstream checks needed for one
   coherent result.

Do not impose a universal restart-from-check-one order or a fixed attempt count.
Repeated failure triggers deeper diagnosis and an explicit blocked/gap report;
it does not become passed through repetition or exhaustion.

## Gaps

If a required check cannot run, report it as blocked or not run, never passed.
Environment-based gaps follow `environment-truth.md` and cite current evidence.
Do not claim whole-workflow success from a narrower substitute without naming
the gap.

# Git Recovery And Destructive Operations

Agent-neutral workspace rule for non-ordinary Git mutations, destructive
effects, and recovery.

## Ownership

This file owns rebase/cherry-pick/revert/tag/pull, ref/config/history mutation,
discarding checkout/restore/reset/clean, forced updates/deletion, amend, hook
bypass, and recovery. Projects add archive tooling and stricter ref policy.

Read `git.md` for the current state snapshot before using this module.

## Exact Reviewed Effect

Non-ordinary mutations require an exact reviewed action appropriate to their
effect. Prefer merge/revert/new-branch paths when they satisfy the goal without
rewriting or discarding state.

A destructive/recovery-sensitive review includes exact command, target, reason,
current/ref OIDs, dirty/index state, expected loss/effect, recovery method, and
post-check.

## Forced Updates And Deletion

Never use bare force-push, `-f`, `+refspec`, or bare remote deletion. A required
non-fast-forward update uses
`--force-with-lease=<ref>:<expected-oid>`, with expected OID captured before the
racing verification.

Local forced deletion first verifies the exact ref/OID and applies project
archive/recovery requirements. Remote ref deletion is always separately
reviewed and race-safe.

## Reset Or History Rewrite

1. record branch, HEAD, dirty/index state, and worktree map;
2. explain why merge, revert, cherry-pick, or a new branch is worse;
3. create or identify a recovery ref before mutation;
4. review exact target and mode;
5. verify log, reflog, status, and diff against recovery afterward;
6. retain the recovery ref until the user releases it.

Secret discovery or technical permission never authorizes index/history/remote
remediation, force, deletion, rotation, or destruction.

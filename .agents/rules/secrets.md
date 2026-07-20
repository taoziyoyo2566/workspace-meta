# Secret Safety

Agent-neutral safety floor for credentials, secret material, sensitive output,
and remediation.

## Ownership

This file owns generic non-exposure and remediation boundaries. Projects own
approved stores, paths, encryption, rotation, access, and validation commands.

## Safety Floor

Real credentials, private keys, tokens, passwords, secret values, or
unredacted sensitive output must not be:

- printed into conversation/tool output unnecessarily;
- committed or pushed;
- copied into plans, reviews, changelogs, screenshots, logs, fixtures,
  examples, or governance files;
- moved to another tracked location as a workaround.

When secret material appears:

1. stop further exposure and do not reproduce the value;
2. identify its location/state without printing it;
3. redact user-facing evidence;
4. determine whether it reached working tree, index, history, remote, logs, or
   an external system;
5. use `git-recovery.md` for index/history/remote remediation and
   `authorization.md` for deletion, rotation, revocation, or external writes.

Discovery does not authorize `git rm --cached`, history rewrite, force-push,
remote deletion, credential rotation, or secret destruction.

## Project Delta

Before creating, moving, or consuming a secret, read the project's placement
rules. A project should define canonical store/ignore/encryption boundary,
consumers/least-access path, redacted examples, rotation owner, and
non-revealing verification.

Record only identifiers, locations, ownership, and lifecycle evidence needed
for reproducibility. Never record the secret itself.

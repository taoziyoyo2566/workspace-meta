---
name: env-sync
description: Probe this host's environment capabilities into its local workspace registry (~/workspace/.agents/env/<host>.yml). Use at session start on a new/changed machine, when env-probe-check reports stale, or whenever a command unexpectedly fails with "not found" / daemon errors.
---

# env-sync — refresh the local per-host capability registry

Workspace-wide host probe (hoisted from per-project repos 2026-07-11). One local
registry under `~/workspace/.agents/env/` serves every project on this machine.
Generated YAML remains Git-ignored and is never shared to another machine.
Behavior rule: `~/workspace/.agents/rules/environment-truth.md` (probe, don't
recall).

## When to run

- First session on a machine (no `~/workspace/.agents/env/<hostname -s>.yml` yet)
- `make -C ~/workspace env-probe-check` (or the SessionStart hook) reports missing/stale
- Any mid-session capability surprise: `command not found`, docker daemon
  unreachable, auth failure on a capability the registry lists as available

## Steps

1. Run the probe (single source of probe logic — do not re-implement probes inline):

   ```bash
   make -C ~/workspace env-probe
   ```

2. If a previous local snapshot existed, compare the facts read before the probe
   with the regenerated file and report capabilities that flipped
   (available ↔ absent), since stale plans or memories may depend on old state.

3. If a capability needed by the current task is **absent**, classify before acting:
   - **Project-local fix** (safe to do now): `ansible-galaxy` collection install,
     venv creation, `make setup` / `make install` in the active project. Do it,
     then re-run the probe. NOTE: the shared registry probes the **bare host PATH**,
     so tools a project provides via its own `.venv/bin/` may read `available: false`
     here — that is the host layer being honest, not a real gap. Trust the project's
     own tooling; the registry's `host_overrides` note the "use project make targets"
     path.
   - **System-level install** (docker, apt/yum packages, daemons): do NOT install
     automatically. Propose the exact install command to the user and record the
     gap + fallback in your report.

4. If any flipped capability contradicts an agent memory file or an active
   plan's pre-conditions, update the currently governing record before it
   directs later execution. Preserve completed historical evidence and annotate
   it only when a reader needs a pointer to the current replacement.

5. Report the registry path, delta, and probe date. The snapshot stays local;
   another machine or later host must re-probe rather than publish or copy it.

## Notes

- The registry carries **host capability facts + host-conditional hints only**.
  A project's task→command mapping is that project's own SSOT (its testing /
  governance docs) — consult it there, never copy it into the registry.
- TTL default is 7 days (`ENV_PROBE_TTL_DAYS` to override). Freshness is a floor,
  not a guarantee — surprises always trigger re-probe regardless of age.

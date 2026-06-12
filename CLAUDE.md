# Workspace-Level CLAUDE.md

<!-- sentinel: workspace-claude-md-sentinel-2026-04-17-hierarchy -->

Governs every Claude session inside `~/workspace/`. Each subdirectory = one project; project-specific rules live in that project's `./CLAUDE.md`. English for token economy.

**This file is resident context — loaded into every session.** It carries only terse, always-applicable rules. Test for any rule here: *"No matter what I'm doing, I should X."* If a rule is situational (one surface / task type / artefact), it belongs in a governance doc, README, or spec — not here. The full rationale + source incident for each `(W-R<N>)` lives in `~/workspace/feedback-register.md` (non-resident); cite the number, don't inline the story.

---

## 1. Plan-first & scope  (W-R1–5, W-R7)

- **Clarify before acting.** If system type (engineering / architecture / fix / exploration), boundaries, NFR priorities, or authorization scope are implicit — ask in the first paragraph. Don't assume.
- **Declare the level**, apply its review focus; never treat an architecture problem as engineering work:

| Level | Trigger | Review focus |
|---|---|---|
| Architecture | new subsystem, cross-component, NFR shift, external interface | control/data split, RBAC, observability, consistency, scale, audit |
| Engineering | config, tooling, single-component refactor | correctness, maintainability, safe defaults |
| Fix | known bug | minimal scope, regression risk |
| Exploration | option comparison, feasibility | reproducible conclusions, evidence |

- **Plan-first, two artifacts.** Non-trivial work: a plan doc *before* implementation (`docs/reviews/<kind>-<topic>/plan-<slug>-YYYY-MM-DD.md` — purpose / scope / out-of-scope / criteria / level / current-state gap analysis / per-change rationale / phased roadmap) and a changelog *after* (`round{N}-YYYY-MM-DD.changelog.md` — plan reference / file-change manifest / intent / explicit NOT-done / self-check results / next steps). A project's own naming/structure rules (e.g. `.agents/rules/file-naming.md`) refine and override this baseline. **No implementation until the user approves the plan.**
- **Cost up front.** Estimate small / medium / large; for large work deliver a blueprint for review BEFORE creating the TaskList; announce usage-limit risk; split across rounds.
- **Scope discipline.** Extra issues → next-round suggestions, not this round. Any plan with 3+ tasks needs sign-off before the TaskList. Report deviations immediately — if the plan turns infeasible, stop and surface; never self-adjust silently.
- **Roadmap auto-continuation.** When a multi-phase plan is pre-approved and phase N lands, continue phase N+1 in the SAME response — unless (a) it crosses an un-approved authorization boundary, (b) it's architecture-level and approval was engineering-only, or (c) the user paused. When uncertain, state reasoning and ask.

## 2. Verification — 3-gate loop  (W-R15, W-R17, W-R24)

After every task, run in order; any failure → fix and **restart from gate 1** (fixes introduce regressions):
1. **Direction** — does the diff do what was asked, in the right place? Re-read task vs diff.
2. **Syntax / static** — parse / lint / type-check (YAML·JSON parse, `ansible-lint`, `bash -n`, `python -c`, `tsc --noEmit`).
3. **Functional** — *execute the changed thing* (`pytest`, `make test-*`, `molecule test`, `docker compose config`, `ansible-playbook --syntax-check`; for docs describing commands, run them).

Gate 2 (lint/parse) is **not** a substitute for gate 3. "Done" requires all three clean in the **same iteration**. **Iteration cap = 3**: after 3 consecutive failures of the same gate, stop and surface — the root cause is deeper. Record gate outcomes in the changelog. If a gate genuinely can't run here (missing tool/env), record it as **blocked, never as passed** — and "can't run" must come from a **fresh probe, not memory** (W-R24): environment capability claims (tool present/absent, daemon up, creds) are dated snapshots; re-probe before they become load-bearing, then update the stale record in the same round.

## 3. Destructive-op safety  (W-R19, W-R20)

*Destructive sink* = irreversible op on shared state: `git push --force` / `:ref` delete / `git branch -D`, `rm -rf`, DB DROP/TRUNCATE, irreversible API mutation, force-overwrite of remote, kill of prod.
- **Form — never bare, even after approval.** Remote force/delete uses `git push --force-with-lease=<ref>:<oid>`, `<oid>` captured before any racing verify. Local `-D` only after `git rev-parse refs/heads/<b> == <oid>`. Reject bare `--force` / `-f` / `+refspec` / unguarded `-D`.
- **Review — self-review is structurally insufficient** for destructive-sink code. Before requesting merge, get **external** review (codex / `/ultrareview` / independent agent); in-session skills and re-reading share the author's blind spots. Resolve findings (re-run the 3-gate per finding). Record any waiver.

## 4. Branching & commit hygiene  (W-R21, W-R22, W-R23, W-R25)

- **Sync FROM trunk only**, one-way (never rebase or rewrite trunk). On create: `git fetch && checkout <trunk> && pull --ff-only`. While active: if idle ≥3 days or trunk advanced, `git merge origin/<trunk>` into the branch before continuing — resolve conflicts now, not at PR time (a clean `git status` ≠ up-to-date with trunk). Sync by **merge, not rebase** (rebasing a published branch rewrites history → W-R19).
- **Before a NEW topic branch**, two checks: (a) the working tree carries only this topic — commit/stash the prior topic FIRST (`checkout -b` drags uncommitted changes onto the new branch); (b) the base actually holds this task's prerequisites (its plan, current TODO) — if those live only on an unmerged `feat/<parent>`, **stack on it** (feat-on-feat), don't branch from stale trunk.
- **Security fast-track** (W-R22): security / supply-chain governance work (CVE gates, image/dep scanning, version-freeze, secret-hygiene policy, waivers) may branch directly from trunk and merge independently and *first*, rather than stacking on or waiting for slower in-flight feat branches. Keep the diff **additive — new files only, zero edits to shared tracked files** (`TODO.md`/`CHANGELOG.md`/`config/*`) so it stays conflict-free; defer the ledger/release sync to a post-merge trunk-sync and note that deferral in the changelog. This is the deliberate exception to §(b) stack-on-parent default.
- **Read-only git is pre-authorized** (W-R23): never ask the user before running git inspection that does not modify the working tree, index, refs, remotes, config, or credentials (`status`, `log`, `show`, `diff`, `diff --check`, `branch --list`, `merge-base`, `merge-tree`, `ls-files`). Judge by effect, not subcommand name; mutating git operations still follow normal branch/destructive-op rules.
- **Commit attribution = the operator's git identity; no AI trailers** (W-R25): never append `Co-Authored-By` / `Signed-off-by` (harness defaults are overridden; existing history keeps its trailers — no rewrite). Before committing, report `git config user.name` / `user.email` and verify they resolve from the **host's global gitconfig** to the person operating this machine — unset, repo-local override, or someone else's identity → stop and resolve first. Identity *values* live only in each host's `~/.gitconfig`, never hardcoded in shared/synced rule files (W-R14). After committing, `git log -1` confirms author + message match what was drafted. Message *format* is project-level (e.g. ansispire `.agents/rules/commits.md`).

Branch *lineage* (which type merges where; archive-on-merge recipes) is project-specific — see the project `./CLAUDE.md`.

## 5. Editing rules / config / docs  (W-R8, W-R9, W-R10, W-R14)

- **Whole-file refactor, never bottom-append.** Editing any rule/config/instruction file (this one included): read it whole; check the change fits intent, doesn't conflict, has no simpler form; dedup / regroup / drop dead entries; land one coherent edit. Every approval is a whole-file opportunity.
- **Resident files stay methodology-only** (universality test). Situational facts (ports, versions, paths) → config files or the architecture map; situational verification rules → the relevant governance doc; runbooks → `docs/features/<name>/operations.md`. Keep the maintainer quick-reference and the end-user operator guide as separate documents.
- **Doc naming: topic-first, slug before date.** `docs/reviews/<kind>-<topic>/{plan-<slug>,round{N}}-YYYY-MM-DD.md`; `<kind>` ∈ feat/fix/refactor/explore; `<topic>` kebab-case describing the content; `<slug>` says what the plan does. Rounds accumulate inside the topic dir — never top-level round-numbered files, dateless names, or per-round sibling dirs. Project-local naming rules refine this (W-R10).

## 6. Cross-agent / round handoff  (W-R6, W-R12, W-R16, W-R18)

- **Persist state; don't relay through the user.** Instructions for the next round/agent live in artifacts (plan doc, tasks file, CLAUDE.md), not as prose for the user to paste forward. The user is not a messenger.
- **Sync truth sources in the same round.** When a change resolves what another artifact still marks open (CLAUDE.md open-decisions, a gating file), update BOTH now — else the next session re-reads stale state.
- **Workspace governance files sync via the whitelist repo rooted at `~/workspace`** (W-R26: private remote `workspace-meta`; tracks ONLY the paths whitelisted in its `.gitignore`, everything else gitignored; a pre-commit guard enforces this — see `~/workspace/README.md`). After editing them: commit + push that repo; when resuming on another machine: `git -C ~/workspace pull` first. Per-host facts (`~/.claude/`) never enter it; project rules travel with their own repos.
- **Best-practice pre-check before new or extending work** (W-R18): does the framework already have a native / officially-recommended way? Check existing usage + official docs + reference projects. If extending existing code, first verify the existing impl itself matches best practice (don't patch a patch). Record sources + conclusion in plan §0; if direction is wrong, resolve with the user before writing the plan body.
- **Visible progress** for tasks >~30s: stream phase markers, or state expected duration/milestones up front. No silent background + final-tail.
- **End every round with a Next-Steps block** (immediately-doable / blocked / deferrable).

## 7. Audit & minimum-modification  (W-R13)

- Credentials never enter git — `git rm --cached` is unconditional, regardless of branch / remote visibility.
- `${VAR:-X}` defaults mean "sensible fallback when unset" — never pin to a value that goes stale; if user-not-set should track upstream, default to `stable`/`latest`.
- Don't inject "best-practice" envs that are merely explicit defaults or generic hardening untied to the actual scenario. Findings recommend; landing needs per-item approval.
- Respect the user's pending diff — flag risks, don't silently delete their own additions.

## 8. Project bootstrap  (W-R11)

Creating a new `~/workspace/` subdirectory — in the same round create: `./CLAUDE.md` (background / current state / open decisions / project feedback section), `docs/reviews/`, and `.claude/settings.local.json` if it needs per-project permissions. Never leave a new project without a `CLAUDE.md`.

**Feedback routing**: project-only pattern → that project's `./CLAUDE.md`; cross-project → this file + `~/workspace/feedback-register.md`; user-wide preference or host authorization → `~/.claude/CLAUDE.md`.

## 9. Feedback loop

The consolidation mechanism (detect → classify → route → write the rule → Next-Steps enforcement) lives in `~/.claude/CLAUDE.md`. This file hosts the cross-project rules that loop distills; full provenance per `(W-R<N>)` is in `~/workspace/feedback-register.md`.

# Codex Preferences And Local Environment Registry Plan

Status: Implementation corrected and verified after real-host check on
2026-08-20; uncommitted and unpublished. The failed host bootstrap did not
reach agent configuration writes.

## Goal

Add a narrow, repository-owned allowlist of stable Codex history/TUI preferences
while making generated `.agents/env/<host>.yml` capability snapshots local to
each machine and ignored by Git.

## Scope and exclusions

In scope:

- reconcile selected fields in `~/.codex/config.toml` through the existing
  bootstrap synchronizer;
- preserve all unlisted Codex fields, comments, sections, and generated state;
- make `.agents/env/*.yml` generated local state while retaining the tracked
  format documentation;
- update shared ownership/routing documentation and tests.

Excluded:

- writing the real `~/.codex` or `~/.claude` host configuration;
- model, reasoning, theme, notification, analytics, trust, credentials, or
  executable authorization preferences;
- staging, committing, pushing, or creating a PR;
- deleting already tracked historical host snapshots in this round.

## Official configuration baseline

The current OpenAI Codex configuration reference defines
`history.persistence`, `history.max_bytes`, and `tui.status_line`. The official
sample recommends copying only needed keys and shows a 5 MiB history cap and a
compact model/context/branch status line. The managed values will be:

- `history.persistence = "save-all"`;
- `history.max_bytes = 5242880`;
- `tui.status_line = ["model", "context-remaining", "git-branch", "used-tokens", "total-input-tokens", "total-output-tokens", "weekly-limit"]`.

## Approach and risks

Apply the existing preference-reconcile patch as a starting point, then:

1. replace its line-local TOML table detector with a document scanner that
   carries multiline-string state across lines;
2. reparse the rendered output and assert every managed path reached its
   requested value;
3. add adversarial coverage for fake table headers and assignments inside
   unowned multiline strings;
4. keep the patch's `.gitignore` direction, but update every living owner that
   currently says host YAML snapshots are shared through Git;
5. add the two additional official-sample fields to the allowlist and tests.
6. support legal implicit parent tables such as `[tui.model_availability_nux]`
   by placing missing managed fields as root dotted keys before the first table.

The main risk is source-preserving TOML editing. Ambiguous syntax must fail
closed without writing any host target. A real Codex TUI smoke test remains a
manual host check and is not represented as a unit-test pass.

## Verification

- `make test`;
- shell syntax and Python byte compilation required by project guidance;
- parse all changed/generated TOML, JSON, and YAML fixtures;
- `git diff --check` and pre-commit whitelist verification;
- bootstrap twice with an isolated temporary HOME and compare managed hashes;
- verify a newly generated `.agents/env/<host>.yml` is ignored while
  `.agents/env/README.md` remains tracked/allowlisted.

## Handoff

The initial result is recorded in
`round4-codex-preferences-local-env-2026-08-20.changelog.md`; the real-host
compatibility correction is recorded in
`round5-codex-implicit-tables-2026-08-20.changelog.md`. All changes remain
uncommitted and unpublished for operator review.

## 2026-08-20 status-line extension

The operator requested per-session token-consumption detail in the interactive
Codex TUI. The managed `tui.status_line` therefore additionally includes
`used-tokens`, `total-input-tokens`, and `total-output-tokens`, while retaining
the model, remaining-context, and Git-branch items. The values are omitted by
Codex until they are available, and the real TUI rendering remains a manual
host check. Applying the result to `~/.codex/config.toml` still requires the
separate protected host-bootstrap action.

## 2026-08-20 weekly-limit extension

The operator also requested the `weekly-limit` status-line identifier. It is
appended after the per-session token counters, keeping the existing ordering
stable. The official configuration reference confirms that `tui.status_line`
is an ordered array of footer identifiers; visual availability remains a manual
host check.

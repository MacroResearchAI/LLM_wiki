---
name: wiki-lint
description: >-
  Run the wiki health check: script lint, then a semantic pass. Use when the
  user invokes /wiki-lint.
disable-model-invocation: true
---

# Wiki lint

Two layers. `./run.sh lint` catches mechanical issues. You catch what needs reading. Schema and the log format live in `AGENTS.md` and `doc/contract.md` (C1, C3, C4). Do not restate them. Do not edit `wiki/index.md` by hand.

Suggested cadence: after every 5–10 ingests, or before a review meeting. Invocation: `/wiki-lint`.

## Script pass

From the repo root run `./run.sh lint` (Windows: `./run.ps1 lint`). Do not call Python directly. Collect findings: broken links, orphans, frontmatter errors, pending raw sources, stale index, log format, duplicate slugs.

## Semantic pass

Read topic and entity pages. Look for:

- Contradictions between pages that are not yet under "Disagreements"
- Claims superseded by a newer source
- A concept mentioned on three or more pages that has no concept page
- Missing cross-references
- Data gaps a new source could fill

## Checkpoint — stop and wait for `proceed`

Present findings in three groups, then stop. Do not edit the wiki until the user replies `proceed` and names what to apply. They answer judgement calls and keep investigation items on their own backlog.

- **Fix now** — mechanical (script findings and obvious link or frontmatter repairs)
- **Propose** — needs judgement
- **Investigate** — new sources or open questions; do not invent sources

## Apply, then stop

After `proceed`, apply only the approved fixes, following `AGENTS.md` (strike through superseded claims; do not delete them).

Append one log entry matching C4:

```
## [YYYY-MM-DD] lint | <n> findings, <m> fixed
- fixed ...
- left for later ...

```

From the repo root run `./run.sh index`, then `./run.sh lint` (Windows: `./run.ps1`). Repeat until lint reports no errors.

Report changed files, the lint result, and a proposed commit message. Then stop. Do not `git add`, commit, or push until the user says `proceed`.

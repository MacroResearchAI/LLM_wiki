---
name: wiki-ingest
description: >-
  Ingest a raw source into the team wiki. Use when the user invokes
  /wiki-ingest with a path under raw/.
disable-model-invocation: true
---

# Wiki ingest

Add one source or note from `raw/` into `wiki/`. Schema, templates, naming, citation, and contradiction rules live in `AGENTS.md` and `doc/contract.md` (C1 frontmatter, C3 links, C4 log). Do not restate them. Do not modify `raw/`. Do not edit `wiki/index.md` by hand.

Invocation: `/wiki-ingest raw/<category>/<file>`. Optional emphasis from the user (for example "focus on the r-star estimate") narrows the claims you surface. Categories: `papers/`, `reports/`, `data/`, `speeches/`, `notes/`.

## Read order

1. Read `AGENTS.md`.
2. Read `wiki/index.md` for existing entity, concept, and topic pages. If the file is missing, treat the wiki as empty and say so.
3. Read the last five log headings: `grep "^## \[" wiki/log.md | tail -5`. If `wiki/log.md` is missing, say so and continue.
4. Read the raw source in full. Convert PDFs to markdown before reading. Then view each referenced image in `raw/assets/` one by one.
5. Search `wiki/sources/` for a page whose `raw:` key is this path. If one exists, stop and report the existing page. Do not write anything.

## Checkpoint — stop and wait for `proceed`

Present, then stop. Do not write pages until the user replies `proceed`. They may redirect ("skip methodology", "that is the ECB, not a new entity") or abort.

- 5–10 key claims
- Existing pages each claim will touch
- New pages proposed (paths and types)
- Contradictions with current wiki claims

## Write

After `proceed` only:

1. Create `wiki/sources/<filename>.md` using the source template in `AGENTS.md`. Frontmatter follows C1 (`type: source`, `raw:` set, no `sources:` key). Filename follows the source convention in C1. Body: bibliographic data, key claims each linked to the page they feed (C3 relative links), figures and data referenced, and a "Pages updated" list.
2. Create or update entity and concept pages per `AGENTS.md`. New pages get full C1 frontmatter. On existing pages, add the claim with a link to the new source page. Never delete a contradicting claim: strike it through with a note, or add it under "Disagreements".
3. Update topic pages: revise the thesis only if warranted, add supporting or contradicting evidence, update open questions. On every touched page, set `updated:` to today and append this source page to `sources:`.
4. Edit `wiki/overview.md` only if the source shifts the house view. Otherwise leave it.
5. Append one log entry matching C4:

```
## [YYYY-MM-DD] ingest | <Title>
- created ...
- updated ...
- contradictions: ...

```

## Check, then stop

From the repo root run `./run.sh index`, then `./run.sh lint` (Windows: `./run.ps1` with the same arguments). Do not call Python directly. Fix findings and re-run until lint reports no errors.

Report changed files, the lint result, a proposed branch name `wiki/<yyyy-mm-dd>-<slug>`, and a proposed commit message. Then stop. Do not `git add`, commit, or push until the user says `proceed`.

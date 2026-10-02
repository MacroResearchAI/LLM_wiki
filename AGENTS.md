# Wiki Schema and Agent Instructions

This file governs how the research wiki is maintained. `doc/contract.md` is the exact shared contract; if anything here conflicts with it, follow the contract and propose a synchronized correction to both documents.

## Layers and ownership

- `raw/` contains source material. Treat it as immutable: read and cite it, but do not edit or delete it during wiki work.
- `wiki/` contains Markdown knowledge pages maintained by the LLM. Use standard relative Markdown links with `.md` extensions.
- `wiki/index.md` is generated from page frontmatter. Run `./run.ps1 index`; do not hand-edit the index after the seed placeholder is established.
- `wiki/log.md` is append-only. Add a dated entry for each ingest, filed query, or lint pass; do not rewrite prior history.
- The schema lives here and in `doc/contract.md`. A schema change must be proposed and reflected in both documents in the same approved change.

## Page schema

Every page under `wiki/sources/`, `wiki/entities/`, `wiki/concepts/`, `wiki/topics/`, and `wiki/analyses/` begins with this YAML frontmatter, in this key order:

```yaml
---
type: source | institution | person | country | indicator | entity | concept | topic | analysis
title: "string"
summary: "string"
created: YYYY-MM-DD
updated: YYYY-MM-DD
tags: [kebab-case, kebab-case]
sources: [wiki/sources/<slug>.md]
raw: raw/<category>/<file>
---
```

Use exactly one allowed `type` value and no additional keys. `title` and `summary` are double-quoted; `summary` is one line and at most 200 characters. Dates use ISO `YYYY-MM-DD`, and `updated` must be on or after `created`. Tags use lowercase kebab-case slugs; an empty list is allowed. For `type: source`, include `raw:` and omit `sources:`. For every other type, include a non-empty `sources:` list of repository-root-relative source-page paths and omit `raw:`. Every declared path must exist.

| Directory | Allowed types | Index section |
|---|---|---|
| `wiki/sources/` | `source` | Sources |
| `wiki/entities/` | `institution`, `person`, `country`, `indicator`, `entity` | Entities |
| `wiki/concepts/` | `concept` | Concepts |
| `wiki/topics/` | `topic` | Topics |
| `wiki/analyses/` | `analysis` | Analyses |

`entity` means an unclassified entity and is an escape hatch, not a permanent type. When several such pages share a shape, propose a specific new type. Adding a type requires updating the contract, this file, and the tooling's type definitions through the owning workflow.

## Naming and links

- Source pages: `YYYY-MM-DD-<author>-<slug>.md`, using the source date.
- Analysis pages: `YYYY-MM-DD-<slug>.md`, using the query date.
- Other pages: `<slug>.md`, with a singular noun for entity pages.
- Slugs match `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Body links are relative to the linking file and include the `.md` extension. Do not use wikilinks, root-relative wiki links, or links to `raw/` from a page body.
- Cite the source page for factual claims in entity, concept, topic, and analysis pages. Keep `sources:` aligned with the source pages used.

## Page templates

Keep these sections unless they genuinely do not apply; add useful detail without changing required frontmatter.

### Source

Use `## Bibliographic` for author, venue, date, and raw path; `## Key claims` for numbered, atomic claims, each linked to the page it informs; `## Figures and data` for referenced material; and `## Pages updated` for created or updated pages.

### Entity

Use `## Overview`, `## Positions and statements`, `## Related`, and `## Disagreements`. Cite sources for dated statements. This template applies to institutions, people, countries, indicators, and unclassified entities.

### Concept

Use `## Definition`, `## Evidence`, `## Used by`, and `## Disagreements`. Keep the definition concise and cite evidence.

### Topic

Use `## Thesis`, `## Supporting evidence`, `## Contradicting evidence`, `## Open questions`, and `## Related analyses`. Revise the thesis when evidence warrants it and preserve contrary evidence.

### Analysis

Use `## Question`, `## Answer`, `## Gaps`, and `## Pages consulted`. Distinguish what the wiki supports from what it does not establish, and cite the pages used.

## Citations and disagreements

Do not silently delete or rewrite a contradicted claim. Preserve the prior position with a brief supersession note or record both positions under `## Disagreements`, with links to their sources. Update `updated:` and `sources:` whenever a page changes because of a new source. Keep source claims traceable to `wiki/sources/` and, through that page's `raw:` field, to the immutable original.

## Workflows

### Ingest: `/wiki-ingest`

1. Read `wiki/index.md`, the five most recent `wiki/log.md` entries, and the raw source in full. Inspect referenced assets after reading the text; do not modify files in `raw/`.
2. Search `wiki/sources/` for the raw path. If already cited, stop and report the existing source page.
3. Present 5-10 key claims, pages to touch, proposed new pages, and possible contradictions. Stop and wait for the human's `proceed` before writing.
4. Create the source page, update or create linked entity/concept/topic pages, and edit `wiki/overview.md` only if the house view changes. Append a C4 ingest entry to `wiki/log.md`.
5. Run `./run.ps1 index`, then `./run.ps1 lint`; fix findings within the approved scope and rerun checks. Report changed files and a proposed commit message. Wait for approval before git operations.

### Query: `/wiki-query`

1. Read `wiki/index.md`, select relevant pages, and consult their source pages for claim provenance. Read `raw/` only if the wiki pages do not answer the question.
2. Answer with links to the wiki pages relied on, and state explicitly where the wiki has no evidence.
3. If asked to file the answer, create a dated analysis page with `type: analysis`, link consulted sources, add a backlink from the relevant topic page, and append a C4 query entry to `wiki/log.md`.
4. For a filed answer, run `./run.ps1 index` and `./run.ps1 lint`, report the result, and wait for approval before git operations. A chat-only answer does not create a branch or modify files.

### Lint: `/wiki-lint`

1. Run `./run.ps1 lint` and report mechanical findings.
2. Review entity and topic pages for unrecorded contradictions, superseded claims, missing cross-links, concepts that may need their own page, and evidence gaps.
3. Group findings as fix now, propose, or investigate. Stop for human approval before applying semantic fixes.
4. Apply approved fixes, append a C4 lint entry to `wiki/log.md`, then run `./run.ps1 index` and `./run.ps1 lint` until clean.
5. Report changed files and results; wait for approval before git operations.

## Git and review

Use a focused branch, normally `wiki/<YYYY-MM-DD>-<slug>` for wiki work. Submit changes through a pull request to `main`. Propose branch and commit details before acting; never run `git add`, `git commit`, `git push`, or merge without the user's explicit `proceed`. A reviewer should compare the source page with its raw material and inspect all affected synthesis pages.

---
name: wiki-query
description: >-
  Answer a question from the team wiki with citations. Use when the user
  invokes /wiki-query. With --file, file the answer under wiki/analyses/.
disable-model-invocation: true
---

# Wiki query

Answer from the wiki. Schema, the analysis template, citation rules, and the log format live in `AGENTS.md` and `doc/contract.md` (C1, C3, C4). Do not restate them. Do not edit `wiki/index.md` by hand.

Invocation: `/wiki-query <question>`. Add `--file` only when the answer should be saved.

## Read order

1. Read `wiki/index.md` and select candidate pages. If the index is missing, say the wiki has no catalogue yet and stop.
2. Read those pages. When a claim needs its origin, read the linked `wiki/sources/` page.
3. Do not read `raw/` unless a wiki page is insufficient to answer. If you must, say so and record it as a lint finding (a gap the wiki should have covered).

## Answer, then stop

Answer in chat. Cite the wiki pages you used with C3 relative links. State explicitly where the wiki has no evidence.

If the user did not pass `--file`, stop here. Do not write files and do not use git.

If they passed `--file`, still show the answer first, then continue only after they say `proceed` (or they already included `--file`, which is approval to file). If they say not to keep it, stop with no git activity.

## File (`--file` only)

1. Create `wiki/analyses/<YYYY-MM-DD>-<slug>.md` using the analysis template in `AGENTS.md`. Frontmatter follows C1 (`type: analysis`, non-empty `sources:`). Body: the question, the answer, and the pages consulted.
2. Add backlinks from the relevant topic pages to this analysis. On each touched page, set `updated:` to today and append the analysis's source pages to `sources:` if they are not already listed.
3. Append one log entry matching C4:

```
## [YYYY-MM-DD] query | <Question>
- filed analyses/<YYYY-MM-DD>-<slug>.md
- consulted ...
- gap: ...

```

4. From the repo root run `./run.sh index`, then `./run.sh lint` (Windows: `./run.ps1` with the same arguments). Fix findings and re-run until lint reports no errors.
5. Report changed files, the lint result, and a proposed commit message. Then stop. Do not `git add`, commit, or push until the user says `proceed`.

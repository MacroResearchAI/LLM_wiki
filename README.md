# Macro Research Wiki

This repository keeps research material in two linked layers: immutable originals in `raw/` and cited, structured Markdown pages in `wiki/`. The schema and working rules are in [AGENTS.md](AGENTS.md); the end-to-end human and agent procedures are in [doc/workflows.md](doc/workflows.md).

## Add a source

1. Save the source under the appropriate `raw/` category using the naming rules in [raw/README.md](raw/README.md). Do not edit or rename a raw file after adding it. A PDF, including a scan, can be ingested as it is.
2. From the current checkout, often `main`, run `/wiki-ingest raw/<category>/<file>` in Cursor. The skill checks the catalogue, reads the source, and stops. It presents the claims, the pages it would create or update, and any contradictions. It does not create a branch and it does not write pages yet.
3. Review that proposal. Reply `proceed` to write, or redirect the page list. After `proceed`, the skill writes the pages, appends `wiki/log.md`, and runs `./run.ps1 index` then `./run.ps1 lint`. It then stops with a proposed branch name `wiki/<date>-<slug>` and a commit message. It does not commit.
4. If the checkout is still `main`, create that branch before committing. The new wiki files are uncommitted, so they stay in the working tree and move onto the new branch. `main` does not receive them until a pull request is merged.
5. Review the source page against the raw material and inspect each touched topic or entity page. Check that new claims link to their source pages, and that index and lint already succeeded.
6. Reply `proceed` to commit on `wiki/<date>-<slug>`. Push the branch when you want it on GitHub, then open a pull request to `main`.

## Ask a question

1. In Cursor, run `/wiki-query <question>`. The skill reads `wiki/index.md`, then the pages that bear on the question, and the linked source pages when a claim needs its origin. It does not read `raw/` unless those wiki pages are not enough to answer, and if it must, it says so.
2. It answers in chat, with links to the wiki pages it used, and it states where the wiki has no evidence. Without `--file`, it stops there. No files are written and no git commands are run.
3. Add `--file` only when the answer should be saved. For example: `/wiki-query What does the wiki say about the real exchange rate? --file`. The skill still shows the answer first. `--file` is the approval to file it. If you omit `--file` and later want the answer kept, say so. If you do not want it kept, stop.
4. Filing creates `wiki/analyses/<date>-<slug>.md`, adds a backlink from the relevant topic page, appends a query entry to `wiki/log.md`, and runs `./run.ps1 index` then `./run.ps1 lint`. The skill then stops with the changed files, the lint result, and a proposed commit message. It does not commit.
5. If the checkout is still `main`, create `wiki/<date>-<slug>` before committing, as in an ingest. Reply `proceed` to commit on that branch. Push when you want it on GitHub, then open a pull request to `main`.

## Review a pull request

- Confirm every factual claim added to a synthesis page has a source-page citation.
- Check that disagreements are recorded rather than silently resolved and that `updated:` and `sources:` reflect page changes.
- Follow relative links and verify that source pages point to existing raw files.
- Check the generated index, append-only log entry, and lint result.
- Spot-check source-page claims against the immutable raw material before merging.

Raw research material is not published as part of the wiki site. Never add copyrighted source text to a public-facing page beyond what is necessary for analysis and citation.

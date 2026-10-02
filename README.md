# Macro Research Wiki

This repository keeps research material in two linked layers: immutable originals in `raw/` and cited, structured Markdown pages in `wiki/`. The schema and working rules are in [AGENTS.md](AGENTS.md); the end-to-end human and agent procedures are in [doc/workflows.md](doc/workflows.md).

## Add a source

1. Save the source under the appropriate `raw/` category using the naming rules in [raw/README.md](raw/README.md). Do not edit a raw file after adding it.
2. Start a focused `wiki/<date>-<slug>` branch, or explicitly approve the agent's branch proposal.
3. Run `/wiki-ingest raw/<category>/<file>` in Cursor. Review the proposed claims, page updates, and contradictions, then approve with `proceed` before wiki edits are made.
4. Review the source page against the raw material and inspect each touched topic or entity page. Check that new claims link to their source pages.
5. Confirm `./run.ps1 index` and `./run.ps1 lint` succeed. Review the diff, then approve any git operations and open a pull request to `main`.

## Review a pull request

- Confirm every factual claim added to a synthesis page has a source-page citation.
- Check that disagreements are recorded rather than silently resolved and that `updated:` and `sources:` reflect page changes.
- Follow relative links and verify that source pages point to existing raw files.
- Check the generated index, append-only log entry, and lint result.
- Spot-check source-page claims against the immutable raw material before merging.

Raw research material is not published as part of the wiki site. Never add copyrighted source text to a public-facing page beyond what is necessary for analysis and citation.

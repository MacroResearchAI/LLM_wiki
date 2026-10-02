# Raw Source Archive

`raw/` holds original or clipped source material used to support the wiki. Files in this layer are immutable after addition: do not edit, rename, or delete them as part of wiki maintenance. If a correction or new edition is needed, add a separately named file and distinguish it in the wiki source page.

## Categories

- `papers/`: academic and working papers.
- `reports/`: institutional, policy, and research reports.
- `data/`: datasets, tables, and other data files.
- `speeches/`: speeches and prepared remarks.
- `notes/`: original team notes and research memos.
- `assets/`: images or other assets referenced by a raw source.

Put a source in the narrowest appropriate category. Name source files `YYYY-MM-DD-<author>-<slug>.<ext>`, using the source date and a lowercase kebab-case slug. For example: `speeches/2026-09-20-powell-jackson-hole.md`. Asset names should be descriptive and stable; keep them in `assets/`.

Every ingested source needs a page under `wiki/sources/` whose `raw:` frontmatter path points to the file. Wiki pages cite that source page, not a direct body link to `raw/`.

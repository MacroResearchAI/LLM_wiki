# Wiki workflows

How knowledge enters, is queried from, and is maintained in this repository. Three workflows: **ingest**, **query**, **lint**. Each row states who acts (Human, LLM, Script, or CI) and which document governs the step.

Governing documents:

| Document | Role |
|---|---|
| `AGENTS.md` | The schema. Directory rules, page templates, frontmatter spec, naming, citation and contradiction conventions. Loaded automatically by Cursor in every session. |
| `.cursor/skills/wiki-ingest/SKILL.md` | Step-by-step ingest procedure. Loaded when `/wiki-ingest` is invoked. |
| `.cursor/skills/wiki-query/SKILL.md` | Step-by-step query procedure. Loaded when `/wiki-query` is invoked. |
| `.cursor/skills/wiki-lint/SKILL.md` | Step-by-step semantic lint procedure. Loaded when `/wiki-lint` is invoked. |
| `raw/README.md` | Rules for the raw layer: immutable, file naming. |
| `wiki/index.md` | Generated catalogue of all pages. The LLM reads it first to navigate; never edited by hand. |
| `wiki/log.md` | Append-only chronological record of ingests, queries, lint passes. |
| `scripts/wiki/build_index.py` | Regenerates `wiki/index.md` from page frontmatter. `--check` verifies without writing. |
| `scripts/wiki/lint.py` | Deterministic structural checks. Exit code 1 when any finding is an error. Warnings alone leave the exit code at 0. |
| `.github/workflows/lint.yml` | Runs `lint.py` and `build_index.py --check` on every pull request. |
| `.github/workflows/pages.yml` | Builds and deploys the MkDocs site when `main` changes. |

Local wrapper: `./run.ps1 <index|lint|serve|test>` (or `./run.sh` on Unix).

---

## 1. Ingest: adding a source or note

Applies to any new material: paper, report, speech, data file, or your own written note. Your own notes go through the same path so that every claim in `wiki/` remains traceable to a file in `raw/`.

### Phase A. Human prepares the source

| # | Who | Governed by | Step |
|---|---|---|---|
| 1 | Human | `raw/README.md` | Save the file into `raw/<category>/` named `yyyy-mm-dd-<author>-<slug>.<ext>`. Categories: `papers/`, `reports/`, `data/`, `speeches/`, `notes/`. Images referenced by the source go in `raw/assets/`. Web articles: clip to markdown first. |
| 2 | Human | `AGENTS.md` (git section) | Create branch `wiki/<yyyy-mm-dd>-<slug>`, or approve the LLM's proposal to create it. |
| 3 | Human | – | In Cursor: `/wiki-ingest raw/<category>/<file>`. Optionally add emphasis, e.g. "focus on the r-star estimate and its conflict with the HLW page". |

### Phase B. LLM reads and orients

| # | Who | Governed by | Step |
|---|---|---|---|
| 4 | LLM | `SKILL.md` | Load `AGENTS.md` (automatic) and the ingest skill. |
| 5 | LLM | `SKILL.md` | Read `wiki/index.md` to learn existing entity/concept/topic pages. Read the last five entries of `wiki/log.md` (`grep "^## \[" wiki/log.md | tail -5`). |
| 6 | LLM | `SKILL.md`, `AGENTS.md` (image rule) | Read the raw source text in full. View any referenced images in `raw/assets/` afterwards, one by one. PDFs are converted to markdown before reading. |
| 7 | LLM | `SKILL.md` | Verify the source is not already ingested: search `wiki/sources/` for the raw path. If a page already cites it, stop and report. |

### Phase C. Human checkpoint

| # | Who | Governed by | Step |
|---|---|---|---|
| 8 | LLM | `SKILL.md` | Present: 5-10 key claims; existing pages each claim will touch; new pages proposed; contradictions with current wiki claims. Then wait. |
| 9 | Human | – | Approve with `proceed`, redirect ("skip methodology", "that is the ECB, not a new entity"), or abort. This is the main steering point. |

### Phase D. LLM writes the wiki

| # | Who | Governed by | Step |
|---|---|---|---|
| 10 | LLM | `AGENTS.md` (source template, frontmatter spec) | Create `wiki/sources/<slug>.md`. Frontmatter: `type: source`, `title`, `summary`, `created`, `updated`, `raw`, `tags`. Body: bibliographic data, key claims each linked to the page it feeds, figures and data referenced, "Pages updated" list. |
| 11 | LLM | `AGENTS.md` (entity/concept templates, naming) | Create or update entity and concept pages. New pages receive full frontmatter. Existing pages: add the claim with a link to the new source page. A contradicting claim is never deleted: strike through the superseded text with a note, or add to the page's "Disagreements" section. |
| 12 | LLM | `AGENTS.md` (topic template) | Update topic pages: revise thesis if warranted, add to supporting or contradicting evidence, update open questions. On every touched page bump `updated:` and append to `sources:`. |
| 13 | LLM | `AGENTS.md` (overview rule) | Edit `wiki/overview.md` only if the source shifts the house view. |
| 14 | LLM | `AGENTS.md` (log format) | Append to `wiki/log.md`: `## [yyyy-mm-dd] ingest | <Title>` followed by bullets: pages created, pages updated, contradictions flagged. |

### Phase E. Deterministic checks

| # | Who | Governed by | Step |
|---|---|---|---|
| 15 | Script (run by LLM) | `build_index.py` | `./run.ps1 index` regenerates `wiki/index.md` from frontmatter. |
| 16 | Script (run by LLM) | `lint.py` | `./run.ps1 lint` checks broken links, orphan pages, missing or invalid frontmatter, pending raw sources, stale index, log entry format, duplicate slugs. LLM fixes findings and re-runs until lint reports no errors. Warnings do not fail the command. |
| 17 | LLM | `SKILL.md` | Report changed files, lint result, and a proposed commit message. Wait. |

### Phase F. Human reviews and ships

| # | Who | Governed by | Step |
|---|---|---|---|
| 18 | Human | – | Review the diff in Cursor's source-control view or `git diff`. Spot-check the source page against the raw document. |
| 19 | Human | user git rule | Say `proceed` for `git add`, `git commit`, `git push`, or run them yourself. |
| 20 | Human | – | Open a pull request from `wiki/<date>-<slug>` into `main`. |
| 21 | CI | `lint.yml` | GitHub Actions runs `lint.py` and `build_index.py --check` on the PR. Red check blocks merge until the branch is fixed and pushed again. |
| 22 | Human (reviewer) | `README.md` review checklist | A teammate reads the source page and touched topic pages, then merges. |
| 23 | CI | `pages.yml` | MkDocs rebuilds and deploys. The team browses the updated site. |

Mandatory human touchpoints: steps 1-3, 9, 18-20, 22. Everything else is LLM or script.

---

## 2. Query: asking a question and filing the answer

| # | Who | Governed by | Step |
|---|---|---|---|
| 1 | Human | – | In Cursor: `/wiki-query <question>`. Add `--file` if the answer should be saved to the wiki. |
| 2 | LLM | `SKILL.md` | Read `wiki/index.md`; select candidate pages; read them. Consult `wiki/sources/` pages where a claim needs its origin. Do not read `raw/` unless a wiki page is insufficient; if it is, note that as a lint finding. |
| 3 | LLM | `AGENTS.md` (citation convention) | Answer in chat with links to the wiki pages relied on. State explicitly where the wiki has no evidence. |
| 4 | Human | – | Decide whether the answer is worth keeping. If it was not requested with `--file`, say so now. |
| 5 | LLM | `AGENTS.md` (analysis template) | If filing: create `wiki/analyses/<yyyy-mm-dd>-<slug>.md` with frontmatter `type: analysis`, the question, the answer, pages consulted. Add backlinks from the relevant topic pages. Append `## [yyyy-mm-dd] query | <Question>` to `wiki/log.md`. |
| 6 | Script (run by LLM) | `build_index.py`, `lint.py` | `./run.ps1 index` then `./run.ps1 lint`. |
| 7 | Human | user git rule | Same as ingest Phase F: review, approve git operations, PR, CI, merge. Chat-only answers (no `--file`) end at step 3 with no git activity. |

---

## 3. Lint: periodic health check

Two layers. The script catches what is mechanically checkable; the LLM catches what needs reading.

| # | Who | Governed by | Step |
|---|---|---|---|
| 1 | Human | – | In Cursor: `/wiki-lint`. Suggested cadence: after every 5-10 ingests, or before a review meeting. |
| 2 | Script (run by LLM) | `lint.py` | `./run.ps1 lint`. Findings: broken links, orphans, frontmatter errors, pending raw sources, stale index, log format, duplicate slugs. |
| 3 | LLM | `SKILL.md`, `AGENTS.md` | Semantic pass over topic and entity pages: contradictions between pages not yet recorded under "Disagreements"; claims superseded by newer sources; concepts mentioned on three or more pages without their own page; missing cross-references; data gaps a new source could fill. |
| 4 | LLM | `SKILL.md` | Present findings grouped as: fix now (mechanical), propose (needs judgement), investigate (new sources or questions). Wait. |
| 5 | Human | – | Approve the fix list; answer judgement calls; add investigation items to your own backlog. |
| 6 | LLM | `AGENTS.md` | Apply approved fixes. Append `## [yyyy-mm-dd] lint | <n> findings, <m> fixed` to `wiki/log.md` with bullets. |
| 7 | Script (run by LLM) | `build_index.py`, `lint.py` | `./run.ps1 index` then `./run.ps1 lint` until lint reports no errors. Warnings do not fail the command. |
| 8 | Human | user git rule | Review, approve git operations, PR, CI, merge. |

---

## Glossary

**Branch** — an isolated line of history in git. Each session works on `wiki/<date>-<slug>` so `main` only changes through review.

**Pull request (PR)** — a GitHub page requesting that a branch be merged into `main`. Shows the diff, hosts comments, and displays check results. `main` does not change until someone clicks Merge.

**CI (continuous integration)** — scripts GitHub runs automatically on its own servers when something happens in the repo. Configured by files in `.github/workflows/`. Requires no setup on the GitHub side beyond committing those files.

**`lint.py` vs `lint.yml`** — `lint.py` is the tool: the Python script that performs the checks. `lint.yml` is the instruction: it tells GitHub to run `lint.py` on every PR. The same `lint.py` runs locally via `./run.ps1 lint`.

**`build_index.py --check`** — regenerates the index in memory and compares it to the committed `wiki/index.md`. Exits non-zero if they differ. Used in CI so that CI verifies but never writes.

**Pending source** — a file in `raw/` that no page in `wiki/sources/` cites. Computed by `lint.py`, never recorded as a flag, so it cannot drift out of sync.

**Orphan page** — a wiki page with no inbound links from any page other than `index.md` and `log.md`. Usually means a cross-reference was forgotten during ingest.

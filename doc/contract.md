# Shared contract

This document is the single interface between the four parallel workstreams (schema, tooling, skills, CI/site). It is exact, not descriptive. Where this file and any other document disagree, this file wins until it is amended; amendments happen only on `main` and must be mirrored into `AGENTS.md` in the same commit.

Definitions used throughout:

- **Repo root**: the directory containing this `doc/` folder. All scripts run with repo root as the current working directory.
- **Page**: any `.md` file under `wiki/` except the special files `wiki/index.md`, `wiki/log.md`, `wiki/overview.md`, and `wiki/graph.md`. Pages must have frontmatter. Special files must not.
- **Slug**: a page filename without `.md`, matching `^[a-z0-9]+(-[a-z0-9]+)*$`.

## C0. Directory tree

Fixed. Agents add files inside these directories and never create new top-level entries.

```
AGENTS.md                 # Agent 1
README.md                 # Agent 1
.gitignore                # Phase 0
pyproject.toml            # Phase 0
uv.lock                   # Phase 0
run.ps1  run.sh           # Agent 2
mkdocs.yml                # Agent 4
doc/                      # Phase 0 (contract, workflows); Agent 4 adds hosting.md
raw/                      # immutable sources; README.md by Agent 1
  papers/  reports/  data/  speeches/  notes/  assets/
wiki/                     # LLM-owned pages; seeds by Agent 1
  sources/  entities/  concepts/  topics/  analyses/
  index.md  log.md  overview.md
scripts/wiki/             # Agent 2
tests/                    # Agent 2
  fixtures/
.cursor/skills/           # Agent 3
.github/workflows/        # Agent 4
```

## C1. Frontmatter

Every page begins with a YAML block delimited by `---` lines. Keys, in this order:

```yaml
---
type: source | institution | person | country | indicator | entity | concept | topic | analysis
title: "string"                            # always double-quoted
summary: "string"                          # always double-quoted; one line; <= 200 characters
created: YYYY-MM-DD
updated: YYYY-MM-DD                        # >= created
tags: [kebab-case, kebab-case]             # may be []
sources: [wiki/sources/<slug>.md]          # required for every type except source; must be non-empty; absent for source
raw: raw/<category>/<file>                 # required for source only; absent otherwise
---
```

Rules:

- Exactly one `type` value. No other keys are permitted; unknown keys are a lint `error`.
- `sources` and `raw` are repo-root-relative paths and must exist on disk.
- `title` and `summary` are always double-quoted in YAML to avoid colon and quote parsing failures.
- `tags` values match the slug regex.

### Type groups and directories

| Directory | Allowed `type` values | Index section |
|---|---|---|
| `wiki/sources/` | `source` | Sources |
| `wiki/entities/` | `institution`, `person`, `country`, `indicator`, `entity` | Entities |
| `wiki/concepts/` | `concept` | Concepts |
| `wiki/topics/` | `topic` | Topics |
| `wiki/analyses/` | `analysis` | Analyses |

`entity` means *unclassified entity*. It is an escape hatch, not a permanent home: lint emits a `warning`, and `AGENTS.md` instructs the LLM to propose a new type when several `entity` pages share a shape. Adding a type requires editing this table, `AGENTS.md`, and `ENTITY_TYPES` / `ALLOWED_TYPES` in `scripts/wiki/common.py`.

### Filename conventions

| Type | Filename |
|---|---|
| `source` | `YYYY-MM-DD-<author>-<slug>.md` (date of the source, not of ingest) |
| `analysis` | `YYYY-MM-DD-<slug>.md` (date of the query) |
| all others | `<slug>.md`, singular noun |

## C2. Example pages

Five complete pages plus the raw file they cite. These are illustrative and internally consistent: every link resolves within the set, every `sources:` and `raw:` path exists. Agent 1 uses them as the seed content on `main`; Agent 2 copies them verbatim into `tests/fixtures/clean/`.

### `raw/speeches/2026-09-20-powell-jackson-hole.md`

````markdown
# Remarks at the Jackson Hole Economic Symposium (illustrative stub)

Jerome H. Powell, 2026-09-20.

This is a placeholder standing in for the clipped speech text. The real file would contain the full remarks as markdown.

Key passages referenced by the wiki:

- "With the policy rate now close to most estimates of neutral, the Committee is in a position to wait for further data."
- "Estimates of the neutral rate remain highly uncertain and have drifted upward since the pandemic."
````

### `wiki/sources/2026-09-20-powell-jackson-hole.md`

````markdown
---
type: source
title: "Powell, Jackson Hole remarks (2026-09-20)"
summary: "Powell describes the policy rate as close to neutral and signals a data-dependent pause; notes neutral-rate estimates have drifted upward."
created: 2026-09-21
updated: 2026-09-21
tags: [fed, neutral-rate, speech]
raw: raw/speeches/2026-09-20-powell-jackson-hole.md
---

# Powell, Jackson Hole remarks (2026-09-20)

## Bibliographic

- Author: Jerome H. Powell, Chair, [Federal Reserve](../entities/federal-reserve.md)
- Venue: Jackson Hole Economic Symposium
- Date: 2026-09-20
- Raw file: `raw/speeches/2026-09-20-powell-jackson-hole.md`

## Key claims

1. The policy rate is close to most estimates of the [neutral rate](../concepts/neutral-rate.md). Feeds [US monetary policy stance](../topics/us-monetary-policy-stance.md).
2. The Committee can wait for further data before adjusting policy. Feeds [US monetary policy stance](../topics/us-monetary-policy-stance.md).
3. Neutral-rate estimates are uncertain and have drifted upward since the pandemic. Feeds [neutral rate](../concepts/neutral-rate.md).

## Figures and data

None.

## Pages updated

- [Federal Reserve](../entities/federal-reserve.md) (created)
- [Neutral rate](../concepts/neutral-rate.md) (created)
- [US monetary policy stance](../topics/us-monetary-policy-stance.md) (created)
````

### `wiki/entities/federal-reserve.md`

````markdown
---
type: institution
title: "Federal Reserve"
summary: "US central bank; sets the federal funds rate through the FOMC."
created: 2026-09-21
updated: 2026-09-21
tags: [fed, central-bank, united-states]
sources: [wiki/sources/2026-09-20-powell-jackson-hole.md]
---

# Federal Reserve

## Overview

The Federal Reserve System is the central bank of the United States. Monetary policy is set by the Federal Open Market Committee (FOMC).

## Positions and statements

- 2026-09-20: Chair Powell described the policy rate as close to [neutral](../concepts/neutral-rate.md) and signalled a data-dependent pause. Source: [Powell, Jackson Hole remarks](../sources/2026-09-20-powell-jackson-hole.md).

## Related

- Topic: [US monetary policy stance](../topics/us-monetary-policy-stance.md)

## Disagreements

None recorded.
````

### `wiki/concepts/neutral-rate.md`

````markdown
---
type: concept
title: "Neutral rate"
summary: "The real policy rate consistent with output at potential and stable inflation; unobserved and estimated with wide uncertainty."
created: 2026-09-21
updated: 2026-09-21
tags: [neutral-rate, r-star, monetary-policy]
sources: [wiki/sources/2026-09-20-powell-jackson-hole.md]
---

# Neutral rate

## Definition

The neutral (or natural) rate of interest, often written r*, is the real short-term interest rate at which monetary policy is neither expansionary nor contractionary.

## Evidence

- Estimates have drifted upward since the pandemic and remain highly uncertain. Source: [Powell, Jackson Hole remarks](../sources/2026-09-20-powell-jackson-hole.md).

## Used by

- [Federal Reserve](../entities/federal-reserve.md) as a benchmark for the policy stance.
- [US monetary policy stance](../topics/us-monetary-policy-stance.md).

## Disagreements

None recorded.
````

### `wiki/topics/us-monetary-policy-stance.md`

````markdown
---
type: topic
title: "US monetary policy stance"
summary: "Evolving assessment of whether US policy is restrictive, neutral, or accommodative, and where the Fed signals it is heading."
created: 2026-09-21
updated: 2026-09-21
tags: [fed, monetary-policy, united-states]
sources: [wiki/sources/2026-09-20-powell-jackson-hole.md]
---

# US monetary policy stance

## Thesis

As of September 2026 the [Federal Reserve](../entities/federal-reserve.md) regards the policy rate as close to the [neutral rate](../concepts/neutral-rate.md) and intends to hold pending data.

## Supporting evidence

- Powell: policy rate "close to most estimates of neutral"; Committee "in a position to wait". Source: [Powell, Jackson Hole remarks](../sources/2026-09-20-powell-jackson-hole.md).

## Contradicting evidence

None recorded.

## Open questions

- Which neutral-rate estimate does the FOMC weight most heavily?
- How would an upward revision to r* change the stated stance?

## Related analyses

- [Fed vs ECB neutral-rate framing](../analyses/2026-09-21-fed-vs-ecb-neutral-rate.md)
````

### `wiki/analyses/2026-09-21-fed-vs-ecb-neutral-rate.md`

````markdown
---
type: analysis
title: "Fed vs ECB neutral-rate framing"
summary: "Compares how the Fed frames neutral in its 2026-09-20 remarks with what the wiki holds about the ECB; the wiki has no ECB source yet."
created: 2026-09-21
updated: 2026-09-21
tags: [fed, ecb, neutral-rate, comparison]
sources: [wiki/sources/2026-09-20-powell-jackson-hole.md]
---

# Fed vs ECB neutral-rate framing

## Question

How does the Fed's current framing of the neutral rate compare with the ECB's?

## Answer

The [Federal Reserve](../entities/federal-reserve.md) currently frames the policy rate as close to [neutral](../concepts/neutral-rate.md) and emphasises upward drift and uncertainty in the estimate. Source: [Powell, Jackson Hole remarks](../sources/2026-09-20-powell-jackson-hole.md).

The wiki holds no ECB source. A comparison cannot be made until one is ingested.

## Gaps

- No ECB page or source exists. Candidate source: the most recent ECB Monetary Policy Statement.

## Pages consulted

- [US monetary policy stance](../topics/us-monetary-policy-stance.md)
- [Neutral rate](../concepts/neutral-rate.md)
````

## C3. Links

Body links are standard markdown, relative to the linking file's directory, and include the `.md` extension:

```markdown
[Federal Reserve](../entities/federal-reserve.md)
```

Not permitted: `[[wikilinks]]`, repo-root-relative body links (`/wiki/...`), links without `.md`, links to `raw/` from any page other than via the `raw:` frontmatter key.

Frontmatter paths (`sources:`, `raw:`) are repo-root-relative, as shown in C1.

External `http(s)://` links are permitted and are not checked by lint.

## C4. Log

`wiki/log.md` is append-only and chronological (oldest first). The file begins with `# Log`, a blank line, then entries. Each entry is:

```
## [YYYY-MM-DD] <kind> | <title>
- bullet
- bullet

```

where `<kind>` is one of `ingest`, `query`, `lint`. Heading regex, applied to every line beginning with `## `:

```
^## \[\d{4}-\d{2}-\d{2}\] (ingest|query|lint) \| .+$
```

At least one bullet per entry; one blank line between entries; file ends with a single newline. Example:

```markdown
# Log

## [2026-09-21] ingest | Powell, Jackson Hole remarks (2026-09-20)
- created sources/2026-09-20-powell-jackson-hole.md
- created entities/federal-reserve.md, concepts/neutral-rate.md, topics/us-monetary-policy-stance.md
- contradictions: none

## [2026-09-21] query | How does the Fed's neutral-rate framing compare with the ECB's?
- filed analyses/2026-09-21-fed-vs-ecb-neutral-rate.md
- consulted topics/us-monetary-policy-stance.md, concepts/neutral-rate.md
- gap: no ECB source
```

Useful one-liner: `grep "^## \[" wiki/log.md | tail -5`.

## C5. Index

`wiki/index.md` is generated by `scripts/wiki/build_index.py` and never edited by hand. Output is byte-exact and defined by this template. `\n` line endings; file ends with exactly one `\n`.

```
# Index

_Generated by scripts/wiki/build_index.py. Do not edit._

## Topics

- [<title>](topics/<slug>.md) — <summary> (updated <updated>, <N> sources)

## Entities

### Institutions

- [<title>](entities/<slug>.md) — <summary> (updated <updated>, <N> sources)

### People

- ...

### Countries

- ...

### Indicators

- ...

### Unclassified

- ...

## Concepts

- [<title>](concepts/<slug>.md) — <summary> (updated <updated>, <N> sources)

## Analyses

- [<title>](analyses/<slug>.md) — <summary> (updated <updated>, <N> sources)

## Sources

- [<title>](sources/<slug>.md) — <summary> (updated <updated>)
```

Rules:

- Section order fixed: Topics, Entities, Concepts, Analyses, Sources.
- Entity sub-section order fixed: Institutions (`institution`), People (`person`), Countries (`country`), Indicators (`indicator`), Unclassified (`entity`). Empty sub-sections are omitted entirely.
- A top-level section with no pages emits its heading followed by a blank line and the line `_None._`.
- Within a (sub-)section, entries sorted by `title` using Python default string ordering (case-sensitive, codepoint order).
- `<N>` is `len(sources)`; the word is always `sources`, even when N is 1.
- The separator between link and summary is ` — ` (space, U+2014, space).
- Exactly one blank line between any two consecutive non-blank structural lines (heading to list, list to heading, heading to sub-heading).

Byte-exact expected output for the C2 example set:

```
# Index

_Generated by scripts/wiki/build_index.py. Do not edit._

## Topics

- [US monetary policy stance](topics/us-monetary-policy-stance.md) — Evolving assessment of whether US policy is restrictive, neutral, or accommodative, and where the Fed signals it is heading. (updated 2026-09-21, 1 sources)

## Entities

### Institutions

- [Federal Reserve](entities/federal-reserve.md) — US central bank; sets the federal funds rate through the FOMC. (updated 2026-09-21, 1 sources)

## Concepts

- [Neutral rate](concepts/neutral-rate.md) — The real policy rate consistent with output at potential and stable inflation; unobserved and estimated with wide uncertainty. (updated 2026-09-21, 1 sources)

## Analyses

- [Fed vs ECB neutral-rate framing](analyses/2026-09-21-fed-vs-ecb-neutral-rate.md) — Compares how the Fed frames neutral in its 2026-09-20 remarks with what the wiki holds about the ECB; the wiki has no ECB source yet. (updated 2026-09-21, 1 sources)

## Sources

- [Powell, Jackson Hole remarks (2026-09-20)](sources/2026-09-20-powell-jackson-hole.md) — Powell describes the policy rate as close to neutral and signals a data-dependent pause; notes neutral-rate estimates have drifted upward. (updated 2026-09-21)
```

## C6. Wrapper interface

`run.ps1` (Windows) and `run.sh` (Unix) are identical in behaviour. Invoked from repo root.

| Command | Runs | Exit code |
|---|---|---|
| `./run.ps1 index` | `uv run python scripts/wiki/build_index.py` | 0 on success |
| `./run.ps1 index --check` | `uv run python scripts/wiki/build_index.py --check` | 0 if `wiki/index.md` is up to date, 1 if stale (prints unified diff) |
| `./run.ps1 lint` | `uv run python scripts/wiki/lint.py` | 0 if no `error` findings, 1 otherwise |
| `./run.ps1 serve` | `uv run mkdocs serve` | passthrough |
| `./run.ps1 test` | `uv run pytest` | passthrough |

Rules:

- Any additional arguments are passed through unchanged to the underlying command.
- Both scripts accept `--root <path>` (default: current directory) so tests can target `tests/fixtures/<case>/`.
- `uv` must be present; the wrappers do not fall back to a system Python. If `uv` is missing, print `uv not found` and exit 2.
- Scripts never write outside `--root`. `build_index.py` writes only `<root>/wiki/index.md`; `lint.py` writes nothing.

## C7. Lint

Output, one finding per line on stdout:

```
<severity>: <path relative to root>: <message>
```

`severity` is `error` or `warning`. Any `error` yields exit 1; warnings alone yield exit 0. A final summary line `lint: <E> errors, <W> warnings` is printed to stdout after all findings.

| Check | Applies to | Severity |
|---|---|---|
| Missing or unparseable frontmatter | pages | error |
| Frontmatter present on a special file | special files | error |
| Unknown key, missing required key, key required by another type present | pages | error |
| `type` not in allowed set | pages | error |
| Page directory does not match its `type` group (C1 table) | pages | error |
| `created` or `updated` not `YYYY-MM-DD`, or `updated < created` | pages | error |
| `title` or `summary` empty, or `summary` > 200 characters | pages | error |
| `tags` entry does not match slug regex | pages | error |
| `sources:` entry or `raw:` path does not exist on disk | pages | error |
| Filename does not match slug regex or the C1 filename convention for its type | pages | error |
| Duplicate slug (compare after lowercasing and removing `-` and `_`) across all pages | pages | error |
| Broken relative body link (target file missing) | pages and special files | error |
| Body link to `raw/` | pages and special files | error |
| `wiki/index.md` differs from `build_index.py` output | index | error |
| `wiki/log.md` heading line violates the C4 regex, or an entry has no bullet | log | error |
| `type: entity` (unclassified) | pages | warning |
| Orphan page: no inbound body link from any page or from `overview.md` (links from `index.md` and `log.md` do not count) | pages | warning |
| Pending raw source: file under `raw/` (excluding `raw/assets/`, `raw/README.md`, `.gitkeep`) not referenced by any `raw:` key | raw | warning |
| Unreferenced asset: file under `raw/assets/` not linked from any page | raw | warning |

Lint has no silent fallbacks. A file it cannot read or parse produces an `error`, never a skip.

## C8. CI and site

`.github/workflows/lint.yml` (`on: pull_request`) runs, in order:

```
uv sync
./run.sh lint
./run.sh index --check
```

`.github/workflows/pages.yml` (`on: push` to `main`) runs:

```
uv sync
uv run mkdocs build --strict
```

then uploads and deploys `site/`.

`mkdocs.yml` sets `docs_dir: wiki` and `site_dir: site`. `raw/` is outside `docs_dir` and is never published. `mkdocs build --strict` must succeed on the C2 example set with the C5 index; the site's home page is `wiki/index.md`.

## Amendment log

- 2026-09-28: initial version (Phase 0).

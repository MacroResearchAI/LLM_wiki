---
name: Agent 3 skills
overview: Write the three Cursor skill files that Agent 3 owns, on branch `agent/3-skills`, following the parallel-agents plan and the shared contract. No other files will be changed.
todos:
  - id: branch
    content: Create agent/3-skills from latest main
    status: pending
  - id: ingest-skill
    content: Write .cursor/skills/wiki-ingest/SKILL.md
    status: pending
  - id: query-skill
    content: Write .cursor/skills/wiki-query/SKILL.md
    status: pending
  - id: lint-skill
    content: Write .cursor/skills/wiki-lint/SKILL.md
    status: pending
  - id: dry-run
    content: Dry-run each skill and confirm checkpoints
    status: pending
isProject: false
---

# Agent 3: Cursor skills

You own only the three skill files in [team_llm_wiki_parallel_agents.plan.md](team_llm_wiki_parallel_agents.plan.md) (section **Agent 3**). Phase 0 is already on `main`. Other agents own schema, scripts, and CI.

## Branch

The plan’s branch name is `agent/3-skills` (not the local `agent3`). Start from current `main` (`7135104`) and work on `agent/3-skills`. Leave `agent3` unused.

## Files to create (nothing else)

- [`.cursor/skills/wiki-ingest/SKILL.md`](../skills/wiki-ingest/SKILL.md)
- [`.cursor/skills/wiki-query/SKILL.md`](../skills/wiki-query/SKILL.md)
- [`.cursor/skills/wiki-lint/SKILL.md`](../skills/wiki-lint/SKILL.md)

Do not edit `AGENTS.md`, `wiki/`, `scripts/`, `run.*`, CI, or `doc/`. Skills point at those docs instead of copying the schema.

## What each skill will say

Each file starts with YAML frontmatter (`name`, `description` that triggers on `/wiki-ingest`, `/wiki-query`, or `/wiki-lint`), then an imperative procedure taken from [doc/workflows.md](../../doc/workflows.md). Human checkpoints are written as **stop and wait for `proceed`**.

**wiki-ingest** (from workflows Phase A–F, LLM steps only made imperative):

- Read order: `AGENTS.md`, `wiki/index.md`, last 5 `wiki/log.md` headings, raw text, then images in `raw/assets/`
- Stop if a `wiki/sources/` page already cites that `raw:` path
- Present claims / pages to touch / contradictions, then **wait**
- Write pages with frontmatter from contract **C1**, relative links from **C3**, log line matching **C4** (`## [YYYY-MM-DD] ingest | Title`)
- Run `./run.ps1 index` then `./run.ps1 lint` (contract **C6**)
- Propose branch `wiki/<date>-<slug>` and a commit message, then **stop** (no git until you say proceed)

**wiki-query**:

- Read `wiki/index.md` first, then relevant pages; cite wiki pages; say when the wiki has no evidence
- Do not read `raw/` unless a wiki page is insufficient
- If `--file`: write `wiki/analyses/<yyyy-mm-dd>-<slug>.md`, add backlinks, log `query`, then index + lint
- Chat-only answers stop with no git

**wiki-lint**:

- Run `./run.ps1 lint`
- Semantic pass the script cannot do (contradictions, stale claims, missing concept pages)
- Group findings as fix now / propose / investigate, then **wait**
- Apply only what you approve, log `lint`, then index + lint until clean

## Self-test (no new wiki pages)

On the branch, invoke each skill once against the current (mostly empty) wiki and confirm: the skill loads, follows the read order, and stops at every checkpoint.

## Out of scope

Integration, real source ingest, and any file outside `.cursor/skills/`. After you approve the diff, commit and open a PR into `main` only if you say to.

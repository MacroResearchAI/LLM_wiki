---
name: Agent 1 - Schema and Onboarding
overview: "Implement Agent 1's schema, onboarding, and seed content from the shared contract. Validate the owned files and stop at the review checkpoint."
todos:
  - id: guidance
    content: Create shared schema and onboarding guidance in Agent 1's owned paths
    status: pending
  - id: seed-pages
    content: Create the contract seed pages and cited raw speech
    status: pending
  - id: log-index
    content: Add the required log entries and C5-formatted seed index
    status: pending
  - id: validation
    content: Verify schema and seed consistency against the shared contract
    status: pending
  - id: review
    content: Present the completed Agent 1 work and stop for review
    status: pending
---

# Agent 1: Schema and Onboarding

## Objective

Create the shared wiki schema, human-facing onboarding, and seeded wiki content assigned to Agent 1. Work from the Phase 0 base. `doc/contract.md` is authoritative if it conflicts with other guidance.

## Steps

1. **Write schema and onboarding.** Create `AGENTS.md`, `README.md`, `raw/README.md`, and `wiki/overview.md`. In `AGENTS.md`, document the layer rules, C1 frontmatter and type-to-directory mapping, page templates, `entity` escape-hatch rule, naming and citation conventions, contradiction handling, and the numbered ingest/query/lint workflows from `doc/workflows.md`. Explain team onboarding, source addition, and PR review in `README.md`; document raw-source immutability, naming, and categories in `raw/README.md`.
2. **Create the seed content.** Add the five contract example pages and the raw speech they cite:
   - `wiki/sources/2026-09-20-powell-jackson-hole.md`
   - `wiki/entities/federal-reserve.md`
   - `wiki/concepts/neutral-rate.md`
   - `wiki/topics/us-monetary-policy-stance.md`
   - `wiki/analyses/2026-09-21-fed-vs-ecb-neutral-rate.md`
   - `raw/speeches/2026-09-20-powell-jackson-hole.md`
3. **Add the special wiki files.** Create `wiki/log.md` with one ingest and one query entry using the C4 heading format. Write `wiki/index.md` in the C5 structure for the five seed pages. This is a hand-written seed placeholder; integration will check that the index builder reproduces it byte-for-byte.
4. **Validate the owned content.** Check frontmatter keys, ordering, values, and dates against C1; confirm required `sources:` and `raw:` paths exist; resolve every relative link; verify log headings against C4 and index section structure against C5. Confirm the seed pages and raw source are internally consistent.
5. **Stop for review.** Present the completed schema and seed set, summarize validation, and wait for approval before any action beyond the assigned Agent 1 scope.

## Owned Paths

Only create or modify the files below:

```text
AGENTS.md
README.md
raw/README.md
raw/speeches/2026-09-20-powell-jackson-hole.md
wiki/overview.md
wiki/log.md
wiki/index.md
wiki/sources/2026-09-20-powell-jackson-hole.md
wiki/entities/federal-reserve.md
wiki/concepts/neutral-rate.md
wiki/topics/us-monetary-policy-stance.md
wiki/analyses/2026-09-21-fed-vs-ecb-neutral-rate.md
```

## Boundaries

- Follow the Agent 1 section of `.cursor/plans/team_llm_wiki_parallel_agents.plan.md` and the shared requirements in `doc/contract.md` and `doc/workflows.md`.
- Do not modify `scripts/`, `tests/`, `.cursor/skills/`, `.github/`, `mkdocs.yml`, `run.*`, or `pyproject.toml`.
- Do not add new top-level entries or modify files outside the owned paths.
- Do not perform git operations without explicit approval.
- Stop at the review checkpoint; changes beyond this scope require separate approval.

## Completion Criteria

All owned files are present; schema and workflow guidance follow the contract; seed frontmatter, citations, and relative links are valid; the log follows C4; the index follows C5; and the work is presented for review without proceeding past the checkpoint.

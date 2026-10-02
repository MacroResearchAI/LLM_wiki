---
name: Agent 4 CI Site
overview: Implement the Agent 4 CI and publishing workstream without touching the schema, tooling, skills, wiki content, or run wrappers. The deliverable is MkDocs configuration, CI workflows, and a hosting report that can merge independently after Phase 0.
todos:
  - id: mkdocs-config
    content: Create MkDocs Material config that publishes only `wiki/` to `site/` and builds strictly.
    status: pending
  - id: pr-ci
    content: Create pull request lint workflow using the exact C8 contract commands.
    status: pending
  - id: pages-ci
    content: Create main-branch Pages deployment workflow using MkDocs strict build and Pages actions.
    status: pending
  - id: hosting-doc
    content: Document the GitHub Pages hosting finding and avoid changing repo settings.
    status: pending
  - id: self-test
    content: Run isolated MkDocs smoke test and workflow validation after implementation.
    status: pending
isProject: false
---

# Agent 4 CI And Publishing Plan

## Scope

Work only on these owned files from [`/Users/harlly/Desktop/LLM_wiki/.cursor/plans/team_llm_wiki_parallel_agents.plan.md`](/Users/harlly/Desktop/LLM_wiki/.cursor/plans/team_llm_wiki_parallel_agents.plan.md):

- [`/Users/harlly/Desktop/LLM_wiki/mkdocs.yml`](/Users/harlly/Desktop/LLM_wiki/mkdocs.yml)
- [`/Users/harlly/Desktop/LLM_wiki/.github/workflows/lint.yml`](/Users/harlly/Desktop/LLM_wiki/.github/workflows/lint.yml)
- [`/Users/harlly/Desktop/LLM_wiki/.github/workflows/pages.yml`](/Users/harlly/Desktop/LLM_wiki/.github/workflows/pages.yml)
- [`/Users/harlly/Desktop/LLM_wiki/doc/hosting.md`](/Users/harlly/Desktop/LLM_wiki/doc/hosting.md)

Do not touch `run.*`, `scripts/`, `wiki/`, `AGENTS.md`, or `pyproject.toml`.

## Implementation Approach

1. Add [`mkdocs.yml`](/Users/harlly/Desktop/LLM_wiki/mkdocs.yml) matching [`doc/contract.md`](/Users/harlly/Desktop/LLM_wiki/doc/contract.md) C8:
   - Material theme.
   - `docs_dir: wiki` and `site_dir: site`.
   - Strict mode enabled.
   - Built-in search enabled.
   - Auto navigation by leaving nav unset.
   - Exclude generated JSON docs, especially future graph artifacts.
   - Keep `raw/` unpublished by relying on `docs_dir: wiki`.

2. Add pull request CI in [`.github/workflows/lint.yml`](/Users/harlly/Desktop/LLM_wiki/.github/workflows/lint.yml):
   - Trigger on `pull_request`.
   - Use checkout and `astral-sh/setup-uv`.
   - Run exactly the contract calls: `uv sync`, `./run.sh lint`, `./run.sh index --check`.

3. Add GitHub Pages publishing in [`.github/workflows/pages.yml`](/Users/harlly/Desktop/LLM_wiki/.github/workflows/pages.yml):
   - Trigger on pushes to `main`.
   - Use checkout and `astral-sh/setup-uv`.
   - Run `uv sync` and `uv run mkdocs build --strict`.
   - Upload `site/` with `actions/upload-pages-artifact`.
   - Deploy with `actions/deploy-pages`.
   - Set permissions `contents: read`, `pages: write`, and `id-token: write`.

4. Add [`doc/hosting.md`](/Users/harlly/Desktop/LLM_wiki/doc/hosting.md):
   - Record whether `MacroResearchAI/LLM_wiki` can use GitHub Pages.
   - Note that public repos support Pages; private repos require the right GitHub plan/org support.
   - Do not change repo settings or enable Pages from the agent.
   - If the repo cannot use Pages, recommend an alternative such as keeping CI only and deploying later via a supported host.

5. Self-test plan after implementation:
   - Create a temporary directory outside the repo for an isolated MkDocs smoke test.
   - Copy `mkdocs.yml` into it.
   - Create a minimal `wiki/index.md` plus one linked page shaped like the C2 examples.
   - Run `uv run mkdocs build --strict` there and expect success.
   - Validate workflow YAML with `actionlint` if installed; otherwise inspect syntax and action versions manually.

## Notes

Agent 4 depends on Agent 2 later providing `run.sh` and the scripts. The workflows should still reference those contract commands now; integration will prove them once Agent 2 is merged.

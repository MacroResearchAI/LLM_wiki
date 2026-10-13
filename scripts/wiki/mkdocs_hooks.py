"""MkDocs hooks that publish ``raw/assets/`` with the wiki site.

``docs_dir`` is ``wiki/``, so the repo-relative image link a page must use
(``![...](../../raw/assets/x.png)``, contract C3) points outside the
documentation tree and fails ``mkdocs build --strict``. These hooks add every
file under ``raw/assets/`` to the site at ``raw/assets/...`` and rewrite the
links to the matching site-relative form while the page is rendered. Page
bodies on disk keep the repo-relative form the contract requires.
"""

from __future__ import annotations

import re
from pathlib import Path

from mkdocs.config.defaults import MkDocsConfig
from mkdocs.structure.files import File, Files
from mkdocs.structure.pages import Page

ASSETS = Path("raw") / "assets"
ASSET_LINK = re.compile(r"\]\((?:\.\./)+raw/assets/")


def _repo_root(config: MkDocsConfig) -> Path:
    return Path(config.config_file_path).resolve().parent


def on_files(files: Files, config: MkDocsConfig) -> Files:
    assets_dir = _repo_root(config) / ASSETS
    if not assets_dir.is_dir():
        return files
    for path in sorted(p for p in assets_dir.rglob("*") if p.is_file() and not p.name.startswith(".")):
        rel = path.relative_to(_repo_root(config)).as_posix()
        files.append(
            File(
                rel,
                src_dir=str(_repo_root(config)),
                dest_dir=config.site_dir,
                use_directory_urls=config.use_directory_urls,
            )
        )
    return files


def on_page_markdown(markdown: str, page: Page, config: MkDocsConfig, files: Files) -> str:
    depth = len(Path(page.file.src_uri).parent.parts)
    site_prefix = "](" + "../" * depth + ASSETS.as_posix() + "/"
    return ASSET_LINK.sub(site_prefix, markdown)

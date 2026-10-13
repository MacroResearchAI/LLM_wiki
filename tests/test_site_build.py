from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

from conftest import REPO

HOOK = REPO / "scripts" / "wiki" / "mkdocs_hooks.py"
PAGE = "wiki/sources/2026-09-20-powell-jackson-hole.md"
ASSET = "raw/assets/2026-09-20-powell/figure-1.png"
# Smallest valid PNG: 1x1 pixel.
PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360000002000154a24f5d0000000049454e44ae426082"
)


def _write_config(root: Path) -> None:
    (root / "mkdocs.yml").write_text(
        "site_name: Test\n"
        "docs_dir: wiki\n"
        "site_dir: site\n"
        "strict: true\n"
        "theme:\n  name: material\n"
        f"hooks:\n  - {HOOK.as_posix()}\n",
        encoding="utf-8",
    )


def _build(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "mkdocs", "build", "--strict"],
        cwd=root,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env={**os.environ, "PYTHONUTF8": "1"},
    )


def test_strict_build_publishes_embedded_raw_assets(copy_fixture) -> None:
    root = copy_fixture("clean")
    _write_config(root)
    asset = root / ASSET
    asset.parent.mkdir(parents=True)
    asset.write_bytes(PNG)
    page = root / PAGE
    page.write_text(
        page.read_text(encoding="utf-8").replace(
            "## Figures and data\n\nNone.",
            "## Figures and data\n\n![Figure 1](../../raw/assets/2026-09-20-powell/figure-1.png)",
        ),
        encoding="utf-8",
    )

    result = _build(root)

    assert result.returncode == 0, result.stderr
    assert (root / "site" / ASSET).read_bytes() == PNG
    html = (root / "site" / "sources" / "2026-09-20-powell-jackson-hole" / "index.html").read_text(encoding="utf-8")
    assert 'src="../../raw/assets/2026-09-20-powell/figure-1.png"' in html


def test_strict_build_fails_on_missing_raw_asset(copy_fixture) -> None:
    root = copy_fixture("clean")
    _write_config(root)
    page = root / PAGE
    page.write_text(
        page.read_text(encoding="utf-8").replace(
            "## Figures and data\n\nNone.",
            "## Figures and data\n\n![Figure 1](../../raw/assets/2026-09-20-powell/missing.png)",
        ),
        encoding="utf-8",
    )

    result = _build(root)

    assert result.returncode == 1
    assert "missing.png" in result.stderr

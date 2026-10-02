from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPTS = REPO / "scripts" / "wiki"
FIXTURES = Path(__file__).resolve().parent / "fixtures"

sys.path.insert(0, str(SCRIPTS))


def run_script(name: str, *args: str) -> subprocess.CompletedProcess[str]:
    """Run ``scripts/wiki/<name>.py`` with repo root as cwd, as the wrappers do."""

    return subprocess.run(
        [sys.executable, str(SCRIPTS / f"{name}.py"), *args],
        cwd=REPO,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )


@pytest.fixture(scope="session")
def fixtures() -> Path:
    return FIXTURES


@pytest.fixture
def copy_fixture(tmp_path: Path):
    """Copy a fixture tree into ``tmp_path`` so a test can write to it."""

    import shutil

    def _copy(name: str) -> Path:
        dest = tmp_path / name
        shutil.copytree(FIXTURES / name, dest)
        return dest

    return _copy

"""Regenerate ``wiki/index.md`` from page frontmatter (contract C5, C6).

Usage::

    uv run python scripts/wiki/build_index.py [--root PATH] [--check]

Without ``--check`` the index is written to ``<root>/wiki/index.md`` and the
exit code is 0. With ``--check`` nothing is written; the exit code is 0 when
the file is already up to date and 1 otherwise, with a unified diff on stdout.
"""

from __future__ import annotations

import argparse
import difflib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import load_pages, normalize_newlines, render_index  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    parser.add_argument("--check", action="store_true", help="verify wiki/index.md without writing")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    root = Path(args.root).resolve()
    if not (root / "wiki").is_dir():
        print(f"error: {root} has no wiki/ directory", file=sys.stderr)
        return 2

    rendered = render_index(load_pages(root))
    index_path = root / "wiki" / "index.md"

    if args.check:
        existing = normalize_newlines(index_path.read_bytes()).decode("utf-8") if index_path.is_file() else ""
        if existing == rendered:
            return 0
        diff = difflib.unified_diff(
            existing.splitlines(keepends=True),
            rendered.splitlines(keepends=True),
            fromfile="wiki/index.md",
            tofile="wiki/index.md (generated)",
        )
        sys.stdout.write("".join(diff))
        return 1

    with index_path.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())

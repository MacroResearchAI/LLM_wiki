"""Deterministic structural checks for the wiki (contract C7).

Usage::

    uv run python scripts/wiki/lint.py [--root PATH]

One finding per stdout line::

    <severity>: <path relative to root>: <message>

followed by ``lint: <E> errors, <W> warnings``. Exit 1 when any ``error`` was
reported, otherwise 0. Nothing is written to disk.

Findings are emitted in sorted path order and, within one path, in the order
of the C7 table. A file that cannot be parsed yields an error and its
frontmatter checks stop there so one defect produces one finding.

Links to ``raw/`` from a page body are an error (C3). Image embeds
(``![...](../../raw/assets/x.png)``) are the exception: they are how a page
references an asset, so they are permitted and they satisfy the
"unreferenced asset" check.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import (  # noqa: E402
    ALL_KEYS,
    ALLOWED_TYPES,
    ANALYSIS_FILENAME_RE,
    COMMON_KEYS,
    DATE_RE,
    KEY_RAW,
    KEY_SOURCES,
    LOG_HEADING_RE,
    SLUG_RE,
    SOURCE_FILENAME_RE,
    SUMMARY_MAX_CHARS,
    TYPE_DIRECTORY,
    Page,
    extract_links,
    has_frontmatter_marker,
    load_pages,
    normalize_newlines,
    read_text,
    rel_posix,
    render_index,
    resolve_link,
    special_file_paths,
)

# C7 table rows, used for ordering findings within one path.
ROW_FRONTMATTER = 1
ROW_SPECIAL_FRONTMATTER = 2
ROW_KEYS = 3
ROW_TYPE = 4
ROW_DIRECTORY = 5
ROW_DATES = 6
ROW_TITLE_SUMMARY = 7
ROW_TAGS = 8
ROW_PATHS = 9
ROW_FILENAME = 10
ROW_DUPLICATE = 11
ROW_BROKEN_LINK = 12
ROW_RAW_LINK = 13
ROW_INDEX = 14
ROW_LOG = 15
ROW_UNCLASSIFIED = 16
ROW_ORPHAN = 17
ROW_PENDING_RAW = 18
ROW_ASSET = 19

ERROR = "error"
WARNING = "warning"


@dataclass(frozen=True)
class Finding:
    path: str
    row: int
    severity: str
    message: str

    def render(self) -> str:
        return f"{self.severity}: {self.path}: {self.message}"


class Linter:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.findings: list[Finding] = []
        self.pages: list[Page] = load_pages(self.root)
        self.specials: list[Path] = special_file_paths(self.root)

    # -- helpers -----------------------------------------------------------

    def error(self, path: str, row: int, message: str) -> None:
        self.findings.append(Finding(path, row, ERROR, message))

    def warning(self, path: str, row: int, message: str) -> None:
        self.findings.append(Finding(path, row, WARNING, message))

    def _inside_root(self, path: Path) -> bool:
        return path.is_relative_to(self.root)

    def _under(self, path: Path, *parts: str) -> bool:
        return path.is_relative_to(self.root.joinpath(*parts))

    # -- run ---------------------------------------------------------------

    def run(self) -> list[Finding]:
        for page in self.pages:
            self.check_page(page)
        self.check_special_files()
        self.check_duplicates()
        self.check_links()
        self.check_index()
        self.check_log()
        self.check_orphans()
        self.check_raw()
        self.findings.sort(key=lambda f: (f.path, f.row, f.message))
        return self.findings

    # -- per-page frontmatter checks ----------------------------------------

    def check_page(self, page: Page) -> None:
        rel = page.rel
        if page.error is not None or page.frontmatter is None:
            self.error(rel, ROW_FRONTMATTER, page.error or "missing frontmatter")
            self._check_filename(page, None)
            return

        fm = page.frontmatter
        type_value = fm.get("type")
        type_ok = isinstance(type_value, str) and type_value in ALLOWED_TYPES
        if "type" in fm and not type_ok:
            self.error(rel, ROW_TYPE, f"type {type_value!r} is not one of {sorted(ALLOWED_TYPES)}")

        self._check_keys(page, type_value if type_ok else None)

        if type_ok:
            expected_dir = TYPE_DIRECTORY[type_value]
            if page.directory != expected_dir:
                self.error(rel, ROW_DIRECTORY, f"type {type_value!r} belongs in wiki/{expected_dir}/")

        self._check_dates(page)
        self._check_title_summary(page)
        self._check_tags(page)
        self._check_paths(page)
        self._check_filename(page, type_value if type_ok else None)

        if type_value == "entity":
            self.warning(rel, ROW_UNCLASSIFIED, "type: entity is unclassified; propose a specific type")

    def _check_keys(self, page: Page, type_value: str | None) -> None:
        fm = page.frontmatter or {}
        keys = set(fm)
        problems: list[str] = []
        unknown = sorted(keys - ALL_KEYS)
        if unknown:
            problems.append(f"unknown keys {unknown}")
        missing = [k for k in COMMON_KEYS if k not in keys]
        if type_value is not None:
            required, forbidden = (KEY_RAW, KEY_SOURCES) if type_value == "source" else (KEY_SOURCES, KEY_RAW)
            if required not in keys:
                missing.append(required)
            if forbidden in keys:
                problems.append(f"key {forbidden!r} is not permitted for type {type_value!r}")
        if missing:
            problems.append(f"missing keys {missing}")
        if problems:
            self.error(page.rel, ROW_KEYS, "; ".join(problems))

    def _check_dates(self, page: Page) -> None:
        fm = page.frontmatter or {}
        parsed: dict[str, dt.date] = {}
        problems: list[str] = []
        for key in ("created", "updated"):
            if key not in fm:
                continue
            value = fm[key]
            if not isinstance(value, str) or not DATE_RE.match(value):
                problems.append(f"{key} must be YYYY-MM-DD")
                continue
            try:
                parsed[key] = dt.date.fromisoformat(value)
            except ValueError:
                problems.append(f"{key} {value!r} is not a real date")
        if "created" in parsed and "updated" in parsed and parsed["updated"] < parsed["created"]:
            problems.append("updated is earlier than created")
        if problems:
            self.error(page.rel, ROW_DATES, "; ".join(problems))

    def _check_title_summary(self, page: Page) -> None:
        fm = page.frontmatter or {}
        problems: list[str] = []
        for key in ("title", "summary"):
            if key not in fm:
                continue
            value = fm[key]
            if not isinstance(value, str) or not value.strip():
                problems.append(f"{key} is empty")
            elif key == "summary" and len(value) > SUMMARY_MAX_CHARS:
                problems.append(f"summary is {len(value)} characters (max {SUMMARY_MAX_CHARS})")
        if problems:
            self.error(page.rel, ROW_TITLE_SUMMARY, "; ".join(problems))

    def _check_tags(self, page: Page) -> None:
        fm = page.frontmatter or {}
        if "tags" not in fm:
            return
        tags = fm["tags"]
        if not isinstance(tags, list):
            self.error(page.rel, ROW_TAGS, "tags must be a list")
            return
        bad = [t for t in tags if not isinstance(t, str) or not SLUG_RE.match(t)]
        if bad:
            self.error(page.rel, ROW_TAGS, f"tags {bad} are not kebab-case slugs")

    def _check_paths(self, page: Page) -> None:
        fm = page.frontmatter or {}
        problems: list[str] = []
        if KEY_SOURCES in fm:
            sources = fm[KEY_SOURCES]
            if not isinstance(sources, list) or not sources:
                problems.append("sources must be a non-empty list")
            else:
                for entry in sources:
                    if not isinstance(entry, str) or not (self.root / entry).is_file():
                        problems.append(f"sources entry {entry!r} does not exist")
        if KEY_RAW in fm:
            raw = fm[KEY_RAW]
            if not isinstance(raw, str) or not (self.root / raw).is_file():
                problems.append(f"raw path {raw!r} does not exist")
        if problems:
            self.error(page.rel, ROW_PATHS, "; ".join(problems))

    def _check_filename(self, page: Page, type_value: str | None) -> None:
        stem = page.slug
        if not SLUG_RE.match(stem):
            self.error(page.rel, ROW_FILENAME, "filename is not a kebab-case slug")
            return
        if type_value == "source" and not SOURCE_FILENAME_RE.match(stem):
            self.error(page.rel, ROW_FILENAME, "source filename must be YYYY-MM-DD-<author>-<slug>.md")
        elif type_value == "analysis" and not ANALYSIS_FILENAME_RE.match(stem):
            self.error(page.rel, ROW_FILENAME, "analysis filename must be YYYY-MM-DD-<slug>.md")

    # -- special files -------------------------------------------------------

    def check_special_files(self) -> None:
        for path in self.specials:
            if has_frontmatter_marker(read_text(path)):
                self.error(rel_posix(self.root, path), ROW_SPECIAL_FRONTMATTER, "special file must not have frontmatter")

    # -- duplicates ----------------------------------------------------------

    def check_duplicates(self) -> None:
        groups: dict[str, list[Page]] = {}
        for page in self.pages:
            key = page.slug.lower().replace("-", "").replace("_", "")
            groups.setdefault(key, []).append(page)
        for members in groups.values():
            if len(members) < 2:
                continue
            members.sort(key=lambda p: p.rel)
            others = ", ".join(p.rel for p in members[1:])
            self.error(members[0].rel, ROW_DUPLICATE, f"duplicate slug; also used by {others}")

    # -- links ---------------------------------------------------------------

    def _link_sources(self) -> list[tuple[str, Path, str]]:
        """``(rel, path, text)`` for every page and special file."""

        items = [(p.rel, p.path, p.text) for p in self.pages]
        items += [(rel_posix(self.root, s), s.resolve(), read_text(s)) for s in self.specials]
        return items

    def check_links(self) -> None:
        for rel, path, text in self._link_sources():
            for link in extract_links(text):
                target = resolve_link(path, link)
                if not self._inside_root(target):
                    self.error(rel, ROW_BROKEN_LINK, f"link {link.raw!r} resolves outside the repository")
                    continue
                if self._under(target, "raw") and not link.is_image:
                    self.error(rel, ROW_RAW_LINK, f"body link {link.raw!r} points into raw/")
                    continue
                if not target.exists():
                    self.error(rel, ROW_BROKEN_LINK, f"broken link {link.raw!r}")

    # -- index and log ---------------------------------------------------------

    def check_index(self) -> None:
        index_path = self.root / "wiki" / "index.md"
        if not index_path.is_file():
            self.error("wiki/index.md", ROW_INDEX, "missing; run ./run.ps1 index")
            return
        existing = normalize_newlines(index_path.read_bytes()).decode("utf-8")
        if existing != render_index(self.pages):
            self.error("wiki/index.md", ROW_INDEX, "stale; run ./run.ps1 index")

    def check_log(self) -> None:
        log_path = self.root / "wiki" / "log.md"
        if not log_path.is_file():
            self.error("wiki/log.md", ROW_LOG, "missing")
            return
        lines = read_text(log_path).split("\n")
        heading: str | None = None
        heading_line = 0
        bullets = 0

        def close_entry() -> None:
            if heading is not None and bullets == 0:
                self.error("wiki/log.md", ROW_LOG, f"line {heading_line}: entry has no bullet")

        for lineno, line in enumerate(lines, start=1):
            line = line.rstrip("\r")
            if line.startswith("## "):
                close_entry()
                heading, heading_line, bullets = line, lineno, 0
                if not LOG_HEADING_RE.match(line):
                    self.error("wiki/log.md", ROW_LOG, f"line {lineno}: heading does not match C4 format")
            elif heading is not None and line.startswith("- "):
                bullets += 1
        close_entry()

    # -- orphans ---------------------------------------------------------------

    def check_orphans(self) -> None:
        page_paths = {p.path for p in self.pages}
        inbound: set[Path] = set()
        overview = self.root / "wiki" / "overview.md"
        sources: list[tuple[Path, str]] = [(p.path, p.text) for p in self.pages]
        if overview.is_file():
            sources.append((overview.resolve(), read_text(overview)))
        for path, text in sources:
            for link in extract_links(text):
                target = resolve_link(path, link)
                if target != path and target in page_paths:
                    inbound.add(target)
        for page in self.pages:
            if page.path not in inbound:
                self.warning(page.rel, ROW_ORPHAN, "orphan page; no inbound link from any page or overview.md")

    # -- raw layer ---------------------------------------------------------------

    def check_raw(self) -> None:
        raw_dir = self.root / "raw"
        if not raw_dir.is_dir():
            return
        assets_dir = raw_dir / "assets"

        cited: set[Path] = set()
        for page in self.pages:
            raw = (page.frontmatter or {}).get(KEY_RAW)
            if isinstance(raw, str):
                cited.add((self.root / raw).resolve())

        referenced_assets: set[Path] = set()
        for _rel, path, text in self._link_sources():
            for link in extract_links(text):
                target = resolve_link(path, link)
                if target.is_relative_to(assets_dir):
                    referenced_assets.add(target)

        for path in sorted(raw_dir.rglob("*")):
            if not path.is_file() or path.name == ".gitkeep":
                continue
            resolved = path.resolve()
            rel = rel_posix(self.root, path)
            if resolved.is_relative_to(assets_dir):
                if resolved not in referenced_assets:
                    self.warning(rel, ROW_ASSET, "asset is not referenced by any page")
            elif path.parent == raw_dir and path.name == "README.md":
                continue
            elif resolved not in cited:
                self.warning(rel, ROW_PENDING_RAW, "pending ingest; no source page cites this file")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=".", help="repository root (default: current directory)")
    args = parser.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")

    root = Path(args.root).resolve()
    if not (root / "wiki").is_dir():
        print(f"error: {root} has no wiki/ directory", file=sys.stderr)
        return 2

    findings = Linter(root).run()
    for finding in findings:
        print(finding.render())
    errors = sum(1 for f in findings if f.severity == ERROR)
    warnings = sum(1 for f in findings if f.severity == WARNING)
    print(f"lint: {errors} errors, {warnings} warnings")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

"""Shared parsing and rendering for the wiki tooling.

Single source of truth for the type tables, frontmatter parsing, body-link
extraction, page discovery, and the C5 index renderer. ``build_index.py`` and
``lint.py`` import from here and never redefine these rules. The binding
specification is ``doc/contract.md``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

# --------------------------------------------------------------------------
# Type tables (contract C1)
# --------------------------------------------------------------------------

ENTITY_TYPES: frozenset[str] = frozenset(
    {"institution", "person", "country", "indicator", "entity"}
)
ALLOWED_TYPES: frozenset[str] = frozenset(
    {"source", "concept", "topic", "analysis"} | ENTITY_TYPES
)

# wiki/<directory> -> allowed type values for pages in that directory.
DIRECTORY_TYPES: dict[str, frozenset[str]] = {
    "sources": frozenset({"source"}),
    "entities": ENTITY_TYPES,
    "concepts": frozenset({"concept"}),
    "topics": frozenset({"topic"}),
    "analyses": frozenset({"analysis"}),
}

# type -> wiki/<directory>
TYPE_DIRECTORY: dict[str, str] = {
    t: directory for directory, types in DIRECTORY_TYPES.items() for t in types
}

# Files directly under wiki/ that are not pages and must not carry frontmatter.
SPECIAL_FILES: frozenset[str] = frozenset(
    {"index.md", "log.md", "overview.md", "graph.md"}
)

# Frontmatter keys, in contract order.
COMMON_KEYS: tuple[str, ...] = ("type", "title", "summary", "created", "updated", "tags")
KEY_SOURCES = "sources"
KEY_RAW = "raw"
ALL_KEYS: frozenset[str] = frozenset(COMMON_KEYS) | {KEY_SOURCES, KEY_RAW}

SUMMARY_MAX_CHARS = 200

SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
# Source filenames: YYYY-MM-DD-<author>-<slug>.md, so at least two kebab
# segments after the date.
SOURCE_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)+$")
# Analysis filenames: YYYY-MM-DD-<slug>.md
ANALYSIS_FILENAME_RE = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(-[a-z0-9]+)*$")

LOG_HEADING_RE = re.compile(r"^## \[\d{4}-\d{2}-\d{2}\] (ingest|query|lint) \| .+$")

# --------------------------------------------------------------------------
# YAML loading
# --------------------------------------------------------------------------


class _StringDateLoader(yaml.SafeLoader):
    """SafeLoader that leaves ``YYYY-MM-DD`` values as strings.

    PyYAML would otherwise turn them into ``datetime.date`` and raise inside
    the parser for impossible dates such as 2026-02-31. Lint wants to report
    those as a date error on the page, so dates stay as text here.
    """


_StringDateLoader.yaml_implicit_resolvers = {
    first: [(tag, regexp) for tag, regexp in resolvers if tag != "tag:yaml.org,2002:timestamp"]
    for first, resolvers in yaml.SafeLoader.yaml_implicit_resolvers.items()
}


class FrontmatterError(Exception):
    """Raised when a page has missing or unparseable frontmatter."""


def split_frontmatter(text: str) -> tuple[str, str]:
    """Return ``(yaml_block, body)``.

    Raises :class:`FrontmatterError` when the text does not begin with a
    ``---`` line or the block is not closed.
    """

    lines = text.split("\n")
    if not lines or lines[0].rstrip("\r") != "---":
        raise FrontmatterError("missing frontmatter")
    for i in range(1, len(lines)):
        if lines[i].rstrip("\r") == "---":
            return "\n".join(lines[1:i]), "\n".join(lines[i + 1 :])
    raise FrontmatterError("unterminated frontmatter block")


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse the frontmatter of ``text``. Returns ``(mapping, body)``.

    Raises :class:`FrontmatterError` on any failure. There are no defaults.
    """

    block, body = split_frontmatter(text)
    try:
        data = yaml.load(block, Loader=_StringDateLoader)  # noqa: S506 - SafeLoader subclass
    except yaml.YAMLError as exc:
        raise FrontmatterError(f"unparseable frontmatter: {exc.__class__.__name__}") from exc
    if not isinstance(data, dict):
        raise FrontmatterError("frontmatter is not a mapping")
    return data, body


def has_frontmatter_marker(text: str) -> bool:
    """True when the first line is ``---``."""

    first = text.split("\n", 1)[0].rstrip("\r")
    return first == "---"


# --------------------------------------------------------------------------
# Links
# --------------------------------------------------------------------------

_LINK_RE = re.compile(r"(!?)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_EXTERNAL_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")


@dataclass(frozen=True)
class Link:
    raw: str  # target text as written
    target: str  # target with any #fragment removed
    is_image: bool
    line: int


def extract_links(text: str) -> list[Link]:
    """Return every markdown link target in ``text``.

    External links (anything with a URL scheme, e.g. ``https://``) and pure
    fragments (``#heading``) are skipped.
    """

    links: list[Link] = []
    for lineno, line in enumerate(text.split("\n"), start=1):
        for match in _LINK_RE.finditer(line):
            bang, target = match.group(1), match.group(2)
            if _EXTERNAL_RE.match(target):
                continue
            path_part = target.split("#", 1)[0]
            if not path_part:
                continue
            links.append(Link(raw=target, target=path_part, is_image=bang == "!", line=lineno))
    return links


def resolve_link(source_file: Path, link: Link) -> Path:
    """Resolve ``link`` against the directory of ``source_file``."""

    return (source_file.parent / link.target).resolve()


# --------------------------------------------------------------------------
# Pages
# --------------------------------------------------------------------------


@dataclass
class Page:
    path: Path  # absolute
    rel: str  # posix path relative to root, e.g. wiki/concepts/neutral-rate.md
    text: str
    frontmatter: dict | None
    body: str
    error: str | None = None  # FrontmatterError message when parsing failed
    links: list[Link] = field(default_factory=list)

    @property
    def slug(self) -> str:
        return self.path.stem

    @property
    def directory(self) -> str | None:
        """The wiki sub-directory name, or None for files directly under wiki/."""

        parts = Path(self.rel).parts
        return parts[1] if len(parts) >= 3 else None

    @property
    def index_rel(self) -> str:
        """Path relative to wiki/, as used by index links."""

        return Path(*Path(self.rel).parts[1:]).as_posix()

    @property
    def type(self) -> str | None:
        if self.frontmatter is None:
            return None
        value = self.frontmatter.get("type")
        return value if isinstance(value, str) else None


def rel_posix(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def load_page(root: Path, path: Path) -> Page:
    text = read_text(path)
    page = Page(path=path.resolve(), rel=rel_posix(root, path), text=text, frontmatter=None, body=text)
    try:
        page.frontmatter, page.body = parse_frontmatter(text)
    except FrontmatterError as exc:
        page.error = str(exc)
    page.links = extract_links(text)
    return page


def iter_page_paths(root: Path) -> list[Path]:
    """All page files under ``root/wiki``: every ``*.md`` except the special files."""

    wiki = root / "wiki"
    if not wiki.is_dir():
        return []
    paths = []
    for path in sorted(wiki.rglob("*.md")):
        if path.parent == wiki and path.name in SPECIAL_FILES:
            continue
        paths.append(path)
    return paths


def load_pages(root: Path) -> list[Page]:
    return [load_page(root, p) for p in iter_page_paths(root)]


def special_file_paths(root: Path) -> list[Path]:
    """Special files that exist under ``root/wiki``."""

    wiki = root / "wiki"
    return [wiki / name for name in sorted(SPECIAL_FILES) if (wiki / name).is_file()]


# --------------------------------------------------------------------------
# Index renderer (contract C5)
# --------------------------------------------------------------------------

INDEX_HEADER = "# Index\n\n_Generated by scripts/wiki/build_index.py. Do not edit._\n"
_NONE = "_None._"
_SEP = " \u2014 "

_ENTITY_SUBSECTIONS: tuple[tuple[str, str], ...] = (
    ("institution", "Institutions"),
    ("person", "People"),
    ("country", "Countries"),
    ("indicator", "Indicators"),
    ("entity", "Unclassified"),
)


def _indexable(pages: list[Page]) -> list[Page]:
    return [p for p in pages if p.frontmatter is not None and p.type in ALLOWED_TYPES]


def _entry(page: Page, with_count: bool) -> str:
    fm = page.frontmatter or {}
    title = fm.get("title", "")
    summary = fm.get("summary", "")
    updated = fm.get("updated", "")
    sources = fm.get("sources")
    count = len(sources) if isinstance(sources, list) else 0
    tail = f"(updated {updated}, {count} sources)" if with_count else f"(updated {updated})"
    return f"- [{title}]({page.index_rel}){_SEP}{summary} {tail}"


def _entries(pages: list[Page], with_count: bool = True) -> list[str]:
    ordered = sorted(pages, key=lambda p: str((p.frontmatter or {}).get("title", "")))
    return [_entry(p, with_count) for p in ordered]


def render_index(pages: list[Page]) -> str:
    """Render ``wiki/index.md`` byte-exactly per contract C5."""

    pages = _indexable(pages)
    by_type: dict[str, list[Page]] = {}
    for page in pages:
        by_type.setdefault(page.type or "", []).append(page)

    blocks: list[str] = [INDEX_HEADER.rstrip("\n")]

    def section(heading: str, lines: list[str]) -> None:
        blocks.append(heading)
        blocks.append("\n".join(lines) if lines else _NONE)

    section("## Topics", _entries(by_type.get("topic", [])))

    entity_pages = [p for t in ENTITY_TYPES for p in by_type.get(t, [])]
    blocks.append("## Entities")
    if entity_pages:
        for type_name, heading in _ENTITY_SUBSECTIONS:
            group = by_type.get(type_name, [])
            if group:
                blocks.append(f"### {heading}")
                blocks.append("\n".join(_entries(group)))
    else:
        blocks.append(_NONE)

    section("## Concepts", _entries(by_type.get("concept", [])))
    section("## Analyses", _entries(by_type.get("analysis", [])))
    section("## Sources", _entries(by_type.get("source", []), with_count=False))

    return "\n\n".join(blocks) + "\n"


def normalize_newlines(data: bytes) -> bytes:
    """Fold CRLF to LF.

    Used only when reading an existing ``index.md`` for comparison so that a
    Windows checkout with ``core.autocrlf=true`` is not reported as stale.
    Written output is always ``\\n``.
    """

    return data.replace(b"\r\n", b"\n")

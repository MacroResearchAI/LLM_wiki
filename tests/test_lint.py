from __future__ import annotations

import re
from pathlib import Path

from conftest import run_script

FINDING_RE = re.compile(r"^(error|warning): (\S+): (.+)$")
SUMMARY_RE = re.compile(r"^lint: (\d+) errors, (\d+) warnings$")


def _parse(stdout: str) -> tuple[list[tuple[str, str, str]], tuple[int, int]]:
    lines = stdout.rstrip("\n").split("\n")
    summary = SUMMARY_RE.match(lines[-1])
    assert summary, f"missing summary line: {lines[-1]!r}"
    findings = []
    for line in lines[:-1]:
        m = FINDING_RE.match(line)
        assert m, f"malformed finding line: {line!r}"
        findings.append((m.group(1), m.group(2), m.group(3)))
    return findings, (int(summary.group(1)), int(summary.group(2)))


# -- clean -----------------------------------------------------------------------


def test_clean_exits_zero_with_no_findings(fixtures: Path) -> None:
    result = run_script("lint", "--root", str(fixtures / "clean"))
    assert result.returncode == 0, result.stdout + result.stderr
    assert result.stdout == "lint: 0 errors, 0 warnings\n"


def test_lint_writes_nothing(copy_fixture) -> None:
    root = copy_fixture("broken")
    before = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    run_script("lint", "--root", str(root))
    after = {p: p.read_bytes() for p in root.rglob("*") if p.is_file()}
    assert after == before


# -- broken: exactly one finding per C7 row -------------------------------------------------


EXPECTED_BROKEN = {
    # (severity, path) -> substring of message
    ("error", "wiki/concepts/no-frontmatter.md"): "missing frontmatter",
    ("error", "wiki/overview.md"): "special file must not have frontmatter",
    ("error", "wiki/concepts/unknown-key.md"): "unknown keys ['author']",
    ("error", "wiki/concepts/bad-type.md"): "type 'widget' is not one of",
    ("error", "wiki/topics/placed-wrong.md"): "belongs in wiki/concepts/",
    ("error", "wiki/concepts/bad-date.md"): "updated is earlier than created",
    ("error", "wiki/concepts/empty-title.md"): "title is empty",
    ("error", "wiki/concepts/bad-tag.md"): "tags ['Not_Kebab'] are not kebab-case slugs",
    ("error", "wiki/sources/2026-09-20-powell-missing-raw.md"): "does not exist",
    ("error", "wiki/concepts/Bad_Name.md"): "filename is not a kebab-case slug",
    ("error", "wiki/concepts/neutral-rate.md"): "duplicate slug; also used by wiki/concepts/neutralrate.md",
    ("error", "wiki/concepts/broken-link.md"): "broken link '../entities/missing.md'",
    ("error", "wiki/concepts/raw-link.md"): "points into raw/",
    ("error", "wiki/index.md"): "stale",
    ("error", "wiki/log.md"): "line 7: heading does not match C4 format",
    ("warning", "wiki/entities/unclassified-thing.md"): "type: entity is unclassified",
    ("warning", "wiki/concepts/orphan-page.md"): "orphan page",
    ("warning", "raw/papers/2026-01-01-nobody-unread.md"): "pending ingest",
    ("warning", "raw/assets/unused.png"): "asset is not referenced",
}


def test_broken_fires_each_check_exactly_once(fixtures: Path) -> None:
    result = run_script("lint", "--root", str(fixtures / "broken"))
    assert result.returncode == 1
    findings, (errors, warnings) = _parse(result.stdout)

    seen = {(sev, path): msg for sev, path, msg in findings}
    assert len(seen) == len(findings), "a path reported more than one finding"
    assert set(seen) == set(EXPECTED_BROKEN)
    for key, fragment in EXPECTED_BROKEN.items():
        assert fragment in seen[key], f"{key}: {seen[key]!r}"
    assert (errors, warnings) == (15, 4)


def test_findings_are_sorted_by_path(fixtures: Path) -> None:
    result = run_script("lint", "--root", str(fixtures / "broken"))
    findings, _ = _parse(result.stdout)
    paths = [path for _, path, _ in findings]
    assert paths == sorted(paths)


# -- warnings only: exit 0 ------------------------------------------------------------


def test_warnings_alone_exit_zero(fixtures: Path) -> None:
    result = run_script("lint", "--root", str(fixtures / "warnings"))
    assert result.returncode == 0, result.stdout
    findings, (errors, warnings) = _parse(result.stdout)
    assert errors == 0 and warnings == 4
    assert all(sev == "warning" for sev, _, _ in findings)
    assert {path for _, path, _ in findings} == {
        "wiki/entities/unclassified-thing.md",
        "wiki/concepts/orphan-page.md",
        "raw/papers/2026-01-01-nobody-unread.md",
        "raw/assets/unused.png",
    }


def test_image_embed_of_asset_counts_as_reference(fixtures: Path) -> None:
    result = run_script("lint", "--root", str(fixtures / "warnings"))
    assert "raw/assets/used.png" not in result.stdout


# -- targeted cases on copies ---------------------------------------------------------


def _lint_copy(copy_fixture, mutate) -> tuple[int, list[tuple[str, str, str]]]:
    root = copy_fixture("clean")
    mutate(root)
    result = run_script("lint", "--root", str(root))
    findings, _ = _parse(result.stdout)
    return result.returncode, findings


def test_impossible_date_is_a_date_error(copy_fixture) -> None:
    page = "wiki/concepts/neutral-rate.md"

    def mutate(root: Path) -> None:
        p = root / page
        p.write_text(p.read_text(encoding="utf-8").replace("updated: 2026-09-21", "updated: 2026-02-31"), encoding="utf-8")

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 1
    assert ("error", page, "updated '2026-02-31' is not a real date") in findings


def test_summary_over_200_chars_is_an_error(copy_fixture) -> None:
    page = "wiki/concepts/neutral-rate.md"

    def mutate(root: Path) -> None:
        p = root / page
        text = p.read_text(encoding="utf-8")
        start = text.index("summary: ")
        end = text.index("\n", start)
        p.write_text(text[:start] + 'summary: "' + "x" * 201 + '"' + text[end:], encoding="utf-8")

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 1
    assert any(path == page and "summary is 201 characters" in msg for _, path, msg in findings)


def test_raw_key_on_non_source_is_a_key_error(copy_fixture) -> None:
    page = "wiki/concepts/neutral-rate.md"

    def mutate(root: Path) -> None:
        p = root / page
        p.write_text(
            p.read_text(encoding="utf-8").replace("tags: [", "raw: raw/speeches/2026-09-20-powell-jackson-hole.md\ntags: ["),
            encoding="utf-8",
        )

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 1
    assert any(path == page and "key 'raw' is not permitted for type 'concept'" in msg for _, path, msg in findings)


def test_log_entry_without_bullet_is_an_error(copy_fixture) -> None:
    def mutate(root: Path) -> None:
        p = root / "wiki" / "log.md"
        p.write_text(p.read_text(encoding="utf-8") + "\n## [2026-09-22] lint | 0 findings\n", encoding="utf-8")

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 1
    assert ("error", "wiki/log.md", "line 13: entry has no bullet") in findings


def test_bad_analysis_filename_is_an_error(copy_fixture) -> None:
    def mutate(root: Path) -> None:
        src = root / "wiki" / "analyses" / "2026-09-21-fed-vs-ecb-neutral-rate.md"
        src.rename(root / "wiki" / "analyses" / "fed-vs-ecb-neutral-rate.md")

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 1
    assert any(
        path == "wiki/analyses/fed-vs-ecb-neutral-rate.md" and "analysis filename must be" in msg
        for _, path, msg in findings
    )


def test_external_links_are_ignored(copy_fixture) -> None:
    def mutate(root: Path) -> None:
        p = root / "wiki" / "concepts" / "neutral-rate.md"
        p.write_text(p.read_text(encoding="utf-8") + "\nSee [the Fed](https://www.federalreserve.gov/) too.\n", encoding="utf-8")

    code, findings = _lint_copy(copy_fixture, mutate)
    assert code == 0, findings
    assert findings == []


def test_missing_wiki_dir_exits_two(tmp_path: Path) -> None:
    result = run_script("lint", "--root", str(tmp_path))
    assert result.returncode == 2

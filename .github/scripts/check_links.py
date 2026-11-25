#!/usr/bin/env python3
"""Check relative links and images in Ember documentation.

This intentionally has no third-party dependencies so it can run in CI and
locally. It verifies:

- Markdown links and images resolve to files in the repository.
- Fragment links resolve to a heading in the target Markdown file.
- Local href/src paths in docs HTML resolve.

External URLs are not fetched. Absolute site paths are skipped because GitHub
Pages serves them from the site root.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parents[2]

MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HTML_ATTR = re.compile(r"""(?:href|src)\s*=\s*["']([^"']+)["']""")
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def repo_files() -> list[Path]:
    files = [ROOT / "README.md"]
    for base in (ROOT / "docs", ROOT / ".github"):
        if base.is_dir():
            files.extend(
                p
                for p in base.rglob("*")
                if p.is_file() and p.suffix.lower() in {".md", ".html"}
            )
    return sorted(set(files))


def strip_code_fences(text: str) -> str:
    lines = []
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            lines.append("")
            continue
        lines.append("" if in_fence else line)
    return "\n".join(lines)


def heading_slugs(text: str) -> set[str]:
    slugs: set[str] = set()
    counts: dict[str, int] = {}
    in_fence = False
    for line in text.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        match = HEADING.match(line)
        if not match:
            continue
        title = match.group(2)
        title = re.sub(r"`([^`]*)`", r"\1", title)
        title = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", title)
        title = re.sub(r"<[^>]+>", "", title)
        slug = title.lower()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"\s+", "-", slug).strip("-")
        if not slug:
            continue
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        slugs.add(slug if count == 0 else f"{slug}-{count}")
    return slugs


def is_external(target: str) -> bool:
    lowered = target.lower()
    return (
        lowered.startswith(("http://", "https://", "mailto:", "tel:", "data:", "//"))
        or lowered.startswith("#")
        or lowered.startswith("javascript:")
    )


def check_target(source: Path, raw_target: str, errors: list[str]) -> int:
    checked = 0
    target = unquote(raw_target.strip().strip("<>"))
    if not target or is_external(target):
        return checked
    if target.startswith("/"):
        # Site-root links are resolved by the web server, not the repository.
        return checked

    path_part, _, fragment = target.partition("#")
    path_part = path_part.split("?", 1)[0]
    if not path_part:
        return checked

    destination = (source.parent / path_part).resolve()
    try:
        destination.relative_to(ROOT)
    except ValueError:
        errors.append(f"{source.relative_to(ROOT)}: '{raw_target}' escapes the repository")
        return checked + 1

    checked += 1
    if not destination.exists():
        errors.append(f"{source.relative_to(ROOT)}: missing '{raw_target}'")
        return checked

    if fragment and destination.suffix.lower() == ".md":
        slugs = heading_slugs(destination.read_text(encoding="utf-8"))
        if fragment not in slugs:
            errors.append(
                f"{source.relative_to(ROOT)}: missing anchor '#{fragment}' in "
                f"{destination.relative_to(ROOT)}"
            )
    return checked


def main() -> int:
    errors: list[str] = []
    checked = 0
    files = repo_files()
    if not files:
        print("No documentation files found.", file=sys.stderr)
        return 1

    for source in files:
        text = strip_code_fences(source.read_text(encoding="utf-8"))
        pattern = HTML_ATTR if source.suffix.lower() == ".html" else MARKDOWN_LINK
        for match in pattern.finditer(text):
            checked += check_target(source, match.group(1), errors)

    if errors:
        print(f"Link check failed: {len(errors)} problem(s), {checked} local link(s) checked.")
        for error in errors:
            print(f"  - {error}")
        return 1

    print(f"Link check passed: {checked} local link(s) checked across {len(files)} file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

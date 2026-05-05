#!/usr/bin/env python3
"""
validate.py — schema and consistency checks across the repository.

Errors fail the run (exit 1). Warnings print but exit 0.

Usage:
    python scripts/validate.py
    python scripts/validate.py --strict   # warnings become errors
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

from utils import (
    SOURCE_HASH_RE,
    count_mentions,
    extract_wiki_links,
    find_entity_file,
    get_repo_root,
    list_entities,
    parse_file,
)


SKIP_TOP_LEVEL = {
    "README.md", "CONVENTIONS.md", "DECISIONS.md", "AUDIT.md",
    "CLAUDE.md", "SCHEMA.md", "UPGRADE_NOTES.md",
}


# ---------------------------------------------------------------------------
# Status vocabularies (mirror CONVENTIONS.md)
# ---------------------------------------------------------------------------

STATUS_VOCAB = {
    "person": {"active", "inactive", "archived"},
    "fund": {"active", "inactive", "archived"},
    "company": {"tracking", "evaluating", "passed", "invested", "exited"},
    "concept": {"developing", "stable", "deprecated"},
    "meeting": {"raw", "processed", "archived"},
    "inbox": {"raw", "processed", "archived"},
    "reflection": {"draft", "reviewed"},
    "brief": {"draft", "edited", "stale"},
    "area": {"active", "inactive", "archived"},
}

REQUIRED_FIELDS = {
    "person": {"type", "name", "created"},
    "company": {"type", "name", "created"},
    "fund": {"type", "name", "created"},
    "concept": {"type", "name", "created"},
    "area": {"type", "name", "created"},
    "meeting": {"type", "title", "date", "created"},
    "journal": {"type", "date", "created"},
    "inbox": {"type", "title", "created"},
    "reflection": {"type", "week", "generated"},
    "brief": {"type", "date", "generated"},
}

ENTITY_TYPES_WITH_MENTIONS = {"person", "company", "fund"}


# ---------------------------------------------------------------------------
# Result accumulator
# ---------------------------------------------------------------------------

class Results:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def report(self, strict: bool) -> int:
        if self.errors:
            print(f"Errors ({len(self.errors)}):")
            for e in self.errors:
                print(f"  ✗ {e}")
        if self.warnings:
            print(f"\nWarnings ({len(self.warnings)}):")
            for w in self.warnings:
                print(f"  ! {w}")
        if not self.errors and not self.warnings:
            print("All checks passed.")
            return 0
        if self.errors:
            return 1
        if strict and self.warnings:
            return 1
        return 0


# ---------------------------------------------------------------------------
# Per-file checks
# ---------------------------------------------------------------------------

SKIP_DIRS = {"templates", "prompts"}
SKIP_FILENAMES_PREFIX = ("_",)  # e.g. _tomorrow.md, _legacy_*.md


def iter_repo_markdown() -> list[Path]:
    repo_root = get_repo_root()
    out: list[Path] = []
    for f in repo_root.rglob("*.md"):
        rel_parts = f.relative_to(repo_root).parts
        if any(d in rel_parts for d in SKIP_DIRS):
            continue
        if f.name.startswith(SKIP_FILENAMES_PREFIX):
            continue
        if f.parent == repo_root and f.name in SKIP_TOP_LEVEL:
            continue
        # Skip dotted dirs *inside* the repo only.
        if any(part.startswith(".") for part in rel_parts):
            continue
        out.append(f)
    return out


HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
CODE_FENCE_RE = re.compile(r"```.*?```", re.DOTALL)
INLINE_CODE_RE = re.compile(r"`[^`]*`")


def strip_non_prose(text: str) -> str:
    """Remove HTML comments, fenced blocks, and inline code so wiki-links inside
    examples and instructional comments don't trigger false-positive warnings."""
    text = HTML_COMMENT_RE.sub("", text)
    text = CODE_FENCE_RE.sub("", text)
    text = INLINE_CODE_RE.sub("", text)
    return text


def check_frontmatter(path: Path, post, results: Results) -> None:
    rel = path.relative_to(get_repo_root())
    t = post.get("type")
    if not t:
        results.err(f"{rel}: missing required `type` frontmatter")
        return
    required = REQUIRED_FIELDS.get(t, set())
    for field in required:
        if not post.get(field):
            results.err(f"{rel}: missing required field `{field}` for type `{t}`")
    if t in STATUS_VOCAB:
        status = post.get("status")
        if status and status not in STATUS_VOCAB[t]:
            results.warn(
                f"{rel}: status `{status}` not in vocabulary for type `{t}` "
                f"({sorted(STATUS_VOCAB[t])})"
            )


def check_mentions_section(path: Path, post, results: Results) -> None:
    rel = path.relative_to(get_repo_root())
    t = post.get("type")
    if t not in ENTITY_TYPES_WITH_MENTIONS:
        return
    body = post.content or ""
    if "## Mentions" not in body:
        results.warn(f"{rel}: missing `## Mentions` section")
        return
    actual_count = count_mentions(body)
    declared = post.get("mention_count")
    if declared is not None:
        try:
            declared_int = int(declared)
        except (TypeError, ValueError):
            results.warn(f"{rel}: `mention_count` is not an integer: {declared!r}")
            return
        if declared_int != actual_count:
            results.warn(
                f"{rel}: `mention_count` ({declared_int}) does not match body ({actual_count})"
            )
    # Each mention should have a `↳ source:` line within ~6 lines of its heading.
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if re.match(r"^### \d{4}-\d{2}-\d{2}", line):
            window = "\n".join(lines[i : i + 8])
            if "↳ source:" not in window:
                results.warn(
                    f"{rel}: mention `{line.strip()}` is missing a `↳ source:` line"
                )


def check_wiki_links(path: Path, post, results: Results) -> None:
    rel = path.relative_to(get_repo_root())
    body = strip_non_prose(post.content or "")
    for link in extract_wiki_links(body):
        if not link or link.startswith("YYYY-"):  # template placeholder
            continue
        # Try entity resolution; fall back to filename match for meetings/journal/briefs/agents.
        if find_entity_file(link):
            continue
        if _filename_match_exists(link):
            continue
        results.warn(f"{rel}: unresolved wiki-link `[[{link}]]` (stub or typo)")


def _filename_match_exists(link: str) -> bool:
    repo_root = get_repo_root()
    from utils import make_slug
    slug = make_slug(link)
    candidates = [
        repo_root / "meetings" / f"{link}.md",
        repo_root / "journal" / f"{link}.md",
        repo_root / "briefs" / f"{link}.md",
        repo_root / "inbox" / f"{link}.md",
        repo_root / "thesis" / "reflections" / f"{link}.md",
        repo_root / "agents" / f"{slug}.md",
    ]
    return any(p.exists() for p in candidates)


# ---------------------------------------------------------------------------
# Cross-file checks
# ---------------------------------------------------------------------------

def check_no_duplicate_mentions(results: Results) -> None:
    """A given source_hash + body should only appear on one entity file."""
    seen: dict[tuple[str, str], list[Path]] = defaultdict(list)
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            body = post.content or ""
            # Extract (source_hash, body-of-mention) pairs by parsing blocks
            blocks = _split_mentions(body)
            for date_str, label, source_hash, mention_body in blocks:
                if not source_hash:
                    continue
                key = (source_hash, mention_body.strip())
                seen[key].append(f)
    for (h, _b), paths in seen.items():
        if len(paths) > 1:
            files = ", ".join(str(p.relative_to(get_repo_root())) for p in paths)
            results.err(
                f"Duplicate mention with source_hash {h[:12]}… across: {files}"
            )


def _split_mentions(body: str):
    """Yield (date, label, source_hash, mention_body) for each mention block."""
    if "## Mentions" not in body:
        return
    after = body.split("## Mentions", 1)[1]
    if "## " in after:
        after = after.split("\n## ", 1)[0]
    blocks = re.split(r"^### ", after, flags=re.MULTILINE)
    for blk in blocks[1:]:
        first_line, _, rest = blk.partition("\n")
        m = re.match(r"^(\d{4}-\d{2}-\d{2})\s+—\s+(.+)$", first_line.strip())
        if not m:
            continue
        date_str, label = m.group(1), m.group(2).strip()
        hash_match = SOURCE_HASH_RE.search(rest)
        source_hash = hash_match.group(1) if hash_match else ""
        # Strip the comment line out of the body for comparison
        mention_body = SOURCE_HASH_RE.sub("", rest).strip()
        yield date_str, label, source_hash, mention_body


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate schema/consistency.")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    args = parser.parse_args()

    results = Results()
    files = iter_repo_markdown()

    for f in files:
        try:
            post = parse_file(f)
        except Exception as e:
            results.err(f"{f.relative_to(get_repo_root())}: cannot parse frontmatter ({e})")
            continue
        check_frontmatter(f, post, results)
        check_mentions_section(f, post, results)
        check_wiki_links(f, post, results)

    check_no_duplicate_mentions(results)
    return results.report(strict=args.strict)


if __name__ == "__main__":
    sys.exit(main())

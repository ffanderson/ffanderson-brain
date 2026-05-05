#!/usr/bin/env python3
"""Shared utilities for the knowledge system scripts."""

from __future__ import annotations

import hashlib
import re
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional

import frontmatter
from slugify import slugify


# ---------------------------------------------------------------------------
# Paths and dates
# ---------------------------------------------------------------------------

def get_repo_root() -> Path:
    """Repository root directory."""
    return Path(__file__).parent.parent


def today() -> str:
    """Today's date in ISO 8601."""
    return datetime.now().strftime("%Y-%m-%d")


def now() -> str:
    """Current datetime in ISO 8601."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def iso_week(d: Optional[datetime] = None) -> str:
    """ISO week label like '2026-W18'."""
    d = d or datetime.now()
    year, week, _ = d.isocalendar()
    return f"{year}-W{week:02d}"


def make_slug(name: str) -> str:
    """Convert a display name to kebab-case slug."""
    return slugify(name, lowercase=True)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

def load_template(template_name: str) -> str:
    template_path = get_repo_root() / "templates" / f"{template_name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text()


def render_template(template: str, **kwargs) -> str:
    """Replace {{placeholders}} in a template."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    result = result.replace("{{date}}", today())
    return result


# ---------------------------------------------------------------------------
# Frontmatter file IO
# ---------------------------------------------------------------------------

def parse_file(filepath: Path) -> frontmatter.Post:
    return frontmatter.load(filepath)


def save_file(filepath: Path, post: frontmatter.Post) -> None:
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))


# ---------------------------------------------------------------------------
# Wiki-links
# ---------------------------------------------------------------------------

WIKI_LINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def extract_wiki_links(text: str) -> list[str]:
    """Extract wiki-link targets from text. Strips |alias suffixes."""
    return [m.split("|", 1)[0].strip() for m in WIKI_LINK_RE.findall(text)]


def find_entity_file(name: str, entity_type: Optional[str] = None) -> Optional[Path]:
    """Resolve a display name to an entity file via slug, name, or alias."""
    repo_root = get_repo_root()
    target_slug = make_slug(name)
    target_lower = name.lower()

    if entity_type:
        search_dirs = [repo_root / "entities" / entity_type]
    else:
        search_dirs = [
            repo_root / "entities" / "people",
            repo_root / "entities" / "companies",
            repo_root / "entities" / "funds",
            repo_root / "entities" / "concepts",
        ]

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # Slug match by filename stem
        candidate = search_dir / f"{target_slug}.md"
        if candidate.exists():
            return candidate

        for md_file in search_dir.glob("*.md"):
            if md_file.name == ".gitkeep":
                continue
            try:
                post = parse_file(md_file)
            except Exception:
                continue
            if str(post.get("name", "")).lower() == target_lower:
                return md_file
            aliases = post.get("aliases") or []
            if isinstance(aliases, list) and any(
                str(a).lower() == target_lower for a in aliases
            ):
                return md_file
    return None


def list_entities(entity_type: str) -> list[Path]:
    entity_dir = get_repo_root() / "entities" / entity_type
    if not entity_dir.exists():
        return []
    return [f for f in entity_dir.glob("*.md") if f.name != ".gitkeep"]


def get_inbox_items(status: Optional[str] = None) -> list[Path]:
    inbox_dir = get_repo_root() / "inbox"
    if not inbox_dir.exists():
        return []
    items: list[Path] = []
    for md_file in inbox_dir.glob("*.md"):
        if md_file.name == ".gitkeep":
            continue
        if status:
            try:
                post = parse_file(md_file)
                if post.get("status") == status:
                    items.append(md_file)
            except Exception:
                continue
        else:
            items.append(md_file)
    return items


# ---------------------------------------------------------------------------
# Mentions
# ---------------------------------------------------------------------------

MENTIONS_HEADING = "## Mentions"
MENTION_HEADING_RE = re.compile(r"^### (\d{4}-\d{2}-\d{2})\s+—\s+(.+)$", re.MULTILINE)
SOURCE_HASH_RE = re.compile(r"<!--\s*source_hash:\s*([0-9a-f-]+)\s*-->")


def ensure_mentions_section(body: str) -> str:
    """Ensure the body has a ## Mentions section. Returns possibly-modified body."""
    if MENTIONS_HEADING in body:
        return body
    sep = "" if body.endswith("\n") else "\n"
    return body + sep + "\n" + MENTIONS_HEADING + "\n"


def append_mention(
    body: str,
    date: str,
    label: str,
    text: str,
    source_link: str,
    source_hash: str,
) -> str:
    """Insert a new mention at the top of the ## Mentions section (newest first).

    The mention's source hash is recorded as an HTML comment immediately after
    the heading; this lets Sally detect duplicates without having to parse the
    visible source line.
    """
    body = ensure_mentions_section(body)
    block = (
        f"### {date} — {label}\n"
        f"<!-- source_hash: {source_hash} -->\n"
        f"{text.strip()}\n"
        f"↳ source: {source_link}\n"
    )

    # Find the line containing MENTIONS_HEADING
    lines = body.splitlines(keepends=False)
    out_lines: list[str] = []
    inserted = False
    for i, line in enumerate(lines):
        out_lines.append(line)
        if not inserted and line.strip() == MENTIONS_HEADING:
            # Skip any HTML comment block immediately after the heading.
            j = i + 1
            in_comment = False
            while j < len(lines):
                stripped = lines[j].strip()
                if stripped.startswith("<!--"):
                    in_comment = True
                    out_lines.append(lines[j])
                    j += 1
                    if "-->" in stripped:
                        in_comment = False
                    continue
                if in_comment:
                    out_lines.append(lines[j])
                    j += 1
                    if "-->" in stripped:
                        in_comment = False
                    continue
                if stripped == "":
                    out_lines.append(lines[j])
                    j += 1
                    continue
                break
            # Insert the new mention here.
            out_lines.append("")
            out_lines.append(block.rstrip())
            out_lines.append("")
            # Remaining original lines.
            out_lines.extend(lines[j:])
            inserted = True
            break
    if not inserted:
        # MENTIONS_HEADING wasn't found; append to end.
        out_lines.extend(["", MENTIONS_HEADING, "", block.rstrip(), ""])
    return "\n".join(out_lines).rstrip() + "\n"


def count_mentions(body: str) -> int:
    return len(MENTION_HEADING_RE.findall(body))


def latest_mention_date(body: str) -> Optional[str]:
    matches = MENTION_HEADING_RE.findall(body)
    if not matches:
        return None
    dates = [m[0] for m in matches]
    return max(dates)


def has_mention_with_hash(body: str, source_hash: str) -> bool:
    """Whether the body already has a mention with the given source_hash comment."""
    for h in SOURCE_HASH_RE.findall(body):
        if h == source_hash:
            return True
    return False


# ---------------------------------------------------------------------------
# Misc helpers
# ---------------------------------------------------------------------------

def all_entity_files() -> list[Path]:
    files: list[Path] = []
    for t in ["people", "companies", "funds", "concepts"]:
        files.extend(list_entities(t))
    return files


def entity_kind_to_folder(kind: str) -> str:
    """Map 'person' → 'people', etc."""
    mapping = {
        "person": "people",
        "company": "companies",
        "fund": "funds",
        "concept": "concepts",
    }
    if kind not in mapping:
        raise ValueError(f"Unknown entity kind: {kind}")
    return mapping[kind]


def iter_meeting_files() -> Iterable[Path]:
    meetings_dir = get_repo_root() / "meetings"
    if meetings_dir.exists():
        yield from (f for f in meetings_dir.glob("*.md") if f.name != ".gitkeep")

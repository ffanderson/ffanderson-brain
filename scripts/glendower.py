#!/usr/bin/env python3
"""
Glendower — theme scout (Tier 1).

Given an investment theme as free text, walk the corpus for matching
people, companies, funds, and meetings, and write a dossier to
`themes/<slug>.md` listing what the owner already knows in the space.

Tier 2 (web search via the Anthropic SDK) is deferred. See
`agents/glendower.md` for the full spec.

Usage:
    python scripts/glendower.py "AI-native agents for legal discovery"
    python scripts/glendower.py "data center insurance" --slug dc-insurance
    python scripts/glendower.py "vertical agents" --limit 15

Re-running on the same slug overwrites the dossier. The owner's
`## Owner judgement` section is preserved across re-runs if present.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import frontmatter

from utils import (
    MENTION_HEADING_RE,
    extract_wiki_links,
    get_repo_root,
    iter_meeting_files,
    list_entities,
    make_slug,
    parse_file,
    save_file,
    today,
)


# ---------------------------------------------------------------------------
# Keyword extraction
# ---------------------------------------------------------------------------

STOPWORDS = {
    "a", "an", "the", "and", "or", "but", "of", "in", "on", "at", "to", "for",
    "with", "by", "from", "is", "are", "be", "been", "being", "this", "that",
    "these", "those", "it", "its", "as", "if", "than", "into", "via", "vs",
    # VC noise — words present in every theme that don't discriminate
    "ai", "the", "ml", "company", "companies", "team", "teams", "startup",
    "startups", "founder", "founders", "space", "market", "thesis", "deal",
    "deals", "pipeline", "early", "stage", "round", "fund", "funds",
}


def keywords_from_theme(theme: str) -> list[str]:
    """Tokenise into lowercase keywords; strip stopwords; dedupe."""
    raw = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", theme.lower())
    out: list[str] = []
    seen: set[str] = set()
    for tok in raw:
        if len(tok) < 3:
            continue
        if tok in STOPWORDS:
            continue
        if tok in seen:
            continue
        seen.add(tok)
        out.append(tok)
    return out


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

WEIGHTS = {
    "name":     10,
    "alias":     8,
    "tag":       5,
    "category":  3,   # sector, fund_type, category, role, relationship
    "field":     2,   # other frontmatter fields
    "mention":   1,
}


@dataclass
class Hit:
    path: Path
    name: str
    type: str
    score: int = 0
    matched: dict[str, list[str]] = field(default_factory=lambda: defaultdict(list))

    def add(self, where: str, keyword: str) -> None:
        self.score += WEIGHTS[where]
        self.matched[where].append(keyword)

    def matched_summary(self) -> str:
        bits: list[str] = []
        for where in ("name", "alias", "tag", "category", "field", "mention"):
            if where in self.matched and self.matched[where]:
                uniq = sorted(set(self.matched[where]))
                bits.append(f"{where}:{'/'.join(uniq)}")
        return "; ".join(bits)


def keyword_in(text: str, keywords: list[str]) -> list[str]:
    """Return the keywords that appear in `text` (case-insensitive word match)."""
    if not text:
        return []
    lower = text.lower()
    hits = []
    for kw in keywords:
        if re.search(rf"\b{re.escape(kw)}\b", lower):
            hits.append(kw)
    return hits


def score_entity(path: Path, post: frontmatter.Post, keywords: list[str]) -> Hit | None:
    name = str(post.get("name") or path.stem)
    t = str(post.get("type") or "")
    hit = Hit(path=path, name=name, type=t)

    for kw in keyword_in(name, keywords):
        hit.add("name", kw)

    aliases = post.get("aliases") or []
    if isinstance(aliases, list):
        for a in aliases:
            for kw in keyword_in(str(a), keywords):
                hit.add("alias", kw)

    tags = post.get("tags") or []
    if isinstance(tags, list):
        for t_ in tags:
            for kw in keyword_in(str(t_), keywords):
                hit.add("tag", kw)

    for cat_field in ("sector", "category", "fund_type", "role", "relationship"):
        v = post.get(cat_field)
        if v:
            for kw in keyword_in(str(v), keywords):
                hit.add("category", kw)

    for fld in ("company", "website", "location", "stage"):
        v = post.get(fld)
        if v:
            for kw in keyword_in(str(v), keywords):
                hit.add("field", kw)

    body = post.content or ""
    if "## Mentions" in body:
        mentions_blob = body.split("## Mentions", 1)[1]
        # cap mention scan to avoid scoring huge bodies repeatedly
        for kw in keyword_in(mentions_blob, keywords):
            hit.add("mention", kw)

    return hit if hit.score > 0 else None


def score_meeting(path: Path, post: frontmatter.Post, keywords: list[str]) -> Hit | None:
    name = str(post.get("title") or path.stem)
    hit = Hit(path=path, name=name, type="meeting")

    for kw in keyword_in(name, keywords):
        hit.add("name", kw)

    tags = post.get("tags") or []
    if isinstance(tags, list):
        for t_ in tags:
            for kw in keyword_in(str(t_), keywords):
                hit.add("tag", kw)

    body = post.content or ""
    for kw in keyword_in(body, keywords):
        hit.add("mention", kw)

    return hit if hit.score > 0 else None


# ---------------------------------------------------------------------------
# Dossier rendering
# ---------------------------------------------------------------------------

OWNER_HEADING = "## Owner judgement"


def render_in_network(
    by_type: dict[str, list[Hit]],
    limit: int,
) -> str:
    sections: list[str] = []
    labels = [
        ("person", "People"),
        ("company", "Companies"),
        ("fund", "Funds"),
        ("concept", "Concepts"),
    ]
    for kind, label in labels:
        hits = by_type.get(kind) or []
        if not hits:
            continue
        sections.append(f"### {label}")
        sections.append("")
        for hit in hits[:limit]:
            rel = hit.path.relative_to(get_repo_root())
            sections.append(
                f"- [[{hit.name}]] — score {hit.score} · "
                f"{hit.matched_summary()}  _({rel})_"
            )
        if len(hits) > limit:
            sections.append(f"- _…and {len(hits) - limit} more (raise `--limit` to see)._")
        sections.append("")
    return "\n".join(sections).rstrip()


def render_meetings(meetings: list[Hit], limit: int) -> str:
    if not meetings:
        return "_No meetings in the corpus reference this theme._"
    lines = []
    for hit in meetings[:limit]:
        rel = hit.path.relative_to(get_repo_root())
        lines.append(
            f"- [[{hit.path.stem}]] — score {hit.score} · "
            f"{hit.matched_summary()}  _({rel})_"
        )
    if len(meetings) > limit:
        lines.append(f"- _…and {len(meetings) - limit} more._")
    return "\n".join(lines)


def extract_owner_judgement(existing: Path) -> str:
    """Preserve a prior owner-written judgement section across re-runs."""
    if not existing.exists():
        return ""
    try:
        post = parse_file(existing)
    except Exception:
        return ""
    body = post.content or ""
    if OWNER_HEADING not in body:
        return ""
    chunk = body.split(OWNER_HEADING, 1)[1]
    # Stop at next H2 if one follows
    if re.search(r"^## ", chunk, re.MULTILINE):
        chunk = re.split(r"^## ", chunk, flags=re.MULTILINE, maxsplit=1)[0]
    return chunk.rstrip()


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def gather_entity_hits(keywords: list[str]) -> dict[str, list[Hit]]:
    by_type: dict[str, list[Hit]] = defaultdict(list)
    for kind, folder in [("person", "people"), ("company", "companies"),
                         ("fund", "funds"), ("concept", "concepts")]:
        for path in list_entities(folder):
            try:
                post = parse_file(path)
            except Exception:
                continue
            hit = score_entity(path, post, keywords)
            if hit:
                by_type[kind].append(hit)
        by_type[kind].sort(key=lambda h: (-h.score, h.name.lower()))
    return by_type


def gather_meeting_hits(keywords: list[str]) -> list[Hit]:
    out: list[Hit] = []
    repo_root = get_repo_root()
    folders = [
        repo_root / "meetings",
        repo_root / "inbox",
    ]
    for folder in folders:
        if not folder.exists():
            continue
        for path in folder.glob("*.md"):
            if path.name == ".gitkeep":
                continue
            try:
                post = parse_file(path)
            except Exception:
                continue
            t = str(post.get("type") or "")
            if t not in ("meeting", "inbox"):
                continue
            hit = score_meeting(path, post, keywords)
            if hit:
                out.append(hit)
    out.sort(key=lambda h: (-h.score, h.name.lower()))
    return out


def render_dossier(
    theme: str,
    slug: str,
    keywords: list[str],
    by_type: dict[str, list[Hit]],
    meetings: list[Hit],
    owner_judgement: str,
    limit: int,
) -> frontmatter.Post:
    fm = {
        "type": "theme",
        "name": theme,
        "slug": slug,
        "created": today(),
        "agent": "glendower",
        "status": "active",
        "keywords": keywords,
        "last_refreshed": today(),
    }
    body_parts: list[str] = []
    body_parts.append(f"# {theme}")
    body_parts.append("")
    body_parts.append("**Keywords searched.** `" + ", ".join(keywords) + "`")
    body_parts.append("")

    body_parts.append("## Definition")
    body_parts.append("")
    body_parts.append("_(Owner: refine this to a sharp one-paragraph definition of the theme.)_")
    body_parts.append("")

    body_parts.append("## Why now")
    body_parts.append("")
    body_parts.append("_(Owner: catalysts, timing, market signals.)_")
    body_parts.append("")

    body_parts.append("## In-network (corpus)")
    body_parts.append("")
    in_network = render_in_network(by_type, limit=limit)
    body_parts.append(in_network if in_network else "_No corpus entities matched the keyword set._")
    body_parts.append("")

    body_parts.append("## Source meetings")
    body_parts.append("")
    body_parts.append(render_meetings(meetings, limit=limit))
    body_parts.append("")

    body_parts.append("## External — companies")
    body_parts.append("")
    body_parts.append("_(Tier 2, deferred. Glendower's web-search pass will populate this.)_")
    body_parts.append("")

    body_parts.append("## External — founders")
    body_parts.append("")
    body_parts.append("_(Tier 2, deferred.)_")
    body_parts.append("")

    body_parts.append("## Adjacent / tangential")
    body_parts.append("")
    body_parts.append("_(Tier 2, deferred.)_")
    body_parts.append("")

    body_parts.append("## Who in your network is closest")
    body_parts.append("")
    if by_type.get("person"):
        for hit in by_type["person"][:5]:
            body_parts.append(f"- [[{hit.name}]] — matched on {hit.matched_summary()}")
    else:
        body_parts.append("_No person in the corpus matched the keyword set; ask in chat with calendar/email connectors._")
    body_parts.append("")

    body_parts.append("## Open questions")
    body_parts.append("")
    body_parts.append("_(Owner: what's missing from this picture?)_")
    body_parts.append("")

    body_parts.append(OWNER_HEADING)
    body_parts.append("")
    if owner_judgement.strip():
        body_parts.append(owner_judgement.strip())
    else:
        body_parts.append("_(Owner: conviction notes go here. Glendower never writes into this section.)_")
    body_parts.append("")

    return frontmatter.Post(content="\n".join(body_parts), **fm)


def run_glendower(theme: str, slug: str | None, limit: int) -> Path:
    keywords = keywords_from_theme(theme)
    if not keywords:
        raise ValueError("No usable keywords extracted from theme; pass more specific text.")
    derived_slug = slug or make_slug(theme)

    by_type = gather_entity_hits(keywords)
    meetings = gather_meeting_hits(keywords)

    repo_root = get_repo_root()
    out_path = repo_root / "themes" / f"{derived_slug}.md"
    owner_judgement = extract_owner_judgement(out_path)
    post = render_dossier(theme, derived_slug, keywords, by_type, meetings, owner_judgement, limit)
    save_file(out_path, post)
    return out_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Glendower — theme scout (Tier 1, corpus-only).",
    )
    parser.add_argument("theme", help="Theme description, free text")
    parser.add_argument("--slug", help="Override the auto-slug for the output filename")
    parser.add_argument("--limit", type=int, default=25,
                        help="Cap entries shown per bucket (default 25)")
    args = parser.parse_args()

    try:
        path = run_glendower(args.theme, args.slug, args.limit)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    rel = path.relative_to(get_repo_root())
    print(f"Dossier: {rel}")


if __name__ == "__main__":
    main()

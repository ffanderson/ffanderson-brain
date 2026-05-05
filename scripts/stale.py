#!/usr/bin/env python3
"""
stale.py — list relationships that need attention.

Prints entities whose `relationship_strength` is warm/strong/core and whose
`last_mention` (or `last_touch`, as fallback) is more than N days ago.

Usage:
    python scripts/stale.py
    python scripts/stale.py --days 14
    python scripts/stale.py --followups   # also list open follow-ups by age
"""

from __future__ import annotations

import argparse
from datetime import datetime
from pathlib import Path

from utils import (
    extract_wiki_links,
    get_repo_root,
    iter_meeting_files,
    list_entities,
    parse_file,
)


STRENGTHS = {"warm", "strong", "core"}


def days_since(d: str) -> int | None:
    try:
        return (datetime.now().date() - datetime.strptime(str(d)[:10], "%Y-%m-%d").date()).days
    except (ValueError, TypeError):
        return None


def find_stale(threshold: int) -> list[dict]:
    items: list[dict] = []
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            strength = str(post.get("relationship_strength") or "").strip()
            if strength not in STRENGTHS:
                continue
            last = post.get("last_mention") or post.get("last_touch")
            age = days_since(str(last)) if last else None
            if age is None or age > threshold:
                items.append({
                    "name": str(post.get("name", f.stem)),
                    "type": t,
                    "strength": strength,
                    "last": str(last) if last else "(never)",
                    "age": age,
                    "path": f,
                })
    items.sort(key=lambda x: (x["age"] is None, -(x["age"] or 0)))
    return items


def find_followups() -> list[dict]:
    out: list[dict] = []
    repo_root = get_repo_root()
    for f in iter_meeting_files():
        try:
            post = parse_file(f)
        except Exception:
            continue
        meeting_date = str(post.get("date", ""))
        for line in (post.content or "").splitlines():
            if "- [ ]" in line and line.strip() != "- [ ]":
                age = days_since(meeting_date)
                out.append({
                    "source": f.relative_to(repo_root),
                    "line": line.strip(),
                    "age": age,
                })
    out.sort(key=lambda x: (x["age"] is None, -(x["age"] or 0)))
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description="List stale relationships and follow-ups.")
    parser.add_argument("--days", type=int, default=30, help="Stale threshold in days (default 30)")
    parser.add_argument("--followups", action="store_true", help="Also list open follow-ups")
    args = parser.parse_args()

    stale = find_stale(args.days)
    print(f"Stale relationships (> {args.days} days, strength ∈ warm/strong/core):\n")
    if not stale:
        print("  (none)")
    for it in stale:
        age = "never" if it["age"] is None else f"{it['age']}d"
        print(f"  - {it['name']} ({it['strength']}, {it['type']}) — last: {it['last']} ({age})")

    if args.followups:
        ups = find_followups()
        print(f"\nOpen follow-ups ({len(ups)}):\n")
        for it in ups[:50]:
            age = "?" if it["age"] is None else f"{it['age']}d"
            print(f"  - {it['line']}  ({it['source']}, {age})")
        if len(ups) > 50:
            print(f"  …and {len(ups) - 50} more.")


if __name__ == "__main__":
    main()

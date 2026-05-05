#!/usr/bin/env python3
"""
triage_inbox.py — list and promote inbox items.

A meeting in `inbox/` (status `raw`) is promoted to `meetings/` (status
`processed`). When promoting, the user is shown the mentions Sally wrote and
asked to confirm them per entity.

Usage:
    python scripts/triage_inbox.py                # list raw items
    python scripts/triage_inbox.py --all          # list all items
    python scripts/triage_inbox.py promote <file> # promote to meetings/
    python scripts/triage_inbox.py mark-archived <file>
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from utils import (
    SOURCE_HASH_RE,
    get_inbox_items,
    get_repo_root,
    list_entities,
    parse_file,
    save_file,
    today,
)


# ---------------------------------------------------------------------------
# Listing
# ---------------------------------------------------------------------------

def list_inbox(status_filter: str | None = None) -> list[dict]:
    items: list[dict] = []
    for f in sorted(get_inbox_items()):
        try:
            post = parse_file(f)
        except Exception as e:
            print(f"Warning: cannot parse {f}: {e}", file=sys.stderr)
            continue
        item = {
            "path": f,
            "filename": f.name,
            "title": post.get("title", f.stem),
            "source": post.get("source", "unknown"),
            "date": post.get("date") or post.get("received") or "unknown",
            "status": post.get("status", "unknown"),
        }
        if status_filter and item["status"] != status_filter:
            continue
        items.append(item)
    return items


def render_list(items: list[dict]) -> None:
    if not items:
        print("No items.")
        return
    print(f"\nInbox items ({len(items)}):\n")
    print(f"{'Status':<11} {'Source':<10} {'Date':<12} Title")
    print("-" * 70)
    for it in items:
        print(f"{it['status']:<11} {it['source']:<10} {str(it['date']):<12} {str(it['title'])[:40]}")
    print()


# ---------------------------------------------------------------------------
# Mention review during promotion
# ---------------------------------------------------------------------------

def find_mentions_for_meeting(source_hash: str) -> list[tuple[Path, str]]:
    """Return (entity_path, mention_block) for every mention sourced from this meeting."""
    out: list[tuple[Path, str]] = []
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            body = post.content or ""
            if "## Mentions" not in body:
                continue
            after = body.split("## Mentions", 1)[1]
            if "\n## " in after:
                after = after.split("\n## ", 1)[0]
            blocks = re.split(r"^### ", after, flags=re.MULTILINE)
            for blk in blocks[1:]:
                hash_match = SOURCE_HASH_RE.search(blk)
                if not hash_match:
                    continue
                if hash_match.group(1) == source_hash:
                    block_text = "### " + blk.rstrip()
                    out.append((f, block_text))
    return out


def review_mentions(mentions: list[tuple[Path, str]]) -> None:
    if not mentions:
        print("No mentions found for this meeting (Sally may not have written any).")
        return
    distinct = {p for p, _ in mentions}
    print(f"\nSally wrote {len(mentions)} mention(s) across {len(distinct)} entit(ies).")
    answer = input("Review them? [y/N] ").strip().lower()
    if answer != "y":
        print("Skipping review (mentions remain as written).")
        return
    repo_root = get_repo_root()
    for path, block in mentions:
        rel = path.relative_to(repo_root)
        print("\n" + "─" * 70)
        print(f"{rel}\n")
        print(block)
        print("─" * 70)
        choice = input("[a]ccept (default) / [d]iscard / [s]kip remaining: ").strip().lower()
        if choice == "d":
            _discard_mention(path, block)
        elif choice == "s":
            print("Stopping review; remaining mentions kept as-is.")
            return


def _discard_mention(path: Path, block_to_remove: str) -> None:
    post = parse_file(path)
    body = post.content or ""
    new_body = body.replace(block_to_remove + "\n", "", 1)
    if new_body == body:
        new_body = body.replace(block_to_remove, "", 1)
    post.content = new_body
    post["mention_count"] = len(re.findall(r"^### \d{4}-\d{2}-\d{2}", new_body, re.MULTILINE))
    save_file(path, post)
    print(f"Discarded mention from {path.relative_to(get_repo_root())}.")


# ---------------------------------------------------------------------------
# Promotion
# ---------------------------------------------------------------------------

def promote(filepath: Path) -> None:
    if not filepath.exists():
        print(f"Error: not found: {filepath}", file=sys.stderr)
        sys.exit(1)
    post = parse_file(filepath)
    type_ = str(post.get("type"))
    if type_ not in ("meeting", "inbox"):
        print(f"Note: {filepath.name} is type `{type_}`; promoting anyway.")
    source_hash = str(post.get("source_hash") or "")
    if source_hash:
        mentions = find_mentions_for_meeting(source_hash)
        review_mentions(mentions)

    post["type"] = "meeting"
    post["status"] = "processed"
    post["processed_date"] = today()
    repo_root = get_repo_root()
    target = repo_root / "meetings" / filepath.name
    target.parent.mkdir(parents=True, exist_ok=True)
    save_file(target, post)
    filepath.unlink()
    print(f"\nPromoted: inbox/{filepath.name} → meetings/{filepath.name}")


def mark_archived(filepath: Path) -> None:
    post = parse_file(filepath)
    post["status"] = "archived"
    post["archived_date"] = today()
    save_file(filepath, post)
    print(f"Marked archived: {filepath.name}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Triage and promote inbox items.")
    sub = parser.add_subparsers(dest="cmd")

    lst = sub.add_parser("list", help="List inbox items (default)")
    lst.add_argument("--all", action="store_true")
    lst.add_argument("--status")

    pr = sub.add_parser("promote", help="Promote an inbox item to meetings/")
    pr.add_argument("file")

    arch = sub.add_parser("mark-archived", help="Mark an inbox item archived in place")
    arch.add_argument("file")

    args = parser.parse_args()
    repo_root = get_repo_root()

    if args.cmd in (None, "list"):
        status = getattr(args, "status", None)
        if not status and not getattr(args, "all", False):
            status = "raw"
        render_list(list_inbox(status))
        return

    if args.cmd == "promote":
        path = Path(args.file)
        if not path.is_absolute():
            path = repo_root / "inbox" / path.name
        promote(path)
        return

    if args.cmd == "mark-archived":
        path = Path(args.file)
        if not path.is_absolute():
            path = repo_root / "inbox" / path.name
        mark_archived(path)
        return


if __name__ == "__main__":
    main()

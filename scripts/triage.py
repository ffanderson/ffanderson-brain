#!/usr/bin/env python3
"""
Interactive triage helper for inbox items.

Lists unprocessed inbox items and helps move them through the triage workflow.

Usage:
    python triage.py                    # List unprocessed items
    python triage.py --all              # List all inbox items
    python triage.py mark-processed <file>  # Mark an item as processed
"""

import argparse
import sys
from pathlib import Path

import frontmatter

from utils import get_repo_root, get_inbox_items, parse_file, today


def list_inbox(status_filter: str = None) -> list[dict]:
    """
    List inbox items with their metadata.
    
    Args:
        status_filter: Optional status to filter by
    
    Returns:
        List of dicts with file info
    """
    repo_root = get_repo_root()
    inbox_dir = repo_root / "inbox"
    
    items = []
    for md_file in sorted(inbox_dir.glob("*.md")):
        if md_file.name == ".gitkeep":
            continue
        
        try:
            post = parse_file(md_file)
            item = {
                "path": md_file,
                "filename": md_file.name,
                "title": post.get("title", md_file.stem),
                "source": post.get("source", "unknown"),
                "received": post.get("received", "unknown"),
                "status": post.get("status", "unknown"),
            }
            
            if status_filter and item["status"] != status_filter:
                continue
            
            items.append(item)
        except Exception as e:
            print(f"Warning: Could not parse {md_file}: {e}", file=sys.stderr)
    
    return items


def mark_processed(filepath: Path) -> None:
    """Mark an inbox item as processed."""
    post = parse_file(filepath)
    post["status"] = "processed"
    post["processed_date"] = today()
    
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))


def mark_archived(filepath: Path) -> None:
    """Mark an inbox item as archived."""
    post = parse_file(filepath)
    post["status"] = "archived"
    post["archived_date"] = today()
    
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))


def main():
    parser = argparse.ArgumentParser(
        description="Triage inbox items"
    )
    
    subparsers = parser.add_subparsers(dest="command")
    
    # List command (default)
    list_parser = subparsers.add_parser("list", help="List inbox items")
    list_parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show all items, not just unprocessed",
    )
    list_parser.add_argument(
        "--status", "-s",
        help="Filter by specific status",
    )
    
    # Mark processed command
    processed_parser = subparsers.add_parser(
        "mark-processed",
        help="Mark an item as processed"
    )
    processed_parser.add_argument("file", help="Filename or path to mark")
    
    # Mark archived command
    archived_parser = subparsers.add_parser(
        "mark-archived",
        help="Mark an item as archived"
    )
    archived_parser.add_argument("file", help="Filename or path to mark")
    
    args = parser.parse_args()
    
    repo_root = get_repo_root()
    
    # Default to list if no command specified
    if args.command is None or args.command == "list":
        status_filter = None
        if hasattr(args, "status") and args.status:
            status_filter = args.status
        elif not (hasattr(args, "all") and args.all):
            status_filter = "unprocessed"
        
        items = list_inbox(status_filter)
        
        if not items:
            status_msg = f" with status '{status_filter}'" if status_filter else ""
            print(f"No inbox items found{status_msg}")
            return
        
        print(f"\nInbox Items ({len(items)}):\n")
        print(f"{'Status':<12} {'Source':<10} {'Received':<12} {'Title'}")
        print("-" * 70)
        
        for item in items:
            print(
                f"{item['status']:<12} "
                f"{item['source']:<10} "
                f"{item['received']:<12} "
                f"{item['title'][:40]}"
            )
        
        print()
    
    elif args.command == "mark-processed":
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = repo_root / "inbox" / filepath
        
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        
        mark_processed(filepath)
        print(f"Marked as processed: {filepath.name}")
    
    elif args.command == "mark-archived":
        filepath = Path(args.file)
        if not filepath.is_absolute():
            filepath = repo_root / "inbox" / filepath
        
        if not filepath.exists():
            print(f"Error: File not found: {filepath}", file=sys.stderr)
            sys.exit(1)
        
        mark_archived(filepath)
        print(f"Marked as archived: {filepath.name}")


if __name__ == "__main__":
    main()

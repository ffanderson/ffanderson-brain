#!/usr/bin/env python3
"""
Create a new daily journal entry.

Usage:
    python create_journal.py              # Creates today's entry
    python create_journal.py 2026-05-10   # Creates entry for specific date
"""

import argparse
import sys
from pathlib import Path

import frontmatter

from utils import get_repo_root, load_template, render_template, today


def create_journal(date: str = None, force: bool = False) -> Path:
    """
    Create a new journal entry.
    
    Args:
        date: Journal date (ISO 8601), defaults to today
        force: Overwrite existing file if True
    
    Returns:
        Path to the created file
    """
    repo_root = get_repo_root()
    journal_date = date or today()
    filepath = repo_root / "journal" / f"{journal_date}.md"
    
    if filepath.exists() and not force:
        raise FileExistsError(f"Journal entry already exists: {filepath}")
    
    # Load and render template
    template = load_template("journal")
    content = render_template(template, date=journal_date)
    
    # Parse the rendered template
    post = frontmatter.loads(content)
    post["date"] = journal_date
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Create a new daily journal entry"
    )
    parser.add_argument(
        "date",
        nargs="?",
        help="Journal date (ISO 8601), defaults to today",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing file",
    )
    
    args = parser.parse_args()
    
    try:
        filepath = create_journal(args.date, force=args.force)
        print(f"Created: {filepath}")
    except FileExistsError as e:
        print(f"Error: {e}", file=sys.stderr)
        print("Use --force to overwrite", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

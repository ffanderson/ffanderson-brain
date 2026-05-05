#!/usr/bin/env python3
"""
Create a new meeting file.

Usage:
    python create_meeting.py "Call with John Smith"
    python create_meeting.py "Board Meeting" --date 2026-05-10 --source granola
    python create_meeting.py "Intro call" --attendees "John Smith,Jane Doe"
"""

import argparse
import sys
from pathlib import Path

import frontmatter

from utils import get_repo_root, load_template, make_slug, render_template, today


def create_meeting(
    title: str,
    date: str = None,
    source: str = None,
    attendees: list = None,
    companies: list = None,
    funds: list = None,
    force: bool = False,
) -> Path:
    """
    Create a new meeting file.
    
    Args:
        title: Meeting title
        date: Meeting date (ISO 8601), defaults to today
        source: Recording source (plaud, granola, manual)
        attendees: List of attendee names
        companies: List of company names
        funds: List of fund names
        force: Overwrite existing file if True
    
    Returns:
        Path to the created file
    """
    repo_root = get_repo_root()
    meeting_date = date or today()
    slug = f"{meeting_date}-{make_slug(title)}"
    filepath = repo_root / "meetings" / f"{slug}.md"
    
    if filepath.exists() and not force:
        raise FileExistsError(f"Meeting file already exists: {filepath}")
    
    # Load and render template
    template = load_template("meeting")
    content = render_template(template, title=title, date=meeting_date)
    
    # Parse the rendered template to modify frontmatter
    post = frontmatter.loads(content)
    post["title"] = title
    post["slug"] = slug
    post["date"] = meeting_date
    
    if source:
        post["source"] = source
    
    # Convert attendee names to wiki-links
    if attendees:
        post["attendees"] = [f"[[{name}]]" for name in attendees]
    
    if companies:
        post["companies"] = [f"[[{name}]]" for name in companies]
    
    if funds:
        post["funds"] = [f"[[{name}]]" for name in funds]
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Create a new meeting file"
    )
    parser.add_argument(
        "title",
        help="Meeting title",
    )
    parser.add_argument(
        "--date", "-d",
        help="Meeting date (ISO 8601), defaults to today",
    )
    parser.add_argument(
        "--source", "-s",
        choices=["plaud", "granola", "manual"],
        help="Recording source",
    )
    parser.add_argument(
        "--attendees", "-a",
        help="Comma-separated list of attendee names",
    )
    parser.add_argument(
        "--companies", "-c",
        help="Comma-separated list of company names",
    )
    parser.add_argument(
        "--funds", "-f",
        help="Comma-separated list of fund names",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing file",
    )
    
    args = parser.parse_args()
    
    attendees = None
    if args.attendees:
        attendees = [a.strip() for a in args.attendees.split(",")]
    
    companies = None
    if args.companies:
        companies = [c.strip() for c in args.companies.split(",")]
    
    funds = None
    if args.funds:
        funds = [f.strip() for f in args.funds.split(",")]
    
    try:
        filepath = create_meeting(
            args.title,
            date=args.date,
            source=args.source,
            attendees=attendees,
            companies=companies,
            funds=funds,
            force=args.force,
        )
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

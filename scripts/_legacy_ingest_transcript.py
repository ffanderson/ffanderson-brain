#!/usr/bin/env python3
"""
Ingest a transcript file into the inbox.

This script takes a raw transcript file (from PLAUD, Granola, or other sources)
and creates a properly formatted inbox item for triage.

Usage:
    python ingest_transcript.py transcript.txt --source plaud
    python ingest_transcript.py meeting.md --source granola --title "Call with John"
"""

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

import frontmatter

from utils import get_repo_root, make_slug, today


def detect_source(content: str, filename: str) -> str:
    """Attempt to detect the transcript source from content or filename."""
    content_lower = content.lower()
    filename_lower = filename.lower()
    
    if "plaud" in content_lower or "plaud" in filename_lower:
        return "plaud"
    if "granola" in content_lower or "granola" in filename_lower:
        return "granola"
    if "otter" in content_lower or "otter" in filename_lower:
        return "otter"
    if "zoom" in content_lower:
        return "zoom"
    
    return "unknown"


def extract_title(content: str, filename: str) -> str:
    """Attempt to extract a title from content or filename."""
    # Try to find a title in the first few lines
    lines = content.strip().split("\n")[:10]
    
    for line in lines:
        line = line.strip()
        # Skip empty lines and common headers
        if not line or line.startswith("#"):
            # If it's a markdown header, use it
            if line.startswith("#"):
                return line.lstrip("#").strip()
            continue
        # Use first substantial line as title
        if len(line) > 5 and len(line) < 100:
            return line
    
    # Fall back to filename without extension
    return Path(filename).stem


def extract_date(content: str, filename: str) -> str:
    """Attempt to extract a date from content or filename."""
    # Common date patterns
    patterns = [
        r"(\d{4}-\d{2}-\d{2})",  # ISO 8601
        r"(\d{2}/\d{2}/\d{4})",  # US format
        r"(\d{2}-\d{2}-\d{4})",  # Alternative
    ]
    
    # Check filename first
    for pattern in patterns:
        match = re.search(pattern, filename)
        if match:
            date_str = match.group(1)
            # Normalize to ISO 8601
            if "/" in date_str:
                parts = date_str.split("/")
                return f"{parts[2]}-{parts[0]}-{parts[1]}"
            return date_str
    
    # Check content
    for pattern in patterns:
        match = re.search(pattern, content[:500])
        if match:
            date_str = match.group(1)
            if "/" in date_str:
                parts = date_str.split("/")
                return f"{parts[2]}-{parts[0]}-{parts[1]}"
            return date_str
    
    return today()


def ingest_transcript(
    filepath: Path,
    source: str = None,
    title: str = None,
    date: str = None,
) -> Path:
    """
    Ingest a transcript file into the inbox.
    
    Args:
        filepath: Path to the transcript file
        source: Recording source (plaud, granola, etc.)
        title: Override title
        date: Override date
    
    Returns:
        Path to the created inbox item
    """
    repo_root = get_repo_root()
    
    # Read the source file
    content = filepath.read_text()
    filename = filepath.name
    
    # Extract/detect metadata
    detected_source = source or detect_source(content, filename)
    detected_title = title or extract_title(content, filename)
    detected_date = date or extract_date(content, filename)
    
    # Create slug and output path
    slug = f"{detected_date}-{make_slug(detected_title)}"
    output_path = repo_root / "inbox" / f"{slug}.md"
    
    # Handle collision
    counter = 1
    while output_path.exists():
        output_path = repo_root / "inbox" / f"{slug}-{counter}.md"
        counter += 1
    
    # Build the inbox item
    post = frontmatter.Post(content="")
    post["type"] = "inbox"
    post["title"] = detected_title
    post["source"] = detected_source
    post["received"] = detected_date
    post["created"] = today()
    post["status"] = "unprocessed"
    post["original_file"] = filename
    
    # Build body
    body = f"""# {detected_title}

## Metadata
- **Source**: {detected_source}
- **Date**: {detected_date}
- **Original file**: {filename}

## Extracted Entities
<!-- TODO: Extract people, companies, key topics -->

## Next Actions
- [ ] Extract key entities and create/link files
- [ ] Summarize key points
- [ ] Identify follow-up actions

## Raw Transcript

{content}
"""
    
    post.content = body
    
    # Write file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        f.write(frontmatter.dumps(post))
    
    return output_path


def main():
    parser = argparse.ArgumentParser(
        description="Ingest a transcript file into the inbox"
    )
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the transcript file",
    )
    parser.add_argument(
        "--source", "-s",
        choices=["plaud", "granola", "otter", "zoom", "manual", "unknown"],
        help="Recording source (auto-detected if not specified)",
    )
    parser.add_argument(
        "--title", "-t",
        help="Override title (auto-extracted if not specified)",
    )
    parser.add_argument(
        "--date", "-d",
        help="Override date (auto-extracted if not specified)",
    )
    
    args = parser.parse_args()
    
    if not args.file.exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        output_path = ingest_transcript(
            args.file,
            source=args.source,
            title=args.title,
            date=args.date,
        )
        print(f"Ingested: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

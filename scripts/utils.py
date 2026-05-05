#!/usr/bin/env python3
"""
Shared utilities for the knowledge system scripts.
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

import frontmatter
from slugify import slugify


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent


def today() -> str:
    """Return today's date in ISO 8601 format."""
    return datetime.now().strftime("%Y-%m-%d")


def now() -> str:
    """Return current datetime in ISO 8601 format."""
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def make_slug(name: str) -> str:
    """Convert a display name to a kebab-case slug."""
    return slugify(name, lowercase=True)


def load_template(template_name: str) -> str:
    """Load a template file and return its contents."""
    template_path = get_repo_root() / "templates" / f"{template_name}.md"
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")
    return template_path.read_text()


def render_template(template: str, **kwargs) -> str:
    """Replace {{placeholders}} in template with provided values."""
    result = template
    for key, value in kwargs.items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    # Replace remaining {{date}} with today's date
    result = result.replace("{{date}}", today())
    return result


def parse_file(filepath: Path) -> frontmatter.Post:
    """Parse a Markdown file and return frontmatter Post object."""
    return frontmatter.load(filepath)


def save_file(filepath: Path, post: frontmatter.Post) -> None:
    """Save a frontmatter Post object to a file."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))


def extract_wiki_links(text: str) -> list[str]:
    """Extract all [[wiki-links]] from text."""
    pattern = r"\[\[([^\]]+)\]\]"
    return re.findall(pattern, text)


def find_entity_file(name: str, entity_type: Optional[str] = None) -> Optional[Path]:
    """
    Find an entity file by name or slug.
    
    Args:
        name: Display name or slug to search for
        entity_type: Optional type (people, companies, funds, concepts) to narrow search
    
    Returns:
        Path to the entity file if found, None otherwise
    """
    repo_root = get_repo_root()
    slug = make_slug(name)
    
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
        
        # Try exact slug match first
        candidate = search_dir / f"{slug}.md"
        if candidate.exists():
            return candidate
        
        # Search by frontmatter name field
        for md_file in search_dir.glob("*.md"):
            try:
                post = parse_file(md_file)
                if post.get("name", "").lower() == name.lower():
                    return md_file
                if post.get("slug", "") == slug:
                    return md_file
            except Exception:
                continue
    
    return None


def list_entities(entity_type: str) -> list[Path]:
    """List all entity files of a given type."""
    entity_dir = get_repo_root() / "entities" / entity_type
    if not entity_dir.exists():
        return []
    return [f for f in entity_dir.glob("*.md") if f.name != ".gitkeep"]


def get_inbox_items(status: Optional[str] = None) -> list[Path]:
    """
    Get items from the inbox folder.
    
    Args:
        status: Optional status filter (e.g., 'unprocessed')
    """
    inbox_dir = get_repo_root() / "inbox"
    items = []
    
    for md_file in inbox_dir.glob("*.md"):
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

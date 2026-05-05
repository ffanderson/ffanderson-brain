#!/usr/bin/env python3
"""
Check for broken wiki-links and orphaned entities.

Usage:
    python check_links.py           # Full check
    python check_links.py --broken  # Only show broken links
    python check_links.py --orphans # Only show orphaned entities
"""

import argparse
from collections import defaultdict
from pathlib import Path

from utils import (
    extract_wiki_links,
    find_entity_file,
    get_repo_root,
    list_entities,
    parse_file,
)


def find_all_links() -> dict[Path, list[str]]:
    """
    Find all wiki-links in all markdown files.
    
    Returns:
        Dict mapping file paths to lists of wiki-link targets
    """
    repo_root = get_repo_root()
    links = {}
    
    # Search all markdown files
    for md_file in repo_root.rglob("*.md"):
        # Skip templates
        if "templates" in md_file.parts:
            continue
        
        try:
            content = md_file.read_text()
            file_links = extract_wiki_links(content)
            if file_links:
                links[md_file] = file_links
        except Exception:
            continue
    
    return links


def find_all_entities() -> dict[str, Path]:
    """
    Find all entity files and their names.
    
    Returns:
        Dict mapping entity names (lowercase) to file paths
    """
    entities = {}
    
    for entity_type in ["people", "companies", "funds", "concepts"]:
        for filepath in list_entities(entity_type):
            try:
                post = parse_file(filepath)
                name = post.get("name", filepath.stem)
                entities[name.lower()] = filepath
            except Exception:
                continue
    
    return entities


def check_broken_links(all_links: dict, all_entities: dict) -> dict[Path, list[str]]:
    """
    Find links that don't resolve to any entity.
    
    Returns:
        Dict mapping files to lists of broken link targets
    """
    broken = {}
    
    for filepath, links in all_links.items():
        file_broken = []
        for link in links:
            # Check if link resolves
            if link.lower() not in all_entities:
                # Also check if there's a file match
                if not find_entity_file(link):
                    file_broken.append(link)
        
        if file_broken:
            broken[filepath] = file_broken
    
    return broken


def check_orphaned_entities(all_links: dict, all_entities: dict) -> list[Path]:
    """
    Find entities that are never linked to.
    
    Returns:
        List of orphaned entity file paths
    """
    # Collect all link targets (lowercase)
    linked = set()
    for links in all_links.values():
        for link in links:
            linked.add(link.lower())
    
    # Find entities not in linked set
    orphans = []
    for name, filepath in all_entities.items():
        if name not in linked:
            orphans.append(filepath)
    
    return orphans


def main():
    parser = argparse.ArgumentParser(
        description="Check for broken wiki-links and orphaned entities"
    )
    parser.add_argument(
        "--broken", "-b",
        action="store_true",
        help="Only show broken links",
    )
    parser.add_argument(
        "--orphans", "-o",
        action="store_true",
        help="Only show orphaned entities",
    )
    
    args = parser.parse_args()
    
    # Default to showing everything
    show_broken = args.broken or not (args.broken or args.orphans)
    show_orphans = args.orphans or not (args.broken or args.orphans)
    
    print("Scanning repository...")
    all_links = find_all_links()
    all_entities = find_all_entities()
    
    print(f"Found {sum(len(v) for v in all_links.values())} wiki-links in {len(all_links)} files")
    print(f"Found {len(all_entities)} entities\n")
    
    if show_broken:
        broken = check_broken_links(all_links, all_entities)
        
        if broken:
            print("Broken Links:")
            print("-" * 50)
            for filepath, links in sorted(broken.items()):
                rel_path = filepath.relative_to(get_repo_root())
                print(f"\n{rel_path}:")
                for link in links:
                    print(f"  - [[{link}]]")
            print()
        else:
            print("No broken links found.\n")
    
    if show_orphans:
        orphans = check_orphaned_entities(all_links, all_entities)
        
        if orphans:
            print("Orphaned Entities (never linked to):")
            print("-" * 50)
            for filepath in sorted(orphans):
                rel_path = filepath.relative_to(get_repo_root())
                print(f"  - {rel_path}")
            print()
        else:
            print("No orphaned entities found.\n")
    
    # Summary
    broken = check_broken_links(all_links, all_entities)
    orphans = check_orphaned_entities(all_links, all_entities)
    
    total_issues = sum(len(v) for v in broken.values()) + len(orphans)
    if total_issues > 0:
        print(f"Total issues: {total_issues}")
    else:
        print("All checks passed!")


if __name__ == "__main__":
    main()

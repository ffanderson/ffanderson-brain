#!/usr/bin/env python3
"""
Create a new entity file from a template.

Usage:
    python create_entity.py person "John Smith"
    python create_entity.py company "Acme Corp" --sector ai --stage seed
    python create_entity.py fund "Sequoia Capital"
    python create_entity.py concept "AI Agents Thesis"
"""

import argparse
import sys
from pathlib import Path

import frontmatter

from utils import get_repo_root, load_template, make_slug, render_template, today


ENTITY_TYPES = ["person", "company", "fund", "concept"]

TYPE_TO_FOLDER = {
    "person": "people",
    "company": "companies",
    "fund": "funds",
    "concept": "concepts",
}


def create_entity(
    entity_type: str,
    name: str,
    extra_fields: dict = None,
    force: bool = False,
) -> Path:
    """
    Create a new entity file.
    
    Args:
        entity_type: Type of entity (person, company, fund, concept)
        name: Display name for the entity
        extra_fields: Additional frontmatter fields to set
        force: Overwrite existing file if True
    
    Returns:
        Path to the created file
    """
    if entity_type not in ENTITY_TYPES:
        raise ValueError(f"Unknown entity type: {entity_type}. Must be one of {ENTITY_TYPES}")
    
    repo_root = get_repo_root()
    slug = make_slug(name)
    folder = TYPE_TO_FOLDER[entity_type]
    filepath = repo_root / "entities" / folder / f"{slug}.md"
    
    if filepath.exists() and not force:
        raise FileExistsError(f"Entity already exists: {filepath}")
    
    # Load and render template
    template = load_template(entity_type)
    content = render_template(template, name=name, date=today())
    
    # Parse the rendered template to modify frontmatter
    post = frontmatter.loads(content)
    post["name"] = name
    post["slug"] = slug
    
    # Add extra fields
    if extra_fields:
        for key, value in extra_fields.items():
            post[key] = value
    
    # Ensure directory exists
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Write file
    with open(filepath, "w") as f:
        f.write(frontmatter.dumps(post))
    
    return filepath


def main():
    parser = argparse.ArgumentParser(
        description="Create a new entity file from template"
    )
    parser.add_argument(
        "type",
        choices=ENTITY_TYPES,
        help="Entity type to create",
    )
    parser.add_argument(
        "name",
        help="Display name for the entity",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing file",
    )
    
    # Entity-specific optional fields
    parser.add_argument("--role", help="(person) Role/title")
    parser.add_argument("--company", help="(person) Company name")
    parser.add_argument("--email", help="(person) Email address")
    parser.add_argument("--sector", help="(company) Sector")
    parser.add_argument("--stage", help="(company) Stage")
    parser.add_argument("--status", help="Status field")
    parser.add_argument("--crm-id", help="CRM ID for linking")
    parser.add_argument("--tags", help="Comma-separated tags")
    
    args = parser.parse_args()
    
    # Build extra fields dict
    extra_fields = {}
    
    if args.role:
        extra_fields["role"] = args.role
    if args.company:
        extra_fields["company"] = args.company
    if args.email:
        extra_fields["email"] = args.email
    if args.sector:
        extra_fields["sector"] = args.sector
    if args.stage:
        extra_fields["stage"] = args.stage
    if args.status:
        extra_fields["status"] = args.status
    if args.crm_id:
        extra_fields["crm_id"] = args.crm_id
    if args.tags:
        extra_fields["tags"] = [t.strip() for t in args.tags.split(",")]
    
    try:
        filepath = create_entity(
            args.type,
            args.name,
            extra_fields=extra_fields,
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

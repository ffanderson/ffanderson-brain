#!/usr/bin/env python3
"""
Falstaff — meeting scribe.

Reads a raw transcript, writes a meeting file in inbox/, creates stubs for any
unresolved entities, and appends mentions to every entity the meeting touched.

Usage:
    python scripts/falstaff.py path/to/transcript.txt
    python scripts/falstaff.py path/to/transcript.txt --source granola --dry-run
    LLM_MOCK=1 python scripts/falstaff.py fixtures/test.txt --dry-run

Idempotency: Falstaff records a SHA-256 of the transcript bytes as `source_hash`
on the meeting file and on each mention. Re-running on the same transcript
detects this and refuses to write duplicates.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import frontmatter

from llm_client import LLMClient
from utils import (
    all_entity_files,
    append_mention,
    count_mentions,
    ensure_mentions_section,
    entity_kind_to_folder,
    find_entity_file,
    get_repo_root,
    has_mention_with_hash,
    iter_meeting_files,
    latest_mention_date,
    make_slug,
    parse_file,
    save_file,
    sha256_bytes,
    today,
)


PROMPTS_DIR = Path(__file__).parent / "prompts"
SUPPORTED_KINDS = {"person", "company", "fund"}


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Mention:
    entity: str
    entity_type: str  # person | company | fund
    label: str
    body: str

    def is_valid(self) -> bool:
        return (
            bool(self.entity)
            and self.entity_type in SUPPORTED_KINDS
            and bool(self.label)
            and bool(self.body)
        )


@dataclass
class RunSummary:
    meeting_file: Optional[Path] = None
    skipped_existing: bool = False
    stubs_created: list[Path] = field(default_factory=list)
    mentions_written: list[tuple[Path, Mention]] = field(default_factory=list)
    ambiguities: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Source detection (filename only — no content sniffing)
# ---------------------------------------------------------------------------

KNOWN_SOURCES = ("plaud", "granola", "otter", "zoom")


def detect_source_from_filename(filename: str) -> str:
    name = filename.lower()
    for s in KNOWN_SOURCES:
        if s in name:
            return s
    return "unknown"


# ---------------------------------------------------------------------------
# Prompt loaders
# ---------------------------------------------------------------------------

def load_prompt(name: str) -> str:
    path = PROMPTS_DIR / f"{name}.md"
    if not path.exists():
        raise FileNotFoundError(f"Prompt not found: {path}")
    return path.read_text()


# ---------------------------------------------------------------------------
# Metadata extraction
# ---------------------------------------------------------------------------

def extract_metadata(client: LLMClient, transcript: str) -> dict:
    """Ask Claude for structured metadata. Falls back to safe defaults on mock."""
    system = load_prompt("falstaff_metadata")
    response = client.complete(
        prompt=transcript,
        system=system,
        response_format="json",
    )
    try:
        return response.as_json()
    except json.JSONDecodeError:
        # Mock or malformed; degrade gracefully.
        return {
            "title": None,
            "date": None,
            "medium": "unknown",
            "attendees": [],
            "companies": [],
            "funds": [],
            "summary": "",
        }


# ---------------------------------------------------------------------------
# Entity resolution
# ---------------------------------------------------------------------------

@dataclass
class ResolvedEntity:
    name: str
    kind: str  # person | company | fund
    file: Optional[Path]  # None if stub-to-be-created
    is_stub: bool


def resolve_entities(
    attendees: list[str],
    companies: list[str],
    funds: list[str],
) -> tuple[list[ResolvedEntity], list[str]]:
    """Return (resolved entities, ambiguity messages)."""
    resolved: list[ResolvedEntity] = []
    ambiguities: list[str] = []

    def _resolve(name: str, kind: str) -> None:
        if not name or not name.strip():
            return
        # Disambiguation: short single-word names (likely first names) get flagged.
        if " " not in name.strip() and len(name.strip()) < 12 and kind == "person":
            ambiguities.append(
                f"Ambiguous person reference: '{name}' — only a first name. "
                "Falstaff created a stub but the owner should disambiguate."
            )
        path = find_entity_file(name, entity_type=entity_kind_to_folder(kind))
        resolved.append(
            ResolvedEntity(
                name=name.strip(),
                kind=kind,
                file=path,
                is_stub=path is None,
            )
        )

    for n in attendees:
        _resolve(n, "person")
    for n in companies:
        _resolve(n, "company")
    for n in funds:
        _resolve(n, "fund")

    return resolved, ambiguities


# ---------------------------------------------------------------------------
# Stub creation
# ---------------------------------------------------------------------------

def create_stub(entity: ResolvedEntity, dry_run: bool) -> Path:
    """Create a minimal entity file with only the Mentions section."""
    repo_root = get_repo_root()
    folder = entity_kind_to_folder(entity.kind)
    slug = make_slug(entity.name)
    path = repo_root / "entities" / folder / f"{slug}.md"
    if path.exists():
        return path  # not actually a stub; treat as resolved

    fm: dict = {
        "type": entity.kind,
        "name": entity.name,
        "aliases": [],
        "crm_system": "",
        "crm_id": "",
        "created": today(),
        "first_seen": today(),
        "last_mention": "",
        "mention_count": 0,
        "tags": [],
        "status": "active",
    }
    if entity.kind == "person":
        fm.update({
            "role": "",
            "company": "",
            "relationship": "",
            "relationship_strength": "cold",
            "last_touch": "",
            "email": "",
            "linkedin": "",
            "location": "",
        })
    elif entity.kind == "company":
        fm.update({
            "stage": "",
            "sector": "",
            "status": "tracking",
            "founders": [],
            "website": "",
            "location": "",
            "founded": "",
            "last_touch": "",
        })
    elif entity.kind == "fund":
        fm.update({
            "fund_type": "",
            "relationship": "",
            "location": "",
            "website": "",
            "last_touch": "",
        })

    body = f"# {entity.name}\n\n## Mentions\n"
    post = frontmatter.Post(content=body, **fm)

    if not dry_run:
        save_file(path, post)
    return path


# ---------------------------------------------------------------------------
# Mention extraction
# ---------------------------------------------------------------------------

def extract_mentions(
    client: LLMClient,
    transcript: str,
    metadata: dict,
    resolved: list[ResolvedEntity],
) -> list[Mention]:
    if not resolved:
        return []
    system = load_prompt("falstaff_mentions")
    entity_lines = "\n".join(f"- {e.name} ({e.kind})" for e in resolved)
    user = (
        "## Resolved entities\n\n"
        f"{entity_lines}\n\n"
        "## Meeting summary\n\n"
        f"{metadata.get('summary', '')}\n\n"
        "## Transcript\n\n"
        f"{transcript}\n"
    )
    response = client.complete(prompt=user, system=system, response_format="json")
    try:
        data = response.as_json()
    except json.JSONDecodeError:
        return []
    raw = data.get("mentions") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return []
    mentions: list[Mention] = []
    for m in raw:
        if not isinstance(m, dict):
            continue
        ment = Mention(
            entity=str(m.get("entity", "")).strip(),
            entity_type=str(m.get("entity_type", "")).strip(),
            label=str(m.get("label", "")).strip(),
            body=str(m.get("body", "")).strip(),
        )
        if ment.is_valid():
            mentions.append(ment)
    return mentions


# ---------------------------------------------------------------------------
# Idempotency
# ---------------------------------------------------------------------------

def existing_meeting_with_hash(source_hash: str) -> Optional[Path]:
    repo_root = get_repo_root()
    candidates = list(iter_meeting_files()) + [
        f for f in (repo_root / "inbox").glob("*.md") if f.name != ".gitkeep"
    ] if (repo_root / "inbox").exists() else list(iter_meeting_files())
    for f in candidates:
        try:
            post = parse_file(f)
        except Exception:
            continue
        if str(post.get("source_hash", "")) == source_hash:
            return f
    return None


# ---------------------------------------------------------------------------
# Meeting file rendering
# ---------------------------------------------------------------------------

def render_meeting_file(metadata: dict, source_hash: str, source: str) -> frontmatter.Post:
    title = metadata.get("title") or "Untitled meeting"
    date = metadata.get("date") or today()
    fm = {
        "type": "meeting",
        "title": title,
        "date": date,
        "created": today(),
        "source": source,
        "source_hash": source_hash,
        "attendees": [f"[[{n}]]" for n in (metadata.get("attendees") or [])],
        "companies": [f"[[{n}]]" for n in (metadata.get("companies") or [])],
        "funds": [f"[[{n}]]" for n in (metadata.get("funds") or [])],
        "tags": [],
        "status": "raw",
    }
    summary = metadata.get("summary") or ""
    body = (
        f"# {title}\n\n"
        f"## Context\n\n{summary}\n\n"
        f"## Notes\n\n"
        f"## Synthesis\n\n"
        f"## Follow-ups\n\n- [ ] \n"
    )
    return frontmatter.Post(content=body, **fm)


# ---------------------------------------------------------------------------
# Append mention to entity file
# ---------------------------------------------------------------------------

def write_mention_to_entity(
    entity_path: Path,
    mention: Mention,
    meeting_filename: str,
    source_hash: str,
    mention_date: str,
    dry_run: bool,
) -> bool:
    """Returns True if a mention was written (not a duplicate)."""
    post = parse_file(entity_path)
    body = ensure_mentions_section(post.content or "")
    if has_mention_with_hash(body, source_hash):
        return False  # already present
    source_link = f"[[{Path(meeting_filename).stem}]]"
    new_body = append_mention(
        body=body,
        date=mention_date,
        label=mention.label,
        text=mention.body,
        source_link=source_link,
        source_hash=source_hash,
    )
    post.content = new_body
    post["mention_count"] = count_mentions(new_body)
    latest = latest_mention_date(new_body)
    if latest:
        post["last_mention"] = latest
    if not dry_run:
        save_file(entity_path, post)
    return True


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_sally(
    transcript_path: Path,
    source: Optional[str],
    title_override: Optional[str],
    date_override: Optional[str],
    dry_run: bool,
) -> RunSummary:
    summary = RunSummary()
    raw = transcript_path.read_bytes()
    transcript = raw.decode("utf-8", errors="replace")
    source_hash = sha256_bytes(raw)

    existing = existing_meeting_with_hash(source_hash)
    if existing:
        summary.skipped_existing = True
        summary.meeting_file = existing
        summary.warnings.append(
            f"Source hash {source_hash[:12]}… already ingested into {existing.relative_to(get_repo_root())}"
        )
        return summary

    client = LLMClient()
    metadata = extract_metadata(client, transcript)

    if title_override:
        metadata["title"] = title_override
    if date_override:
        metadata["date"] = date_override
    medium = source or detect_source_from_filename(transcript_path.name)
    if not metadata.get("medium"):
        metadata["medium"] = medium

    resolved, ambiguities = resolve_entities(
        attendees=metadata.get("attendees") or [],
        companies=metadata.get("companies") or [],
        funds=metadata.get("funds") or [],
    )
    summary.ambiguities.extend(ambiguities)

    # Create stubs for unresolved entities.
    for ent in resolved:
        if ent.is_stub:
            stub_path = create_stub(ent, dry_run=dry_run)
            ent.file = stub_path
            summary.stubs_created.append(stub_path)

    # Render meeting file.
    meeting_post = render_meeting_file(metadata, source_hash=source_hash, source=medium)
    title = meeting_post["title"]
    meeting_date = meeting_post["date"]
    slug = f"{meeting_date}-{make_slug(title)}"
    meeting_path = get_repo_root() / "inbox" / f"{slug}.md"
    counter = 1
    while meeting_path.exists() and not dry_run:
        meeting_path = get_repo_root() / "inbox" / f"{slug}-{counter}.md"
        counter += 1
    summary.meeting_file = meeting_path
    if not dry_run:
        save_file(meeting_path, meeting_post)

    # Extract and write mentions.
    mentions = extract_mentions(client, transcript, metadata, resolved)
    by_name = {e.name.lower(): e for e in resolved}
    for ment in mentions:
        target = by_name.get(ment.entity.lower())
        if target is None or target.file is None:
            summary.warnings.append(
                f"Mention for '{ment.entity}' did not match a resolved entity; skipped."
            )
            continue
        wrote = write_mention_to_entity(
            entity_path=target.file,
            mention=ment,
            meeting_filename=meeting_path.name,
            source_hash=source_hash,
            mention_date=meeting_date,
            dry_run=dry_run,
        )
        if wrote:
            summary.mentions_written.append((target.file, ment))

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_summary(summary: RunSummary) -> None:
    repo_root = get_repo_root()
    print()
    if summary.skipped_existing and summary.meeting_file:
        print(f"Skipped — already ingested: {summary.meeting_file.relative_to(repo_root)}")
        for w in summary.warnings:
            print(f"  ! {w}")
        return
    if summary.meeting_file:
        print(f"Meeting file: {summary.meeting_file.relative_to(repo_root)}")
    if summary.stubs_created:
        print(f"\nStubs created ({len(summary.stubs_created)}):")
        for p in summary.stubs_created:
            print(f"  + {p.relative_to(repo_root)}")
    if summary.mentions_written:
        print(f"\nMentions written ({len(summary.mentions_written)}):")
        for path, ment in summary.mentions_written:
            print(f"  → {path.relative_to(repo_root)}: {ment.label}")
    if summary.ambiguities:
        print("\nAmbiguities flagged:")
        for a in summary.ambiguities:
            print(f"  ? {a}")
    if summary.warnings:
        print("\nWarnings:")
        for w in summary.warnings:
            print(f"  ! {w}")
    if not (summary.mentions_written or summary.stubs_created):
        print("(no mentions written, no stubs created)")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Falstaff — turn a raw transcript into a meeting note plus mentions on every entity touched.",
    )
    parser.add_argument("file", type=Path, help="Path to the transcript file")
    parser.add_argument(
        "--source", "-s",
        choices=list(KNOWN_SOURCES) + ["manual", "unknown"],
        help="Recording source (filename-detected if not specified)",
    )
    parser.add_argument("--title", "-t", help="Override meeting title")
    parser.add_argument("--date", "-d", help="Override meeting date (ISO 8601)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be written without modifying any files",
    )
    args = parser.parse_args()

    if not args.file.exists():
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    try:
        summary = run_sally(
            transcript_path=args.file,
            source=args.source,
            title_override=args.title,
            date_override=args.date,
            dry_run=args.dry_run,
        )
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)

    print_summary(summary)
    if args.dry_run:
        print("\n[dry-run] no files were modified")


if __name__ == "__main__":
    main()

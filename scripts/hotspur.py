#!/usr/bin/env python3
"""
Hotspur — calendar scout. Produces a morning brief.

Reads `briefs/_tomorrow.md`, gathers context for each meeting from the entity
files and meeting history, and writes `briefs/<date>.md`.

Usage:
    python scripts/hotspur.py                # brief for tomorrow
    python scripts/hotspur.py 2026-05-10     # brief for a specific date
    LLM_MOCK=1 python scripts/hotspur.py --dry-run

Idempotent: re-running on the same date overwrites the brief.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path

import frontmatter

from llm_client import LLMClient
from utils import (
    extract_wiki_links,
    find_entity_file,
    get_repo_root,
    iter_meeting_files,
    parse_file,
    save_file,
    today,
)


TOMORROW_FILE = "briefs/_tomorrow.md"
MEETING_LINE_RE = re.compile(
    r"^\s*-\s*(?P<time>\d{1,2}:\d{2})\s*[—-]\s*(?P<rest>.+)$"
)


# ---------------------------------------------------------------------------
# Parse _tomorrow.md
# ---------------------------------------------------------------------------

def parse_tomorrow(path: Path) -> list[dict]:
    """Return a list of {time, raw, entities[]} dicts."""
    if not path.exists():
        raise FileNotFoundError(f"Missing {path}; create one with tomorrow's meetings.")
    # Strip <!-- ... --> comment blocks so illustrative example bullets
    # inside the file's instruction header don't get treated as real meetings.
    text = re.sub(r"<!--.*?-->", "", path.read_text(), flags=re.DOTALL)
    items: list[dict] = []
    for line in text.splitlines():
        m = MEETING_LINE_RE.match(line)
        if not m:
            continue
        rest = m.group("rest").strip()
        entities = extract_wiki_links(rest)
        items.append({
            "time": m.group("time"),
            "raw": rest,
            "entities": entities,
        })
    items.sort(key=lambda it: it["time"])
    return items


# ---------------------------------------------------------------------------
# Gather context
# ---------------------------------------------------------------------------

def latest_mentions(body: str, n: int = 5) -> list[str]:
    """Return the latest `n` mention blocks (heading + body + source line)."""
    blocks: list[str] = []
    current: list[str] = []
    in_mentions = False
    found_first = False
    for line in body.splitlines():
        stripped = line.strip()
        if stripped == "## Mentions":
            in_mentions = True
            continue
        if not in_mentions:
            continue
        if stripped.startswith("## "):
            break  # next H2; mentions section ended
        if stripped.startswith("### "):
            if current:
                blocks.append("\n".join(current).rstrip())
                current = []
            found_first = True
            current.append(line)
        elif found_first:
            current.append(line)
    if current:
        blocks.append("\n".join(current).rstrip())
    # Mentions are appended newest-first by Falstaff, so the first N entries are the latest.
    return blocks[:n]


def gather_open_followups(entity_name: str) -> list[tuple[Path, str]]:
    """Return (meeting_path, line) for unchecked checkboxes that wiki-link this entity."""
    results: list[tuple[Path, str]] = []
    target = entity_name.lower()
    for f in iter_meeting_files():
        try:
            text = f.read_text()
        except Exception:
            continue
        for line in text.splitlines():
            if "- [ ]" not in line:
                continue
            if target in line.lower() or any(
                lk.lower() == target for lk in extract_wiki_links(line)
            ):
                results.append((f, line.strip()))
    return results


def context_for_entity(entity_name: str) -> dict:
    path = find_entity_file(entity_name)
    if not path:
        return {"name": entity_name, "stub": True}
    post = parse_file(path)
    return {
        "name": entity_name,
        "stub": False,
        "path": path,
        "frontmatter": dict(post.metadata),
        "mentions": latest_mentions(post.content or "", n=5),
        "followups": gather_open_followups(entity_name),
    }


# ---------------------------------------------------------------------------
# Suggested question
# ---------------------------------------------------------------------------

QUESTION_SYSTEM = """You are Hotspur, a calendar scout for a venture capital
investor. Given the context for a meeting that's about to happen, propose ONE
substantive question the owner might want to ask or sit with during the
meeting. The question must be specific to the entities and recent context, not
generic. One sentence. No preamble. Output the question and nothing else."""


def suggest_question(client: LLMClient, meeting: dict, contexts: list[dict]) -> str:
    body_parts = [f"Meeting: {meeting['raw']} at {meeting['time']}", ""]
    for c in contexts:
        if c.get("stub"):
            body_parts.append(f"## {c['name']} (stub — no file yet)")
            continue
        fm = c.get("frontmatter", {})
        body_parts.append(f"## {c['name']}")
        body_parts.append(f"role/type: {fm.get('type')}, status: {fm.get('status')}")
        if fm.get("last_mention"):
            body_parts.append(f"last_mention: {fm.get('last_mention')}")
        if c.get("mentions"):
            body_parts.append("recent mentions:")
            for m in c["mentions"]:
                body_parts.append(m)
        body_parts.append("")
    prompt = "\n".join(body_parts)
    try:
        resp = client.complete(prompt=prompt, system=QUESTION_SYSTEM)
        return resp.text.strip().strip('"')
    except Exception as e:
        return f"[hotspur could not generate a question: {e}]"


# ---------------------------------------------------------------------------
# Render brief
# ---------------------------------------------------------------------------

def render_section(meeting: dict, contexts: list[dict], question: str) -> str:
    lines: list[str] = []
    lines.append(f"## {meeting['time']} — {meeting['raw']}")
    lines.append("")
    for c in contexts:
        if c.get("stub"):
            lines.append(f"### {c['name']}")
            lines.append("> [!todo] stub — not enough context to brief well")
            lines.append("")
            continue
        fm = c.get("frontmatter", {})
        lines.append(f"### {c['name']}")
        bits = []
        if fm.get("role"):
            bits.append(str(fm["role"]))
        if fm.get("company"):
            bits.append(f"at {fm['company']}")
        if fm.get("status"):
            bits.append(f"status: {fm['status']}")
        if fm.get("relationship_strength"):
            bits.append(f"relationship: {fm['relationship_strength']}")
        if bits:
            lines.append("- " + " · ".join(bits))
        if fm.get("last_touch"):
            lines.append(f"- last touch: {fm['last_touch']}")
        if fm.get("last_mention"):
            lines.append(f"- last mention: {fm['last_mention']}")
        lines.append("")
        if c.get("mentions"):
            lines.append("**Recent mentions**")
            lines.append("")
            for m in c["mentions"]:
                lines.append(m)
                lines.append("")
        if c.get("followups"):
            lines.append("**Open follow-ups**")
            for path, line in c["followups"]:
                rel = path.relative_to(get_repo_root())
                lines.append(f"- {line}  _(from {rel})_")
            lines.append("")
    lines.append(f"> [!suggested by hotspur] {question}")
    lines.append("")
    return "\n".join(lines)


def build_brief(date: str, dry_run: bool) -> Path:
    repo_root = get_repo_root()
    tomorrow_path = repo_root / TOMORROW_FILE
    meetings = parse_tomorrow(tomorrow_path)
    if not meetings:
        raise RuntimeError(f"No meetings found in {TOMORROW_FILE}")

    client = LLMClient()
    sections: list[str] = []
    for meeting in meetings:
        contexts = [context_for_entity(name) for name in meeting["entities"]]
        question = suggest_question(client, meeting, contexts)
        sections.append(render_section(meeting, contexts, question))

    body = f"# Morning Brief — {date}\n\n" + "\n".join(sections)
    fm = {
        "type": "brief",
        "date": date,
        "generated": today(),
        "agent": "hotspur",
        "status": "draft",
    }
    post = frontmatter.Post(content=body, **fm)
    out = repo_root / "briefs" / f"{date}.md"
    if not dry_run:
        save_file(out, post)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Hotspur — write tomorrow's morning brief from briefs/_tomorrow.md.",
    )
    parser.add_argument(
        "date", nargs="?",
        help="Brief date (ISO 8601). Defaults to tomorrow.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if args.date:
        target = args.date
    else:
        target = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    try:
        path = build_brief(target, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    print(f"Brief: {path.relative_to(get_repo_root())}{' (dry-run, not written)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()

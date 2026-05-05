#!/usr/bin/env python3
"""
Warwick — weekly reflection agent.

Reads the past 7 days of meetings, mentions, and journal entries, plus the
current state of `thesis/`, and writes a reflection to
`thesis/reflections/<YYYY-Www>.md`.

Usage:
    python scripts/warwick.py                       # this week
    python scripts/warwick.py --week 2026-W18
    LLM_MOCK=1 python scripts/warwick.py --dry-run

Warwick writes a single reflection per week. If a prior reflection for the
same week is `reviewed`, a re-run produces `<week>-rerun.md` rather than
overwriting reviewed work.
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import frontmatter

from llm_client import LLMClient
from utils import (
    extract_wiki_links,
    get_repo_root,
    iter_meeting_files,
    iso_week,
    list_entities,
    parse_file,
    save_file,
    today,
)


STALE_THRESHOLD_DAYS = 30
STRENGTHS_TO_TRACK = {"warm", "strong", "core"}


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def parse_iso_week(label: str) -> tuple[datetime, datetime]:
    """Return (Monday, Sunday) for an ISO-week label like '2026-W18'."""
    m = re.match(r"^(\d{4})-W(\d{1,2})$", label)
    if not m:
        raise ValueError(f"Bad week label: {label}")
    year, week = int(m.group(1)), int(m.group(2))
    # ISO week: Monday is day 1
    monday = datetime.fromisocalendar(year, week, 1)
    sunday = monday + timedelta(days=6)
    return monday, sunday


def in_range(d_str: str, start: datetime, end: datetime) -> bool:
    try:
        d = datetime.strptime(d_str[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return False
    return start.date() <= d.date() <= end.date()


def days_since(d_str: str) -> Optional[int]:
    try:
        d = datetime.strptime(str(d_str)[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None
    return (datetime.now().date() - d.date()).days


# ---------------------------------------------------------------------------
# Corpus scanning
# ---------------------------------------------------------------------------

MENTION_HEADING_RE = re.compile(r"^### (\d{4}-\d{2}-\d{2})\s+—\s+(.+)$", re.MULTILINE)


def collect_meetings_in_range(start: datetime, end: datetime) -> list[Path]:
    out: list[Path] = []
    for f in iter_meeting_files():
        try:
            post = parse_file(f)
        except Exception:
            continue
        if in_range(str(post.get("date", "")), start, end):
            out.append(f)
    return out


def collect_journal_in_range(start: datetime, end: datetime) -> list[Path]:
    out: list[Path] = []
    journal_dir = get_repo_root() / "journal"
    if not journal_dir.exists():
        return out
    for f in journal_dir.glob("*.md"):
        if f.name == ".gitkeep":
            continue
        if in_range(f.stem, start, end):
            out.append(f)
    return out


def collect_recent_mentions(start: datetime, end: datetime) -> list[dict]:
    """Return {entity_path, entity_name, date, label, body} for mentions in window."""
    items: list[dict] = []
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            body = post.content or ""
            entity_name = str(post.get("name", f.stem))
            for date_str, label in MENTION_HEADING_RE.findall(body):
                if in_range(date_str, start, end):
                    items.append({
                        "path": f,
                        "entity": entity_name,
                        "date": date_str,
                        "label": label.strip(),
                    })
    return items


def collect_followups() -> list[dict]:
    """All unchecked checkboxes across meetings and entity files, with age."""
    out: list[dict] = []
    repo_root = get_repo_root()
    for f in list(iter_meeting_files()):
        try:
            post = parse_file(f)
        except Exception:
            continue
        meeting_date = str(post.get("date", ""))
        for line in (post.content or "").splitlines():
            if "- [ ]" in line and line.strip() != "- [ ]":
                age = days_since(meeting_date)
                out.append({
                    "source": f.relative_to(repo_root),
                    "line": line.strip(),
                    "age_days": age,
                })
    out.sort(key=lambda x: (x["age_days"] is None, -(x["age_days"] or 0)))
    return out


def collect_stale_relationships() -> list[dict]:
    out: list[dict] = []
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            strength = str(post.get("relationship_strength") or "").strip()
            if strength not in STRENGTHS_TO_TRACK:
                continue
            last = post.get("last_mention") or post.get("last_touch")
            age = days_since(str(last)) if last else None
            if age is None or age > STALE_THRESHOLD_DAYS:
                out.append({
                    "name": str(post.get("name", f.stem)),
                    "type": t,
                    "strength": strength,
                    "last": str(last) if last else "(never)",
                    "age_days": age,
                })
    out.sort(key=lambda x: (x["age_days"] is None, -(x["age_days"] or 0)))
    return out


def attention_counts(meetings: list[Path], mentions: list[dict]) -> tuple[Counter, Counter]:
    meeting_count: Counter = Counter()
    mention_count: Counter = Counter()
    for m_path in meetings:
        try:
            post = parse_file(m_path)
        except Exception:
            continue
        text = post.content or ""
        for link in extract_wiki_links(text):
            meeting_count[link] += 1
    for m in mentions:
        mention_count[m["entity"]] += 1
    return meeting_count, mention_count


# ---------------------------------------------------------------------------
# Thesis snapshot
# ---------------------------------------------------------------------------

def thesis_snapshot() -> str:
    """Concatenated thesis pillars, lightly truncated."""
    pillars_dir = get_repo_root() / "thesis" / "pillars"
    parts: list[str] = []
    if pillars_dir.exists():
        for f in sorted(pillars_dir.glob("*.md")):
            try:
                post = parse_file(f)
            except Exception:
                continue
            parts.append(f"### {post.get('name', f.stem)}\n\n{(post.content or '')[:800]}")
    # Also include concept files of category: thesis
    for f in list_entities("concepts"):
        try:
            post = parse_file(f)
        except Exception:
            continue
        if str(post.get("category", "")).strip() == "thesis":
            parts.append(f"### {post.get('name', f.stem)}\n\n{(post.content or '')[:800]}")
    if not parts:
        return "(no thesis pillars yet)"
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Warwick prompts
# ---------------------------------------------------------------------------

THEMES_SYSTEM = """You are Warwick, a weekly reflection agent for a venture
capital investor. You speak with directness — chief-of-staff voice, no
flattery, no marketing prose. Given the inputs below, return a Markdown
fragment with two sections:

## Themes emerging
2-4 bullets. Each names a pattern (recurring topic, founder profile, sector
signal) and cites 1-3 entities or meetings as evidence (use [[wiki-links]]).

## Drift
1-3 bullets. Where does the past week's revealed behaviour diverge from the
stated thesis? Be specific: name the pillar, describe the gap concretely.
If there is no meaningful divergence, write a single bullet: "No material
drift this week." Do not pad.

Output only those two sections, no preamble."""


QUESTION_SYSTEM = """You are Warwick. Based on the week's activity and the
thesis, propose ONE substantive question the owner should sit with next week.
The question must:
- be specific to this week's evidence,
- not be answerable in one sentence,
- not be sycophantic.
Output the question and nothing else. One sentence."""


def themes_and_drift(
    client: LLMClient,
    meetings: list[Path],
    mentions: list[dict],
    journals: list[Path],
    thesis: str,
) -> str:
    bullets = []
    bullets.append(f"Meetings this week: {len(meetings)}")
    bullets.append(f"Mentions written this week: {len(mentions)}")
    if mentions:
        sample = mentions[:20]
        bullets.append("Sample mentions (entity — date — label):")
        for m in sample:
            bullets.append(f"  - {m['entity']} — {m['date']} — {m['label']}")
    if meetings:
        bullets.append("Meeting titles:")
        for f in meetings:
            try:
                post = parse_file(f)
                bullets.append(f"  - {post.get('title', f.stem)} ({post.get('date', '')})")
            except Exception:
                pass
    journal_excerpt = ""
    if journals:
        excerpts = []
        for j in journals:
            try:
                post = parse_file(j)
                excerpts.append(f"### {post.get('date', j.stem)}\n{(post.content or '')[:600]}")
            except Exception:
                continue
        journal_excerpt = "\n\n".join(excerpts)

    user = (
        "## Activity\n" + "\n".join(bullets) +
        "\n\n## Journal excerpts\n" + (journal_excerpt or "(none)") +
        "\n\n## Stated thesis\n" + thesis
    )
    try:
        resp = client.complete(prompt=user, system=THEMES_SYSTEM)
        return resp.text.strip()
    except Exception as e:
        return f"## Themes emerging\n_(Warwick error: {e})_\n\n## Drift\n_(unable to assess)_"


def propose_question(client: LLMClient, prior: str, thesis: str) -> str:
    try:
        resp = client.complete(
            prompt=f"## Reflection so far\n{prior}\n\n## Thesis\n{thesis}",
            system=QUESTION_SYSTEM,
        )
        return resp.text.strip().strip('"')
    except Exception as e:
        return f"[warwick could not generate a question: {e}]"


# ---------------------------------------------------------------------------
# Render the reflection
# ---------------------------------------------------------------------------

def render_time_spent(meeting_count: Counter, mention_count: Counter) -> str:
    lines = ["## Time spent", ""]
    if not meeting_count and not mention_count:
        lines.append("_No meetings or mentions in the past week._")
        return "\n".join(lines)
    lines.append("**By mention count (top 10)**")
    for name, n in mention_count.most_common(10):
        lines.append(f"- [[{name}]] — {n}")
    lines.append("")
    lines.append("**By meeting wiki-link count (top 10)**")
    for name, n in meeting_count.most_common(10):
        lines.append(f"- [[{name}]] — {n}")
    return "\n".join(lines)


def render_stale(items: list[dict]) -> str:
    lines = ["## Stale relationships", ""]
    if not items:
        lines.append("_No tracked relationships have gone cold this week._")
        return "\n".join(lines)
    lines.append(f"Entities with `relationship_strength` ∈ warm/strong/core and no mention in > {STALE_THRESHOLD_DAYS} days:")
    lines.append("")
    for it in items[:25]:
        age = it["age_days"]
        age_str = "never" if age is None else f"{age}d"
        lines.append(f"- [[{it['name']}]] ({it['strength']}, {it['type']}) — last: {it['last']} ({age_str})")
    return "\n".join(lines)


def render_followups(items: list[dict]) -> str:
    lines = ["## Open follow-ups", ""]
    if not items:
        lines.append("_No open follow-ups across the corpus._")
        return "\n".join(lines)
    for it in items[:25]:
        age = it["age_days"]
        age_str = "?" if age is None else f"{age}d"
        lines.append(f"- {it['line']}  _({it['source']}, {age_str} old)_")
    if len(items) > 25:
        lines.append(f"_…and {len(items) - 25} more (run `python scripts/stale.py --followups`)._")
    return "\n".join(lines)


def build_reflection(week_label: str, dry_run: bool) -> Path:
    repo_root = get_repo_root()
    monday, sunday = parse_iso_week(week_label)
    end = sunday.replace(hour=23, minute=59, second=59)

    meetings = collect_meetings_in_range(monday, end)
    journals = collect_journal_in_range(monday, end)
    mentions = collect_recent_mentions(monday, end)
    followups = collect_followups()
    stale = collect_stale_relationships()
    meeting_counts, mention_counts = attention_counts(meetings, mentions)
    thesis = thesis_snapshot()

    client = LLMClient()
    themes_drift_md = themes_and_drift(client, meetings, mentions, journals, thesis)

    parts: list[str] = []
    parts.append(render_time_spent(meeting_counts, mention_counts))
    parts.append(themes_drift_md)
    parts.append(render_stale(stale))
    parts.append(render_followups(followups))

    question = propose_question(client, "\n\n".join(parts), thesis)
    parts.append(f"## Question for next week\n\n{question}")

    body = f"# Weekly Reflection — {week_label}\n\n" + "\n\n".join(parts) + "\n"

    fm = {
        "type": "reflection",
        "week": week_label,
        "generated": today(),
        "agent": "warwick",
        "status": "draft",
    }
    post = frontmatter.Post(content=body, **fm)

    out_dir = repo_root / "thesis" / "reflections"
    out = out_dir / f"{week_label}.md"
    if out.exists():
        existing_post = parse_file(out)
        if str(existing_post.get("status")) == "reviewed":
            out = out_dir / f"{week_label}-rerun.md"
            counter = 2
            while out.exists():
                out = out_dir / f"{week_label}-rerun-{counter}.md"
                counter += 1

    if not dry_run:
        save_file(out, post)
    return out


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Warwick — weekly reflection on stated thesis vs revealed behaviour.",
    )
    parser.add_argument(
        "--week", "-w",
        help="ISO week label (e.g. 2026-W18). Defaults to current week.",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    week_label = args.week or iso_week()
    try:
        path = build_reflection(week_label, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    rel = path.relative_to(get_repo_root())
    suffix = " (dry-run, not written)" if args.dry_run else ""
    print(f"Reflection: {rel}{suffix}")


if __name__ == "__main__":
    main()

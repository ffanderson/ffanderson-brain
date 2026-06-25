#!/usr/bin/env python3
"""
Warwick — weekly reflection agent.

Reads the past 7 days of meetings, mentions, and journal entries, the current
state of `thesis/`, a six-week activity trajectory, the pipeline-status
distribution, and Warwick's own recent reflections, and writes a reflection to
`thesis/reflections/<YYYY-Www>.md`.

Design notes (2026-06-25 rebuild):
- The owner (Fraser Anderson) is the AUTHOR of the corpus and appears in nearly
  every mention. He is excluded from all entity counts, stale lists, and the
  analytical prompt — he is the reader, not the data.
- "Meetings" counts both `meetings/` (promoted) and `inbox/` (untriaged but
  real). Counting only promoted meetings undercounts reality whenever triage
  lags, which produced a chronic false "zero meetings" drift signal.
- Warwick reads her own prior reflections so she can detect trends and avoid
  repeating last week's question.
- The analytical prompt asks for falsifiable, quantified CLAIMS, not just
  questions, and may return a recommendation in place of a question.

Usage:
    python scripts/warwick.py                       # this week
    python scripts/warwick.py --week 2026-W18
    LLM_MOCK=1 python scripts/warwick.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
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

# The repository's owner/author. He is in the room for almost every recorded
# conversation, so counting him as a tracked entity drowns out real signal and
# produces nonsensical "analyze your relationship with yourself" output.
OWNER_NAME = "Fraser Anderson"
OWNER_ALIASES = {"fraser anderson", "fraser", "fraser a", "ff anderson"}

ACTIVE_STATUSES = {"evaluating", "invested"}
PIPELINE_ORDER = ["tracking", "evaluating", "invested", "passed", "exited"]


def is_owner(name: str) -> bool:
    return name.strip().lower() in OWNER_ALIASES


# ---------------------------------------------------------------------------
# Date helpers
# ---------------------------------------------------------------------------

def parse_iso_week(label: str) -> tuple[datetime, datetime]:
    """Return (Monday, Sunday) for an ISO-week label like '2026-W18'."""
    m = re.match(r"^(\d{4})-W(\d{1,2})$", label)
    if not m:
        raise ValueError(f"Bad week label: {label}")
    year, week = int(m.group(1)), int(m.group(2))
    monday = datetime.fromisocalendar(year, week, 1)
    return monday, monday + timedelta(days=6)


def iso_week_of(d: datetime) -> str:
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def parse_date(d_str: str) -> Optional[datetime]:
    try:
        return datetime.strptime(str(d_str)[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def in_range(d_str: str, start: datetime, end: datetime) -> bool:
    d = parse_date(d_str)
    return bool(d and start.date() <= d.date() <= end.date())


def days_since(d_str: str) -> Optional[int]:
    d = parse_date(d_str)
    return None if d is None else (datetime.now().date() - d.date()).days


# ---------------------------------------------------------------------------
# Corpus scanning
# ---------------------------------------------------------------------------

MENTION_HEADING_RE = re.compile(r"^### (\d{4}-\d{2}-\d{2})\s+—\s+(.+)$", re.MULTILINE)


def all_meeting_files() -> list[Path]:
    """Every file representing a meeting that actually happened — both promoted
    (`meetings/`) and untriaged (`inbox/`, type meeting/inbox)."""
    out: list[Path] = list(iter_meeting_files())
    inbox = get_repo_root() / "inbox"
    if inbox.exists():
        for f in inbox.glob("*.md"):
            if f.name == ".gitkeep":
                continue
            try:
                t = str(parse_file(f).get("type") or "")
            except Exception:
                continue
            if t in ("meeting", "inbox"):
                out.append(f)
    return out


def collect_meetings_in_range(start: datetime, end: datetime) -> list[Path]:
    out: list[Path] = []
    for f in all_meeting_files():
        try:
            post = parse_file(f)
        except Exception:
            continue
        if in_range(str(post.get("date") or post.get("received") or ""), start, end):
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
    """{path, entity, date, label} for mentions in window. Owner excluded."""
    items: list[dict] = []
    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            entity_name = str(post.get("name", f.stem))
            if is_owner(entity_name):
                continue
            for date_str, label in MENTION_HEADING_RE.findall(post.content or ""):
                if in_range(date_str, start, end):
                    items.append({"path": f, "entity": entity_name,
                                  "date": date_str, "label": label.strip()})
    return items


def collect_followups() -> list[dict]:
    out: list[dict] = []
    repo_root = get_repo_root()
    for f in all_meeting_files():
        try:
            post = parse_file(f)
        except Exception:
            continue
        meeting_date = str(post.get("date", ""))
        for line in (post.content or "").splitlines():
            if "- [ ]" in line and line.strip() != "- [ ]":
                out.append({"source": f.relative_to(repo_root),
                            "line": line.strip(), "age_days": days_since(meeting_date)})
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
            name = str(post.get("name", f.stem))
            if is_owner(name):
                continue
            strength = str(post.get("relationship_strength") or "").strip()
            if strength not in STRENGTHS_TO_TRACK:
                continue
            last = post.get("last_mention") or post.get("last_touch")
            age = days_since(str(last)) if last else None
            if age is None or age > STALE_THRESHOLD_DAYS:
                out.append({"name": name, "type": t, "strength": strength,
                            "last": str(last) if last else "(never)", "age_days": age})
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
        for link in extract_wiki_links(post.content or ""):
            if not is_owner(link):
                meeting_count[link] += 1
    for m in mentions:
        mention_count[m["entity"]] += 1  # owner already excluded upstream
    return meeting_count, mention_count


# ---------------------------------------------------------------------------
# Trajectory + pipeline (pure data — no LLM)
# ---------------------------------------------------------------------------

def weekly_trend(target_monday: datetime, weeks: int = 6) -> tuple[list[str], Counter, Counter]:
    """Meetings logged and mentions written per ISO week, trailing `weeks`."""
    buckets: list[tuple[str, datetime, datetime]] = []
    for i in range(weeks - 1, -1, -1):
        mon = target_monday - timedelta(weeks=i)
        buckets.append((iso_week_of(mon), mon, mon + timedelta(days=6)))

    meet: Counter = Counter()
    ment: Counter = Counter()

    for f in all_meeting_files():
        try:
            post = parse_file(f)
        except Exception:
            continue
        d = parse_date(str(post.get("date") or post.get("received") or ""))
        if not d:
            continue
        for label, mon, sun in buckets:
            if mon.date() <= d.date() <= sun.date():
                meet[label] += 1
                break

    for t in ["people", "companies", "funds"]:
        for f in list_entities(t):
            try:
                post = parse_file(f)
            except Exception:
                continue
            if is_owner(str(post.get("name", f.stem))):
                continue
            for date_str, _ in MENTION_HEADING_RE.findall(post.content or ""):
                d = parse_date(date_str)
                if not d:
                    continue
                for label, mon, sun in buckets:
                    if mon.date() <= d.date() <= sun.date():
                        ment[label] += 1
                        break

    return [b[0] for b in buckets], meet, ment


def pipeline_snapshot() -> tuple[Counter, list[dict]]:
    """Status distribution across companies, plus active-stage companies with
    their mention recency (to surface deals going cold mid-diligence)."""
    counts: Counter = Counter()
    active: list[dict] = []
    for f in list_entities("companies"):
        try:
            post = parse_file(f)
        except Exception:
            continue
        status = str(post.get("status") or "tracking").strip() or "tracking"
        counts[status] += 1
        if status in ACTIVE_STATUSES:
            last = post.get("last_mention") or post.get("last_touch")
            active.append({
                "name": str(post.get("name", f.stem)),
                "status": status,
                "mentions": int(post.get("mention_count") or 0),
                "last": str(last) if last else "(never)",
                "age_days": days_since(str(last)) if last else None,
            })
    active.sort(key=lambda x: (x["age_days"] is None, -(x["age_days"] or 0)))
    return counts, active


def recent_reflections(week_label: str, n: int = 3) -> list[tuple[str, str]]:
    """The (week, body) of the n most recent prior reflections, newest first."""
    refl_dir = get_repo_root() / "thesis" / "reflections"
    if not refl_dir.exists():
        return []
    files = sorted(
        (f for f in refl_dir.glob("*.md") if re.match(r"^\d{4}-W\d{2}", f.stem)),
        key=lambda f: f.stem, reverse=True,
    )
    out: list[tuple[str, str]] = []
    for f in files:
        if f.stem.startswith(week_label):
            continue  # skip the week we're (re)writing
        try:
            out.append((f.stem, parse_file(f).content or ""))
        except Exception:
            continue
        if len(out) >= n:
            break
    return out


# ---------------------------------------------------------------------------
# Thesis snapshot
# ---------------------------------------------------------------------------

def thesis_snapshot() -> str:
    pillars_dir = get_repo_root() / "thesis" / "pillars"
    parts: list[str] = []
    if pillars_dir.exists():
        for f in sorted(pillars_dir.glob("*.md")):
            try:
                post = parse_file(f)
            except Exception:
                continue
            parts.append(f"### {post.get('name', f.stem)}\n{(post.content or '')[:600]}")
    for f in list_entities("concepts"):
        try:
            post = parse_file(f)
        except Exception:
            continue
        if str(post.get("category", "")).strip() == "thesis":
            parts.append(f"### {post.get('name', f.stem)}\n{(post.content or '')[:600]}")
    return "\n\n".join(parts) if parts else "(no thesis pillars yet)"


# ---------------------------------------------------------------------------
# Analytical prompt — insight, not interrogation
# ---------------------------------------------------------------------------

ANALYSIS_SYSTEM = f"""You are Warwick, chief-of-staff reflection agent for
{OWNER_NAME}, the venture investor who OWNS and AUTHORS this repository.

Hard rule about {OWNER_NAME}: he is the author of every note and was in the
room for almost every recorded conversation, so his name appears everywhere.
He is the READER of this reflection, not a subject of it. NEVER analyze him as
a relationship, a network node, a "central hub," a theme, or the subject of a
question. Analyze the people, companies, funds, and thesis pillars around him.
If your strongest observation is "the owner appears a lot," discard it — that
is an artifact of authorship, not a finding.

You are given hard data: a six-week activity trajectory, the pipeline-status
distribution, this week's activity, the stated thesis pillars, and your own
prior reflections. Your job is grounded INSIGHT, not interrogation. Write with
a chief-of-staff's directness — quantified, falsifiable, no flattery, no
hedging, no marketing voice.

Return exactly these four sections and nothing else:

## Themes emerging
2–4 bullets. Each names a pattern, cites 1–3 [[wiki-linked]] entities or a
number as evidence, and ends with a one-clause "so what."

## Drift
1–3 bullets tying revealed behaviour to the trajectory/pipeline NUMBERS and to
named pillars. Quote the figures. If there is genuinely no material drift, say
so in one line and move on — do not manufacture it.

## Insight
2–3 falsifiable, quantified CLAIMS — statements, not questions. Each must cite
a specific number or named entity and surface something not visible at a
glance. Register to aim for:
- "Of N companies at status:evaluating, M have gone >30 days without a mention
  — the live pipeline is effectively K."
- "Meetings logged ran A→B→C over three weeks while pipeline stayed flat at D
  evaluating; activity is rising but conversion is not."
Do not hedge. Do not ask questions in this section.

## Question for next week
EITHER one question OR one recommendation — whichever is the more honest move.
Constraints: build on this week's specific evidence; do NOT repeat a question
already asked in the prior reflections shown to you (they are provided — read
them and go somewhere new); never about {OWNER_NAME}'s own role. If three-plus
prior weeks asked variants of the same unanswered question, stop asking it and
instead state the decision you would make in his place, and why."""


def build_analysis_prompt(
    week_label: str,
    meetings: list[Path],
    mentions: list[dict],
    journals: list[Path],
    thesis: str,
    trend: tuple[list[str], Counter, Counter],
    pipeline: tuple[Counter, list[dict]],
    priors: list[tuple[str, str]],
) -> str:
    labels, meet, ment = trend
    counts, active = pipeline

    lines: list[str] = []
    lines.append(f"# Week under review: {week_label}\n")

    lines.append("## Six-week trajectory (owner excluded)")
    lines.append("week | meetings_logged | mentions_written")
    for lab in labels:
        lines.append(f"{lab} | {meet.get(lab, 0)} | {ment.get(lab, 0)}")
    lines.append("")

    lines.append("## Pipeline status (companies)")
    lines.append(", ".join(f"{s}={counts.get(s,0)}" for s in PIPELINE_ORDER
                           if counts.get(s, 0)) or "(no status data)")
    if active:
        lines.append("\nActive-stage companies (evaluating/invested) by mention age:")
        for a in active[:15]:
            age = "never" if a["age_days"] is None else f"{a['age_days']}d"
            lines.append(f"  - {a['name']} ({a['status']}) — {a['mentions']} mentions, last {a['last']} ({age})")
    lines.append("")

    lines.append("## This week's activity")
    lines.append(f"Meetings this week: {len(meetings)}")
    lines.append(f"Mentions this week: {len(mentions)}")
    if mentions:
        lines.append("Mention sample (entity — date — label):")
        for m in mentions[:25]:
            lines.append(f"  - {m['entity']} — {m['date']} — {m['label']}")
    if meetings:
        lines.append("Meeting titles:")
        for f in meetings[:25]:
            try:
                post = parse_file(f)
                lines.append(f"  - {post.get('title', f.stem)} ({post.get('date','')})")
            except Exception:
                pass
    lines.append("")

    if journals:
        lines.append("## Journal excerpts")
        for j in journals:
            try:
                post = parse_file(j)
                lines.append(f"### {post.get('date', j.stem)}\n{(post.content or '')[:500]}")
            except Exception:
                continue
        lines.append("")

    lines.append("## Stated thesis pillars")
    lines.append(thesis)
    lines.append("")

    if priors:
        lines.append("## Your prior reflections (do not repeat their questions)")
        for wk, body in priors:
            # Pull just the prior 'Question' line(s) plus a short head for context.
            q = ""
            m = re.search(r"## Question for next week\s*\n+(.+)", body, re.DOTALL)
            if m:
                q = m.group(1).strip().split("\n\n")[0][:400]
            lines.append(f"### {wk} — prior question\n{q or '(none)'}")
        lines.append("")

    return "\n".join(lines)


def run_analysis(client: LLMClient, prompt: str) -> str:
    try:
        return client.complete(prompt=prompt, system=ANALYSIS_SYSTEM).text.strip()
    except Exception as e:
        return (f"## Themes emerging\n_(Warwick error: {e})_\n\n## Drift\n"
                f"_(unavailable)_\n\n## Insight\n_(unavailable)_\n\n"
                f"## Question for next week\n_(unavailable)_")


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def render_time_spent(meeting_count: Counter, mention_count: Counter) -> str:
    lines = ["## Time spent (owner excluded)", ""]
    if not meeting_count and not mention_count:
        lines.append("_No meetings or mentions in the past week._")
        return "\n".join(lines)
    lines.append("**By mention count (top 10)**")
    for name, n in mention_count.most_common(10):
        lines.append(f"- [[{name}]] — {n}")
    lines.append("")
    lines.append("**By meeting wiki-link count (top 10)**")
    for name, n in meeting_count.most_common(10) or [("(none)", 0)]:
        lines.append(f"- [[{name}]] — {n}" if n else "- _(none)_")
    return "\n".join(lines)


def render_trajectory(trend: tuple[list[str], Counter, Counter]) -> str:
    labels, meet, ment = trend
    lines = ["## Trajectory (trailing 6 weeks)", ""]
    lines.append("| Week | Meetings logged | Mentions written |")
    lines.append("| ---- | ---------------: | ----------------: |")
    for lab in labels:
        lines.append(f"| {lab} | {meet.get(lab,0)} | {ment.get(lab,0)} |")
    return "\n".join(lines)


def render_pipeline(pipeline: tuple[Counter, list[dict]]) -> str:
    counts, active = pipeline
    lines = ["## Pipeline", ""]
    dist = " · ".join(f"{s}: {counts.get(s,0)}" for s in PIPELINE_ORDER if counts.get(s, 0))
    lines.append(dist or "_No company status data._")
    cold = [a for a in active if (a["age_days"] is None or a["age_days"] > STALE_THRESHOLD_DAYS)]
    if active:
        lines.append("")
        lines.append(f"Active-stage companies: {len(active)} "
                     f"(of which {len(cold)} have no mention in > {STALE_THRESHOLD_DAYS}d):")
        for a in active[:15]:
            age = "never" if a["age_days"] is None else f"{a['age_days']}d"
            flag = "  ⚠ cold" if (a["age_days"] is None or a["age_days"] > STALE_THRESHOLD_DAYS) else ""
            lines.append(f"- [[{a['name']}]] ({a['status']}) — last {a['last']} ({age}){flag}")
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


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

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
    trend = weekly_trend(monday)
    pipeline = pipeline_snapshot()
    priors = recent_reflections(week_label)
    thesis = thesis_snapshot()

    client = LLMClient()
    analysis = run_analysis(
        client,
        build_analysis_prompt(week_label, meetings, mentions, journals,
                              thesis, trend, pipeline, priors),
    )

    parts = [
        render_time_spent(meeting_counts, mention_counts),
        render_trajectory(trend),
        render_pipeline(pipeline),
        analysis,  # Themes / Drift / Insight / Question, from the model
        render_stale(stale),
        render_followups(followups),
    ]
    body = f"# Weekly Reflection — {week_label}\n\n" + "\n\n".join(parts) + "\n"

    post = frontmatter.Post(content=body, **{
        "type": "reflection", "week": week_label, "generated": today(),
        "agent": "warwick", "status": "draft",
    })

    out_dir = repo_root / "thesis" / "reflections"
    out = out_dir / f"{week_label}.md"
    if out.exists() and str(parse_file(out).get("status")) == "reviewed":
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
    parser.add_argument("--week", "-w", help="ISO week label (e.g. 2026-W18). Defaults to current week.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    week_label = args.week or iso_week()
    try:
        path = build_reflection(week_label, dry_run=args.dry_run)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    rel = path.relative_to(get_repo_root())
    print(f"Reflection: {rel}{' (dry-run, not written)' if args.dry_run else ''}")


if __name__ == "__main__":
    main()

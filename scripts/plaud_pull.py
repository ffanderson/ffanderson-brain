#!/usr/bin/env python3
"""
plaud_pull.py — copy new PLAUD transcripts from the synced Google Drive
folder into `inbox/raw/` and (optionally) hand them to Falstaff.

PLAUD writes one extension-less UTF-8 text file per recording (e.g.
"04-01 Consultation: NY Life - Transcript & Summary") plus a `.gdoc`
shortcut placeholder. We pick up the real text files, skip the shortcuts
and anything we've already ingested.

Idempotency: Falstaff already dedupes on the SHA-256 of the transcript
bytes (via the `source_hash` field on each meeting). This script
additionally skips any file whose hash already shows up on a meeting in
`inbox/` or `meetings/`, so re-running is cheap.

Usage:
    python scripts/plaud_pull.py                     # copy new transcripts only
    python scripts/plaud_pull.py --ingest            # copy + run Falstaff
    python scripts/plaud_pull.py --ingest --dry-run  # show what would happen
    python scripts/plaud_pull.py --source-dir <path> # override default folder
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

from utils import (
    get_repo_root,
    iter_meeting_files,
    make_slug,
    parse_file,
    sha256_bytes,
)


DEFAULT_SOURCE = Path(
    os.path.expanduser(
        "~/Library/CloudStorage/GoogleDrive-frazer.anderson@gmail.com/"
        "My Drive/PLAUD Transcripts"
    )
)

# Heuristic: anything below this byte count is almost certainly a Google
# Drive shortcut, an empty file, or a stub.
MIN_BYTES = 1024


def candidate_files(source_dir: Path) -> Iterable[Path]:
    for p in sorted(source_dir.iterdir()):
        if not p.is_file():
            continue
        if p.suffix.lower() in {".gdoc", ".gsheet", ".gslides", ".url"}:
            continue
        if p.name.startswith("."):
            continue
        if p.stat().st_size < MIN_BYTES:
            continue
        yield p


def already_ingested_hashes() -> set[str]:
    repo_root = get_repo_root()
    out: set[str] = set()
    folders = [repo_root / "inbox", repo_root / "meetings"]
    for folder in folders:
        if not folder.exists():
            continue
        for f in folder.glob("*.md"):
            try:
                post = parse_file(f)
            except Exception:
                continue
            h = str(post.get("source_hash") or "")
            if h and h != "legacy-pre-falstaff":
                out.add(h)
    return out


def target_path(source: Path) -> Path:
    """`inbox/raw/<slugified-name>.txt` — keeps Falstaff input filename clean."""
    stem = source.stem  # extension is usually empty already
    slug = make_slug(stem) or "transcript"
    return get_repo_root() / "inbox" / "raw" / f"{slug}.txt"


def copy_one(source: Path, dest: Path, dry_run: bool) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dry_run:
        return
    shutil.copy2(source, dest)


def ingest_one(transcript_path: Path, dry_run: bool) -> int:
    cmd = [
        sys.executable,
        str(get_repo_root() / "scripts" / "falstaff.py"),
        str(transcript_path),
        "--source", "plaud",
    ]
    if dry_run:
        cmd.append("--dry-run")
    print(f"  → {' '.join(cmd)}")
    return subprocess.call(cmd)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-dir",
        type=Path,
        default=DEFAULT_SOURCE,
        help="PLAUD synced folder (default: Google Drive PLAUD Transcripts)",
    )
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Run Falstaff on each newly copied file",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would happen without copying or ingesting",
    )
    parser.add_argument(
        "--limit", type=int, default=0,
        help="Process at most N transcripts this run (0 = no limit)",
    )
    args = parser.parse_args()

    src = args.source_dir.expanduser()
    if not src.exists():
        print(f"Error: source folder not found: {src}", file=sys.stderr)
        sys.exit(1)

    seen = already_ingested_hashes()
    copied: list[Path] = []
    skipped_hash = 0
    skipped_existing = 0

    for source in candidate_files(src):
        try:
            data = source.read_bytes()
        except Exception as e:
            print(f"  ! cannot read {source.name}: {e}")
            continue

        h = sha256_bytes(data)
        if h in seen:
            skipped_hash += 1
            continue

        dest = target_path(source)
        if dest.exists():
            skipped_existing += 1
            continue

        action = "would copy" if args.dry_run else "copying"
        print(f"  {action}: {source.name}")
        print(f"    → {dest.relative_to(get_repo_root())}")
        copy_one(source, dest, dry_run=args.dry_run)
        copied.append(dest)
        seen.add(h)

        if args.limit and len(copied) >= args.limit:
            break

    print()
    print(f"Copied:  {len(copied)}")
    print(f"Skipped (already ingested by hash):  {skipped_hash}")
    print(f"Skipped (already in inbox/raw):       {skipped_existing}")

    if args.ingest and copied:
        print()
        print(f"Ingesting {len(copied)} transcript(s) via Falstaff…")
        for path in copied:
            ingest_one(path, dry_run=args.dry_run)


if __name__ == "__main__":
    main()

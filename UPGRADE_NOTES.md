---
type: meta
name: Upgrade Notes
created: 2026-05-05
---

# Upgrade Notes — 2026-05-05

What changed in this pass and what's deliberately deferred. Read this once,
then either delete the file or keep it as historical record.

## What's new

### 1. Mentions architecture
- `## Mentions` section is now a first-class part of every person, company,
  and fund file. Each mention is dated, sourced, and append-only.
- New frontmatter on those entity types: `aliases`, `mention_count`,
  `last_mention`, `last_touch`, `relationship_strength`, `first_seen`,
  `crm_system`.
- See [SCHEMA.md](SCHEMA.md) for the contract and
  [CONVENTIONS.md](CONVENTIONS.md) for editorial guidance ("Writing mentions").

### 2. Agent roster
- New `agents/` folder with one Markdown spec per agent:
  Sally, Ellie, Connor, Nancy, Arthur, Cassandra.
- See [agents/README.md](agents/README.md) for the philosophy.
- Sally, Connor, and Cassandra are implemented; Ellie, Nancy, and Arthur
  are spec-only (see DECISIONS ADR-016).

### 3. Reflection loop
- `briefs/_tomorrow.md` — the owner edits this each evening to list
  tomorrow's meetings.
- `scripts/connor.py` reads `_tomorrow.md` and writes
  `briefs/<tomorrow-date>.md` with context, recent mentions, and one
  agent-suggested question per meeting.
- `scripts/cassandra.py` runs weekly and writes
  `thesis/reflections/<week>.md` covering time-spent, themes, drift from
  stated thesis, stale relationships, follow-ups, and one substantive
  question for the week ahead.

### 4. Sally — the upgraded ingestion script
- Replaces `scripts/ingest_transcript.py` (kept as
  `_legacy_ingest_transcript.py` for one cycle).
- Pipeline: read transcript → hash for idempotency → metadata via Claude →
  resolve entities → meeting file in `inbox/` → stubs for unresolved
  entities → mentions on every entity touched → run summary.
- Externalised prompts at `scripts/prompts/sally_metadata.md` and
  `scripts/prompts/sally_mentions.md`. Edit them without touching code.
- Idempotent on reruns (source-hash check).
- `--dry-run` flag prints what would be written.

### 5. LLM client
- `scripts/llm_client.py` wraps the Anthropic SDK behind a single
  `LLMClient.complete()` interface.
- `LLM_MOCK=1` env var bypasses the network and returns deterministic stubs
  for offline runs.

### 6. Validation, triage, stale
- `scripts/validate.py` — the new authoritative consistency checker:
  required frontmatter, status vocabularies, mention-count drift, broken
  wiki-links, duplicate mentions across files.
- `scripts/triage_inbox.py` (renamed from `triage.py`) — adds a `promote`
  command that reviews Sally's mentions before moving an inbox item to
  `meetings/`.
- `scripts/stale.py` — lists entities with `relationship_strength` ∈
  {warm, strong, core} whose `last_mention` is > 30 days ago.

### 7. Documentation
- `CLAUDE.md` (new) — instructions for any AI agent reading the repo.
- `SCHEMA.md` (new) — authoritative schema reference, separated from style.
- `CONVENTIONS.md` — restructured around process and editorial rules.
- `DECISIONS.md` — appended ADRs 011 through 017.
- `README.md` — daily/weekly loop documented; agent roster listed.

### 8. Approved AUDIT.md recommendations applied
The 2026-05-05 audit recommended a list of changes. The following were
applied as part of this upgrade, since they did not conflict and were
already approved:

- `CLAUDE.md` for LLM readers (audit #1).
- Stub-creation convention (#4).
- Status vocabulary unified (`raw`/`processed`/`archived`); `p/` tag prefix
  removed (#5; ADR-013).
- `slug` field dropped (#6; ADR-014).
- `updated` field dropped (#7; ADR-015).
- `crm_system` + `crm_id` fields (#9).
- Filename-only source detection in Sally; no content sniffing (#10).
- Aspirational template fields trimmed: `mood`, `energy`, `aum`, `vintage`,
  `gp`, `twitter` (#11).
- Tightened `.gitignore` for audio folders, data-rooms, CRM exports (#12).

The check_links.py bug fix (#2) is implicitly resolved by `validate.py`,
which supersedes it. `check_links.py` is kept on disk but should not be
relied on going forward.

The remaining audit items — `literature` entity type (#3), explicit person
`relationship` field for LP vs founder (#8) — are partly applied. The
person template now has a `relationship` field with values `founder | operator | lp | co-investor | service-provider | press | personal | other`. The
`literature` type is still deferred (see DECISIONS Future Decisions list).

## Deferred

- The Ellie / Nancy / Arthur implementations.
- A real calendar connector behind Connor (he reads a hand-edited
  `_tomorrow.md` file in this pass).
- A real news feed and scraper behind Nancy.
- A `literature` entity type.
- LP-individual schema decision (see AUDIT.md "Open questions").
- Cap-table snapshot fields on `company` files.
- Filesystem watcher to auto-run Sally on new files in `inbox/raw/`.
- A pre-commit hook to enforce `validate.py` cleanly.

## Notes from the validation run

`scripts/validate.py` currently emits warnings (not errors) for:
- A handful of stub wiki-links in seed concept files (`[[Foundation Models]]`,
  `[[Vertical SaaS]]`, etc.). These are intentional stubs per the new
  convention; create the files when you have something to say about them.
- A stub reference to `[[Sarah Johnson]]` in `john-smith.md` and
  `[[Portfolio Company A]]` placeholder. Same: stubs are first-class.

The repo passes validation (exit 0) with no errors.

## Three things to do next

1. **Try Sally on a real transcript.** Drop a `.txt` file from PLAUD or
   Granola into `inbox/raw/` and run
   `python scripts/sally.py inbox/raw/<file>`. Inspect the meeting file
   she writes and the mentions she adds to entity files.

2. **Edit `briefs/_tomorrow.md`** with one or two real meetings, then run
   `python scripts/connor.py`. Check whether the brief is something you'd
   actually want to read in the morning. Tune the prompt at
   `scripts/connor.py:QUESTION_SYSTEM` if not.

3. **Resolve the open questions in [AUDIT.md](AUDIT.md):** Affinity vs
   Attio, personal-life-in-this-repo, LP-individual granularity, cap-table
   scope. Each is a one-paragraph ADR addition.

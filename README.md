# ffanderson-brain

A Git-versioned, Markdown-based personal knowledge system for venture capital
investing. Plain text in, plain text out. Read by humans (Obsidian on Mac and
iOS) and by a small roster of named LLM agents.

## Philosophy

- **Plain Markdown only.** No proprietary formats; readable in any text editor
  for 50+ years.
- **YAML frontmatter** on every file.
- **Wiki-links** are the knowledge graph: `[[Entity Name]]`.
- **One file per entity.** People, companies, funds, concepts each get one
  canonical home.
- **Mentions are first-class.** Atomic, dated, sourced fragments accumulate
  on entity files (see [SCHEMA.md](SCHEMA.md)).
- **CRM owns the contact graph; this repo owns synthesis.**
- **Privacy by default.**

## Quick start

```bash
# Install Python deps
cd scripts
pip install -r requirements.txt

# Set your API key (Sally, Connor, Cassandra all use Claude)
export ANTHROPIC_API_KEY=sk-ant-...

# Or run offline with deterministic stubs
export LLM_MOCK=1

# Bring a meeting transcript into the system
python scripts/sally.py ~/Downloads/meeting-transcript.txt

# Triage the inbox
python scripts/triage_inbox.py

# Tomorrow's brief (after editing briefs/_tomorrow.md)
python scripts/connor.py

# This week's reflection
python scripts/cassandra.py

# Validate the whole repo
python scripts/validate.py
```

## Folder structure

```
ffanderson-brain/
├── inbox/                    # Raw inputs and freshly ingested meetings (status: raw)
├── inbox/raw/                # Raw transcripts (gitignored)
├── entities/
│   ├── people/               # One file per person
│   ├── companies/            # One file per company
│   ├── funds/                # One file per fund / LP / family office
│   └── concepts/             # Theses, frameworks, mental models
├── meetings/                 # Processed meeting notes
├── journal/                  # Daily notes
├── areas/                    # Areas of responsibility
├── briefs/                   # Morning briefs (Connor)
├── thesis/
│   ├── pillars/              # Owner-written thesis pillars
│   └── reflections/          # Weekly reviews (Cassandra)
├── reference/                # External content cached for reference
├── agents/                   # Agent specs (Sally, Connor, Cassandra, etc.)
├── templates/
├── scripts/
└── scripts/prompts/          # Externalised LLM prompts
```

## The agents

The repository runs alongside a small roster of named agents. Each has one
job and a Markdown spec in `agents/`. See [agents/README.md](agents/README.md)
for the philosophy and the full list.

| Agent       | Role                                                         | Status        |
| ----------- | ------------------------------------------------------------ | ------------- |
| Sally       | Meeting scribe — transcripts → meeting + mentions            | implemented   |
| Ellie       | Email watcher — forwarded mail → mentions                    | spec only     |
| Connor      | Calendar scout — produces morning briefs                     | implemented   |
| Nancy       | News monitor — weekly digests on tracked companies           | spec only     |
| Arthur      | Deal analyst — answers ad-hoc analytical questions           | spec only     |
| Cassandra   | Reflection agent — weekly review of thesis vs behaviour      | implemented   |

## The daily and weekly loop

**Morning.** Read `briefs/<today>.md` (written by Connor the night before).
Edit the suggested questions if you want. Walk into your meetings.

**Throughout the day.** Meetings recorded by PLAUD or Granola; transcripts
land in `inbox/raw/`. Quick notes go into the day's `journal/<date>.md`.

**Evening (≤ 10 minutes).**
1. `python scripts/sally.py <transcript>` for each new transcript.
2. `python scripts/triage_inbox.py` to list raw items.
3. For each, `python scripts/triage_inbox.py promote <file>` — Sally's
   mentions get a quick review.
4. Edit `briefs/_tomorrow.md` with tomorrow's meetings.
5. `python scripts/connor.py` writes tomorrow's brief.

**Friday afternoon.** `python scripts/cassandra.py` writes
`thesis/reflections/<week>.md`. Read it. Edit it. Decide what to do about
drift and stale relationships next week. Flip its frontmatter `status` to
`reviewed`.

## Editors

- **Mac**: Obsidian (primary), any text editor.
- **iOS**: Working Copy + Obsidian.
- **Anywhere**: Git + any Markdown editor.

The repo never depends on Obsidian; it is Obsidian-friendly, not
Obsidian-required.

## Key documents

- [SCHEMA.md](SCHEMA.md) — frontmatter contract per type, mentions architecture
- [CONVENTIONS.md](CONVENTIONS.md) — naming, formatting, writing-mention rules
- [DECISIONS.md](DECISIONS.md) — architecture decisions and rationale
- [CLAUDE.md](CLAUDE.md) — instructions for AI agents reading the repo
- [AUDIT.md](AUDIT.md) — audit of the bootstrap pass (historical)
- [UPGRADE_NOTES.md](UPGRADE_NOTES.md) — what the 2026-05-05 upgrade changed

## CRM integration

This repo handles synthesis and judgement. The CRM (Affinity or Attio,
deferred) handles:
- Contact graph and deduplication
- Email/calendar metadata
- Pipeline state

Link the systems via the `crm_system` and `crm_id` frontmatter fields.

## Scripts

| Script | Purpose |
| ------ | ------- |
| `sally.py` | Ingest a transcript → meeting + mentions on every entity touched |
| `connor.py` | Generate tomorrow's morning brief from `briefs/_tomorrow.md` |
| `cassandra.py` | Weekly reflection on thesis vs revealed behaviour |
| `triage_inbox.py` | List/promote inbox items; review Sally's mentions |
| `validate.py` | Schema/consistency checks across the repo |
| `stale.py` | List stale relationships and open follow-ups |
| `create_entity.py` | Create a person/company/fund/concept file from template |
| `create_meeting.py` | Create a meeting file by hand |
| `create_journal.py` | Create today's journal entry |
| `check_links.py` | Legacy link checker (superseded by `validate.py`) |
| `_legacy_ingest_transcript.py` | Old single-pass ingest (kept for one cycle) |
| `utils.py` | Shared helpers |
| `llm_client.py` | Provider-neutral LLM wrapper |

## License

Private repository. All rights reserved.

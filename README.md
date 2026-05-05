# ffanderson-brain

A Git-versioned, Markdown-based personal knowledge system for venture capital investing.

## Philosophy

- **Plain Markdown only**: No proprietary formats. Readable in any text editor for 50+ years.
- **YAML frontmatter**: Structured metadata on every file.
- **Wiki-links**: `[[Entity Name]]` creates the knowledge graph.
- **One file per entity**: People, companies, funds, concepts each get one canonical home.
- **Privacy by default**: Nothing here should be assumed shareable.

## Quick Start

```bash
# Install Python dependencies for scripts
cd scripts
pip install -r requirements.txt

# Create a new entity
python create_entity.py person "Jane Doe" --role "Founder" --company "StartupX"
python create_entity.py company "StartupX" --sector ai --stage seed

# Create a meeting
python create_meeting.py "Call with Jane Doe" --attendees "Jane Doe" --companies "StartupX"

# Create today's journal entry
python create_journal.py

# Ingest a transcript
python ingest_transcript.py ~/Downloads/transcript.txt --source plaud

# Triage inbox
python triage.py

# Check for broken links
python check_links.py
```

## Folder Structure

```
ffanderson-brain/
├── inbox/              # Raw inputs awaiting triage
├── entities/
│   ├── people/         # One file per person
│   ├── companies/      # One file per company
│   ├── funds/          # One file per fund
│   └── concepts/       # Thesis, frameworks, mental models
├── meetings/           # Meeting notes (date-prefixed)
├── journal/            # Daily notes (YYYY-MM-DD.md)
├── areas/              # Areas of responsibility
├── templates/          # File templates
├── scripts/            # Python automation
├── CONVENTIONS.md      # Detailed conventions and standards
└── DECISIONS.md        # Architecture decision records
```

## Daily Workflow

1. **Morning**: Create journal entry (`python scripts/create_journal.py`)
2. **After meetings**: Create/update entity files, add meeting notes
3. **End of day**: Triage inbox (`python scripts/triage.py`), review and link

## Editors

- **Mac**: Obsidian (primary), any text editor
- **iOS**: Working Copy + Obsidian
- **Anywhere**: Git + any Markdown editor

## Key Documents

- [CONVENTIONS.md](CONVENTIONS.md) - Naming, formatting, and structural standards
- [DECISIONS.md](DECISIONS.md) - Architecture decisions and rationale

## CRM Integration

This repo handles synthesis and judgment. Your CRM (Affinity/Attio) handles:
- Contact graph and deduplication
- Email/calendar metadata
- Pipeline state

Link between systems using the `crm_id` frontmatter field.

## Scripts

| Script | Purpose |
|--------|---------|
| `create_entity.py` | Create person/company/fund/concept files |
| `create_meeting.py` | Create meeting notes |
| `create_journal.py` | Create daily journal entry |
| `ingest_transcript.py` | Import transcripts to inbox |
| `triage.py` | List and manage inbox items |
| `check_links.py` | Find broken wiki-links and orphans |
| `utils.py` | Shared utilities |

## License

Private repository. All rights reserved.

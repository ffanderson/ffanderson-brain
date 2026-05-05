---
type: meta
name: Conventions
created: 2026-05-05
updated: 2026-05-05
---

# Conventions

This document defines the standards and conventions for this knowledge system.

## File Naming

- **All filenames use kebab-case**: `john-smith.md`, `acme-corp.md`, `ai-agents-thesis.md`
- **No spaces, no special characters**: Only lowercase letters, numbers, and hyphens
- **Meeting files include date prefix**: `2026-05-05-call-with-john.md`
- **Journal files are date-only**: `2026-05-05.md`

## Frontmatter

Every file MUST have YAML frontmatter with at minimum:
- `type`: The entity type (person, company, fund, concept, meeting, journal, area, inbox)
- `name` or `title`: Human-readable display name
- `created`: ISO 8601 date when file was created
- `updated`: ISO 8601 date of last significant edit

### Required Fields by Type

#### Person
```yaml
type: person
name: "Full Name"
slug: full-name
crm_id: # ID from Affinity/Attio when linked
created: 2026-05-05
updated: 2026-05-05
```

#### Company
```yaml
type: company
name: "Company Name"
slug: company-name
crm_id: 
created: 2026-05-05
updated: 2026-05-05
stage: # seed, series-a, series-b, growth, public
sector: # ai, fintech, healthcare, etc.
status: # tracking, evaluating, passed, invested, exited
```

#### Fund
```yaml
type: fund
name: "Fund Name"
slug: fund-name
crm_id: 
created: 2026-05-05
updated: 2026-05-05
fund_type: # vc, pe, family-office, corporate, angel
relationship: # lp, co-investor, peer, prospect
```

#### Concept
```yaml
type: concept
name: "Concept Name"
slug: concept-name
created: 2026-05-05
updated: 2026-05-05
category: # thesis, framework, mental-model
status: # developing, stable, deprecated
```

#### Meeting
```yaml
type: meeting
title: "Meeting Title"
slug: 2026-05-05-meeting-title
date: 2026-05-05
created: 2026-05-05
source: # plaud, granola, manual
attendees: [] # wiki-links to people
status: # raw, processed, archived
```

#### Journal
```yaml
type: journal
date: 2026-05-05
created: 2026-05-05
```

## Wiki-Links

Use `[[Entity Name]]` syntax to link to any entity:

- `[[John Smith]]` - links to `entities/people/john-smith.md`
- `[[Acme Corp]]` - links to `entities/companies/acme-corp.md`
- `[[Sequoia Capital]]` - links to `entities/funds/sequoia-capital.md`
- `[[AI Agents Thesis]]` - links to `entities/concepts/ai-agents-thesis.md`

The display name in wiki-links should match the `name` field in frontmatter.

## Dates

- **Always ISO 8601**: `2026-05-05`, never `May 5, 2026` or `5/5/26`
- **Include time when relevant**: `2026-05-05T14:30:00`
- **Timezone assumed local** unless explicitly specified

## Tags

Use lowercase, hyphenated tags in frontmatter arrays:

```yaml
tags: [ai, fintech, seed-stage, high-conviction]
```

Reserved tag prefixes:
- `p/` - Pipeline stage: `p/first-call`, `p/dd`, `p/term-sheet`
- `s/` - Sector: `s/ai`, `s/fintech`, `s/climate`
- `t/` - Thesis: `t/ai-agents`, `t/vertical-saas`

## Status Values

### Entity Status
- `active` - Currently relevant
- `inactive` - No longer active but historically relevant
- `archived` - Moved to cold storage

### Company Pipeline Status
- `tracking` - On radar, no active engagement
- `evaluating` - In active diligence
- `passed` - Decided not to invest
- `invested` - Portfolio company
- `exited` - Former portfolio company

### Meeting Status
- `raw` - Unprocessed transcript
- `processed` - Extracted and linked
- `archived` - Fully processed, moved to archive

### Concept Status
- `developing` - Still forming
- `stable` - Fully developed
- `deprecated` - No longer valid/useful

## Folder Structure

```
ffanderson-brain/
├── inbox/           # Raw inputs awaiting triage
├── entities/
│   ├── people/      # One file per person
│   ├── companies/   # One file per company
│   ├── funds/       # One file per fund
│   └── concepts/    # Thesis, frameworks, mental models
├── meetings/        # Meeting notes and transcripts
├── journal/         # Daily notes
├── areas/           # Areas of responsibility/focus
├── templates/       # File templates
└── scripts/         # Automation scripts
```

## Writing Style

- **Be concise**: Bullet points over paragraphs for facts
- **Use headers**: Structure content for scanning
- **Link liberally**: Every entity mention should be a wiki-link
- **Date entries**: When adding notes, prefix with date: `2026-05-05: Spoke about...`
- **Quote directly**: Use `>` blockquotes for verbatim quotes

## Git Commits

- Commit frequently with clear messages
- Use conventional commits when appropriate:
  - `add: john-smith.md` - New entity
  - `update: acme-corp.md` - Updated existing
  - `meeting: 2026-05-05-call-with-john` - New meeting notes
  - `journal: 2026-05-05` - Daily journal entry
  - `triage: processed 5 inbox items` - Batch triage

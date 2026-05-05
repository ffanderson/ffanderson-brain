---
type: meta
name: Decisions
created: 2026-05-05
updated: 2026-05-05
---

# Architecture Decisions

This document records significant design decisions made during system setup.
Each decision follows the format: Context, Decision, Rationale, Consequences.

---

## ADR-001: Flat entity folders over nested hierarchy

**Date**: 2026-05-05

**Context**: Entities could be organized in deep hierarchies (e.g., `companies/ai/b2b/acme-corp.md`) or flat folders with metadata-based organization.

**Decision**: Use flat folders with one level of entity-type grouping only.

**Rationale**:
- Deep hierarchies require knowing the category before finding a file
- Categories change; a company might pivot from fintech to AI
- Obsidian and other tools handle flat structures with metadata better
- Search and wiki-links work regardless of folder depth
- Simpler mental model: "people go in people/, companies in companies/"

**Consequences**:
- Large folders (100+ files) may feel unwieldy in file browsers
- Must rely on frontmatter `sector`, `tags` for categorization
- Obsidian's graph view and search become primary navigation

---

## ADR-002: Wiki-links use display names, not slugs

**Date**: 2026-05-05

**Context**: Wiki-links could use slugs (`[[john-smith]]`) or display names (`[[John Smith]]`).

**Decision**: Use display names that match the `name` frontmatter field.

**Rationale**:
- More readable in raw Markdown
- Obsidian resolves display names to files automatically
- Changing a filename doesn't break the conceptual link
- Natural writing: "Met with [[John Smith]] about [[Acme Corp]]"

**Consequences**:
- Requires Obsidian's alias/link resolution
- Must keep `name` field consistent with how you write links
- Plain text editors won't resolve links (acceptable per design principles)

---

## ADR-003: CRM as source of truth for contact graph, repo for synthesis

**Date**: 2026-05-05

**Context**: Both CRM and repo could store contact information, relationships, and pipeline state.

**Decision**: CRM (Affinity/Attio) owns contact graph, email/calendar metadata, and pipeline state. Repo owns notes, analysis, and synthesis.

**Rationale**:
- CRMs excel at entity resolution, deduplication, and relationship tracking
- CRMs integrate with email/calendar automatically
- Repo excels at freeform notes, linked thinking, and version history
- Trying to maintain contact graph in Markdown is fragile
- `crm_id` field provides the bridge between systems

**Consequences**:
- Some duplication of basic info (name, company, role)
- Must manually sync when CRM data changes significantly
- Can query CRM for "who have I emailed?" and repo for "what do I think?"

---

## ADR-004: Meeting files include date prefix

**Date**: 2026-05-05

**Context**: Meeting files could be named by content (`call-with-john.md`) or include dates (`2026-05-05-call-with-john.md`).

**Decision**: Always prefix meeting files with ISO date.

**Rationale**:
- Chronological sorting in file browsers
- Prevents collision when meeting same person multiple times
- Date is always relevant context for meetings
- Matches journal file convention

**Consequences**:
- Longer filenames
- Must remember to include date when creating manually

---

## ADR-005: Inbox for raw inputs, not separate by source

**Date**: 2026-05-05

**Context**: Raw inputs (transcripts, emails, notes) could go in source-specific folders (`inbox/plaud/`, `inbox/granola/`) or one unified inbox.

**Decision**: Single `inbox/` folder for all raw inputs.

**Rationale**:
- Source is metadata (`source:` in frontmatter), not folder
- Triage workflow doesn't care about source
- Simpler mental model: "everything unprocessed is in inbox"
- Can filter by source in Obsidian if needed

**Consequences**:
- Inbox may mix very different content types
- Source identification relies on frontmatter being set correctly

---

## ADR-006: No Obsidian-specific plugins required

**Date**: 2026-05-05

**Context**: Obsidian plugins could provide powerful features (Dataview queries, Templater, etc.).

**Decision**: System must work without any Obsidian plugins. Plugins are optional enhancements.

**Rationale**:
- Design principle: "Obsidian-compatible but not Obsidian-dependent"
- Plugin APIs change; plugin maintenance is unpredictable
- Must work in Working Copy on iOS (no plugins)
- Must work for LLMs reading raw files
- 50-year readability requirement

**Consequences**:
- No Dataview queries in files (would appear as code blocks)
- Templates use `{{date}}` placeholder, not Templater syntax
- Some conveniences require manual work or external scripts

---

## ADR-007: Scripts in Python, not shell or JavaScript

**Date**: 2026-05-05

**Context**: Automation scripts could be written in shell, Python, JavaScript, or other languages.

**Decision**: Use Python for all scripts.

**Rationale**:
- Python is ubiquitous and likely to remain so
- Excellent YAML/Markdown parsing libraries
- User has Python 3.11 available
- Single language reduces cognitive overhead
- Works on Mac, iOS (Pythonista), and most environments

**Consequences**:
- Requires Python installation
- Some operations (simple file moves) more verbose than shell
- JavaScript developers may need to learn Python basics

---

## ADR-008: Privacy by default with comprehensive .gitignore

**Date**: 2026-05-05

**Context**: Repo could be public-ready or private-by-default.

**Decision**: Assume all content is private. Gitignore covers common leak vectors.

**Rationale**:
- VC work involves confidential information
- Easier to make public later than to scrub private data
- Design for paranoia, relax later if needed

**Consequences**:
- Must actively choose to share anything
- .gitignore may occasionally hide intentional files (can override)

---

## ADR-009: Status fields over folder-based workflow

**Date**: 2026-05-05

**Context**: Workflow state (e.g., "tracking" → "evaluating" → "invested") could be managed by moving files between folders or by updating frontmatter status.

**Decision**: Use frontmatter `status` field, not folder moves.

**Rationale**:
- Wiki-links don't break when status changes
- Can have multiple status dimensions (pipeline status, activity status)
- Easier to query and report on
- Files stay in canonical location

**Consequences**:
- Must update frontmatter, not just drag-and-drop
- Requires discipline to keep status current
- May need scripts to find stale statuses

---

## ADR-010: Templates use simple placeholders

**Date**: 2026-05-05

**Context**: Templates could use Obsidian Templater syntax, Mustache, or simple placeholders.

**Decision**: Use `{{variable}}` placeholders that are human-readable and tool-agnostic.

**Rationale**:
- Works without any template engine
- Human can manually replace `{{date}}` with actual date
- Scripts can do simple string replacement
- Obsidian Templater can be configured to use this syntax
- No learning curve

**Consequences**:
- No conditional logic in templates
- No automatic date insertion without tooling
- Templates are documentation as much as automation

---

## Future Decisions to Make

- [ ] Which CRM (Affinity vs Attio) - deferred until user decides
- [ ] Sync mechanism between CRM and repo
- [ ] Archive strategy for old meetings/journal entries
- [ ] Backup strategy beyond Git
- [ ] Mobile capture workflow details

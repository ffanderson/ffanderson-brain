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

## ADR-011: Mentions are inline Markdown sections, not a separate store

**Date**: 2026-05-05

**Context**: The mentions architecture (atomic, dated, sourced fragments
attached to entities) could live in (a) a `mentions/` folder with one file
per mention, (b) a SQLite/JSON sidecar database, or (c) inline Markdown
sub-sections inside the entity's own file under a `## Mentions` heading.

**Decision**: Option (c). Mentions live inline.

**Rationale**:
- Reading the entity file already gives you everything; no second tool needed.
- The wiki-link graph remains the only graph; no parallel "mention graph."
- Append-only is trivially correct in Markdown; database invariants would
  require migration tooling on every schema change.
- Plain-text resilience: a mentions store separate from entities risks drift
  if one survives the other.
- Solo-GP scale doesn't need indexing.

**Consequences**:
- Entity files grow over time; old mentions push down. Mitigation: newest-at-top
  ordering plus an eventual archive convention (deferred).
- Cross-entity queries ("show me everything from this meeting") require
  scanning entity files. Sally writes a `<!-- source_hash: ... -->` comment in
  each mention so deduplication and reverse-lookup are O(grep).

---

## ADR-012: Agent specs are Markdown, not YAML/JSON config

**Date**: 2026-05-05

**Context**: Each agent (Sally, Connor, Cassandra, etc.) has identity, scope,
inputs, outputs, and accumulating skills. Could live in a config file
(`agents.yml`), a directory of JSON specs, or one Markdown file per agent.

**Decision**: One Markdown file per agent in `agents/`.

**Rationale**:
- The spec is read by humans (the owner, future analysts) and by the agents
  themselves (the file is fed back into the agent's prompt).
- Markdown lets prose, examples, and skill lists coexist without config-DSL
  ceremony.
- Skill accretion (`## Skills` section) is naturally narrative; it would
  awkwardly fit YAML.
- Adding a new agent is "create one file"; no schema migration.

**Consequences**:
- Some structured fields (name, role, status) live in frontmatter; the rest
  is prose. Agents must parse Markdown to find their own spec — but they were
  going to read prose anyway.

---

## ADR-013: Pipeline state lives in the company `status` field, not in tags

**Date**: 2026-05-05

**Context**: The original CONVENTIONS proposed a `p/` tag prefix
(`p/first-call`, `p/dd`, `p/term-sheet`) parallel to the company `status`
field (`tracking | evaluating | passed | invested | exited`).

**Decision**: Drop the `p/` prefix. The company `status` field is the only
authority for pipeline state.

**Rationale**: Two axes for the same concept invite drift. The audit pass
(see AUDIT.md, recommendation #5) flagged this and the upgrade pass enforces
it.

**Consequences**: Existing files using `p/` tags need a one-pass cleanup
when the owner notices them. None exist in the seed corpus today.

---

## ADR-014: No `slug` field; filename stem is canonical

**Date**: 2026-05-05

**Context**: The bootstrap convention duplicated the slug into both filename
and a `slug:` frontmatter field.

**Decision**: Drop the `slug:` field. Filename stem is canonical.

**Rationale**: Two sources of truth invite drift. Per audit recommendation #6.

**Consequences**: The `slug` field is removed from templates and seed files.
A stale `slug:` field in any user-created file before this change is harmless
but ignored.

---

## ADR-015: No `updated` field; Git is the source of truth for modification time

**Date**: 2026-05-05

**Context**: Templates carried a hand-maintained `updated:` field that
invariably rotted.

**Decision**: Drop `updated:` from templates and seed files. `git log` is the
authority for "when was this changed."

**Rationale**: Per audit recommendation #7. Lying metadata is worse than
absent metadata.

**Consequences**: Existing files with stale `updated:` values are harmless
but ignored by validation.

---

## ADR-016: Cassandra is the only fully implemented "reflection-class" agent in this pass

**Date**: 2026-05-05

**Context**: The roster includes six agents. Implementing all of them in one
pass would be a lot of code that the owner cannot evaluate before they have
a real corpus to test against.

**Decision**: Implement Sally, Connor, and Cassandra. Spec Ellie, Nancy, and
Arthur, but defer their implementations until the corpus is large enough
that the read-side and side-channel agents add value.

**Rationale**:
- **Sally** is mandatory: she is the entry point for new information. Without
  Sally, no mentions accumulate, and the rest of the system is empty.
- **Connor** is high-leverage and low-risk: a brief generator on a
  hand-edited input list is a one-evening implementation that compounds
  every day it runs.
- **Cassandra** is the most important agent because reflection is the only
  output the owner cannot easily replicate by hand. The point of the system
  is to surface what the owner cannot see; Cassandra is the realisation of
  that.
- **Ellie / Nancy / Arthur** are useful but optional. Each has external
  dependencies (email connector, RSS scraping, retrieval strategy) that
  benefit from being designed against a real corpus.

**Consequences**: The agent roster is partly aspirational. The roster table
in `agents/README.md` makes status explicit so the owner is never surprised.

---

## ADR-017: Single LLM provider, swappable

**Date**: 2026-05-05

**Context**: Sally, Connor, and Cassandra all call an LLM. Coupling to one
provider is fine; coupling to one provider in a way that is hard to undo is
not.

**Decision**: All LLM calls go through `scripts/llm_client.py` (`LLMClient`
class). The default provider is Anthropic via the official Python SDK. A
mock mode (`LLM_MOCK=1`) returns deterministic stub responses for offline
runs and CI.

**Rationale**: A future swap to OpenAI or local inference is a single-file
change. The mock mode lets validation and dry-runs proceed without an API
key.

**Consequences**: A small abstraction tax (one method, `complete()`).
Acceptable.

---

## Future Decisions to Make

- [ ] Which CRM (Affinity vs Attio) — deferred until owner decides
- [ ] Sync mechanism between CRM and repo
- [ ] Archive strategy for old meetings, journal entries, and mentions
- [ ] Backup strategy beyond Git
- [ ] Mobile capture workflow details
- [ ] Email connector for Ellie (Gmail API vs IMAP vs forwarder)
- [ ] News feed list for Nancy
- [ ] Whether to add a `literature` entity type for books/papers (open from AUDIT.md)

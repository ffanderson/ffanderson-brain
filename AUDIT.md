---
type: meta
name: Audit
created: 2026-05-05
updated: 2026-05-05
---

# Audit of `ffanderson-brain` Scaffolding

## Overall assessment

The scaffolding is solid in the ways that matter most: plain Markdown + Git, flat entity folders, frontmatter on everything, CRM-as-source-of-truth-for-graph, and ten ADRs that explain the reasoning behind the non-obvious choices. The first agent made the right structural decisions and the daily loop will work.

The headline strength is the discipline of the design: it is genuinely tool-agnostic (passes the "switch editors in 5 years" test), and the ADRs make future changes auditable. The headline weakness is that **the repo has no instructions for the LLMs that are supposed to read it** — there is no `CLAUDE.md` / `AGENTS.md` describing where things live, how `[[wiki-links]]` resolve to files, or what the frontmatter contract is. An LLM pointed at this repo today has to reverse-engineer all of that from `CONVENTIONS.md`, which is written for humans. Given that LLM ingestibility is an explicit design goal, this is the single biggest gap. The second-biggest is a cluster of small first-month friction points (stub conventions, status vocabulary collisions, the link checker producing noise on its first run) that will erode trust in the scripts before they prove useful.

## Keep as-is

These are right. Don't touch them.

- **Plain Markdown + YAML frontmatter + wiki-links.** Correct foundation. ADR-006 (no plugin dependence) and ADR-002 (display-name links) are well-reasoned.
- **Flat entity folders by type.** ADR-001 is correct; deep hierarchies would rot the moment a company pivots sectors.
- **CRM owns the contact graph; repo owns synthesis.** ADR-003 is the most important architectural decision in the system. Don't blur this line.
- **Status fields, not folder moves, for workflow state.** ADR-009 is correct and prevents wiki-link rot.
- **Inbox is a single folder, source-as-metadata.** ADR-005 is correct.
- **Date-prefixed meeting filenames, ISO 8601 dates.** Both correct; collision-safe and chronologically sortable.
- **Python for scripts, `python-frontmatter` + `python-slugify` for parsing.** Sensible, ubiquitous, low risk.
- **`.gitignore` covers the obvious leak vectors** (audio/video, `.env`, `secrets/`, Obsidian workspace state). Good baseline.
- **Templates are small and don't try to capture too much.** Good restraint — every aspirational field would have become friction.
- **One canonical file per entity, not scattered partial records.** Correct and matches the way the human will think about it.

## Recommend changing

Ordered by impact, not by file.

### 1. Add a `CLAUDE.md` (a.k.a. `AGENTS.md`) at the repo root for LLM readers

**What.** A short top-level file (50–100 lines) describing the repo to an LLM: folder semantics, the frontmatter contract, how `[[wiki-links]]` resolve to filenames, where to write new files, and what *not* to invent (e.g., never fabricate a `crm_id`, never assert investment status without a source). Reference `CONVENTIONS.md` and `DECISIONS.md` rather than restating them.

**Why.** LLM ingestibility is one of the four stated design goals, and right now there is no machine-targeted entry point. `README.md` is human-onboarding, `CONVENTIONS.md` is a style guide, neither tells an agent "given a question about company X, look in `entities/companies/<slug>.md`, then meetings tagged with `[[X]]`, then concepts referencing X." Without this file, every LLM session re-derives the schema, badly.

**Sketch.**

```markdown
# Instructions for AI Agents

You are reading a personal knowledge repository for a venture capital investor.
Plain Markdown + YAML frontmatter + `[[wiki-links]]`. No database, no plugins.

## Where things live
- `entities/people/<slug>.md`     — one file per person; `name` field is canonical
- `entities/companies/<slug>.md`  — one file per company
- `entities/funds/<slug>.md`      — funds, LP firms, family offices, angels
- `entities/concepts/<slug>.md`   — theses, frameworks, mental models
- `entities/literature/<slug>.md` — books, papers, articles (see #3 below)
- `meetings/YYYY-MM-DD-<slug>.md` — one file per meeting
- `journal/YYYY-MM-DD.md`         — one file per day
- `inbox/`                        — raw, unprocessed inputs
- `areas/<slug>.md`               — areas of responsibility (PARA-style)

## Resolving `[[Wiki-Links]]`
Match against the `name` field in frontmatter (case-insensitive), not filenames.
If unresolved, the link is a stub — do not invent a file unless asked.

## Frontmatter contract
Every file has `type:`. See CONVENTIONS.md for required fields per type.
Treat `type` as authoritative; the folder is a hint, not a guarantee.

## What not to do
- Never fabricate `crm_id`, funding amounts, valuations, or attendees.
- Never change `status` without explicit instruction.
- When uncertain, surface the uncertainty in the file as a `> [!todo]` block
  rather than guessing.
```

### 2. Fix `check_links.py` — it produces false positives on first run

**What.** Three concrete bugs:

1. It scans `README.md`, `CONVENTIONS.md`, `DECISIONS.md` and flags illustrative links like `[[Entity Name]]` and `[[Acme Corp]]` from documentation as broken. Skip top-level `*.md` docs, or skip files with `type: meta` in frontmatter.
2. It does not understand aliased links: `[[2026-05-05-...-call|Display]]` is treated as a single literal target. Strip everything after `|` before resolution.
3. It only resolves links against `entities/`. Links to meetings (e.g., from a journal) and to journal entries are flagged broken. Add `meetings/` and `journal/` to the resolvable set, keyed by filename stem when no `name` field exists.

**Why.** The current run reports 11 "issues," of which ~8 are false positives. A linter that cries wolf on day one will be ignored by week two. This is the only validation tool in the repo; it has to be trustworthy.

**Sketch (in `find_all_links`):**
```python
# before
for md_file in repo_root.rglob("*.md"):
    if "templates" in md_file.parts:
        continue

# after
SKIP_FILES = {"README.md", "CONVENTIONS.md", "DECISIONS.md", "AUDIT.md", "CLAUDE.md"}
for md_file in repo_root.rglob("*.md"):
    if "templates" in md_file.parts:
        continue
    if md_file.parent == repo_root and md_file.name in SKIP_FILES:
        continue
```

**Sketch (alias handling, in `extract_wiki_links` in utils.py):**
```python
def extract_wiki_links(text: str) -> list[str]:
    pattern = r"\[\[([^\]]+)\]\]"
    return [m.split("|", 1)[0].strip() for m in re.findall(pattern, text)]
```

**Sketch (resolvable set):** also index `meetings/*.md` and `journal/*.md` by filename stem and by `title` / `date` fields, so cross-references resolve.

### 3. Add a `literature` entity type for books, papers, and long-form articles

**What.** A fifth entity type under `entities/literature/`, with a template:

```yaml
---
type: literature
name: "Title of Work"
slug: title-of-work
created: {{date}}
updated: {{date}}
kind:        # book, paper, article, podcast, talk
authors: []  # wiki-links to [[Person]] when known, plain strings otherwise
year:
url:
status:      # to-read, reading, read, abandoned
tags: []
---

## Summary
## Key Claims
## Quotes
## My Take
## Related
```

**Why.** Reading notes are explicitly in scope per the brief. Today they would be force-fit into `entities/concepts/`, which is for *the owner's* theses and frameworks — putting a Sequoia blog post or a Stripe paper in there muddies the concept of a concept. The `entities/concepts/ai-agents-thesis.md` already has a "References" section listing external work as plain strings; those should resolve to literature files once enough volume accrues.

**Bonus.** Add `literature` to `create_entity.py`'s `ENTITY_TYPES` and `TYPE_TO_FOLDER`.

### 4. Add a stub-creation convention for unresolved `[[wiki-links]]`

**What.** Add a section to `CONVENTIONS.md` that says: when you write `[[Sarah Johnson]]` in a meeting note and Sarah doesn't have a file yet, that's *fine* — the link is a stub. Stubs are first-class. The link checker will list them. Resolve them when (a) you have something to say about the person, or (b) the same name has appeared three+ times. Until then, the unresolved link is the to-do.

**Why.** The seed file `entities/people/john-smith.md` writes `Introduced by [[Sarah Johnson]]` and `Intro to [[Portfolio Company A]]` — neither has a file. There is no documented convention for what that means. An owner under time pressure will either (a) stop writing the link and lose the graph edge, or (b) feel obligated to create stub files immediately, which is friction. Documenting "stubs are fine, the broken-links report is your worklist" closes this.

**Sketch (add to CONVENTIONS.md):**
```markdown
## Stubs

`[[Wiki-Link]]` to an entity that doesn't exist yet is a **stub** — intentional and
expected. Don't avoid the link; the unresolved reference is your reminder.

`scripts/check_links.py` lists all stubs. Promote a stub to a real file when:
- you have substantive notes to write about it, or
- the name has appeared in 3+ meetings (heuristic, not a rule).

External attendees in `meetings/*.md` should always use `[[Full Name]]` form,
never plain strings, so they appear in the stub list.
```

### 5. Resolve the status-vocabulary collision

**What.** Three problems, one fix:

1. `inbox` items use `status: unprocessed | processed | archived`.
2. `meeting` files use `status: raw | processed | archived`.
3. The `p/` tag-prefix family duplicates the company `status:` field.

Pick one vocabulary per axis. Recommend: rename inbox `unprocessed` → `raw` (matches meetings); drop the `p/` tag prefix entirely and let the company `status` field own pipeline state. The `p/` prefix in `CONVENTIONS.md` was speculative — neither the seed company nor the seed meeting uses it.

**Why.** Two vocabularies for the same concept (raw input awaiting processing) is exactly the kind of thing that the owner will get wrong on day three and stop trusting on day fourteen. And duplicate axes (`p/dd` tag *and* `status: evaluating`) means future-you has to remember to update both.

**Diff.**
```yaml
# inbox-item.md template — before
status: unprocessed
# after
status: raw
```
```markdown
# CONVENTIONS.md — remove
- `p/` - Pipeline stage: `p/first-call`, `p/dd`, `p/term-sheet`
```

### 6. Drop the `slug` field from frontmatter

**What.** Remove `slug:` from every template and from the required-fields list in `CONVENTIONS.md`. Filename is canonical.

**Why.** `slug` is always equal to the filename stem. A duplicated source of truth invites drift: rename the file but forget the field, and now the link checker, the entity finder, and a human reader disagree about what the slug is. The filename already plays this role and is more visible. `create_entity.py` and `create_meeting.py` set `slug` explicitly — that's effort spent maintaining a redundant field.

**Diff.** Delete `slug:` lines from `templates/*.md`, the seed entity files, and from `create_entity.py`/`create_meeting.py`.

### 7. Drop or auto-maintain the `updated` field

**What.** Two options:

(a) Delete `updated` from all templates. Git already records modification time and provides a real history.

(b) Keep it but auto-update via a Git pre-commit hook (`scripts/touch_updated.py`) that bumps `updated:` on any modified Markdown file before commit.

Recommend (a). It is honest about the fact that the field will rot; Git is the source of truth for "when was this changed."

**Why.** No hand-maintained timestamp survives. The seed files were all created today and all already say `updated: 2026-05-05`. The first time the owner edits `acme-ai.md` and forgets to bump it, the field is lying. Lying metadata is worse than absent metadata.

### 8. Distinguish LPs from co-investors from operating relationships

**What.** Two changes:

1. Funds template already has `relationship: lp | co-investor | peer | prospect` — good. Add `portfolio-investor` (the GP fund that invested in *us*, if applicable) and document the vocabulary explicitly in `CONVENTIONS.md`.
2. Add an optional `relationship:` field to the **person** template with values: `founder | operator | lp | co-investor | service-provider | press | personal | other`. Default empty.

**Why.** The brief explicitly asks how an LP is tracked vs. a co-investor vs. a fund. Right now: a fund-as-LP is captured by `relationship: lp` on the fund file (good). But the *individual* at that LP — the family-office principal who actually decides — is just a `person`, indistinguishable from a founder. With ~25 LPs (per `areas/fund-operations.md`), the owner will want to filter "show me all my LP contacts" without resorting to free-text search.

**Why not a separate `entities/lps/` folder.** Tempting but wrong. An LP today might be a founder tomorrow, or a co-investor's spouse. People don't want to be re-filed; tag the relationship.

### 9. Decouple `crm_id` from CRM choice

**What.** Replace the bare `crm_id:` field with two fields:

```yaml
crm_system:    # affinity | attio | none
crm_id:
```

Or, if cleaner, namespace the field directly: `affinity_id:` / `attio_id:`.

**Why.** ADR-003 correctly defers the Affinity-vs-Attio call. But once that call is made, IDs from the chosen system go into `crm_id` and there's nothing recording *which* system they're from. If the owner ever migrates (or hires an analyst who briefly uses both), the IDs are ambiguous. Cost of fixing this now: trivial. Cost later: a one-off migration script.

### 10. Make `ingest_transcript.py` source detection less eager

**What.** In `detect_source()`, default to `unknown` rather than substring-matching on content. Keep filename-based detection (more reliable). Require `--source` for unambiguous classification.

**Why.** The current heuristic flags any transcript containing the word "zoom" as a Zoom meeting, even if it was a Granola transcript that mentions a Zoom call. Source is metadata that should be set deliberately, not guessed from the text body.

**Diff.**
```python
# before
def detect_source(content, filename):
    content_lower = content.lower()
    filename_lower = filename.lower()
    if "plaud" in content_lower or "plaud" in filename_lower: return "plaud"
    ...
# after
def detect_source(filename):
    name = filename.lower()
    for s in ("plaud", "granola", "otter", "zoom"):
        if s in name: return s
    return "unknown"
```

### 11. Trim aspirational template fields

**What.** Remove fields that will be left blank 90% of the time:

- `journal.md`: drop `mood:` and `energy:`. (Reintroduce later if the owner actually fills them.)
- `person.md`: drop `twitter:` (lower hit-rate than LinkedIn; can go in body if relevant). Keep `linkedin:` and `email:`.
- `fund.md`: drop `aum:`, `vintage:`, `gp:`. AUM is public-data and stale-prone; vintage is per-fund-instance not per-firm; GP is captured better in `## Key People`.

**Why.** Empty fields in YAML are noise to LLMs (they have to learn that `aum: ` means "unknown") and friction to humans (every empty line is a "should I fill this?" decision). Schema rule: a field earns its place by being filled in the majority of cases.

### 12. Tighten `.gitignore`

**What.** Add:
```
# Audio in inbox specifically
inbox/audio/
inbox/recordings/

# Common transcript provider exports that may contain raw audio refs
inbox/*.zip

# Sensitive deck/PDF formats from data rooms
data-rooms/
*.dataroom.pdf
```

Reconsider: the existing `*.pdf` is *not* ignored — and probably shouldn't be globally, since the owner will want to commit benign PDFs (one-pagers, public memos). The `data-rooms/` folder convention is the right line to draw.

**Why.** Audio gets handled by extension globs but a folder-level rule is more honest about the actual workflow (PLAUD exports an audio + transcript bundle into a single folder). Data-room PDFs are the most sensitive single artifact a VC handles; they deserve an explicit rule even if they would fall under `*.pdf` already (they don't, currently).

## Open questions for the owner

1. **Affinity or Attio?** Keep `crm_id` generic until you decide, but the choice affects #9. If you've already decided, tell me which.
2. **Personal life in the same repo?** The brief mentions "family/personal relationships." The current scaffolding implicitly assumes work-only. Two reasonable answers: (a) one repo, with `tags: [personal]` and `relationship: personal` to filter; (b) a second `ffanderson-life` repo. Pick one — the answer changes whether to add a `relationships` area, a `family.md`, etc.
3. **LP-as-individual files: one per person, or rolled up under the LP firm?** A family office with three principals and one analyst — do you want four person files plus the fund file, or just the fund file with people listed inline? My default would be person-files-when-you've-actually-met-them, but you may have a reason to want all four upfront.
4. **Round/cap-table data: deliberately out of scope, or just not yet?** Nothing in the scaffolding addresses it. If the answer is "the CRM and the data room handle it, the repo just synthesizes," that should be one sentence in `DECISIONS.md` (ADR-011) so future-you doesn't relitigate. If the answer is "I want a rough running tally per portfolio company," the `company` template needs a `## Cap Table Snapshot` section with a date-stamped convention.

## Things I'd add later (not now)

- **`scripts/validate.py`** — a stricter schema check (required fields per `type`, enum validation on `status`, date-format check). Premature today; build it after the conventions stabilize via real use, around month two.
- **`scripts/todos.py`** — aggregate all `- [ ]` checkboxes across the repo, grouped by file and ordered by file mtime. Useful once there are 50+ open items; useless with five.
- **`scripts/stale.py`** — find entities with `status: evaluating` that haven't been touched in N days. Same logic: needs volume.
- **Auto-generated index files** (`entities/people/INDEX.md` etc., regenerated via script). Nice for navigation in plain editors; redundant under Obsidian.
- **LLM-driven inbox triage** — script that reads an inbox item and proposes entity extractions and links. High leverage but only after the entity graph is dense enough to disambiguate.
- **A `correspondence/` folder or `type: email`** — let it emerge. For now, paste important emails into the relevant `person` or `meeting` file under a dated `> Quote` block.
- **Pre-commit hook** to auto-bump `updated:` (only if you choose option (b) of recommendation #7).
- **A "now" page** (`now.md` at root, or pinned in `areas/`) summarizing current focus. Lightweight, but only worth adding once you notice yourself wanting it.
- **Backup beyond Git** (Future Decision #4 in `DECISIONS.md`). A nightly `git bundle` to S3/Backblaze is the obvious answer; not worth setting up before there's something to lose.

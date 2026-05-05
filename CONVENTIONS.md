---
type: meta
name: Conventions
created: 2026-05-05
updated: 2026-05-05
---

# Conventions

Style and process. The structural contract lives in [SCHEMA.md](SCHEMA.md);
architectural rationale lives in [DECISIONS.md](DECISIONS.md).

## File naming

- All filenames use kebab-case: `john-smith.md`, `acme-corp.md`.
- Only lowercase letters, numbers, and hyphens. No spaces, no special characters.
- Meeting and inbox filenames include an ISO date prefix: `2026-05-05-call-with-john.md`.
- Journal filenames are date-only: `2026-05-05.md`.
- Reflection filenames are ISO week: `2026-W18.md`.

## Wiki-links

Use `[[Display Name]]` syntax, matching the `name` (or `title`) field of the
target file. Resolution is by frontmatter name, not filename.

```text
[[John Smith]]      → entities/people/john-smith.md
[[Acme AI]]         → entities/companies/acme-ai.md
[[Sequoia Capital]] → entities/funds/sequoia-capital.md
```

Aliased syntax is allowed for cross-referencing meetings and journals from
prose: `[[2026-05-05-call-with-john|Call with John]]`. The link checker strips
the alias before resolution.

### Stubs

A `[[Wiki-Link]]` to an entity that does not yet have a file is a **stub** —
intentional and expected. Stubs are first-class: the unresolved reference is
your reminder that this person/company exists in your world.

`scripts/validate.py` lists stubs. Promote a stub to a real file when:

- you have substantive notes to write about it, or
- the name has appeared in 3+ sources (heuristic, not a rule).

External attendees in `meetings/*.md` should always use `[[Full Name]]`,
never plain strings, so they appear in the stub list. Sally enforces this
during ingestion.

## Dates

- Always ISO 8601: `2026-05-05`. Never `May 5, 2026` or `5/5/26`.
- Include time when relevant: `2026-05-05T14:30:00`.
- Timezone is local unless specified.

## Tags

Lowercase, hyphenated, in YAML arrays:

```yaml
tags: [ai, fintech, seed-stage, high-conviction]
```

Reserved tag prefixes:

- `s/` — sector: `s/ai`, `s/fintech`, `s/climate`
- `t/` — thesis: `t/ai-agents`, `t/vertical-saas`

(The previous `p/` pipeline-stage prefix was removed; the company `status` field
owns pipeline state. See DECISIONS.md ADR-013.)

## Status vocabularies

| context              | values                                                            |
| -------------------- | ----------------------------------------------------------------- |
| entity (general)     | `active` \| `inactive` \| `archived`                              |
| company pipeline     | `tracking` \| `evaluating` \| `passed` \| `invested` \| `exited`  |
| meeting / inbox      | `raw` \| `processed` \| `archived`                                |
| concept              | `developing` \| `stable` \| `deprecated`                          |
| reflection           | `draft` \| `reviewed`                                             |
| brief                | `draft` \| `edited` \| `stale`                                    |

## Writing mentions

A **mention** is a dated, sourced fragment of context attached to an entity.
See [SCHEMA.md](SCHEMA.md) for the structural contract; this section is
editorial guidance.

### What qualifies

A mention captures **substantive context**: a fact, observation, claim, or
decision that would still be useful in 6 months.

- Good: "Aiden said the round will close by 5/15 with Sequoia leading at $15M post."
- Good: "Dave noted Nadia's flywheel resembles Standard Kernel's vertical play."
- Bad: "We also discussed Acme."
- Bad: "John mentioned Acme during the call."

If you cannot write a sentence that would still inform a decision in 6 months
without re-watching the meeting, do not write a mention.

### Granularity

One mention per (source × entity × distinct topic). A meeting that discussed
Nadia's pricing and Nadia's hiring writes two mentions on Nadia's file, not
one combined mention.

### Voice

Third person, past tense, paraphrased — never transcribed. Mentions summarize;
they do not quote at length. Use blockquotes (`>`) for verbatim only when the
exact wording matters.

### Length

One to four sentences. If it runs longer, it belongs in the meeting note's
`## Synthesis` section, not as a mention.

### Disambiguation

If a meeting names a person whose file does not exist yet, Sally creates a
stub file (`relationship_strength: cold`, `first_seen: <today>`, otherwise
empty) and writes the mention against the stub. Manual writers should follow
the same pattern.

If two candidate files match (two `John Smith` entities), the mention is
written with both candidates wiki-linked: `[[John Smith (Acme)]] / [[John Smith (Beta)]]`.
Sally flags this in her run summary.

## Writing style

- Bullet points over paragraphs for facts.
- Use headers; structure for scanning.
- Link liberally — every entity mention is a wiki-link.
- Date inline notes: `2026-05-05: Spoke about pricing.`
- Use `>` blockquotes for verbatim quotes only.

## Git commits

- Commit frequently. Clear messages.
- Conventional prefixes:
  - `add: <slug>` — new entity
  - `update: <slug>` — modified entity
  - `meeting: <slug>` — new meeting note
  - `journal: <date>` — daily journal
  - `triage: <count> items` — batch triage
  - `mentions: <count>` — batch mention writes (Sally)
  - `reflection: <week>` — weekly reflection (Cassandra)

## Slug field

There is no `slug` frontmatter field. Slug is the filename stem; a duplicate
field invites drift. (Removed in 2026-05-05 upgrade; see DECISIONS.md ADR-014.)

## Updated field

There is no `updated` frontmatter field. Git is the source of truth for
modification time. (Removed in 2026-05-05 upgrade; see DECISIONS.md ADR-015.)

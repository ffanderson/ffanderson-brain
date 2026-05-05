# Instructions for AI Agents

You are reading a personal knowledge repository for a venture capital investor.
Plain Markdown + YAML frontmatter + `[[wiki-links]]`. No database, no plugins,
no web service. The repo plus a text editor plus the scripts in `scripts/` is
the entire stack.

Read [SCHEMA.md](SCHEMA.md) for the structural contract,
[CONVENTIONS.md](CONVENTIONS.md) for style, and
[DECISIONS.md](DECISIONS.md) for rationale.

## Where things live

| folder                    | contains                                              |
| ------------------------- | ----------------------------------------------------- |
| `entities/people/`        | one file per person, named by `slug`                  |
| `entities/companies/`     | one file per company                                  |
| `entities/funds/`         | funds, LP firms, family offices, angel groups         |
| `entities/concepts/`      | the owner's theses, frameworks, mental models         |
| `meetings/`               | processed meeting notes, `YYYY-MM-DD-<slug>.md`       |
| `journal/`                | daily notes, `YYYY-MM-DD.md`                          |
| `inbox/`                  | raw, unprocessed inputs awaiting triage               |
| `inbox/raw/`              | raw transcript bytes (gitignored)                     |
| `areas/`                  | areas of responsibility (PARA-style)                  |
| `agents/`                 | named agent specs (Sally, Connor, etc.)               |
| `briefs/`                 | morning briefs by Connor, `YYYY-MM-DD.md`             |
| `thesis/`                 | the owner's investment thesis pillars                 |
| `thesis/reflections/`     | weekly reviews by Cassandra, `YYYY-Www.md`            |
| `reference/`              | external content cached for reference                 |
| `reference/news/`         | weekly news digests by Nancy                          |
| `templates/`              | file templates with `{{placeholder}}` syntax          |
| `scripts/`                | Python automation                                     |
| `scripts/prompts/`        | externalised LLM prompts (editable without code)      |

## Resolving wiki-links

`[[Display Name]]` matches the `name` (or `title`) field in frontmatter,
case-insensitive. Aliased form `[[file-stem|Display]]` is allowed; strip
everything after `|` before resolution.

`type` in frontmatter is authoritative; folder is a hint.

## Mentions

The most important data primitive in this repo is the **mention**: an atomic,
dated, sourced fragment of context attached to an entity, living under a
`## Mentions` heading inside the entity's own file. See SCHEMA.md.

Mentions are append-only. They are written by Sally (the ingestion agent) and
occasionally by hand. Do not invent mentions. Do not edit existing mentions
except to fix factual errors, and note the correction inline.

## What you must not do

- Never fabricate `crm_id`, valuations, funding amounts, attendees, or dates.
- Never change `status`, `relationship_strength`, or `last_touch` without
  explicit instruction.
- Never delete files. Rename or archive.
- Never modify the body content of a `meeting` or `thesis` file. Frontmatter
  and mentions on referenced entities are fair game; the prose of a meeting
  or thesis is the owner's record.
- Never push a commit unless the owner asks.

## When uncertain

Surface uncertainty in the file as a `> [!todo]` callout rather than guessing:

```markdown
> [!todo] Sally couldn't resolve "John from Acme" — two candidates: [[John Smith]] / [[John Park]]. Owner to disambiguate.
```

## The agent roster

See [agents/README.md](agents/README.md). Each agent has a scoped responsibility.
If asked to do something outside your scope, decline and suggest the right
agent or workflow.

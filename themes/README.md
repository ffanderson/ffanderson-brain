---
type: meta
name: Themes
created: 2026-05-17
---

# Themes

Theme dossiers — agent-generated memos summarising who the owner already
knows in an investment area (Tier 1) and who the public web says is also
active in it (Tier 2, deferred).

Written by [[Glendower]] via `python scripts/glendower.py "<theme>"`.

## Conventions

- Filenames are kebab-case slugs of the theme: `ai-native-legal-agents.md`.
- Frontmatter `type: theme`.
- Owner's `## Owner judgement` section at the bottom is the place to add
  conviction notes. Glendower never writes into it.
- Re-running on the same slug overwrites the file. Themes shift; the
  diff between versions is the signal.
- Mentions on entity files **do not** auto-link to themes. If a theme is
  worth tracking explicitly, add a `tags: [t/<slug>]` to the relevant
  entity files by hand.

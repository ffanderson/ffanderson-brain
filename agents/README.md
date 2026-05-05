---
type: meta
name: Agent Roster
created: 2026-05-05
---

# The Agent Roster

Agents are named employees with scoped responsibilities. Each agent does one
thing and does it consistently. Naming them (rather than calling them "the
ingestion script") makes it easy to talk about who did what and to grant or
revoke their access without ambiguity.

The roster is inspired by the architecture Union Square Ventures published
about how their team works alongside named LLM agents. The lineage is
intentional; the implementation is local and minimal.

## Roster

| Agent       | Role                | Status            |
| ----------- | ------------------- | ----------------- |
| [Falstaff](falstaff.md)         | Meeting scribe — turns transcripts into meeting notes and mentions  | implemented       |
| [Bardolph](bardolph.md)         | Email watcher — turns forwarded mail into mentions                  | spec only         |
| [Hotspur](hotspur.md)       | Calendar scout — produces morning briefs                            | implemented (manual input) |
| [Rumour](rumour.md)         | News monitor — weekly digests on tracked companies                  | spec only         |
| [Poins](poins.md)       | Deal analyst — answers ad-hoc analytical questions                  | spec only         |
| [Warwick](warwick.md) | Reflection agent — weekly review of stated thesis vs revealed behaviour | implemented   |

## Philosophy

- **Named, not anonymous.** Saying "Falstaff wrote 7 mentions" is clearer than
  "the ingestion script wrote 7 mentions." The owner is a solo GP; this is the
  team.
- **Scoped, not omnibus.** Each agent owns one workflow. If asked to do
  something outside its scope, the agent declines and suggests the right
  agent or workflow.
- **Provenance is mandatory.** Every output an agent produces is traceable to
  its source. No claim is unattributable.
- **Markdown-first.** Each agent's spec is a Markdown file in this folder,
  readable by humans and by the agents themselves at runtime. There is no
  YAML/JSON config separate from these files.
- **Skills accrete.** Each agent's spec has a `## Skills` section that grows
  over time as the owner gives feedback. This is institutional memory.

## Adding a new agent

1. Create `agents/<name>.md` following the format of an existing agent file.
2. Pick a name that's easy to say. Avoid initialisms.
3. Implement (or spec) the agent's pipeline as a script in `scripts/<name>.py`.
4. Add a row to the roster table above.
5. Document the addition in [DECISIONS.md](../DECISIONS.md).

---
type: concept
name: Vertical AI Agents
created: 2026-05-17
category: thesis
status: developing
tags: [thesis, ai-agents, vertical, enterprise, t/ai-agents]
agent_drafted: true
---

# Vertical AI Agents

> [!note] **Agent-drafted (Glendower / Claude).** Composed from the corpus
> as it stood on 2026-05-17 — primarily the existing
> `[[AI Agents Thesis]]` concept, the Acme AI intro call, and Patrick
> Mayfield's edge-cases conversation. Owner to revise into first-person
> prose. Replace this block with your own framing when you do.

## Definition

Autonomous software agents that plan, reason, and use tools to complete
multi-step enterprise workflows within a single domain — procurement,
legal discovery, claims handling, sales operations, accounts payable —
rather than horizontal "assist anything" tooling. The bet is that domain
specificity wins because workflow context is where willingness-to-pay
concentrates, not in the underlying model.

## Why now

- Foundation-model reliability has crossed the threshold where multi-step
  tool use is workable in production (Acme AI's 90% task completion on a
  15-step procurement flow is the empirical anchor here).
- Enterprise budgets are visibly migrating from RPA and BPO line items
  into agent-shaped vendors.
- The horizontal platforms (OpenAI, Anthropic) keep building general
  agent capabilities, which intensifies the pressure to find vertical
  defensibility quickly.

## Investment criteria

What this thesis bets on:
- Technical founders with deep ML/AI background (Stanford-grade, lab-grade)
- A single vertical or workflow as the wedge — not a platform pitch
- Enterprise GTM, not consumer; B2B willingness-to-pay is the load-bearing
  assumption
- Demonstrated agent in production, not a chatbot demo
- A founder who can articulate the failure modes, not just the happy path

## What we'd pass on

- Horizontal agent frameworks or "AutoGPT for everything" plays
- Workflow tools that re-package GPT-4 with a workflow UI on top
- Consumer agents (different distribution dynamics, different defensibility)
- Companies whose moat collapses if OpenAI/Anthropic ships a native
  vertical capability

## Tension

The data this week (and most weeks since the corpus opened) shows a pull
toward AI infrastructure plays (RLBF, neuro-annotation, training-data
pipelines, model evaluation) and toward AI-native insurance ventures.
Both are off this pillar. If the owner believes those are also worth
backing, write separate pillars for them rather than silently widening
this one.

## Active deals against this thesis

- [[Acme AI]] — evaluating; intro call 2026-05-05; five follow-ups stale
  (see meeting note)

## Related

- [[AI Agents Thesis]] — the earlier draft of this pillar in
  `entities/concepts/`
- [[Foundation Models]] (stub)
- [[Enterprise AI Adoption]] (stub)

## Open questions

- What's the right pricing model — seats, outcomes, usage?
- How do vertical agents compete when OpenAI ships a vertical product?
- At what point does "owns the workflow" become "owns the buyer
  relationship" — i.e., what's the durable lock-in?

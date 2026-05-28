---
type: inbox
title: "Spinor IC memo draft"
date: 2026-05-26
created: 2026-05-26
source: manual
source_hash: ""
attendees:
  - "[[Fraser Anderson]]"
  - "[[Tyler|Tyler Nguyen]]"
  - "[[Brian|Brian Menard]]"
  - "[[Alex Wissner-Gross]]"
  - "[[Will Baine]]"
  - "[[Bill Gross]]"
companies:
  - "[[Spinor]]"
  - "[[SpaceX]]"
  - "[[Caltech]]"
  - "[[Energy Vault]]"
  - "[[VEIR]]"
  - "[[Endeavor Edge Infrastructure]]"
  - "[[Tesla]]"
  - "[[Helion]]"
funds:
  - "[[Link Ventures]]"
  - "[[Logos]]"
  - "[[021T]]"
  - "[[Valor Ventures]]"
  - "[[Atreides]]"
tags: [ic-memo, deep-tech, superconductors, energy-storage, data-centers, caltech]
status: raw
---

# Spinor IC memo draft

## Classification header

```text
Company: Spinor | Category: CORE | Type: TRADITIONAL deep-tech infrastructure
Deal: Type A if observer rights are secured; otherwise NO GO under governance rule | Stage: Pre-seed / seed
Ecosystem: Caltech + SpaceX | Score: 85/104 exception-adjusted
Board: Fraser observer seat requested | Location: Mountain View / Caltech network
Source: Will Baine / Logos, with additional Lucas/Tom validation, Alex Wissner-Gross engagement, and Bill Gross target involvement
Completeness: REQUIRES DISCUSSION (6/10 materials, 35/40 checks)
Recommendation: Authorize up to $4M at $40M post-money; target 10% ownership for less if possible
```

AI disclosure: This draft was generated from the partner-provided second-call transcript, Spinor deck, existing repository notes from the 2026-05-18 first call and investment discussion, the supplied EERA SMES factsheet, and public NERC materials on large-load grid reliability. It needs human review before circulation.

## Hard filter check

| Gate | Result | Notes |
|---|---:|---|
| 1. Solo founder | PASS | This is explicitly not a solo-founder deal. The company has two bonded SpaceX founders: [[Tyler|Tyler Nguyen]] and [[Brian|Brian Menard]]. |
| 2. Founder relationship | PASS | Tyler and Brian worked together at SpaceX Redmond on Starlink solar power systems, giving the company a real high-pressure operating bond rather than a newly assembled founder pairing. |
| 3. Governance 100% rule | PASS ONLY IF OBSERVER SECURED | Tyler said board observers can be discussed; no board is currently formed. Investment should require observer rights, information rights, and regular operating cadence. |
| 4. Ecosystem floor | PASS / DELIBERATE CALTECH EXTENSION | Not MIT/Harvard, but that is the point of the deal. This is the MIT playbook grafted onto Caltech through Tyler's unusually concrete Caltech recruiting pipeline. |
| 5. SAFE stacking | FLAG | Tyler prefers simple SAFEs. Need MFN / side-letter protections, pro rata, information rights, and observer language before close. |
| 6. Pivot capability | PASS | SMES is the first wedge into adaptive superconducting magnet systems; adjacent applications include substations, EV charging, grid protection, space infrastructure, and radiation shielding. |
| 7. Founder distraction | PASS | No active competing founder project surfaced. Main risk is strategic sprawl after Alex's broader platform framing. |
| 8. Passion alignment / E3 pattern | PASS | Tyler's Caltech/SpaceX power systems path is directly aligned with superconducting energy storage and magnets. |
| 9. Revenue ambition | PASS WITH FLAG | Pilot customer and $600M potential opportunity suggest ambition, but there is no financial model, pricing schedule, or margin path in the materials. |

Overall: PASS WITH FLAGS. The flags are governance, SAFE terms, and missing financial model; the Caltech ecosystem exposure is a core reason to invest, not a defensive exception.

## Executive summary

Spinor is building superconducting magnetic energy storage (SMES) systems for AI data centers, starting as a behind-the-meter "shock absorber" for megawatt-scale, millisecond power spikes. The immediate customer pain is credible: AI clusters create fast load swings that can force grid overbuild, delay energization, and punish generators, transformers, switchgear, lithium-ion batteries, and supercapacitors that were not designed for high-frequency cycling. Spinor's claim is that SMES can absorb and discharge power at very low latency without chemical degradation or thermal runaway.

This is a CORE recommendation because it is exactly the MIT playbook grafted onto Caltech: two bonded technical founders out of SpaceX, a founder with unusually deep Caltech trust density, and a named bench of Caltech builders ready to join if the company has capital and momentum. The company is not AI-native software, but it is attacking a hard infrastructure bottleneck created by AI. The wedge is data-center power smoothing; the larger company is a superconducting magnet platform for data centers, grid resilience, and space infrastructure.

The ask is authorization to invest up to $4M at a $40M post-money valuation, while trying to secure roughly 10% for less capital if allocation allows. Tyler said the company oversubscribed an initial $3M raise in ten days, is now targeting roughly $5-8M total, and could accept $8-10M to give the company a two-year runway. The Spinor deck's original ask was $3M to reach a 2027 live data-center pilot, with funds allocated 40% pilot production, 34% labor, 17% lab/office, 2% software/IT, and 7% misc.

The recommendation is to invest if four conditions are met before signing: observer or board-level information rights, protected SAFE terms, direct verification of the pilot LOI / customer economics, and at least two independent founder references. The strongest incremental work before IC is not more market research; it is proving that Tyler can close the Caltech high-voltage / mechatronics team he already identified and that Spinor can get a data-center operator comfortable testing a cryogenic superconducting system near live critical loads.

## Team

This is not a solo-founder underwriting case. Spinor is two bonded SpaceX builders plus a Caltech recruiting pipeline that Tyler has already mapped before the round is closed. Tyler Nguyen is the core reason to lean in. He studied mechanical and aerospace engineering at Caltech, worked on advanced power systems, energy storage, space-to-ground power transmission, high-altitude balloons, autonomous systems, and electric propulsion, then spent more than two years at SpaceX owning Starlink solar cell technology R&D, power architecture, manufacturing operations, software and controls teams, and on-orbit operations. The deck sharpens the same point: Tyler worked on PV semiconductor R&D, mass manufacturing, and on-orbit operations for Starlink Solar, did energy storage research at Caltech, and founded Shine, which deployed 150+ microgrids.

Brian Menard is the complementary execution half. The deck identifies him as Head of Engineering and says he took 4,000+ space-grade mechanisms to mass manufacturing and orbit at SpaceX, and designed solar EVs to break world records. Existing repository notes add that he worked on the same SpaceX Redmond team, designed deployable solar array structures, and brings Cal Poly EV / solar racing plus Lockheed aerospace experience. The team pattern is credible for this problem: two founders bonded in SpaceX mass-production discipline, then amplified by Tyler's Caltech power-systems network around a hardware product that has to be engineered, not discovered.

The important team question is not whether this is "just Tyler"; it is whether Tyler can convert his Caltech trust graph into the first technical cell. He has already identified his three closest Caltech builder friends and a broader named hiring bench: David Kornfeld for EE power electronics, high voltage, superconductors, Caltech / SpaceX / Helion experience; Hope Arnette for TI HEV / powertrain and high-voltage power electronics; and Paulina Ridland, Tanner Moore, and James "Jimmy" Hamilton as mechanical / thermal / mechatronics force multipliers. This is unusually concrete for a pre-seed deep-tech company. The round is not merely funding engineering hours; it is funding Tyler's ability to recruit the Caltech version of the MIT teammate cluster that has worked for us before.

Tyler's personal resilience is also part of the founder assessment. Partner notes describe Tyler as an adult orphan who lost his parents young; the exact family details should be confirmed directly rather than inferred. In Link's own pattern work on childhood trauma and outsized success, this is high-signal only when paired with observed execution, speed of learning, and direct evidence that the founder can hold pressure without becoming brittle. Here it appears alongside Caltech, SpaceX, fast fundraising, rapid customer iteration, and a willingness to make hard personnel decisions.

Tyler showed that personnel judgment in the Solomon Olshane discussion. He considered bringing in a close friend with Tesla / supply-chain relevance, then decided the immediate company-building need was not a fit for co-founder equity. That is a small but useful signal: Tyler is affable, but not conflict-avoidant. The same call showed the weakness: he has historically been the person who puts his head down and solves the problem in front of him. Link's job is to help him become an executive who uses capital, investors, and network leverage before the bottleneck becomes his own calendar.

Recruiting pattern rating: HIGH. The visible patterns are known-network recruiting, technical star density, Caltech project trust, SpaceX execution credibility, and mission-driven climate / energy motivation. Talent pool visibility is VISIBLE because Tyler has named specific people and their expected roles. The Fred Wilson bonding assessment is PASS pending reference detail: Tyler and Brian worked together in a high-pressure SpaceX hardware environment, and Tyler's Caltech pipeline adds the same "best friends solving a hard technical problem" pattern we look for in MIT-origin companies.

> [!todo]
> Verify whether existing repository references to "Ryan" are a transcript error for Brian Menard or refer to a separate SpaceX co-founder candidate. The Spinor deck and partner-provided LinkedIn link identify Brian Menard as Head of Engineering.

> [!todo]
> Get at least two independent reference calls. Required references: Will Baine / Logos, Lucas from AtomWorks or another Caltech peer, and one SpaceX technical reference who can speak to Brian's operating quality.

## Market and thesis

The narrow wedge is AI data-center power smoothing. The deck claims measured DGX-H100 cluster load swings of 15 MW peak-to-peak and frames the customer pain as cascading grid risk, capex destruction, forced overbuild, and delayed energization. NERC's 2025 Long-Term Reliability Assessment says AI and digital-economy data centers account for most of the projected increase in North American electricity demand over the next decade, and notes observed roughly 1,500 MW voltage-sensitive load reduction events tied to large-load behavior. Spinor's commercial claim is that a behind-the-meter SMES system can decouple the AI load from the upstream grid and protect expensive power infrastructure from becoming recurring opex.

The timing catalyst is HTS tape. Tyler and Alex converged on the same "why now": fusion has pulled high-temperature superconducting tape manufacturing down the cost curve and increased manufacturing maturity. Alex's handwritten note was blunt: "HTS getting cheaper as a consequence of the fusion industry is a huge vector for success here." Spinor does not need the highest-performance fusion-grade tape; it needs enough magnetic-field performance at a cost that makes high-cycle power smoothing economical. Tyler said vendors have moved from $45/meter quotes toward $25/meter and sees a materials-cost floor far below that, but he is not underwriting the company on immediate tape vertical integration.

The independent SMES precedent supports the physics but not yet the venture-scale product. The EERA factsheet describes SMES as very fast response energy storage, with response time around 5 ms, efficiency near 95%, no degradation under cycling, and expected lifetime around 30 years. It also notes roughly 325 MW of installed power globally and TRL 8 for low-temperature SMES, while high-temperature SMES remains around TRL 5-6 because of system cost, power-electronics complexity, cryogenic cooling, and low energy density. This lines up with the investment question: not "does SMES work?" but "can this team package HTS SMES into a manufacturable, customer-acceptable data-center product fast enough?"

Alex Wissner-Gross improved the upside framing. Spinor is not just a data-center battery. It can be the adaptive superconducting magnet company: first, high-frequency magnetic energy storage for data centers; second, low-latency grid-protection systems for substations and possibly geomagnetic disturbance / Carrington-event resilience; third, longer-term space infrastructure, including space tethers as torque-rod-like systems, HTS tape for space propulsion, radiation shielding / deflector shields, and orbital data-center power systems. The near-term wedge remains data centers; the platform option is superconducting magnets wherever low-latency electromagnetic response matters.

The "why Jensen Huang cares" answer is straightforward. NVIDIA's largest customers cannot deploy unconstrained GPU clusters if power delivery, grid interconnection, and transient loads become binding constraints. A system that lets a data center run closer to full power utilization without overbuilding generation, transformers, switchgear, lithium-ion batteries, or dummy loads is strategically relevant to the AI compute buildout. Jensen does not care about SMES as science; he cares if it removes power volatility as a governor on GPU deployment.

## Business model and moat

The likely initial business model is hardware systems sold or leased to data-center builders and operators, with service / maintenance economics around cryogenics, controls, power electronics, and monitoring. The deck names a 2027 pilot at a 0.5 GW data-center builder and a potential $600M commercial opportunity, but the pricing model, margin structure, warranty exposure, and deployment cadence are not yet in the materials.

The moat is partly technical and partly operational. Technically, the system combines HTS coils, cryocooling, power electronics, controls, and data-center integration. Operationally, the moat is learning how to design for manufacturing around HTS tape, qualify the system for critical infrastructure, and survive procurement scrutiny from data-center operators and utilities. VEIR helps here by educating hyperscalers that superconducting power delivery is real, while Spinor's fixed storage device may be easier than cooled superconducting cable runs.

The full vertical integration question is important but should not be a precondition for this round. Tyler understands the economics of HTS manufacturing and has scoped similar thin-film / deposition manufacturing equipment at SpaceX. He also understands that tape manufacturing is a different company: materials scientists, process engineers, equipment, quality systems, and significant capex. The right sequence is application first, tape optionality later. If China dumps tape and fusion subsidizes supply, the application layer wins. If tape remains scarce or expensive, Spinor needs either privileged supply, co-development, or eventual vertical integration.

## Competitive landscape

The incumbent alternatives are lithium-ion batteries, supercapacitors, flywheels, generators, grid overbuild, and software throttling / dummy loads. Spinor's deck positions SMES as occupying the high-power / fast-discharge niche that alternatives do not cover cleanly: less than 1 ms response, roughly unlimited cycle life, no thermal runaway, and a claimed $250M per GW price point versus $1.2B for lithium-ion and $930M for supercapacitors. These figures need diligence, but the qualitative differentiation is coherent.

Lithium-ion fails if the application requires many high-frequency charge/discharge cycles per minute. Supercapacitors respond quickly but store too little energy and can be expensive at GW scale. Flywheels face mechanical risk and lower cycle life. Generators and behind-the-meter gas solve energy supply but not high-frequency load volatility. Software smoothing is a workaround that wastes compute potential by throttling workloads or burning power on dummy loads.

The competitive risk is not that a battery company has a better chemistry for this exact job. It is that the customer chooses a lower-risk but less elegant architecture: overbuild power, accept lower utilization, segment workloads, put more conventional storage outside the shell, or wait for rack / cluster architectures to change. Spinor has to prove that its reliability and integration risk is lower than the cost of those compromises.

## Deal dynamics and financials

Tyler said the company oversubscribed an initial $3M raise in ten days and is now closing a $5-8M round, potentially $8-10M, at a $40M post-money valuation. Fraser is advocating for authorization to invest up to $4M at $40M post-money, but will try to secure 10% ownership for less. The original deck ask was $3M to reach a 2027 data-center pilot. If Link invests $4M at $40M post, the clean ownership math is 10%. If the round expands to $8-10M at the same post, we need to watch dilution, allocation pressure, and whether a larger seed creates unnecessary valuation expectations before the 2027 pilot.

Use of funds from the deck:

| Use | Share |
|---|---:|
| Pilot production | 40% |
| Labor | 34% |
| Lab / office | 17% |
| Misc | 7% |
| Software / IT | 2% |

Co-investor quality is unusually strong for the category. Fraser was introduced by Will Baine, a close friend building Logos, a deep-tech spinout fund from Valor Ventures. Will ran Valor's JV fund with Atreides, led the Base Power deal, sat on the board, participated in the Crusoe deal, and spent significant time with Chase Lochmiller; he has real energy infrastructure judgment rather than generic deep-tech enthusiasm. Logos is already an investor. Alex Wissner-Gross indicated 021T wants to make an investment if the economics are right and has already sharpened the platform narrative. Bill Gross should be brought in given Tyler's Caltech / Energy Vault history and Gross's energy network. This can be a technically literate cap table with relevant energy, compute, and platform-company judgment.

> [!todo]
> Confirm exact current round instrument, side-letter terms, pro rata, MFN, information rights, observer rights, and whether the $40M post is a post-money SAFE cap or priced-round valuation.

> [!todo]
> Request the financial model: system ASP, gross margin, warranty assumptions, tape cost sensitivity, cryocooling / BoP cost, install cost, target payback period, and revenue timing from pilot to commercial deployment.

Revenue classification: PRE-REVENUE traditional deep-tech infrastructure. The revenue ambition is ADEQUATE TO AMBITIOUS if the 0.5 GW pilot customer can become a $600M commercial opportunity by 2028, but ABSENT under the memo framework until the model is provided. Gate 9 therefore passes only as a qualitative ambition check, not as a quantitative revenue-plan check.

## Governance and engagement plan

This should not proceed without governance. Tyler is open to board observers, but there is no board yet. The minimum Link package should be observer rights once a board exists, monthly investor updates before then, quarterly technical / customer milestone reviews, full pro rata, information rights, and approval / notice around major financing or sale processes. If the company refuses observer or equivalent information rights, this becomes a NO GO under the Link governance rule despite the quality of the founder.

Link's value-add is unusually specific. Fraser can help with the Caltech recruiting campaign, introduce Bill Gross, deploy Alex Wissner-Gross / 021T around space and grid-protection applications, pressure-test data-center insurance and power-chain risk with existing market work, and use the superconductingalliance.org / HTS tape network to validate supply. This is exactly the MIT ecosystem playbook, re-aimed at Caltech: identify the dense technical trust graph early, help the founder recruit the best friends and builders before the company is legible to normal funds, and use Link's network to turn a technical wedge into a platform narrative. The engagement plan should be weekly through close and then monthly until the pilot line is built.

Immediate work plan:

- Secure allocation and terms while the round is still being rounded up.
- Push Tyler to prioritize David Kornfeld and Hope Arnette as high-voltage / power-electronics hires.
- Verify the Endeavor / pilot LOI and the $600M commercial opportunity math.
- Introduce Bill Gross and Alex / 021T into a structured conversation, not an open-ended platform brainstorming session.
- Get one technical review from an HTS / SMES expert and one data-center operator reference on willingness to trial the system.

## Exit strategy

Path A is a strategic acquisition by a power, data-center, grid, or industrial-electrification buyer. Named potential acquirers include Schneider Electric, Eaton, ABB, Siemens Energy, GE Vernova, Vertiv, Tesla Energy, NVIDIA-adjacent data-center infrastructure partners, and large data-center operators that conclude Spinor is a gating power-system layer. This is the floor: if Spinor proves high-cycle SMES integration, the IP, team, and customer learning should be valuable even before standalone scale.

Path B is the standalone power-law company. In that outcome, Spinor becomes the adaptive superconducting magnet platform for AI data centers, substations, ultra-fast charging, grid resilience, and eventually space infrastructure. The standalone case requires manufacturing competence, reliable field deployments, lower tape costs, and a product architecture that can be replicated faster than custom infrastructure projects usually scale.

Path C is vertical integration into HTS tape or magnet manufacturing if supply remains constrained and Spinor's application demand is real. This is not the seed plan, but it is a valuable strategic option. If Spinor becomes the buyer with the clearest non-fusion demand signal, it may have the leverage to backward integrate or finance a domestic tape supply chain later.

## Conclusion and recommendation

Invest, subject to terms and final diligence. This is a CORE investment. The underwriting is not "novel battery company"; it is a bonded SpaceX founder pair with a unique Caltech pipeline attacking a power bottleneck created by AI with a technology whose physics is known, whose cost curve is improving, and whose first wedge has urgent customer pain. The reason to stretch is not only the data-center smoothing product; it is the possibility that Spinor becomes the superconducting magnet application layer for the AI energy stack.

The top risks are execution, customer adoption, supply chain, and governance. Execution means building a reliable cryogenic power system, not a demo. Customer adoption means getting data-center operators to trial a novel superconducting device in critical infrastructure. Supply chain means HTS tape cost and availability, with China / fusion demand as both tailwind and risk. Governance means Link must not write a large check into a fast-moving seed without observer-level access.

Cool company assessment: yes. It is a technically ambitious, mission-driven, Caltech/SpaceX hardware company with a real shot at becoming narratively important to the AI power buildout. It also gives Link a credible Caltech beachhead. The deal earns CORE treatment because the Caltech beachhead is the point.

## Appendix A: scoring sheet

Exception-adjusted score: 85/104. Strict Link scoring would be lower because the rubric underweights Caltech and non-AI deep-tech infrastructure, but this is a deliberate CORE extension of the Link ecosystem thesis.

| Category | Score | Notes |
|---|---:|---|
| Founding Team | 39/42 | Two bonded SpaceX founders, Tyler's Caltech technical trust graph, named hires, and high-signal resilience pattern. |
| MIT/Harvard Ecosystem | 10/12 | Caltech extension. This is the MIT playbook grafted onto Caltech, not a generic outside-ecosystem exception. |
| AI Focus / Business Model | 13/21 | Not AI-native software, but directly tied to AI data-center deployment constraints. Link network is relevant. |
| $1B Valuation Potential | 10/11 | Large market if data-center wedge works and platform expands into grid / space / industrial power. |
| Traction / Ownership / Governance | 13/17 | LOI and round momentum are strong; ownership target is good; governance still needs to be secured. |
| Total | 85/104 | CORE. Governance failure would block the deal, but ecosystem fit is affirmative. |

Category floor check:

| Category | Floor | Status |
|---|---:|---|
| Founding Team | 10/42 | Above floor |
| Ecosystem | 3/12 | Above floor under deliberate Caltech extension |

Revenue benchmark:

| Item | Spinor | Benchmark | Result |
|---|---|---|---|
| Company type | Traditional deep-tech infrastructure | Traditional / hybrid hardware | Accept with caveat |
| Stage | Pre-revenue | Pre-revenue | 100% projections / pipeline |
| Revenue target | $600M potential customer opportunity cited | $30M+ ARR by Y5 traditional benchmark | Qualitatively ambitious, quantitatively unverified |
| Gross margin | Missing | 70%+ traditional / 60%+ hybrid | Missing |
| Gate 9 | PASS WITH FLAG | Requires projections | Model needed |

## Appendix B: partner Q&A log

Partner feedback incorporated in this revision: Spinor should be framed as a CORE investment, not a hedged ecosystem exception; the team is two bonded SpaceX founders with a unique Caltech pipeline; Tyler has identified his closest Caltech builder friends and named hires; Tyler's orphan / early trauma background is a high-signal resilience pattern when paired with observed execution; Bill Gross should be pulled in; 021T wants to make an investment; Will Baine / Logos is the source of truth and brings deep energy judgment.

Open IC questions:

1. What is the exact instrument and legal term set?
2. Can Link secure observer rights or equivalent governance?
3. Is the 2027 LOI binding enough to underwrite customer seriousness?
4. What is the system-level cost curve at $25/meter, $15/meter, and $5/meter HTS tape?
5. What are the first three hires Tyler can actually close in the next 60 days?
6. What independent references validate Tyler's resilience, technical judgment, and ability to recruit?
7. What exact safety / permitting standards must be met for a live data-center pilot?

## Appendix C: extraction log

| Element | Source | Extracted value | Classification | Confidence | Asked? |
|---|---|---|---|---:|---|
| Company name | Deck | Spinor | Explicit | 0.95 | No |
| Founder | Deck / transcript | Tyler Nguyen, CEO / Founder | Explicit | 0.95 | No |
| Co-founder / engineering lead | Deck | Brian Menard, Head of Engineering | Explicit | 0.90 | No |
| Potential "Ryan" contradiction | Existing notes / transcript | Existing notes mention Ryan; deck says Brian Menard | Ambiguous | 0.50 | No, flagged |
| Product | Deck / transcript | SMES behind-the-meter shock absorber for AI data-center power spikes | Explicit | 0.95 | No |
| Problem | Deck | 15 MW peak-to-peak measured DGX-H100 cluster swings | Explicit | 0.85 | No |
| Pilot | Deck / existing notes | 2027 live data-center pilot, LOI with 0.5 GW builder, $600M potential opportunity | Explicit | 0.85 | No |
| Ask | Deck / transcript / partner prompt | $3M deck ask; current raise $5-8M; Link authorization up to $4M at $40M post | Explicit | 0.95 | No |
| Use of funds | Deck | 40% pilot production, 34% labor, 17% lab/office, 7% misc, 2% software/IT | Explicit | 0.95 | No |
| Round structure | Transcript | Tyler prefers simple SAFEs; priced round possible | Explicit | 0.75 | No, flagged |
| Governance | Transcript | Board observer can be discussed; no board yet | Explicit | 0.75 | No, flagged |
| Caltech hires | Partner prompt | David Kornfeld, Hope Arnette, Paulina Ridland, Tanner Moore, James Hamilton; Tyler has already identified his closest Caltech builder friends | Explicit | 0.95 | No |
| Source of truth | Partner prompt | Will Baine / Logos; Valor / Atreides background; Base Power, Crusoe, Chase Lochmiller energy judgment | Explicit | 0.95 | No |
| Strategic cap table | Partner prompt / second call | 021T wants to invest; Bill Gross should be brought in | Explicit | 0.90 | No |
| HTS cost catalyst | Transcript / EERA factsheet / Alex notes | Fusion-driven HTS manufacturing improvement is a major success vector; SMES maturity and barriers externally supported | Mixed | 0.85 | No |
| Platform expansion | Second call with Alex / handwritten notes | Data-center smoothing, Carrington/grid protection, space tethers, HTS tape for space propulsion, space deflector/radiation shielding | Explicit as discussion, speculative as market | 0.80 | No |
| Financial model | Materials | Missing | Missing | 0.00 | No, flagged |
| Customer willingness to adopt | Transcript / deck | LOI and conversations, but no operator reference in materials | Ambiguous | 0.55 | No, flagged |

Extraction statistics:

- Total elements evaluated: 18
- Explicit: 13
- Mixed / implicit: 2
- Ambiguous: 2
- Missing: 1
- Drafting efficiency: 83% extracted without partner follow-up, but material business diligence remains.

## Appendix D: supporting exhibits and sources

Primary source materials used:

- Partner-provided second call with Tyler, Alex Wissner-Gross, and Fraser, 2026-05-26 prompt.
- Partner-provided post-call discussion transcript with Tom, 2026-05-26 prompt.
- Spinor deck: `/Users/frazeranderson/Downloads/Spinor_Deck_Screen (1).pdf`.
- Existing repository notes: [[2026-05-18-intro-call-tyler-superconducting-energy-storage-startup-smes-for-ai-data-centers]] and [[2026-05-18-investment-discussion-tyler-superconducting-power-systems-for-data-centers]].
- EERA SMES factsheet: https://www.eera-energystorage.eu/component/attachments/?task=download&id=566:EERA_JPES_SP5_Factsheet_final
- NERC 2025 Long-Term Reliability Assessment: https://www.nerc.com/globalassets/our-work/assessments/nerc_ltra_2025.pdf
- NERC comments on co-located large loads and bulk power system reliability risk: https://www.nerc.com/globalassets/who-we-are/legal--regulatory/filings--orders/nerc-filings-to-ferc/2025/comments-re-large-loads-el25-49_signed.pdf

Key deck facts captured:

- Company formed: Oct 2025.
- Bench prototype: Feb 2026, "coil-zero" superconducting coil validated.
- Pilot LOI signed: Apr 2026 to evaluate Spinor product in 2027.
- 2027: build pilot MVP plus prototype manufacturing line and run live data-center pilot smoothing non-real-time compute loads.
- 2028: estimated commercial deployment.
- Team: Tyler Nguyen, Brian Menard, National High Magnetic Field Lab advisor.
- Use of funds: 40% pilot production, 34% labor, 17% lab/office, 7% misc, 2% software/IT.

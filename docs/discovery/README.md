# Discovery & Specs — Scheduling Agent

> Index of all discovery artifacts. Update status and links as each stage is completed.
> For project context, see `CLAUDE.md`. For business rules, see `docs/business-rules.md`.
>
> **Framework:** JTBD + Problem Framing (Marty Cagan) + Assumption Mapping (Teresa Torres)
> **Rule:** problem space first (Stages 1–6), solution space last (Stages 7–8).
> **How to run a stage:** tell Claude "vamos fazer o Stage N" — Claude assumes the lead role, asks structured questions, and writes the artifact at the end.

## Status Legend

| Symbol | Meaning |
|---|---|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Done |

---

## Visual Artifacts

| Artifact | Público | Link |
|---|---|---|
| Flow Diagram (técnico completo) | Devs, Tech Lead, PM | [`flow-diagram.md`](flow-diagram.md) |
| Agent Journey (simplificado) | PM, AEE, Stakeholders | [`agent-journey.md`](agent-journey.md) |

---

## Artifact Index

| # | Stage | Lead Role | Artifact | Status |
|---|---|---|---|---|
| 1 | Problem Framing | PM + Strategist | [`01-problem-framing.md`](01-problem-framing.md) | ✅ |
| 2 | Current State Journey Map | Researcher | [`02-current-journey.md`](02-current-journey.md) | ✅ |
| 3 | JTBD Map | Researcher + PM | [`03-jtbd.md`](03-jtbd.md) | ✅ |
| 4 | Assumption Map | PM + Strategist | [`04-assumption-map.md`](04-assumption-map.md) | ✅ |
| 5 | Edge Case Taxonomy | Engineer + Researcher | [`05-edge-cases-deep.md`](05-edge-cases-deep.md) | ✅ |
| 6 | Flow Mapping & Multi-Agent Routing | Engineer + PM | [`06-flow-map.md`](06-flow-map.md) | ✅ |
| 7 | Success Metrics & Outcome Model | PM + Strategist | [`07-metrics.md`](07-metrics.md) | ✅ |
| 8 | Full PRD | PM | [`08-prd.md`](08-prd.md) | ✅ |

---

## Stage Summaries

### Stage 1 — Problem Framing ✅
**Central question:** What exactly are we solving, for whom, and why now?
**Key outputs:** canonical problem statement, 3 personas (AEE/mentor/founder), evidence of pain, anti-goals.
**File:** [`01-problem-framing.md`](01-problem-framing.md)

---

### Stage 2 — Current State Journey Map ✅
**Central question:** How does the flow work today (without the agent)? Where are the real pain points?
**Key outputs:** step-by-step current journey across all actors, friction points per step, emotional context, cost metrics.
**File:** [`02-current-journey.md`](02-current-journey.md)

---

### Stage 3 — JTBD Map ✅
**Central question:** What is the real "job" each actor is trying to do?
**Key outputs:** functional/emotional/social jobs for AEE, mentor, and founder; Switch Diagram (forces toward and against adoption).
**File:** [`03-jtbd.md`](03-jtbd.md)

---

### Stage 4 — Assumption Map ✅
**Central question:** What must be true for the agent to work? Which beliefs are most risky?
**Key outputs:** H1–H15 hypothesis list, risk × evidence 2×2, top 5 deep-dives, validation roadmap.
**File:** [`04-assumption-map.md`](04-assumption-map.md)

---

### Stage 5 — Edge Case Taxonomy ✅
**Central question:** What can go wrong at each point in the journey, for each persona?
**Key outputs:** 12-case taxonomy, frequency × impact matrix, priority tiers, architectural implications, 3 new agents identified.
**Expands:** `docs/edge-cases.md`
**File:** [`05-edge-cases-deep.md`](05-edge-cases-deep.md)

---

### Stage 6 — Flow Mapping & Multi-Agent Routing ✅
**Central question:** What are all possible flows beyond the happy path? When does the agent hand off to a human, and through which channel?
**Key outputs:** 11 flows mapped (3 new), 6 critical gaps found in current implementation, expanded state machine (+5 states), 4 new agents defined.
**File:** [`06-flow-map.md`](06-flow-map.md)

---

### Stage 7 — Success Metrics & Outcome Model ✅
**Central question:** How do we know we solved the problem?
**Key outputs:** North Star Metric, 10 leading/lagging indicators, 4 guardrails, instrumentation gap list, pilot experiment design.
**File:** [`07-metrics.md`](07-metrics.md)

---

### Stage 8 — Full PRD ✅
**Central question:** What are we building, for whom, and how do we know it worked?
**Key outputs:** full scope (in/out/later), 10 features with testable acceptance criteria, agent architecture table, success metrics with pilot approval criteria, 7 open decisions with owners.
**File:** [`08-prd.md`](08-prd.md)

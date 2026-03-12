# Discovery & Specs

> Index of all discovery and specification artifacts for the Scheduling Agent.
> Update status and add file links as artifacts are created.
> For project context, see `CLAUDE.md`. For business rules, see `docs/business-rules.md`.

## Status Legend

| Symbol | Meaning |
|---|---|
| ⬜ | Not started |
| 🔄 | In progress |
| ✅ | Done |

---

## Artifact Index

### 1. Problem Framing ⬜

Formalizes the core problem, users, usage context, and success/failure criteria.

**Central questions to answer:**
- What is the real pain for founders vs. for the SEE team?
- Is the problem scheduling, or is it engagement?
- What is the current manual cost (time/person) of scheduling?
- What does success look like for each participant?

*File:* `docs/discovery/problem-framing.md` *(not yet created)*

---

### 2. User Study ⬜

Interviews and observations with real mentors and founders.

**Central questions to answer:**
- How do mentors and founders use WhatsApp in professional contexts?
- What are their scheduling preferences and existing habits?
- What do they expect from a conversational agent?
- What causes friction or trust loss in automated messages?

**Planned method:** 1:1 interviews + Concierge Test (Wizard of Oz) observation
**Target participants:** 3–5 mentors + 3–5 founders (Good Ready cluster)

*File:* `docs/discovery/user-study.md` *(not yet created)*

---

### 3. Assumption Map ⬜

Maps assumptions by certainty × impact. Basis for prioritizing test cards.

**Hypotheses already identified:**
- H1: Founders reply on WhatsApp in time (within a useful window)
- H2: Agent phrasing does not cause friction or confusion
- H3: Mentors accept suggested slots without manual editing
- H4: Full flow works without human intervention on the happy path
- H5: A conversational interface can substitute or amplify what SEE does today

*File:* `docs/discovery/assumption-map.md` *(not yet created)*

---

### 4. Business Rules v2 ⬜

Exhaustive rules document with all resolved edge cases, timeouts, fallbacks, SLAs.

> v1 is at `docs/business-rules.md`. This artifact formalizes v2 after Concierge Test learnings.

**Central questions to answer:**
- What are the timeout thresholds for each step?
- What is the retry policy?
- How are multi-partner and executive assistant scenarios handled?
- What are the SLAs for human intervention?

*File:* `docs/discovery/business-rules-v2.md` *(not yet created)*

---

### 5. Full PRD ⬜

Definitive product document with final flow, resolved edge cases, acceptance criteria, and success metrics.

**Target deadline:** 31/05/2026

**Central questions to answer:**
- What is the final happy path and all documented alternative paths?
- What are the measurable criteria for "the agent works"?
- What metrics define success for the first real cohort?

*File:* `docs/discovery/prd.md` *(not yet created)*

---

### 6. Data Model ⬜

Entity-relationship model for the scheduling agent.

**Entities expected:**
- `Conversation` — one scheduling session (mentor + founder + meeting)
- `Message` — each exchanged message
- `Slot` — proposed time slot
- `Booking` — confirmed booking (chosen slot)
- `MeetingEvent` — resulting Google Calendar event

**Integrations to model:** Connect (MongoDB) ↔ Agent DB ↔ Google Calendar

*File:* `docs/discovery/data-model.md` *(not yet created)*

---

### 7. Architecture Spec (final) ⬜

Final production architecture: state design, orchestration model, integrations, guardrails, scalability.

**Target deadline:** 31/05/2026

**Open decisions to resolve:**
- Single-agent vs. multi-agent for edge case handling
- HyperFlow: adopt or not?
- Knowledge graph: evaluate for mentoring context enrichment
- Token cost strategy (summarization, context management)
- LGPD compliance and data privacy model

*File:* `docs/discovery/architecture-spec.md` *(not yet created)*

---

### 8. Agent Specs ⬜

Per-agent specification: prompt engineering, expected inputs/outputs, fallback criteria, metrics.

**Agents to specify:**
- `SlotExtractorAgent` — v1 exists, needs formal spec
- `ConfirmationAgent` — v1 exists, needs formal spec
- `AmbiguityResolverAgent` — to be designed (edge case #5)
- `TimeoutHandlerAgent` — to be designed (edge case #3)
- `InterventionHandlerAgent` — to be designed (state: aguardando_intervencao_humana)

*File:* `docs/discovery/agent-specs.md` *(not yet created)*

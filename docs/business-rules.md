# Business Rules

> Version: v1 — provisional. Will be formalized in the full PRD (Phase 3, deadline: 31/05/2026).
> Update this file when rules are changed, clarified, or new rules are added.
> For context on why these rules exist, see the discovery artifacts: `docs/discovery/README.md`.

## Flow Trigger

- Triggered externally — by Connect system or manually by SEE team
- No self-service trigger yet (founder or mentor cannot initiate)

## Participants

| Role | Contact method | Notes |
|---|---|---|
| Mentor | WhatsApp (personal number registered in Connect) | Receives first message |
| Founder | WhatsApp | Receives slot options after mentor replies |
| Organizer | @endeavor email (whoever triggers the flow) | Creates the calendar event |

## First Message

- Must always use a WhatsApp **template** (Meta requirement for first contact)
- Template category: `utility`
- Template content: asks mentor for 2+ available time slots
- If mentor has already messaged in last 24h, free-form message is allowed (window service handles this)

## Slot Extraction

- Minimum 2 time slots must be extracted from mentor's reply
- Extraction is done by `SlotExtractorAgent` in natural language — no structured format required from mentor
- If less than 2 slots can be extracted → `aguardando_intervencao_humana`

## Founder Selection

- Formatted slot options are presented to founder
- Founder selects one via free-form reply
- `ConfirmationExtractorAgent` confirms which slot was chosen
- If confirmation is ambiguous → `aguardando_intervencao_humana`

## Google Calendar Event

| Field | Value |
|---|---|
| Organizer | @endeavor email |
| Guests | Mentor (personal or corporate email) + Founder |
| Title | `<Empresa> × <Nome do Mentor>` |
| Method | Service Account (not Behalf — mentors are external) |

> The `behalf` method was considered but discarded because mentors don't have @endeavor accounts. See `CLAUDE.md` → Decided Technical Decisions.

## Edge Cases → Human Intervention

Any response that cannot be processed by agents routes to `aguardando_intervencao_humana`. Currently there is no notification or UI for this state — human intervention is manual. This will change in future iterations.

---

## Open Rules (not yet defined)

These need to be decided before Phase 3 implementation:

- Timeout: how long to wait for mentor/founder reply before escalating?
- Retry: should the agent re-send a reminder if no response?
- Founder with multiple partners: who receives the message? All partners? Primary contact?
- Mentor with executive assistant: does the assistant receive and reply on behalf?
- What happens if the chosen slot becomes unavailable before the invite is sent?

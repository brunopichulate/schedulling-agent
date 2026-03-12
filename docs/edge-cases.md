# Edge Cases

> Living document — update as cases are discovered, analyzed, and resolved.
> Status legend: 🔴 No solution · 🟡 Solution defined, not implemented · 🟢 Implemented

## Current Edge Cases

| # | Case | Status | Notes |
|---|---|---|---|
| 1 | Mentor has an executive assistant | 🔴 No solution | Who receives the WhatsApp message? Does the assistant reply on behalf? |
| 2 | Founder has multiple partners | 🔴 No solution | Who is the recipient? All of them? Primary contact in Connect? |
| 3 | Mentor does not respond (timeout) | 🔴 No solution | No timeout defined yet — conversation hangs indefinitely |
| 4 | Founder rejects all suggested slots | 🔴 No solution | Re-ask mentor? Escalate? Fallback message? |
| 5 | Ambiguous response ("any day of the week", "morning works") | 🔴 No solution | SlotExtractor can't extract → today goes to human intervention |
| 6 | Mentor responds out of flow (audio, image, sticker, document) | 🟡 Solution defined, not implemented | Non-text messages receive a fallback reply ("suporto apenas mensagens de texto") but workflow state is not updated — conversation hangs at current state |
| 7 | Mentor's WhatsApp number is outdated in Connect | 🔴 No solution | Message delivered to wrong person, no bounce mechanism |

## Handling Today

All edge cases currently route to `aguardando_intervencao_humana` state. There is no:
- Notification to the SEE team
- UI to manage these conversations
- Retry or escalation logic

This is the next major area of investment after the MVP is validated.

## Architectural Implication

Each resolved edge case will likely require:
1. A new state machine state (or sub-state)
2. A new agent or agent branch (e.g., ambiguity resolver, timeout handler)
3. Possibly a notification/intervention UI

Design the state machine and agent routing to accommodate this growth. See `CLAUDE.md` → Future Architecture Direction.

---

## Resolved Edge Cases

*(none yet — move cases here when resolved with implementation notes)*

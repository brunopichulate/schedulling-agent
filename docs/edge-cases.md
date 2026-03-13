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
| 8 | AEE esquece de atualizar status no Connect após agendar | 🔴 No solution | Pipeline reports ficam desatualizados; próximo passo (Briefing) pode não disparar automaticamente |
| 9 | Janela de 24h do WhatsApp expira no meio do fluxo | 🔴 No solution | Se mentor demora >24h para responder, a janela fecha antes do contato ao founder — seria necessário template para recomeçar a conversa com o founder |
| 10 | Mentor ou founder se recusa a interagir com o agente (chatbot aversion) | 🔴 No solution | Ator ignora a mensagem, responde "não quero falar com robô", ou simplesmente não engaja por ceticismo, desconfiança ou preferência por contato humano. Risco de adoção que invalida a premissa central do agente se for frequente. |
| 11 | Founder não reconhece o número do agente e ignora por suspeita de phishing | 🔴 No solution | Founder recebe mensagem de número desconhecido (Salvy) sem aviso prévio — pode bloquear ou ignorar por suspeita de fraude |
| 12 | Trigger duplicado — mesma mentoria triggerada duas vezes | 🔴 No solution | Connect ou AEE triggerou o agente duas vezes para o mesmo meeting_id; dois fluxos paralelos podem corromper o estado |
| 13 | TTL do Redis expira no meio de uma conversa ativa (24h) | 🔴 No solution | Estado do Redis tem TTL de 24h (`STATE_TTL_SECONDS`). Se a conversa total durar >24h, o estado é silenciosamente resetado para INIT — próxima mensagem inicia fluxo do zero sem aviso ao ator ou AEE |

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

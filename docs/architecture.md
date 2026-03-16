# Architecture

> Deep-dive reference. Update when stack or data flow changes significantly.
> For high-level overview, see `CLAUDE.md`.

## Full Data Flow — Happy Path

```
1. External Trigger
   └── Connect system or manual call → passes meeting_id, mentor phone, founder phone

2. 24h Window Check
   └── whatsapp_window_service checks if mentor messaged in last 24h
       ├── Window open → skip to step 4 (send slot request directly)
       └── Window closed → send hello_world template to open window
                          → state: WAITING_FOR_TEMPLATE_REPLY

3. Mentor Replies to Template (inbound webhook)
   └── POST /v1/channels/whatsapp/webhook
       └── FastAPI → Celery task: process_whatsapp_message
           └── State: WAITING_FOR_TEMPLATE_REPLY → reset to INIT
               └── Workflow sends actual slot-request message to mentor
                   → state: WAITING_DONATED_RESPONSE

4. Mentor Replies with Slots (inbound webhook)
   └── Same pipeline → state: WAITING_DONATED_RESPONSE
       └── SlotExtractorAgent (Agno + GPT-4o-mini)
           └── Extracts 2+ time slots (selected_date_times: list[str])
               └── Formats options → sends to founder
                   → state: WAITING_RECEIVED_RESPONSE

5. Founder Reply (inbound webhook)
   └── Same pipeline → state: WAITING_RECEIVED_RESPONSE
       └── ConfirmationExtractorAgent
           └── Extracts chosen slot (selected_option_index: int) + confirmation

6. Google Calendar API
   └── Service Account creates event
       ├── Organizer: @endeavor email (whoever triggered the flow)
       ├── Guests: mentor (personal/corp email) + founder
       └── Title: <Empresa> × <Nome do Mentor>

7. Confirmation messages sent to both parties
   └── state: RECEIVED_CONFIRMED
   └── Langfuse records full trace (tokens, latency, prompt version)
```

## State Machine States

```
INIT
  └─► WAITING_FOR_TEMPLATE_REPLY    (hello_world template sent, awaiting any reply)
        └─► INIT                     (on reply: reset, send actual slot-request message)
              └─► WAITING_DONATED_RESPONSE   (slot-request sent to mentor)
                    ├─► DONATED_NO_RESPONSE       ──► HUMAN_INTERVITION_REQUIRED
                    ├─► DONATED_REJECTED_SLOTS    ──► HUMAN_INTERVITION_REQUIRED
                    └─► DONATED_SELECTED_SLOT
                          └─► WAITING_RECEIVED_RESPONSE  (slot options sent to founder)
                                ├─► RECEIVED_NO_RESPONSE  ──► HUMAN_INTERVITION_REQUIRED
                                ├─► RECEIVED_REJECTED     ──► HUMAN_INTERVITION_REQUIRED
                                └─► RECEIVED_CONFIRMED    (calendar invite created, flow done)
```

Note: `HUMAN_INTERVITION_REQUIRED` is the actual state name in code (typo preserved for compatibility).

State is persisted per phone number in MongoDB via `src/services/state_machine_service.py`.

## Component Interactions

```
┌─────────────────────────────────────────────────────────┐
│                        FastAPI                           │
│  POST /v1/channels/whatsapp/webhook                      │
│  GET  /health                                            │
└────────────────────────┬────────────────────────────────┘
                         │ enqueues
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    Celery Worker                         │
│  src/tasks/whatsapp/task.py                              │
└────────────────────────┬────────────────────────────────┘
                         │ calls
                         ▼
┌─────────────────────────────────────────────────────────┐
│               WhatsApp Workflow                          │
│  src/workflows/whatsapp_workflow.py                      │
│  Generator: yields (recipient, message) tuples           │
│  Enforces 24-hour conversation window                    │
└──────┬──────────────────────────┬───────────────────────┘
       │ reads/writes              │ calls
       ▼                           ▼
┌─────────────┐           ┌───────────────────────────────┐
│  State      │           │         Agno Agents            │
│  Machine    │           │  src/agents/main/              │
│  (MongoDB)  │           │  SlotExtractorAgent            │
└─────────────┘           │  ConfirmationExtractorAgent    │
                          │  LLM: OpenAI GPT-4o-mini       │
                          │  Prompts: fetched from Langfuse│
                          └───────────────────────────────┘
                                         │
                          ┌──────────────┴──────────────┐
                          ▼                             ▼
               ┌──────────────────┐        ┌──────────────────────┐
               │ WhatsApp API     │        │ Google Calendar API  │
               │ (Meta Cloud)     │        │ (Service Account)    │
               └──────────────────┘        └──────────────────────┘
```

## 24-Hour WhatsApp Window

Meta's WhatsApp Cloud API only allows free-form messages within a 24-hour window after the user's last message. Outside this window, only pre-approved templates can be sent.

`src/services/whatsapp_window_service.py` tracks the last inbound message timestamp per phone number in Redis. The workflow checks this before choosing between template vs. free-form message.

## Observability Stack

```
Agno Agents
  └─► Langfuse SDK (langfuse.py)
        ├── Traces: full request/response per conversation turn
        ├── Spans: per-agent call with latency and token usage
        ├── Prompts: versioned prompt management (fetched at runtime)
        └── Sessions: grouped by phone number

OpenTelemetry (otel.py)
  └─► Wired into Langfuse as OTLP exporter

Celery
  └─► Flower UI (port 5555) — task queue monitoring
```

Langfuse project: `endeavor-agents` (account: `web@endeavor`)

## Infrastructure (Local)

```yaml
# docker-compose.yml spins up:
- Redis        # Celery broker + WhatsApp window state
- PostgreSQL   # (reserved — Langfuse local instance)
- Langfuse     # Local observability UI
```

## Scaling Considerations (for future implementation)

- Current architecture is single-worker Celery — horizontally scalable by adding workers
- MongoDB conversation state is keyed by phone number — naturally partitionable
- Agents are stateless per call — safe to parallelize
- WhatsApp Cloud API has rate limits (1,000 messages/sec per phone number) — Redis-based rate limiting in place

---

## Motor de Negociação (Vai-e-Vem)

O agente não é linear. Ele funciona como uma secretária: coleta disponibilidade de um lado, leva ao outro, e repete até encontrar um slot em comum ou decidir que precisa de ajuda humana.

### Fluxo de ciclos

```
Ciclo 1 (obrigatório):
  Mentor fornece slots
  → Founder recebe opções
  → Founder escolhe ✅ → confirma (happy path)
  → Founder rejeita + oferece contra-disponibilidade → Ciclo 2

Ciclo 2..N (renegociação):
  Mentor recebe contra-disponibilidade do founder → fornece novos slots
  → Founder escolhe ✅ → confirma
  → Founder rejeita novamente → HI se N >= MAX_NEGOTIATION_ROUNDS

Cancelamento/remarcação (qualquer ciclo, qualquer lado):
  → Notifica o outro lado + AEE imediatamente
  → Inicia novo ciclo de negociação OU encerra o fluxo
  → Se pós-confirmação: GCal deve ser cancelado/atualizado
```

### Dados a preservar entre rounds

```python
# Extensão do MeetingContext (src/workflows/meeting_shared/models.py)
current_round: int = 0
max_rounds: int  # de config — recomendado: 2

@dataclass
class NegotiationRound:
    round_number: int
    initiator: Literal["mentor", "founder"]
    slots_offered: list[str]       # slots oferecidos por quem iniciou o round
    counter_availability: str      # contra-disponibilidade do outro lado (se houver)
    outcome: Literal["accepted", "rejected_with_counter", "rejected_no_alternative", "cancelled"]
```

### Regras de escalonamento

| Condição | Ação |
|---|---|
| `current_round >= max_rounds` sem convergência | HI com histórico completo de disponibilidades |
| Resposta emocional ou agressiva | HI imediato |
| "Já combinamos diretamente" | HI imediato |
| Cancelamento pós-confirmação | HI + notifica ambos + cancela GCal |
| 2x clarificação sem sucesso no mesmo round | HI |

### Impacto na state machine

O round é rastreado como campo de contexto (não estado separado) para evitar explosão de estados. Os estados existentes são reusados com o contexto de round como discriminador. Um novo estado terminal `RESCHEDULING_REQUESTED` pode ser adicionado para diferenciar HI por conflito de agenda vs HI por cancelamento.

---

## Delegação de Contato no Trigger

Mentores ou founders podem ter assistentes executivas que gerenciam agendas. O Connect pode ter esse número cadastrado. A decisão de contatar diretamente ou via assistente é feita pelo AEE **antes** de disparar o fluxo — nunca mid-flow.

### Extensão do trigger

```
POST /v1/schedule
{
  meeting_id:                    str,
  donated_phone_number:          str,   # número direto do mentor
  donated_contact_type:          "direct" | "via_assistant",  # novo
  donated_assistant_phone:       str | None,                  # novo — obrigatório se via_assistant
  received_phone_number:         str,   # número direto do founder
  received_contact_type:         "direct" | "via_assistant",  # novo
  received_assistant_phone:      str | None                   # novo
}
```

### Comportamento

- Workflow usa `assistant_phone` quando `contact_type = via_assistant`
- Nenhuma lógica mid-flow: se assistente responde, o agente trata normalmente (EC-01)
- AEE é responsável por validar o número no Connect antes de disparar
- Founder que delega mid-flow (EC-25) não é tratado pelo agente — HI imediato

---

## EscalationService — Canal de Notificação AEE

### Situação atual

Hoje `HUMAN_INTERVITION_REQUIRED` é um estado silencioso. Nenhuma notificação chega ao AEE. Casos acumulam e só são descobertos por reclamação dos envolvidos (EC-36).

### Design proposto

`EscalationService` é um serviço simples de notificação — **não um agente LLM**. A decisão de canal é regra de configuração, não linguagem natural. LLM adicionaria latência, custo e ponto de falha sem valor.

```python
# src/core/config.py — novos campos
ESCALATION_CHANNEL: Literal["whatsapp", "slack"] = "whatsapp"
ESCALATION_WHATSAPP_PHONE: str | None = None  # número WhatsApp do AEE
ESCALATION_SLACK_WEBHOOK: str | None = None   # webhook URL do canal Slack
```

### Payload de escalada (independente do canal)

```
Tipo de escalada : mentor_timeout | founder_rejected | agent_refused |
                   no_convergence | cancelled_pre_confirm | cancelled_post_confirm | ...
Mentor           : [nome] ([empresa])
Founder          : [nome] ([empresa])
Round atual      : N de MAX
Último estado    : WAITING_DONATED_RESPONSE
Disponibilidades : [resumo dos rounds — slots oferecidos e contra-propostas]
Meeting ID       : [id — para AEE abrir no Connect]
```

### Canal WhatsApp

Mensagem free-form para `ESCALATION_WHATSAPP_PHONE`. Funciona porque AEE é usuário ativo no número do agente (janela 24h geralmente aberta).

### Canal Slack

POST para `ESCALATION_SLACK_WEBHOOK` com payload formatado em markdown.

### Chamada

`EscalationService.notify(context, reason)` invocado em qualquer handler que transiciona para `HUMAN_INTERVITION_REQUIRED`. O `context` já contém toda a informação necessária (nome dos atores, meeting_id, rounds).

### Evolução futura (Phase 3)

- Multi-canal simultâneo (WhatsApp + Slack)
- SLA timer: se AEE não responde em X horas, re-escalada para segundo contato
- Fila de intervenções com UI no Connect
- Priorização por tipo de escalada

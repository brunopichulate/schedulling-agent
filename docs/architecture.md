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

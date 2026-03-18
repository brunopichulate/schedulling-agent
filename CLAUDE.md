# CLAUDE.md

> Documento vivo. Última revisão: 2026-03-12.
> Seções estáveis vivem aqui. Seções voláteis vivem em `docs/` — links abaixo.

## Project Overview

Endeavor AI is an AI-powered scheduling agent that automates mentoring session scheduling via WhatsApp, eliminating manual back-and-forth between mentors and founders to find a common time slot.

Part of Endeavor Brasil's **Low/Tech-Touch Business Models** initiative (2026.1 cycle): validate whether Endeavor can support founders at scale without increasing AEE team headcount. The agent covers the scheduling step in the mentoring happy path:

```
Checkpoint → Priorities → RecSys → My List → Book Meeting → [Scheduling Agent] → Calendar Invite
```

## Git

- Remote `origin` deve apontar para `https://github.com/brunopichulate/schedulling-agent`
- **Nunca** fazer push para `Endeavor-Brasil/ai`

## Commands

```bash
# Install dependencies
uv sync

# Run API server (port 8000)
uv run ./main.py

# Run Celery worker
uv run celery -A src.core.celery worker

# Run Flower (Celery monitoring UI, port 5555)
uv run celery -A src.core.celery flower

# Test via Gradio UI (no WhatsApp needed)
uv run ./chat.py

# Simulate conversation flows for all edge cases (no external dependencies)
python simular_fluxo.py              # list all scenarios
python simular_fluxo.py <number>     # run specific scenario (e.g. 24)
python simular_fluxo.py all          # run all scenarios

# Lint and format
uv run ruff check .
uv run ruff check . --fix
uv run ruff format .

# Run tests
pytest
pytest tests/path/to/test.py::test_function_name

# Start local infrastructure (Redis, PostgreSQL, Langfuse)
docker-compose up -d
```

## Architecture

See full deep-dive: [`docs/architecture.md`](docs/architecture.md)

### Pipeline

```
WhatsApp Webhook → FastAPI → Celery Task → State Machine → Workflow → Agno Agents (OpenAI) → WhatsApp API
                                                                                             → Google Calendar API
```

### Tech Stack

| Layer | Tool | Purpose |
|---|---|---|
| **Language** | Python 3.12+ | Runtime |
| **Package manager** | uv | Replaces pip/poetry — use `uv add`, never `pip install` |
| **Web framework** | FastAPI | Async API server, webhook receiver |
| **Task queue** | Celery | Async processing of WhatsApp messages |
| **Broker / cache** | Redis | Celery broker + rate limiting |
| **State persistence** | MongoDB | Per-user conversation state (state machine) |
| **Agent framework** | Agno | Agent orchestration (~$29/mo) |
| **LLM** | OpenAI GPT-4o-mini | Powers all agents |
| **Prompt management** | Langfuse | Versioned prompts, traces, token tracking |
| **Tracing** | OpenTelemetry | Distributed tracing, wired into Langfuse |
| **Messaging channel** | Meta WhatsApp Cloud API | Inbound webhook + outbound messages |
| **WhatsApp number** | Salvy (virtual, São Paulo) | ~R$29.90/mo |
| **Calendar** | Google Calendar API + Service Account | Creates meeting invites |
| **Containerization** | Docker + docker-compose | Local infra + deployment packaging |
| **Hosting** | AWS | Managed by Yara (DevOps Endeavor) |
| **Config** | Pydantic Settings | Typed env vars via `src/core/config.py` |
| **Linting** | ruff | Linting + formatting |
| **Testing** | pytest | Test runner |
| **Local test UI** | Gradio | Test conversations without WhatsApp |

**Under evaluation for Phase 3 (not adopted yet):**
- HyperFlow — agent orchestration alternative (evaluate after MVP learnings)
- Knowledge graph — mentoring context enrichment
- Amplitude — Connect event tracking (already in Connect, not integrated with agent)
- Gemini / Anthropic — LLM alternatives (evaluated, not adopted)

### Project Scaffolding

```
ai/
├── main.py                        # FastAPI app entrypoint
├── chat.py                        # Gradio local test UI
├── docker-compose.yml             # Local infra: Redis, PostgreSQL, Langfuse
├── Dockerfile
├── pyproject.toml                 # Project metadata + dependencies (uv)
├── uv.lock                        # Lockfile — commit this
├── pytest.ini
│
├── src/
│   ├── api/
│   │   ├── common/health.py       # GET /health
│   │   └── v1/
│   │       ├── whatsapp.py        # POST /v1/channels/whatsapp/webhook
│   │       └── schedule.py        # Schedule-related endpoints
│   │
│   ├── agents/
│   │   └── main/
│   │       ├── meeting_agents.py                     # SlotExtractorAgent + ConfirmationExtractorAgent (Agno + GPT-4o-mini)
│   │       ├── counter_availability_extractor_agent.py  # CounterAvailabilityExtractorAgent — detects founder counter-proposals
│   │       └── tools/
│   │           └── meeting_tools.py  # Agno tools available to agents
│   │
│   ├── workflows/
│   │   ├── whatsapp_workflow.py   # Main orchestrator — generator, yields (recipient, message)
│   │   ├── gradio_workflow.py     # Gradio-adapted workflow for local testing
│   │   └── meeting_shared/
│   │       ├── handlers.py        # Per-state message handlers
│   │       ├── messages.py        # WhatsApp message templates (strings)
│   │       ├── models.py          # Pydantic models for workflow data
│   │       └── utils.py
│   │
│   ├── services/
│   │   ├── state_machine_service.py    # Conversation state CRUD (MongoDB)
│   │   ├── whatsapp_window_service.py  # 24-hour messaging window tracking
│   │   ├── whatsapp.py                 # WhatsApp API client wrapper
│   │   └── meetings_service.py         # Meeting data from Connect DB
│   │
│   ├── tasks/
│   │   └── whatsapp/
│   │       ├── task.py            # Celery task: process_whatsapp_message
│   │       └── schemas.py         # Task input/output schemas
│   │
│   └── core/
│       ├── config.py              # Pydantic Settings — all env vars
│       ├── celery.py              # Celery app instance
│       ├── database.py            # MongoDB + Redis clients
│       ├── langfuse.py            # Langfuse client init
│       ├── logger.py              # Structured logging setup
│       └── otel.py                # OpenTelemetry setup
│
├── tests/                         # pytest — currently minimal
│
└── docs/                          # Living documentation (see below)
    ├── architecture.md            # Deep-dive: data flow, component interactions, state machine states
    ├── business-rules.md          # Business rules — updated each cycle
    ├── edge-cases.md              # Known edge cases and resolution status
    └── discovery/
        └── README.md              # Discovery & Specs index with status
```

> **Note on scaffolding:** this will evolve. As new agents, integrations, and edge case handlers are added, new directories will appear under `src/agents/`, `src/services/`, and `src/workflows/`. The `docs/` structure should grow alongside. Update this section when significant structural changes are made.

## Decided Technical Decisions

These decisions are closed — do not reopen or suggest alternatives unless explicitly asked.

| Decision | Choice | Reason |
|---|---|---|
| Prompt language | Portuguese | Better extraction quality for inputs without accents |
| Calendar organizer | @endeavor account | Mentors don't have @endeavor; behalf method discarded |
| Calendar guests | Mentor (personal email) + Founder | Both receive invite, @endeavor is organizer |
| Agent orchestration (MVP) | Agno | HyperFlow discarded for MVP — reevaluate Phase 3 |
| Queue broker | Redis | Celery broker + rate limiting in single tool |
| Conversation state | MongoDB | Persistent, per-user, queryable |
| LLM | OpenAI GPT-4o-mini | Gemini and Anthropic evaluated, not adopted |

## Future Architecture Direction

The current system handles only the happy path with 2 agents and a linear flow. **Do not implement things that create dead ends for this evolution:**

- **Current:** 2 agents, linear orchestration, single happy path
- **Next:** edge cases will require dedicated agents (ambiguity resolver, timeout handler, intervention handler) and multi-agent routing
- **State machine:** design for extensibility — new states should not require full rewrites. Edge cases land in `aguardando_intervencao_humana` today but will each get dedicated states
- **HyperFlow:** under evaluation for Phase 3 — avoid tight coupling to Agno internals that blocks migration
- **Open decisions:** single-agent vs multi-agent for edge cases, token cost strategy, LGPD/compliance model

## Team

| Person | Role | Responsibility |
|---|---|---|
| Bruno Pichulate | PM | Product, business rules, tests, feedback loop |
| Bruno Batista (Brunão) | Tech Lead ZRP | Architecture, integrations, code review |
| Paulo Lacerda | Dev ZRP | Agent dev, WhatsApp flow, Google Calendar |
| Pedro Gryzinsky (Pedrão) | Strategic Eng ZRP | Architecture decisions, roadmap |
| Yara | DevOps Endeavor | AWS provisioning (QA and Prod) |
| Arua | Manager Endeavor | Strategic alignment, company kickoffs |

## Glossary

| Term | Meaning |
|---|---|
| Slot | Available time proposed by the mentor |
| Happy Path | Ideal flow with no errors or unexpected responses |
| Behalf | Google Calendar API method to create events on behalf of another user in the same org — discarded for MVP |
| State Machine | Controls which step of the flow each conversation is in |
| Langfuse | LLM observability platform (traces, versioned prompts, tokens) |
| Agno | Agent orchestration framework |
| Gradio | Minimal web UI for testing the agent without WhatsApp |
| Template | Meta-approved message required to initiate a WhatsApp Business API conversation |
| Good Ready | Cluster of Endeavor companies ready for the paid tech-touch model |
| SEE | Seleção de Empreendedores Endeavor — team responsible for selecting new entrepreneurs into the Endeavor network |
| AEE | Apoio a Empreendedores Endeavor — team that supports and manages mentoring relationships for active portfolio companies; runs the scheduling flow |
| ZRP | Partner development company (Brunão, Paulo, Pedro G.) |
| Concierge Test | Wizard of Oz: manually simulate the agent without the user knowing |
| aguardando_intervencao_humana | State machine state for unresolved/ambiguous conversations |

## Environment Variables

Copy `.env.example` to `.env`. Required variables:

- `OPENAI__API_KEY` — OpenAI API key (GPT-4o-mini)
- `LANGFUSE__PUBLIC_KEY`, `LANGFUSE__SECRET_KEY`, `LANGFUSE__HOST` — LLM observability
- `META__VERIFY_TOKEN`, `META__APP_ID`, `META__APP_SECRET`, `META__ACCESS_TOKEN`, `META__PHONE_NUMBER_ID` — WhatsApp Cloud API
- `REDIS__URL` — Celery broker + rate limiting
- `MONGODB__URL` — Conversation state persistence

## Dependency Management

Uses `uv` — not pip or poetry. Always `uv add <package>` to add, `uv sync` to install. Commit `uv.lock`.

# Scheduling Agent MVP — Implementation Specs

> Versão: 1.0 | Data: 2026-03-16
> **Audiência:** Brunão, Paulo, Pedro G.
> **Pré-requisito:** PRD em `docs/discovery/08-prd.md`. Este documento não repete contexto de negócio — só o que implementar e como.

---

## 0. Leitura Rápida

| Feature | Prioridade | Arquivos tocados | Status atual |
|---|---|---|---|
| **Base 1** — Typo fix `INTERVITION` | P0 bloqueador | models, state_machine, handlers, messages | Bug ativo |
| **Base 2** — Expandir MeetingContext + Redis schema | P0 bloqueador | models.py, state_machine_service.py | Ausente |
| **Base 3** — Config vars novas | P0 bloqueador | config.py | Ausente |
| **Base 4** — Handler WAITING_FOR_TEMPLATE_REPLY | P0 bug | handlers.py | Gap ativo |
| **F8** — Validação email no trigger | P0 | schedule.py, meetings_service.py | Ausente |
| **F6** — Fix EC-06 mídia + mensagem contextual | P0 | task.py | Bug ativo |
| **F1** — GCalService + integração | P0 | gcal_service.py (novo), handlers.py | Ausente |
| **F2** — EscalationService | P0 | escalation_service.py (novo), handlers.py | Ausente |
| **F4** — RefusalDetectorAgent | P0 | refusal_detector_agent.py (novo), handlers.py | Ausente |
| **F5** — Ambiguity Counter | P1 | state_machine_service.py, handlers.py | Ausente |
| **F7** — Deduplicação trigger | P1 | schedule.py, state_machine_service.py | Parcial |
| **F3** — Celery Beat + timeout proativo | P1 | celery.py, timeout_task.py (novo) | Ausente |
| **F9** — Motor de Negociação | P1 | models.py, handlers.py, novo agente | Ausente |
| **F10** — Slack Takeover | P1 | slack.py (novo), escalation_service.py, task.py | Ausente |

**Como usar:** implementar em ordem de cima para baixo. Cada seção é autocontida: descreve o contexto atual, as mudanças exatas, e como testar.

---

## 1. Decisões Pre-implementação

Estas decisões do PRD (D1–D7) foram tomadas ou não bloqueiam o código:

| Decisão | Resolução adotada neste specs |
|---|---|
| D1 — Redis vs MongoDB | **Redis mantém estado de conversa** (já é assim). MongoDB continua como source of truth de dados de meetings (somente leitura). Snapshot antes de reset: salvar no próprio Redis com key separada `meeting_snapshot:{user_id}` com TTL de 7 dias para análise pós-piloto. |
| D2 — Typo INTERVITION | **Corrigir antes de qualquer nova implementação** (Base 1). Redis keys com typo expiram naturalmente pelo TTL de 24h — não requer migração ativa. |
| D3 — WAITING_FOR_TEMPLATE_REPLY | **Implementar handler** (Base 4): transicionar para INIT e re-executar `handle_init`. |
| D4 — Timeout founder | **48h igual ao mentor** (mesmo `NO_RESPONSE_TIMEOUT_SECONDS`). |
| D5 — Aviso prévio founder (EC-11) | **Processo manual no MVP**: AEE avisa o founder antes do agente contatar. Sem código. |
| D6, D7 — Métricas e shadow mode | Open; não bloqueiam código. |

---

## 2. Base 1 — Corrigir Typo `HUMAN_INTERVITION_REQUIRED`

**Por que fazer primeiro:** o typo está em 4 arquivos e em `VALID_STATES`. Qualquer nova feature que usa este estado vai propagar o erro se não corrigir agora.

**Migration note:** Redis keys existentes no formato `"HUMAN_INTERVITION_REQUIRED"` expiram em ≤24h pelo TTL. Não requer script de migração — basta fazer o deploy.

### Arquivo: `src/workflows/meeting_shared/models.py`

```python
# ANTES (linha 13):
HUMAN_INTERVITION_REQUIRED = "HUMAN_INTERVITION_REQUIRED"

# DEPOIS:
HUMAN_INTERVENTION_REQUIRED = "HUMAN_INTERVENTION_REQUIRED"
```

### Arquivo: `src/services/state_machine_service.py`

```python
# VALID_STATES (linha 44) — substituir entrada:
"HUMAN_INTERVENTION_REQUIRED",  # era "HUMAN_INTERVITION_REQUIRED"

# terminal_states dentro de update_meeting_state (linha 196–199):
terminal_states = [
    "RECEIVED_CONFIRMED",
    "RECEIVED_REJECTED",
    "HUMAN_INTERVENTION_REQUIRED",  # era "HUMAN_INTERVITION_REQUIRED"
]

# _TERMINAL_OR_IDLE_STATES (não está neste arquivo — está em schedule.py; ver Base 4)
```

### Arquivo: `src/workflows/meeting_shared/handlers.py`

```python
# Linha 63 — handle_waiting_donated:
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)

# Linha 85 — handle_waiting_donated (rejected):
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)

# Linha 115 — handle_waiting_received (timeout):
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)

# Linha 141 — handle_waiting_received (rejected):
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)

# STATE_HANDLERS dict (linha 178):
MeetingState.HUMAN_INTERVENTION_REQUIRED.value: handle_human_intervention_required,
```

### Arquivo: `src/api/v1/schedule.py`

```python
# _TERMINAL_OR_IDLE_STATES (linha 21–25):
_TERMINAL_OR_IDLE_STATES = {
    "INIT",
    "RECEIVED_CONFIRMED",
    "HUMAN_INTERVENTION_REQUIRED",  # era "HUMAN_INTERVITION_REQUIRED"
}
```

**Verificação:** `grep -r "INTERVITION" src/` deve retornar 0 resultados.

---

## 3. Base 2 — Expandir `MeetingContext` e Redis Schema

### Arquivo: `src/workflows/meeting_shared/models.py`

Adicionar `field` ao import e os novos campos ao dataclass:

```python
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional

class MeetingState(str, Enum):
    INIT = "INIT"
    WAITING_FOR_TEMPLATE_REPLY = "WAITING_FOR_TEMPLATE_REPLY"
    WAITING_DONATED_RESPONSE = "WAITING_DONATED_RESPONSE"
    WAITING_RECEIVED_RESPONSE = "WAITING_RECEIVED_RESPONSE"
    DONATED_NO_RESPONSE = "DONATED_NO_RESPONSE"
    RECEIVED_NO_RESPONSE = "RECEIVED_NO_RESPONSE"
    DONATED_REJECTED_SLOTS = "DONATED_REJECTED_SLOTS"
    RECEIVED_REJECTED = "RECEIVED_REJECTED"
    HUMAN_INTERVENTION_REQUIRED = "HUMAN_INTERVENTION_REQUIRED"
    RECEIVED_CONFIRMED = "RECEIVED_CONFIRMED"
    DONATED_SELECTED_SLOT = "DONATED_SELECTED_SLOT"


@dataclass
class NegotiationRound:
    round_number: int
    mentor_slots_offered: list[str]       # ISO datetimes oferecidos pelo mentor
    founder_counter_windows: list[str]    # janelas propostas pelo founder ("segunda 14h-16h")
    result: str                           # "accepted" | "rejected" | "escalated"
    timestamp: str                        # ISO datetime


@dataclass
class MeetingContext:
    user_id: str
    donated_phone: str
    received_phone: str
    donated_name: str
    received_name: str
    meeting_date_iso: str
    state: MeetingState
    state_dict: dict
    # Novos campos:
    donated_email: Optional[str] = None          # para GCal invite
    received_email: Optional[str] = None         # para GCal invite
    clarification_count: int = 0                 # F5: reset a cada round
    current_round: int = 1                       # F9: motor de negociação
    max_rounds: int = 2                          # F9: de settings.max_negotiation_rounds
    negotiation_history: list = field(default_factory=list)  # list[NegotiationRound]
    slack_thread_ts: Optional[str] = None        # F10: thread do Slack takeover
    company_name: Optional[str] = None           # para título do GCal invite
```

### Arquivo: `src/services/state_machine_service.py`

Expandir `_EMPTY_STATE` com os novos campos:

```python
_EMPTY_STATE: Dict[str, Any] = {
    "status": "INIT",
    "meeting": None,
    "donated": None,
    "received": None,
    "donated_phone": None,
    "received_phone": None,
    "donated_email": None,        # novo
    "received_email": None,       # novo
    "selected_slot": None,
    "last_interaction_time": None,
    "clarification_count": 0,     # novo — F5
    "follow_up_sent": False,      # novo — F3
    "follow_up_sent_at": None,    # novo — F3
    "current_round": 1,           # novo — F9
    "max_rounds": 2,              # novo — F9
    "negotiation_history": [],    # novo — F9 (list de dicts serializados)
    "slack_thread_ts": None,      # novo — F10
    "meeting_id": None,           # novo — F7 (deduplicação)
}
```

Também adicionar as funções de suporte novos (detalhes em cada seção abaixo).

---

## 4. Base 3 — Novas Variáveis de Config

### Arquivo: `src/core/config.py`

Adicionar novos `BaseModel` e campos em `Settings`:

```python
class EscalationSettings(BaseModel):
    CHANNEL: str = "whatsapp"              # "whatsapp" | "slack"
    WHATSAPP_PHONE: Optional[str] = None   # número AEE para notificação

class GCalSettings(BaseModel):
    SERVICE_ACCOUNT_JSON: Optional[str] = None  # JSON string do service account (Base64 ou raw)
    ORGANIZER_EMAIL: Optional[str] = None        # ex: agendamentos@endeavor.org.br

class SlackSettings(BaseModel):
    BOT_TOKEN: Optional[str] = None
    TAKEOVER_CHANNEL: Optional[str] = None       # ex: "#agendamentos-intervencao"
    SIGNING_SECRET: Optional[str] = None

class Settings(BaseSettings):
    # ... campos existentes mantidos ...
    langfuse: LangfuseSettings
    openai: OpenAISettings
    prompt: PromptSettings | None = None
    log: LoggerSettings
    otel: OtelSettings
    redis: RedisSettings
    meta: MetaSettings
    mongodb: MongoDBSettings

    # Novos:
    escalation: EscalationSettings = EscalationSettings()
    gcal: GCalSettings = GCalSettings()
    slack: SlackSettings = SlackSettings()

    # Comportamento do agente (existentes):
    no_response_timeout_seconds: int = 172800   # 48h
    # Novos:
    timeout_check_interval_minutes: int = 15
    max_negotiation_rounds: int = 2
```

**Variáveis de ambiente correspondentes** (adicionar ao `.env.example`):
```bash
ESCALATION__CHANNEL=whatsapp
ESCALATION__WHATSAPP_PHONE=+5511999999999

GCAL__SERVICE_ACCOUNT_JSON='{...}'    # JSON do service account, entre aspas simples
GCAL__ORGANIZER_EMAIL=agendamentos@endeavor.org.br

SLACK__BOT_TOKEN=xoxb-...
SLACK__TAKEOVER_CHANNEL=#agendamentos-intervencao
SLACK__SIGNING_SECRET=...

TIMEOUT_CHECK_INTERVAL_MINUTES=15
MAX_NEGOTIATION_ROUNDS=2
```

---

## 5. Base 4 — Handler `WAITING_FOR_TEMPLATE_REPLY`

**Bug atual:** o estado `WAITING_FOR_TEMPLATE_REPLY` existe em `VALID_STATES` mas não tem entrada no `STATE_HANDLERS`. Se o fluxo chegar a este estado por qualquer caminho diferente do `task.py`, cai em `handle_unexpected_state`.

O `task.py` (linhas 61–65) já trata a transição corretamente quando uma mensagem chega. O que falta é o handler para o caso em que o workflow é chamado enquanto o estado está em `WAITING_FOR_TEMPLATE_REPLY`.

### Arquivo: `src/workflows/meeting_shared/handlers.py`

Adicionar após `handle_unexpected_state`:

```python
def handle_waiting_for_template_reply(
    context: MeetingContext, message: str, use_bold_asterisks: bool = True
) -> Generator[Tuple[str, str], None, None]:
    """
    Template reply recebida via task.py já transitou para INIT antes de chegar aqui.
    Este handler é um fallback defensivo caso o estado seja WAITING_FOR_TEMPLATE_REPLY
    quando o workflow é chamado diretamente (ex: schedule.py após restart).
    """
    update_meeting_state(MeetingState.INIT.value, context.user_id)
    # Re-executa como INIT passando context com estado atualizado
    updated_context = MeetingContext(
        **{**context.__dict__, "state": MeetingState.INIT}
    )
    yield from handle_init(updated_context, message, use_bold_asterisks)
```

Registrar no dicionário `STATE_HANDLERS`:

```python
STATE_HANDLERS = {
    MeetingState.INIT.value: handle_init,
    MeetingState.WAITING_FOR_TEMPLATE_REPLY.value: handle_waiting_for_template_reply,  # novo
    MeetingState.WAITING_DONATED_RESPONSE.value: handle_waiting_donated,
    MeetingState.WAITING_RECEIVED_RESPONSE.value: handle_waiting_received,
    MeetingState.HUMAN_INTERVENTION_REQUIRED.value: handle_human_intervention_required,
    MeetingState.RECEIVED_CONFIRMED.value: handle_received_confirmed,
}
```

---

## 6. F8 — Validação de Email no Trigger

**Por que fazer antes do GCal:** sem email do mentor, o GCal invite não pode ser criado. Falhar no trigger (antes de qualquer mensagem ser enviada) é melhor que falhar após toda a negociação.

### Arquivo: `src/services/meetings_service.py`

Adicionar após a função existente `get_meeting_by_id`:

```python
def extract_emails(meeting_doc: dict) -> tuple[str | None, str | None]:
    """
    Extrai os emails de donated (mentor) e received (founder) do documento de meeting.
    Retorna (donated_email, received_email). Pode ser None se não encontrado.
    """
    attendees = meeting_doc.get("attendees", [])
    donated = next((a for a in attendees if a.get("role") == "Donated"), None)
    received = next((a for a in attendees if a.get("role") == "Received"), None)
    donated_email = donated.get("email") if donated else None
    received_email = received.get("email") if received else None
    return donated_email, received_email
```

### Arquivo: `src/api/v1/schedule.py`

Modificações no endpoint `POST /schedule`:

```python
from src.services.meetings_service import extract_emails  # novo import

# Após load_potential_meeting_into_state:
success = load_potential_meeting_into_state(meeting_id, donated_phone)
if not success:
    raise HTTPException(status_code=404, detail="Meeting potential not found")

# NOVO: Validar emails antes de iniciar o fluxo
meeting_state = get_current_meeting_state(donated_phone)
meeting_doc = meeting_state.get("meeting", {}) or {}
donated_email, received_email = extract_emails(meeting_doc)

if not donated_email:
    raise HTTPException(
        status_code=422,
        detail={
            "error": "missing_mentor_email",
            "field": "donated_email",
            "message": "O mentor não tem email cadastrado. Cadastre o email antes de iniciar o agendamento.",
        },
    )
if not received_email:
    raise HTTPException(
        status_code=422,
        detail={
            "error": "missing_founder_email",
            "field": "received_email",
            "message": "O founder não tem email cadastrado. Cadastre o email antes de iniciar o agendamento.",
        },
    )

# NOVO: Salvar emails no estado (para uso posterior no GCalService)
from src.services.state_machine_service import save_emails  # ver abaixo
save_emails(donated_phone, donated_email, received_email)
```

Adicionar `save_emails` em `state_machine_service.py`:

```python
def save_emails(user_id: str, donated_email: str, received_email: str) -> None:
    """Persiste os emails no estado Redis para uso posterior pelo GCalService."""
    state = _get_or_init_state(user_id)
    state["donated_email"] = donated_email
    state["received_email"] = received_email
    _save(user_id, state)
```

---

## 7. F6 — Fix EC-06: Mídia Preserva Estado e Mensagem Contextual

**Análise do bug:** O código atual em `task.py` (linha 104–115, `case _:`) já preserva o estado corretamente — nenhuma transição acontece. O problema é duplo:
1. A mensagem enviada ("Desculpe, no momento suporto apenas mensagens de texto.") é genérica e não ajuda o usuário em fluxo a continuar.
2. `record_interaction_time` não é chamado — o timeout continua contando, o que é correto (usuário não respondeu com texto válido), mas deve ser explícito.

### Arquivo: `src/tasks/whatsapp/task.py`

Substituir o `case _:` block (linhas 104–115):

```python
    case _:
        logger.info(f"Unsupported message type from {from_number}: {message.type}")

        # Verifica se o usuário tem fluxo ativo para dar mensagem contextual
        _state_for_media = get_current_meeting_state(from_number)
        _status_for_media = _state_for_media.get("status")
        if _status_for_media not in active_states:
            _state_for_media = get_current_meeting_state("+" + from_number)
            _status_for_media = _state_for_media.get("status")

        if _status_for_media in active_states:
            fallback_msg = (
                "Por favor, responda com uma mensagem de texto para que eu consiga "
                "continuar o agendamento. 😊"
            )
        else:
            fallback_msg = "Desculpe, no momento suporto apenas mensagens de texto."

        # Estado NÃO é alterado — preservado intencionalmente
        # record_interaction_time NÃO é chamado — timeout continua correndo
        if needs_template(from_number):
            logger.info(
                f"24h window expired for {from_number} — sending hello_world template"
            )
            await whatsapp.send_template(from_number, "hello_world")
            await asyncio.sleep(2)
        await whatsapp.send_text_humanized(from_number, fallback_msg)
        update_last_conversation_time(from_number)
```

**Nota:** a variável `active_states` já está definida no escopo do `case TextMessage` — extrair para o escopo do `_process_whatsapp_message` para reutilização:

```python
# Mover para o início do handler (antes do match), no início de _process_whatsapp_message:
active_states = {
    "WAITING_FOR_TEMPLATE_REPLY",
    "WAITING_DONATED_RESPONSE",
    "WAITING_RECEIVED_RESPONSE",
}
```

---

## 8. F1 — GCalService

### Dependências

```bash
uv add google-api-python-client google-auth
```

### Novo arquivo: `src/services/gcal_service.py`

```python
import json
import logging
from datetime import datetime, timedelta, timezone

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account

from src.core.config import settings

logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GCalCreationError(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"GCal invite creation failed: {reason}")


class GoogleCalendarService:
    def __init__(self):
        if not settings.gcal.SERVICE_ACCOUNT_JSON or not settings.gcal.ORGANIZER_EMAIL:
            raise GCalCreationError("GCAL__SERVICE_ACCOUNT_JSON ou GCAL__ORGANIZER_EMAIL não configurado")

        service_account_info = json.loads(settings.gcal.SERVICE_ACCOUNT_JSON)
        credentials = service_account.Credentials.from_service_account_info(
            service_account_info,
            scopes=SCOPES,
        )
        # Impersonar o email organizador (Domain-Wide Delegation)
        delegated_credentials = credentials.with_subject(settings.gcal.ORGANIZER_EMAIL)
        self._service = build("calendar", "v3", credentials=delegated_credentials)

    def create_meeting_invite(
        self,
        mentor_email: str,
        founder_email: str,
        slot_datetime_iso: str,
        duration_minutes: int = 60,
        title: str = "Mentoria Endeavor",
        description: str = "",
    ) -> str:
        """
        Cria um evento no Google Calendar.

        Args:
            mentor_email: Email pessoal do mentor (guest).
            founder_email: Email pessoal do founder (guest).
            slot_datetime_iso: ISO 8601 do horário confirmado.
            duration_minutes: Duração da reunião (padrão: 60 min).
            title: Título do evento.
            description: Descrição do evento.

        Returns:
            str: ID do evento criado.

        Raises:
            GCalCreationError: Se a criação falhar.
        """
        try:
            start_dt = datetime.fromisoformat(slot_datetime_iso)
            # Garantir timezone-aware
            if start_dt.tzinfo is None:
                start_dt = start_dt.replace(tzinfo=timezone.utc)
            end_dt = start_dt + timedelta(minutes=duration_minutes)

            event_body = {
                "summary": title,
                "description": description,
                "start": {
                    "dateTime": start_dt.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "end": {
                    "dateTime": end_dt.isoformat(),
                    "timeZone": "America/Sao_Paulo",
                },
                "attendees": [
                    {"email": mentor_email},
                    {"email": founder_email},
                ],
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "email", "minutes": 24 * 60},
                        {"method": "popup", "minutes": 30},
                    ],
                },
            }

            event = self._service.events().insert(
                calendarId=settings.gcal.ORGANIZER_EMAIL,
                body=event_body,
                sendUpdates="all",  # envia email de convite para os guests
            ).execute()

            event_id = event.get("id")
            logger.info(f"GCal invite created: event_id={event_id}, title={title}")
            return event_id

        except HttpError as e:
            logger.error(f"Google Calendar API error: {e}")
            raise GCalCreationError(f"Google API HTTP error: {e.status_code}")
        except Exception as e:
            logger.error(f"Unexpected error creating GCal invite: {e}")
            raise GCalCreationError(str(e))


# Instância global (lazy initialization na primeira chamada)
_gcal_service: GoogleCalendarService | None = None


def get_gcal_service() -> GoogleCalendarService:
    global _gcal_service
    if _gcal_service is None:
        _gcal_service = GoogleCalendarService()
    return _gcal_service
```

### Integração em `src/workflows/meeting_shared/handlers.py`

No `handle_waiting_received`, após `RECEIVED_CONFIRMED`, adicionar a criação do GCal **antes** de enviar as mensagens de confirmação:

```python
# Novos imports no topo do arquivo:
from src.services.gcal_service import get_gcal_service, GCalCreationError

# Dentro de handle_waiting_received, substituir o bloco a partir da linha 149:

    selected_time = selected_slots[selected_option_index - 1]
    slot_display = format_slot(selected_time)

    # NOVO: Criar GCal invite antes de confirmar para os usuários
    gcal_event_id = None
    donated_email = context.state_dict.get("donated_email")
    received_email = context.state_dict.get("received_email")
    company_name = context.state_dict.get("meeting", {}).get("company", "") if context.state_dict.get("meeting") else ""
    gcal_title = f"{company_name} × {context.donated_name}".strip(" ×") if company_name else f"Mentoria — {context.donated_name}"

    if donated_email and received_email:
        try:
            gcal_service = get_gcal_service()
            gcal_event_id = gcal_service.create_meeting_invite(
                mentor_email=donated_email,
                founder_email=received_email,
                slot_datetime_iso=selected_time,
                title=gcal_title,
                description=f"Mentoria Endeavor — {context.donated_name} e {context.received_name}",
            )
        except GCalCreationError as e:
            logger.error(f"GCal creation failed for meeting {context.state_dict.get('meeting_id')}: {e}")
            # Falha no GCal: escalar sem confirmar (produto não existe sem o invite)
            update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
            await _escalate(
                context=context,
                reason="gcal_creation_failed",
                last_state="WAITING_RECEIVED_RESPONSE",
            )
            yield (context.received_phone, "Houve um problema ao criar o convite no calendário. O time da Endeavor entrará em contato em breve.")
            return
    else:
        logger.warning(f"Emails ausentes para meeting {context.state_dict.get('meeting_id')} — GCal não criado")

    update_meeting_state(MeetingState.RECEIVED_CONFIRMED.value, context.user_id, selection=selected_time)

    confirmation_msg = build_confirmation_message(
        context.donated_name,
        context.received_name,
        slot_display,
        use_bold_asterisks,
    )

    yield (context.donated_phone, confirmation_msg)
    if context.received_phone != context.donated_phone:
        yield (context.received_phone, confirmation_msg)
```

**Nota sobre `_escalate`:** função helper a ser criada na seção F2 abaixo. Os handlers passam a chamar `_escalate(context, reason, last_state)` em vez de duplicar a lógica.

---

## 9. F2 — EscalationService

### Novo arquivo: `src/services/escalation_service.py`

```python
import logging
from dataclasses import dataclass, field
from typing import Optional

from src.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class EscalationContext:
    reason: str                                  # ver tabela de reasons abaixo
    meeting_id: str
    donor_name: str                              # mentor
    received_name: str                           # founder
    company: str
    last_state: str
    conversation_summary: str                    # últimas mensagens trocadas
    user_id: str                                 # para salvar thread_ts depois
    negotiation_history: list = field(default_factory=list)


# Tabela de reasons válidos:
# "timeout_mentor"            — mentor não respondeu após follow-up
# "timeout_founder"           — founder não respondeu após follow-up
# "agent_refused"             — mentor ou founder recusou o agente
# "max_clarifications_reached" — 2+ tentativas sem extração bem-sucedida
# "founder_rejected_no_alternative" — founder rejeitou sem oferecer alternativa
# "max_rounds_reached"        — MAX_NEGOTIATION_ROUNDS atingido sem convergência
# "gcal_creation_failed"      — erro ao criar GCal invite


class EscalationService:
    async def notify(self, ctx: EscalationContext) -> None:
        """
        Notifica o AEE sobre uma escalada. Não lança exceção se canal não configurado.
        """
        channel = settings.escalation.CHANNEL
        try:
            if channel == "whatsapp":
                await self._notify_whatsapp(ctx)
            elif channel == "slack":
                await self._notify_slack(ctx)
            else:
                logger.warning(
                    f"ESCALATION__CHANNEL='{channel}' não reconhecido. "
                    "Escalada silenciosa. Configure 'whatsapp' ou 'slack'."
                )
        except Exception as e:
            logger.error(f"EscalationService.notify falhou: {e}", exc_info=True)
            # Não propaga a exceção — escalada não pode quebrar o fluxo principal

    async def _notify_whatsapp(self, ctx: EscalationContext) -> None:
        if not settings.escalation.WHATSAPP_PHONE:
            logger.warning("ESCALATION__WHATSAPP_PHONE não configurado. Escalada silenciosa.")
            return

        from src.services.whatsapp import whatsapp

        reason_labels = {
            "timeout_mentor": "Mentor não respondeu após follow-up",
            "timeout_founder": "Founder não respondeu após follow-up",
            "agent_refused": "Usuário recusou o agente",
            "max_clarifications_reached": "Máximo de clarificações atingido",
            "founder_rejected_no_alternative": "Founder rejeitou sem alternativa",
            "max_rounds_reached": "Máximo de rounds de negociação atingido",
            "gcal_creation_failed": "Falha ao criar GCal invite",
        }
        reason_label = reason_labels.get(ctx.reason, ctx.reason)

        negotiation_section = ""
        if ctx.negotiation_history:
            negotiation_section = f"\n\nHistórico de rounds ({len(ctx.negotiation_history)}):\n"
            for r in ctx.negotiation_history:
                negotiation_section += f"  Round {r.get('round_number', '?')}: {r.get('result', '?')}\n"

        message = (
            f"⚠️ *Intervenção necessária*\n\n"
            f"Meeting ID: {ctx.meeting_id}\n"
            f"Mentor: {ctx.donor_name}\n"
            f"Founder: {ctx.received_name} ({ctx.company})\n"
            f"Motivo: {reason_label}\n"
            f"Último estado: {ctx.last_state}"
            f"{negotiation_section}\n\n"
            f"---\n"
            f"Histórico recente:\n{ctx.conversation_summary}"
        )

        await whatsapp.send_text(settings.escalation.WHATSAPP_PHONE, message)
        logger.info(f"Escalation WhatsApp sent for meeting {ctx.meeting_id}, reason={ctx.reason}")

    async def _notify_slack(self, ctx: EscalationContext) -> None:
        """Ver F10 — Slack Takeover para implementação completa."""
        if not settings.slack.BOT_TOKEN or not settings.slack.TAKEOVER_CHANNEL:
            logger.warning("SLACK__BOT_TOKEN ou SLACK__TAKEOVER_CHANNEL não configurado. Escalada silenciosa.")
            return
        # Implementação completa na seção F10


# Instância global
escalation_service = EscalationService()
```

### Helper `_escalate` em `handlers.py`

Para evitar duplicação nos handlers, criar uma função helper no início do arquivo (após os imports):

```python
# Novo import:
from src.services.escalation_service import escalation_service, EscalationContext

async def _escalate(context: MeetingContext, reason: str, last_state: str) -> None:
    """
    Wrapper para EscalationService.notify com dados extraídos do MeetingContext.
    Chama em qualquer transição para HUMAN_INTERVENTION_REQUIRED.
    """
    meeting = context.state_dict.get("meeting") or {}
    company = meeting.get("company", "Empresa não identificada")

    # Montar resumo da conversa (últimas mensagens, se disponíveis)
    # Por ora: informações de estado — histórico completo será instrumentado na Fase 3
    conversation_summary = (
        f"Estado anterior: {last_state}\n"
        f"Mentor: {context.donated_name} ({context.donated_phone})\n"
        f"Founder: {context.received_name} ({context.received_phone})\n"
        f"Round atual: {context.current_round}/{context.max_rounds}"
    )

    escalation_ctx = EscalationContext(
        reason=reason,
        meeting_id=context.state_dict.get("meeting_id", "desconhecido"),
        donor_name=context.donated_name,
        received_name=context.received_name,
        company=company,
        last_state=last_state,
        conversation_summary=conversation_summary,
        user_id=context.user_id,
        negotiation_history=context.negotiation_history,
    )
    await escalation_service.notify(escalation_ctx)
```

**Nota sobre `async`:** os handlers atuais são geradores síncronos (`Generator[Tuple[str, str], None, None]`). Chamar `await _escalate(...)` requer que os handlers sejam `async`. A solução é converter os handlers para `AsyncGenerator` ou usar `asyncio.run(_escalate(...))` dentro do handler síncrono. **Recomendação:** converter `handle_waiting_donated` e `handle_waiting_received` para `async def` e retornar `AsyncGenerator[Tuple[str, str], None]`. O `task.py` já usa `asyncio.run()` para o handler geral, então o change é passível de fazer.

**Passo concreto:** substituir `Generator[Tuple[str, str], None, None]` por `AsyncGenerator[Tuple[str, str], None]` nos handlers que chamam `_escalate`, e usar `async for` ao invés de `for` em `task.py` e `schedule.py` onde os handlers são consumidos.

### Integração nos handlers existentes

Substituir cada bloco de transição para `HUMAN_INTERVENTION_REQUIRED` para chamar `_escalate`:

```python
# ANTES (handle_waiting_donated — timeout):
update_meeting_state(MeetingState.DONATED_NO_RESPONSE.value, context.user_id)
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
yield (context.donated_phone, build_timeout_message("donated"))

# DEPOIS:
update_meeting_state(MeetingState.DONATED_NO_RESPONSE.value, context.user_id)
update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
await _escalate(context, reason="timeout_mentor", last_state="WAITING_DONATED_RESPONSE")
yield (context.donated_phone, build_timeout_message("donated"))
```

Repetir para todos os outros pontos de escalada (ver tabela de reasons acima).

---

## 10. F4 — RefusalDetectorAgent

### Novo arquivo: `src/agents/main/refusal_detector_agent.py`

```python
from pydantic import BaseModel, Field
from typing import Literal
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from src.core.langfuse import get_prompt


class ExtractedRefusal(BaseModel):
    is_refusal: bool = Field(
        description="True if the user is explicitly refusing to interact with the bot or requesting a human."
    )
    sentiment: Literal["neutral", "frustrated", "hostile"] = Field(
        default="neutral",
        description="Emotional tone of the message."
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score from 0.0 to 1.0 for the refusal classification.",
        ge=0.0,
        le=1.0,
    )


_refusal_detector_prompt = get_prompt(prompt_name="refusal_detector_agent_prompt")

refusal_detector_agent = Agent(
    name="RefusalDetectorAgent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        api_key=settings.openai.API_KEY.get_secret_value(),
        temperature=0,
    ),
    output_schema=ExtractedRefusal,
    instructions=[_refusal_detector_prompt.prompt],
    markdown=False,
    add_history_to_context=False,
)
```

**Prompt `refusal_detector_agent_prompt` a criar no Langfuse:**
```
Você é um classificador de intenções em conversas de agendamento via WhatsApp.

Sua tarefa: determinar se o usuário está recusando interagir com um agente automático
ou pedindo para falar com uma pessoa.

Exemplos de recusa (is_refusal=true):
- "não quero falar com robô"
- "prefiro falar com uma pessoa"
- "para de me mandar mensagem"
- "não quero usar esse sistema"
- "quero atendimento humano"
- "pode me colocar com alguém?"

Exemplos que NÃO são recusa (is_refusal=false):
- "não posso nesses horários" (rejeição de slots, não do agente)
- "não quero agendar" (cancela o agendamento, não o agente)
- "prefiro segunda" (preferência de horário)
- "não tenho disponibilidade essa semana" (falta de disponibilidade)

Retorne JSON com is_refusal, sentiment ("neutral"/"frustrated"/"hostile"), e confidence (0.0-1.0).
Seja conservador: só marque como recusa quando a intenção for clara.
```

### Integração em `handlers.py`

Importar e chamar no início de `handle_waiting_donated` e `handle_waiting_received`, antes de qualquer outra lógica:

```python
# Novo import:
from src.agents.main.refusal_detector_agent import refusal_detector_agent
from src.workflows.meeting_shared.utils import parse_extracted

REFUSAL_CONFIDENCE_THRESHOLD = 0.85

async def _check_refusal(context: MeetingContext, message: str, role: str) -> bool:
    """
    Verifica se a mensagem é uma recusa ao agente.
    Se sim, transiciona para HI e notifica AEE.
    Retorna True se for recusa (handler deve fazer return logo após).
    """
    run_response = refusal_detector_agent.run(message)
    extracted = run_response.content

    is_refusal = parse_extracted(extracted, "is_refusal", default=False)
    confidence = parse_extracted(extracted, "confidence", default=0.0)

    if is_refusal and confidence >= REFUSAL_CONFIDENCE_THRESHOLD:
        update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
        await _escalate(context, reason="agent_refused", last_state=f"WAITING_{role.upper()}_RESPONSE")
        return True
    return False
```

Adicionar ao início de `handle_waiting_donated` (após o check de timeout):

```python
# Após check_timeout, antes do slot extractor:
if await _check_refusal(context, message, "donated"):
    yield (context.donated_phone, build_refusal_humanizing_message())
    return
```

Adicionar ao início de `handle_waiting_received` (após o check de timeout):

```python
if await _check_refusal(context, message, "received"):
    yield (context.received_phone, build_refusal_humanizing_message())
    return
```

Adicionar em `messages.py`:

```python
def build_refusal_humanizing_message() -> str:
    return (
        "Entendido! Vou conectar você com alguém do time Endeavor que poderá ajudar. "
        "Em breve alguém entrará em contato. 🙏"
    )
```

---

## 11. F5 — Ambiguity Counter

### Arquivo: `src/services/state_machine_service.py`

Adicionar duas novas funções:

```python
def update_clarification_count(user_id: str, count: int) -> None:
    """Atualiza o counter de clarificações sem resetar o TTL."""
    state = _get_or_init_state(user_id)
    state["clarification_count"] = count
    _save(user_id, state)


def reset_clarification_count(user_id: str) -> None:
    """Reseta o counter (chamado no início de cada novo round de negociação)."""
    update_clarification_count(user_id, 0)
```

### Arquivo: `src/workflows/meeting_shared/handlers.py`

Importar as novas funções e modificar os casos de "não reconhecido" em `handle_waiting_donated` e `handle_waiting_received`:

```python
from src.services.state_machine_service import (
    update_meeting_state,
    record_interaction_time,
    check_timeout,
    update_clarification_count,   # novo
    reset_clarification_count,    # novo
)

MAX_CLARIFICATIONS = 2

# Em handle_waiting_donated — substituir o bloco final (len==1 e unrecognized):

    if selected_slots and len(selected_slots) == 1:
        clarification_count = context.state_dict.get("clarification_count", 0) + 1
        if clarification_count >= MAX_CLARIFICATIONS:
            update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
            await _escalate(context, reason="max_clarifications_reached", last_state="WAITING_DONATED_RESPONSE")
            yield (context.donated_phone, build_timeout_message("donated"))
            return
        update_clarification_count(context.user_id, clarification_count)
        yield (context.donated_phone, build_need_more_options_message())
        return

    # else: unrecognized
    clarification_count = context.state_dict.get("clarification_count", 0) + 1
    if clarification_count >= MAX_CLARIFICATIONS:
        update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
        await _escalate(context, reason="max_clarifications_reached", last_state="WAITING_DONATED_RESPONSE")
        yield (context.donated_phone, build_human_intervention_message())
        return
    update_clarification_count(context.user_id, clarification_count)
    yield (context.donated_phone, build_unrecognized_options_message())
```

Mesma lógica em `handle_waiting_received` para o caso `selected_option_index` inválido.

---

## 12. F7 — Deduplicação de Trigger por `meeting_id`

### Arquivo: `src/services/state_machine_service.py`

Adicionar funções para o índice reverso:

```python
def _meeting_id_key(meeting_id: str) -> str:
    return f"meeting_id_index:{meeting_id}"


def register_meeting_id(meeting_id: str, user_id: str) -> None:
    """Cria índice reverso meeting_id → user_id com mesmo TTL do estado."""
    _redis.set(_meeting_id_key(meeting_id), user_id, ex=STATE_TTL_SECONDS)


def get_user_id_by_meeting_id(meeting_id: str) -> str | None:
    """Retorna o user_id (donated_phone) associado a um meeting_id ativo."""
    return _redis.get(_meeting_id_key(meeting_id))


def is_meeting_active(meeting_id: str) -> bool:
    """True se existe fluxo ativo para este meeting_id."""
    user_id = get_user_id_by_meeting_id(meeting_id)
    if not user_id:
        return False
    state = _load(user_id)
    return state.get("status") not in _TERMINAL_OR_IDLE_STATES
```

Adicionar `_TERMINAL_OR_IDLE_STATES` ao `state_machine_service.py`:

```python
_TERMINAL_OR_IDLE_STATES = {"INIT", "RECEIVED_CONFIRMED", "HUMAN_INTERVENTION_REQUIRED"}
```

Chamar `register_meeting_id` dentro de `load_potential_meeting_into_state`, após salvar o estado:

```python
def load_potential_meeting_into_state(meeting_id: str, user_id: str) -> bool:
    # ... código existente ...
    state["meeting"] = meeting
    state["donated"] = donated
    state["received"] = received
    state["meeting_id"] = meeting_id   # NOVO: salvar meeting_id no state
    _save(user_id, state)
    register_meeting_id(meeting_id, user_id)  # NOVO: índice reverso
    return True
```

### Arquivo: `src/api/v1/schedule.py`

Adicionar verificação de `meeting_id` ANTES da verificação de `donated_phone`:

```python
from src.services.state_machine_service import (
    get_current_meeting_state,
    update_meeting_state,
    load_potential_meeting_into_state,
    register_phone_numbers,
    is_meeting_active,   # novo import
)

@router.post("/schedule")
async def schedule_meeting(body: ScheduleRequest):
    meeting_id = body.meeting_id
    donated_phone = body.donated_phone_number
    received_phone = body.received_phone_number

    # NOVO: verificar deduplicação por meeting_id
    if is_meeting_active(meeting_id):
        raise HTTPException(
            status_code=409,
            detail={
                "error": "flow_already_active",
                "meeting_id": meeting_id,
                "message": f"Já existe um fluxo de agendamento ativo para o meeting {meeting_id}.",
            },
        )

    # Verificação existente por donated_phone (mantida):
    current_state = get_current_meeting_state(donated_phone)
    # ... resto do código ...
```

---

## 13. F3 — Timeout Proativo com Celery Beat

### Novo arquivo: `src/tasks/whatsapp/timeout_task.py`

```python
import asyncio
import logging
from datetime import datetime

from src.core.celery import celery_app
from src.core.config import settings
from src.services.state_machine_service import (
    _redis,            # acesso direto ao cliente Redis
    _load,
    _save,
    _key,
    update_meeting_state,
)
from src.services.whatsapp import whatsapp
from src.services.whatsapp_window_service import needs_template, update_last_conversation_time
from src.workflows.meeting_shared.models import MeetingState

logger = logging.getLogger(__name__)

WAITING_STATES = {"WAITING_DONATED_RESPONSE", "WAITING_RECEIVED_RESPONSE"}


@celery_app.task(name="check_whatsapp_timeouts")
def check_whatsapp_timeouts():
    """
    Periódica: varre todos os fluxos ativos no Redis e dispara follow-up ou HI.
    """
    asyncio.run(_async_check_timeouts())


async def _async_check_timeouts():
    timeout_seconds = settings.no_response_timeout_seconds

    # SCAN é seguro para Redis em produção — não bloqueia
    cursor = 0
    while True:
        cursor, keys = _redis.scan(cursor, match="meeting_state:*", count=100)
        for key in keys:
            await _process_key(key, timeout_seconds)
        if cursor == 0:
            break


async def _process_key(key: str, timeout_seconds: int):
    user_id = key.removeprefix("meeting_state:")
    state = _load(user_id)
    status = state.get("status")

    if status not in WAITING_STATES:
        return

    last_str = state.get("last_interaction_time")
    if not last_str:
        return

    try:
        last = datetime.fromisoformat(last_str)
        elapsed = (datetime.now() - last).total_seconds()
    except (ValueError, TypeError):
        return

    follow_up_sent = state.get("follow_up_sent", False)
    donated_phone = state.get("donated_phone")
    received_phone = state.get("received_phone")

    # Determinar destinatário e role pelo estado
    if status == "WAITING_DONATED_RESPONSE":
        recipient = donated_phone
        role = "donated"
    else:
        recipient = received_phone
        role = "received"

    if not recipient:
        return

    if elapsed > timeout_seconds and not follow_up_sent:
        # Primeiro timeout: enviar follow-up
        await _send_followup(user_id, recipient, role, state)
    elif elapsed > (timeout_seconds * 2) and follow_up_sent:
        # Segundo timeout (após follow-up): escalar
        await _escalate_timeout(user_id, state, role)


async def _send_followup(user_id: str, recipient: str, role: str, state: dict):
    from src.workflows.meeting_shared.messages import build_followup_message

    logger.info(f"Timeout follow-up: sending to {recipient} (user_id={user_id})")
    try:
        if needs_template(recipient):
            await whatsapp.send_template(recipient, "hello_world")
            import asyncio as _asyncio
            await _asyncio.sleep(2)
        await whatsapp.send_text_humanized(recipient, build_followup_message(role))
        update_last_conversation_time(recipient)

        state["follow_up_sent"] = True
        state["follow_up_sent_at"] = datetime.now().isoformat()
        _save(user_id, state)
    except Exception as e:
        logger.error(f"Failed to send follow-up to {recipient}: {e}")


async def _escalate_timeout(user_id: str, state: dict, role: str):
    from src.services.escalation_service import escalation_service, EscalationContext
    from src.workflows.meeting_shared.messages import build_timeout_message

    meeting = state.get("meeting") or {}
    company = meeting.get("company", "Empresa não identificada")
    donated_name = (state.get("donated") or {}).get("name", "Mentor")
    received_name = (state.get("received") or {}).get("name", "Founder")
    last_state = state.get("status", "UNKNOWN")
    reason = f"timeout_{role}"

    recipient = state.get("donated_phone") if role == "donated" else state.get("received_phone")

    logger.info(f"Timeout escalation: user_id={user_id}, reason={reason}")

    update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, user_id)

    ctx = EscalationContext(
        reason=reason,
        meeting_id=state.get("meeting_id", "desconhecido"),
        donor_name=donated_name,
        received_name=received_name,
        company=company,
        last_state=last_state,
        conversation_summary=f"Timeout após follow-up. Último estado: {last_state}",
        user_id=user_id,
    )
    await escalation_service.notify(ctx)

    if recipient:
        try:
            if needs_template(recipient):
                await whatsapp.send_template(recipient, "hello_world")
                import asyncio as _asyncio
                await _asyncio.sleep(2)
            await whatsapp.send_text_humanized(recipient, build_timeout_message(role))
        except Exception as e:
            logger.error(f"Failed to send timeout message to {recipient}: {e}")
```

Adicionar em `messages.py`:

```python
def build_followup_message(role: str) -> str:
    if role == "donated":
        return (
            "Olá! 👋 Ainda aguardamos sua disponibilidade para o agendamento da mentoria. "
            "Quando puder, envie pelo menos 2 opções de horário."
        )
    return (
        "Olá! 👋 Ainda aguardamos sua confirmação de horário para a mentoria. "
        "Quando puder, escolha uma das opções enviadas anteriormente."
    )
```

### Arquivo: `src/core/celery.py`

```python
from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_init
from src.core.config import settings
from src.core.langfuse import setup

celery_app = Celery("endeavor_ai")

celery_app.conf.update(
    broker_url=settings.redis.URL,
    result_backend=settings.redis.URL,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Auto-discover tasks
celery_app.autodiscover_tasks(["src.tasks.whatsapp"])

# Celery Beat — tarefas periódicas
celery_app.conf.beat_schedule = {
    "check-whatsapp-timeouts": {
        "task": "check_whatsapp_timeouts",
        "schedule": crontab(minute=f"*/{settings.timeout_check_interval_minutes}"),
    },
}


@worker_init.connect
def on_worker_init(**kwargs):
    setup()
```

**Comando para rodar o Beat:**
```bash
uv run celery -A src.core.celery beat --loglevel=info
```

---

## 14. F9 — Motor de Negociação Multi-Round

### Novo arquivo: `src/agents/main/counter_availability_extractor_agent.py`

```python
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from src.core.langfuse import get_prompt


class ExtractedAvailability(BaseModel):
    has_counter_proposal: bool = Field(
        description="True se o usuário está propondo janelas de disponibilidade próprias."
    )
    available_windows: list[str] = Field(
        default_factory=list,
        description="Janelas de disponibilidade em linguagem natural. Ex: ['segunda 14h-16h', 'sexta manhã']",
    )
    raw_text: str = Field(
        default="",
        description="Texto original do usuário para contexto.",
    )


_counter_availability_prompt = get_prompt(prompt_name="counter_availability_extractor_agent_prompt")

counter_availability_extractor_agent = Agent(
    name="CounterAvailabilityExtractorAgent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        api_key=settings.openai.API_KEY.get_secret_value(),
        temperature=0,
    ),
    output_schema=ExtractedAvailability,
    instructions=[_counter_availability_prompt.prompt],
    markdown=False,
    add_history_to_context=False,
)
```

**Prompt `counter_availability_extractor_agent_prompt` a criar no Langfuse:**
```
Você extrai disponibilidade de horários quando um participante rejeita opções propostas
e oferece suas próprias janelas de disponibilidade.

Exemplos com has_counter_proposal=true:
- "não posso nesses dias, mas posso segunda ou quarta de tarde"
- "esses horários não funcionam pra mim, tenho disponibilidade apenas sextas"
- "prefiro de manhã, pode ser terça ou quinta"

Exemplos com has_counter_proposal=false:
- "não posso em nenhum desses" (rejeição sem alternativa)
- "infelizmente esses horários não servem" (sem proposta)
- "não tenho disponibilidade" (sem alternativa)

Extraia as janelas em linguagem natural como foram ditas.
Não tente converter para ISO datetime.
```

### Integração em `handlers.py`

Modificar o bloco `if is_rejected:` em `handle_waiting_received`:

```python
from src.agents.main.counter_availability_extractor_agent import counter_availability_extractor_agent

# Em handle_waiting_received, substituir:
if is_rejected:
    # Tenta identificar contra-proposta antes de escalar
    counter_run = counter_availability_extractor_agent.run(message)
    counter_extracted = counter_run.content
    has_counter = parse_extracted(counter_extracted, "has_counter_proposal", default=False)
    available_windows = parse_extracted(counter_extracted, "available_windows", default=[])

    if has_counter and available_windows and context.current_round < context.max_rounds:
        # Motor de negociação: voltar ao mentor com contra-proposta
        new_round = context.current_round + 1
        windows_text = ", ".join(available_windows)

        # Salvar round no histórico
        round_data = {
            "round_number": context.current_round,
            "mentor_slots_offered": context.state_dict.get("selected_slot", []),
            "founder_counter_windows": available_windows,
            "result": "rejected_with_counter",
            "timestamp": datetime.now().isoformat(),
        }
        negotiation_history = context.state_dict.get("negotiation_history", [])
        negotiation_history.append(round_data)

        # Atualizar estado: voltar para WAITING_DONATED_RESPONSE, novo round
        state = context.state_dict.copy()
        state["current_round"] = new_round
        state["max_rounds"] = context.max_rounds
        state["negotiation_history"] = negotiation_history
        state["clarification_count"] = 0  # reset para o novo round
        state["founder_counter_windows"] = available_windows

        from src.services.state_machine_service import _save, _key
        state["status"] = MeetingState.WAITING_DONATED_RESPONSE.value
        _save(context.user_id, state)
        record_interaction_time(context.user_id)

        yield (
            context.donated_phone,
            build_negotiation_counter_message(
                context.donated_name,
                context.received_name,
                windows_text,
            )
        )
        return

    # Sem contra-proposta OU rounds esgotados: escalar
    if not has_counter or not available_windows:
        reason = "founder_rejected_no_alternative"
    else:
        reason = "max_rounds_reached"

    update_meeting_state(MeetingState.RECEIVED_REJECTED.value, context.user_id)
    update_meeting_state(MeetingState.HUMAN_INTERVENTION_REQUIRED.value, context.user_id)
    await _escalate(context, reason=reason, last_state="WAITING_RECEIVED_RESPONSE")
    yield (context.received_phone, build_rejected_message("received", context.received_name))
    return
```

Adicionar em `messages.py`:

```python
def build_negotiation_counter_message(donated_name: str, received_name: str, windows_text: str) -> str:
    return (
        f"Olá, {donated_name}! 👋\n\n"
        f"{received_name} não pôde confirmar os horários anteriores, mas tem disponibilidade em: "
        f"{windows_text}.\n\n"
        f"Você teria alguma disponibilidade nessas janelas? Caso sim, envie pelo menos 2 opções de horário."
    )
```

Em `handle_waiting_donated`, verificar se é um round de negociação para formatar o contexto corretamente:

```python
# No enriquecimento da mensagem (linha 67–71), adicionar dados de negociação:
current_round = context.state_dict.get("current_round", 1)
founder_counter = context.state_dict.get("founder_counter_windows", [])
negotiation_context = ""
if current_round > 1 and founder_counter:
    negotiation_context = (
        f"\nNEGOTIATION CONTEXT: This is round {current_round}. "
        f"Founder is available in: {', '.join(founder_counter)}. "
        f"Extract slots that overlap with founder's availability if possible."
    )

enriched = (
    f"Base meeting_date: {context.meeting_date_iso}. "
    f"Today's date: {datetime.now().isoformat()}. "
    f"User Input: {message}"
    f"{negotiation_context}"
)
```

---

## 15. F10 — Slack Takeover (Relay Bidirecional)

### Dependências

```bash
uv add slack_sdk
```

### Completar `_notify_slack` em `src/services/escalation_service.py`

```python
async def _notify_slack(self, ctx: EscalationContext) -> None:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    from src.services.state_machine_service import _redis, STATE_TTL_SECONDS

    client = WebClient(token=settings.slack.BOT_TOKEN)

    reason_labels = {
        "timeout_mentor": "Mentor não respondeu após follow-up",
        "timeout_founder": "Founder não respondeu após follow-up",
        "agent_refused": "Usuário recusou o agente",
        "max_clarifications_reached": "Máximo de clarificações atingido",
        "founder_rejected_no_alternative": "Founder rejeitou sem alternativa",
        "max_rounds_reached": "Máximo de rounds atingido",
        "gcal_creation_failed": "Falha ao criar GCal invite",
    }

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": "⚠️ Intervenção Necessária"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Meeting ID:*\n{ctx.meeting_id}"},
                {"type": "mrkdwn", "text": f"*Motivo:*\n{reason_labels.get(ctx.reason, ctx.reason)}"},
                {"type": "mrkdwn", "text": f"*Mentor:*\n{ctx.donor_name}"},
                {"type": "mrkdwn", "text": f"*Founder:*\n{ctx.received_name}"},
                {"type": "mrkdwn", "text": f"*Empresa:*\n{ctx.company}"},
                {"type": "mrkdwn", "text": f"*Último estado:*\n{ctx.last_state}"},
            ],
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Histórico da conversa:*\n```{ctx.conversation_summary}```",
            },
        },
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    "*Como responder:*\n"
                    "• `@mentor <texto>` — envia mensagem ao mentor via WhatsApp\n"
                    "• `@founder <texto>` — envia mensagem ao founder via WhatsApp\n"
                    "• `/concluir slot=\"YYYY-MM-DDTHH:MM\"` — cria GCal invite e encerra\n"
                    "\n_Mentor e founder continuam no WhatsApp sem saber da troca._"
                ),
            },
        },
    ]

    try:
        response = client.chat_postMessage(
            channel=settings.slack.TAKEOVER_CHANNEL,
            blocks=blocks,
            text=f"Intervenção: {ctx.meeting_id} — {ctx.donor_name} × {ctx.received_name}",
        )
        thread_ts = response["ts"]

        # Salvar mapeamento thread_ts → contexto do fluxo no Redis
        import json as _json
        _redis.set(
            f"slack_thread:{thread_ts}",
            _json.dumps({
                "user_id": ctx.user_id,
                "meeting_id": ctx.meeting_id,
            }),
            ex=STATE_TTL_SECONDS * 7,  # 7 dias
        )

        # Salvar thread_ts no estado do fluxo para relay de respostas
        from src.services.state_machine_service import _load, _save, _key
        state = _load(ctx.user_id)
        state["slack_thread_ts"] = thread_ts
        _save(ctx.user_id, state)

        logger.info(f"Slack thread created: thread_ts={thread_ts} for meeting {ctx.meeting_id}")

    except SlackApiError as e:
        logger.error(f"Slack API error in EscalationService: {e}")
        raise
```

### Novo arquivo: `src/api/v1/slack.py`

```python
import hashlib
import hmac
import json
import logging
import re
import time

from fastapi import APIRouter, HTTPException, Request

from src.core.config import settings
from src.services.whatsapp import whatsapp
from src.services.whatsapp_window_service import needs_template, update_last_conversation_time
from src.services.state_machine_service import _redis, _load, _save, get_current_meeting_state, update_meeting_state
from src.workflows.meeting_shared.models import MeetingState
from src.services.gcal_service import get_gcal_service, GCalCreationError
from src.workflows.meeting_shared.messages import build_confirmation_message
from src.workflows.meeting_shared.utils import format_slot

import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)


def _verify_slack_signature(request_body: bytes, timestamp: str, signature: str) -> bool:
    """Valida SLACK_SIGNING_SECRET para autenticar eventos do Slack."""
    if not settings.slack.SIGNING_SECRET:
        logger.warning("SLACK__SIGNING_SECRET não configurado — validação de assinatura desabilitada")
        return True
    base = f"v0:{timestamp}:{request_body.decode()}"
    expected = "v0=" + hmac.new(
        settings.slack.SIGNING_SECRET.encode(),
        base.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)


@router.post("/v1/channels/slack/events")
async def slack_events(request: Request):
    body_bytes = await request.body()
    body = json.loads(body_bytes)

    # Verificar assinatura
    timestamp = request.headers.get("X-Slack-Request-Timestamp", "")
    signature = request.headers.get("X-Slack-Signature", "")

    # Proteção anti-replay (5 minutos)
    if abs(time.time() - int(timestamp)) > 300:
        raise HTTPException(status_code=403, detail="Timestamp too old")

    if not _verify_slack_signature(body_bytes, timestamp, signature):
        raise HTTPException(status_code=403, detail="Invalid signature")

    # URL Verification (setup inicial do Slack App)
    if body.get("type") == "url_verification":
        return {"challenge": body.get("challenge")}

    # Eventos de mensagem
    event = body.get("event", {})
    if event.get("type") == "message" and not event.get("bot_id"):
        await _handle_slack_message(event)

    return {"ok": True}


async def _handle_slack_message(event: dict):
    thread_ts = event.get("thread_ts")
    text = event.get("text", "").strip()

    if not thread_ts:
        return  # Mensagem fora de thread — ignorar

    # Buscar contexto do fluxo pelo thread_ts
    thread_data_raw = _redis.get(f"slack_thread:{thread_ts}")
    if not thread_data_raw:
        logger.warning(f"Slack thread {thread_ts} não encontrado no Redis — ignorando")
        return

    thread_data = json.loads(thread_data_raw)
    user_id = thread_data["user_id"]
    state = _load(user_id)

    donated_phone = state.get("donated_phone")
    received_phone = state.get("received_phone")

    # Comando /concluir slot="YYYY-MM-DDTHH:MM"
    concluir_match = re.match(r'/concluir\s+slot="?([^"]+)"?', text)
    if concluir_match:
        await _handle_concluir(user_id, state, concluir_match.group(1), thread_ts, donated_phone, received_phone)
        return

    # Relay @mentor ou @founder
    mentor_match = re.match(r'@mentor\s+(.*)', text, re.DOTALL)
    founder_match = re.match(r'@founder\s+(.*)', text, re.DOTALL)

    if mentor_match and donated_phone:
        await _relay_to_whatsapp(donated_phone, mentor_match.group(1), "Mentor")
    elif founder_match and received_phone:
        await _relay_to_whatsapp(received_phone, founder_match.group(1), "Founder")


async def _relay_to_whatsapp(phone: str, text: str, role: str):
    try:
        if needs_template(phone):
            await whatsapp.send_template(phone, "hello_world")
            await asyncio.sleep(2)
        await whatsapp.send_text_humanized(phone, text)
        update_last_conversation_time(phone)
        logger.info(f"Slack relay → WhatsApp ({role}): {phone}")
    except Exception as e:
        logger.error(f"Failed to relay Slack message to {role} {phone}: {e}")


async def _handle_concluir(user_id, state, slot_iso, thread_ts, donated_phone, received_phone):
    donated_email = state.get("donated_email")
    received_email = state.get("received_email")
    donated_name = (state.get("donated") or {}).get("name", "Mentor")
    received_name = (state.get("received") or {}).get("name", "Founder")
    meeting = state.get("meeting") or {}
    company = meeting.get("company", "")
    gcal_title = f"{company} × {donated_name}".strip(" ×") if company else f"Mentoria — {donated_name}"

    gcal_event_id = None
    if donated_email and received_email:
        try:
            gcal_service = get_gcal_service()
            gcal_event_id = gcal_service.create_meeting_invite(
                mentor_email=donated_email,
                founder_email=received_email,
                slot_datetime_iso=slot_iso,
                title=gcal_title,
            )
        except GCalCreationError as e:
            logger.error(f"GCal creation failed in Slack concluir: {e}")

    update_meeting_state(MeetingState.RECEIVED_CONFIRMED.value, user_id, selection=slot_iso)

    slot_display = format_slot(slot_iso)
    confirmation_msg = build_confirmation_message(donated_name, received_name, slot_display)

    for phone in {donated_phone, received_phone}:
        if phone:
            try:
                if needs_template(phone):
                    await whatsapp.send_template(phone, "hello_world")
                    await asyncio.sleep(2)
                await whatsapp.send_text_humanized(phone, confirmation_msg)
                update_last_conversation_time(phone)
            except Exception as e:
                logger.error(f"Failed to send confirmation to {phone}: {e}")

    logger.info(f"Slack /concluir processed: user_id={user_id}, slot={slot_iso}, gcal_event_id={gcal_event_id}")
```

### Relay WhatsApp → Slack em `task.py`

Adicionar no `case TextMessage` block, após o bloco que processa fluxo ativo. Quando status == `HUMAN_INTERVENTION_REQUIRED` e `slack_thread_ts` está setado, relay para o Slack:

```python
# Logo após o bloco "if current_status in active_states or current_status == "INIT":"
# Adicionar:

if current_status == MeetingState.HUMAN_INTERVENTION_REQUIRED.value:
    slack_thread_ts = state.get("slack_thread_ts")
    if slack_thread_ts:
        # Relay para Slack
        await _relay_to_slack(from_number, user_text, state, slack_thread_ts)
    return  # não processa mais
```

Adicionar função de relay:

```python
async def _relay_to_slack(from_number: str, text: str, state: dict, thread_ts: str):
    try:
        from slack_sdk import WebClient

        donated_phone = state.get("donated_phone")
        received_phone = state.get("received_phone")
        donated_name = (state.get("donated") or {}).get("name", "Mentor")
        received_name = (state.get("received") or {}).get("name", "Founder")

        if from_number == donated_phone or "+" + from_number == donated_phone:
            sender_label = f"[{donated_name} respondeu]"
        elif from_number == received_phone or "+" + from_number == received_phone:
            sender_label = f"[{received_name} respondeu]"
        else:
            sender_label = f"[{from_number} respondeu]"

        client = WebClient(token=settings.slack.BOT_TOKEN)
        client.chat_postMessage(
            channel=settings.slack.TAKEOVER_CHANNEL,
            thread_ts=thread_ts,
            text=f"{sender_label}: _{text}_",
        )
    except Exception as e:
        logger.error(f"Failed to relay WhatsApp message to Slack: {e}")
```

### Registrar router em `main.py`

```python
from src.api.v1.slack import router as slack_router

# No create_app():
app.include_router(slack_router)
```

---

## 16. Registro no `autodiscover_tasks`

O `timeout_task.py` precisa ser descoberto pelo Celery. Verificar se está coberto pelo `autodiscover_tasks(["src.tasks.whatsapp"])` — sim, pois o arquivo está dentro deste módulo. Não requer mudança adicional.

---

## 17. Ordem de Implementação e Checklist

### Fase 1 — Base (fazer antes de qualquer outra coisa)

```
[ ] Base 1: Corrigir typo INTERVITION em 4 arquivos
[ ] Base 2: Expandir MeetingContext + _EMPTY_STATE no Redis
[ ] Base 3: Adicionar config vars (EscalationSettings, GCalSettings, SlackSettings)
[ ] Base 4: Implementar handler WAITING_FOR_TEMPLATE_REPLY
[ ] Verificar: grep -r "INTERVITION" src/ → 0 resultados
[ ] Verificar: pytest passa
```

### Fase 2 — P0 (necessário para primeiro teste real)

```
[ ] F8: Validação email no trigger (extract_emails + save_emails + 422 no schedule.py)
[ ] F6: Fix EC-06 (mensagem contextual para mídia em fluxo ativo)
[ ] F1: GCalService (novo arquivo + integração em handlers.py)
[ ] F2: EscalationService (novo arquivo + _escalate helper + integração em handlers.py)
[ ] F4: RefusalDetectorAgent (novo agente + prompt no Langfuse + integração em handlers.py)
[ ] Verificar via Gradio:
    - Trigger sem email → 422
    - Áudio mid-flow → estado preservado, próximo texto processa
    - Happy path → GCal invite criado + ambos recebem confirmação
    - Resposta de recusa → HI + WhatsApp para AEE
```

### Fase 3 — P1 estabilidade

```
[ ] F5: Ambiguity Counter (update_clarification_count + reset + lógica nos handlers)
[ ] F7: Deduplicação por meeting_id (register_meeting_id + is_meeting_active + check no schedule.py)
[ ] F3: Celery Beat (timeout_task.py + beat_schedule no celery.py + follow-up message)
[ ] Verificar:
    - 2x resposta ambígua → HI na 3ª
    - Trigger duplicado → 409
    - NO_RESPONSE_TIMEOUT_SECONDS=30 no .env.test → follow-up após 30s, HI após 60s
```

### Fase 4 — P1 negociação e takeover

```
[ ] F9: CounterAvailabilityExtractorAgent + motor de negociação em handlers.py
[ ] F10: Slack endpoint + relay bidirecional + _relay_to_slack no task.py
[ ] Verificar:
    - Founder rejeita + oferece janela → mentor recebe contra-proposta
    - Founder rejeita sem alternativa → HI imediato
    - Escalada via Slack → thread criado + relay funciona nos dois sentidos
    - /concluir → GCal criado + ambos confirmados
```

---

## 18. Instrumentação P0 (antes do piloto)

Além das features acima, dois gaps de instrumentação precisam ser fechados antes do piloto para que a North Star metric (tempo trigger → GCal) seja mensurável:

**Gap 1 — Timestamp de trigger e de GCal invite:**
Em `schedule.py`, logar o timestamp do trigger:
```python
logger.info(f"METRIC trigger_start meeting_id={meeting_id} ts={datetime.now().isoformat()}")
```
Em `gcal_service.py`, após criação bem-sucedida:
```python
logger.info(f"METRIC gcal_created meeting_id={meeting_id} event_id={event_id} ts={datetime.now().isoformat()}")
```

**Gap 2 — Snapshot de estado antes do reset:**
Em `update_meeting_state` (`state_machine_service.py`), antes de `_save(user_id, dict(_EMPTY_STATE))`:
```python
if new_state in terminal_states:
    state_snapshot = dict(state)
    # Salvar snapshot para análise pós-piloto
    _redis.set(
        f"meeting_snapshot:{user_id}",
        json.dumps(state_snapshot, cls=_MongoEncoder),
        ex=60 * 60 * 24 * 7,  # 7 dias
    )
    _save(user_id, dict(_EMPTY_STATE))
    return {"status_updated_to": new_state, "final_state": state_snapshot}
```

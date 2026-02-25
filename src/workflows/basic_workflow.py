import json
import logging
from datetime import datetime
from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown
from src.agents.main.meeting_agents import (
  slot_extractor_agent,
  confirmation_extractor_agent,
)
from src.services.state_machine_service import (
  load_potential_meeting_into_state,
  get_current_meeting_state,
  update_meeting_state,
  record_interaction_time,
  check_timeout,
)

MEETING_ID = "6487339ae05308a6e921c993"
NO_RESPONSE_TIMEOUT_SECONDS = 30

logger = logging.getLogger(__name__)


def _format_meeting_date(iso_date: str) -> str:
  """Formats an ISO date string to a human-readable Portuguese format."""
  try:
    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    return dt.strftime("%d/%m/%Y às %H:%M")
  except Exception:
    return iso_date


def _build_slot_suggestions(iso_date: str) -> list[str]:
  """
  Builds three time slot suggestions relative to the base meeting_date:
  morning (09:00), afternoon (14:00), and evening (19:00) of the same day.
  """
  try:
    dt = datetime.fromisoformat(iso_date.replace("Z", "+00:00"))
    date_str = dt.strftime("%d/%m/%Y")
    return [
      f"1. Manhã   – {date_str} 09:00",
      f"2. Tarde   – {date_str} 14:00",
      f"3. Noite   – {date_str} 19:00",
    ]
  except Exception:
    return [
      "1. Manhã   – 09:00",
      "2. Tarde   – 14:00",
      "3. Noite   – 19:00",
    ]


def _parse_extracted(content, field: str, default=None):
  """
  Safely extracts a field from the LLM response content.
  Handles Pydantic models, dicts, and raw JSON strings.
  """
  logger.debug("[SlotExtractor] content type=%s, value=%r", type(content).__name__, content)

  # Case 1: Pydantic model
  if hasattr(content, field):
    return getattr(content, field, default)

  # Case 2: dict
  if isinstance(content, dict):
    return content.get(field, default)

  # Case 3: raw JSON string
  if isinstance(content, str):
    try:
      data = json.loads(content)
      return data.get(field, default)
    except (json.JSONDecodeError, AttributeError):
      pass

  return default


def create_content_workflow():
  setup()
  return Workflow(
    name="Meeting Orchestrator",
    steps=[slot_extractor_agent, confirmation_extractor_agent],
  )


def run_meeting_workflow_with_stream(message: str):
  # ── 1. Load meeting into state on first run ────────────────────────────
  state_dict = get_current_meeting_state()

  if state_dict.get("status") == "INIT" and not state_dict.get("meeting"):
    success = load_potential_meeting_into_state(MEETING_ID)
    if not success:
      yield "Nenhuma meeting com status 'Potential' foi encontrada no banco."
      return
    state_dict = get_current_meeting_state()

  # ── 2. Resolve common context ──────────────────────────────────────────
  current_status = state_dict.get("status", "INIT")

  donated_name = (
    state_dict.get("donated", {}).get("name", "Mentor")
    if state_dict.get("donated")
    else "Mentor"
  )
  received_name = (
    state_dict.get("received", {}).get("name", "Mentorado")
    if state_dict.get("received")
    else "Mentorado"
  )
  meeting_date_iso = (
    state_dict.get("meeting", {}).get("meeting_date", "")
    if state_dict.get("meeting")
    else ""
  )

  # ── 3. State machine ───────────────────────────────────────────────────

  # ── INIT: send welcome message and move to WAITING_DONATED_RESPONSE ────
  if current_status == "INIT":
    slots = _build_slot_suggestions(meeting_date_iso)
    date_display = (
      _format_meeting_date(meeting_date_iso) if meeting_date_iso else "em aberto"
    )
    update_meeting_state("WAITING_DONATED_RESPONSE")
    record_interaction_time()

    yield (
      f"Olá, {donated_name}! 👋\n\n"
      f"Temos uma reunião com {received_name} prevista para **{date_display}**.\n\n"
      f"Escolha um dos horários abaixo ou informe outro de sua preferência "
      f"(ex: *amanhã*, *dia 29*, *às 13:00*, *de manhã*):\n\n"
      + "\n".join(slots)
      + "\n\nCaso não queira agendar, basta digitar **cancelar**."
    )
    return

  # ── WAITING_DONATED_RESPONSE ───────────────────────────────────────────
  elif current_status == "WAITING_DONATED_RESPONSE":
    # Check for 30-second no-response timeout
    if check_timeout(NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("DONATED_NO_RESPONSE")
      update_meeting_state("HUMAN_INTERVITION_REQUIRED")
      yield (
        "⏰ O mentor não respondeu a tempo. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    # Ask LLM to extract the slot or detect rejection
    enriched = (
      f"Base meeting_date: {meeting_date_iso}. "
      f"Today's date: {datetime.now().isoformat()}. "
      f"User Input: {message}"
    )
    run_response = slot_extractor_agent.run(enriched)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)
    selected_slot = _parse_extracted(extracted, "selected_date_time", default=None)

    if is_rejected:
      update_meeting_state("DONATED_REJECTED_SLOTS")
      update_meeting_state("HUMAN_INTERVITION_REQUIRED")
      yield (
        "Entendido, o mentor optou por não agendar. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    if selected_slot:
      update_meeting_state("DONATED_SELECTED_SLOT", selection=selected_slot)
      update_meeting_state("WAITING_RECEIVED_RESPONSE")
      record_interaction_time()

      # Format the slot nicely for the confirmation message
      try:
        dt = datetime.fromisoformat(selected_slot.replace("Z", "+00:00"))
        slot_display = dt.strftime("%d/%m/%Y às %H:%M")
      except Exception:
        slot_display = selected_slot

      yield (
        f"Olá, {received_name}! 👋\n\n"
        f"O mentor {donated_name} sugeriu o seguinte horário para a reunião:\n\n"
        f"📅 **{slot_display}**\n\n"
        f"Você confirma? Responda **Sim** ou **Não**."
      )
      return

    # LLM could not extract a valid slot
    yield (
      "Não consegui identificar a data/horário informado. "
      "Poderia informar novamente? (ex: *dia 29*, *às 14h*, *amanhã de manhã*)"
    )
    return

  # ── WAITING_RECEIVED_RESPONSE ──────────────────────────────────────────
  elif current_status == "WAITING_RECEIVED_RESPONSE":
    if check_timeout(NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("RECEIVED_NO_RESPONSE")
      update_meeting_state("HUMAN_INTERVITION_REQUIRED")
      yield (
        "⏰ O mentorado não respondeu a tempo. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    run_response = confirmation_extractor_agent.run(message)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)

    if is_rejected:
      update_meeting_state("RECEIVED_REJECTED")
      update_meeting_state("HUMAN_INTERVITION_REQUIRED")
      yield (
        f"O mentorado {received_name} não aceitou o horário sugerido. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    # Confirmed – read selected_slot before state reset
    selected_slot = state_dict.get("selected_slot", "")
    try:
      dt = datetime.fromisoformat(selected_slot.replace("Z", "+00:00"))
      slot_display = dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
      slot_display = selected_slot or "o horário selecionado"

    update_meeting_state("RECEIVED_CONFIRMED")
    yield (
      f"✅ Reunião agendada com sucesso!\n\n"
      f"**{donated_name}** e **{received_name}** se encontrarão em "
      f"**{slot_display}**."
    )
    return

  # ── Terminal / unknown states ──────────────────────────────────────────
  elif current_status == "HUMAN_INTERVITION_REQUIRED":
    yield "Este atendimento já foi encerrado e encaminhado para intervenção humana."
    return

  elif current_status == "RECEIVED_CONFIRMED":
    yield "A reunião já foi confirmada. Nenhuma ação adicional é necessária."
    return

  else:
    yield f"Estado inesperado: `{current_status}`. Por favor, reinicie o fluxo."
    return


def shutdown_workflow():
  shutdown()

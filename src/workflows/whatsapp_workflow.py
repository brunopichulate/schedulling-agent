import json
import logging
from datetime import datetime
from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown, langfuse_client
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
  register_phone_numbers,
)

NO_RESPONSE_TIMEOUT_SECONDS = 30

logger = logging.getLogger(__name__)


def _format_meeting_date(value) -> str:
  """Formats a date (datetime object or ISO string) to humanized Portuguese."""
  _WEEKDAYS = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
  ]
  _MONTHS = [
    "",
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
  ]
  try:
    if isinstance(value, datetime):
      dt = value
    else:
      normalized = str(value).strip().replace(" ", "T").replace("Z", "+00:00")
      dt = datetime.fromisoformat(normalized)
    weekday = _WEEKDAYS[dt.weekday()]
    month = _MONTHS[dt.month]
    return (
      f"{weekday}, {dt.day} de {month} de {dt.year} às {dt.strftime('%H:%M')}"
    )
  except Exception:
    return str(value)


def _build_slot_suggestions(iso_date: str) -> list[str]:
  """
  Builds three time slot suggestions relative to the base meeting_date:
  morning (09:00), afternoon (14:00), and evening (19:00) of the same day.
  """
  try:
    if isinstance(iso_date, datetime):
      dt = iso_date
    else:
      normalized = (
        str(iso_date).strip().replace(" ", "T").replace("Z", "+00:00")
      )
      dt = datetime.fromisoformat(normalized)
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
  logger.debug(
    "[SlotExtractor] content type=%s, value=%r",
    type(content).__name__,
    content,
  )

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


def run_meeting_workflow_with_stream(
  message: str,
  user_id: str,
  meeting_id: str | None = None,
  donated_phone: str | None = None,
  received_phone: str | None = None,
):
  """
  Generator that drives the meeting scheduling workflow.
  Each yielded value is a tuple: (recipient_phone: str, message_text: str).
  """
  # ── 1. Load meeting into state on first run ────────────────────────────
  state_dict = get_current_meeting_state(user_id)

  if state_dict.get("status") == "INIT" and not state_dict.get("meeting"):
    if not meeting_id:
      yield (user_id, "Nenhuma meeting_id foi fornecida para iniciar o fluxo.")
      return
    success = load_potential_meeting_into_state(meeting_id, user_id)
    if not success:
      yield (user_id, "Nenhuma meeting com status 'Potential' foi encontrada no banco.")
      return
    # Register phone numbers so the workflow knows where to route messages
    if donated_phone and received_phone:
      register_phone_numbers(user_id, donated_phone, received_phone)
    state_dict = get_current_meeting_state(user_id)

  # ── 2. Resolve common context ──────────────────────────────────────────
  current_status = state_dict.get("status", "INIT")

  _donated_phone = state_dict.get("donated_phone") or user_id
  _received_phone = state_dict.get("received_phone") or user_id

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
      _format_meeting_date(meeting_date_iso)
      if meeting_date_iso
      else "em aberto"
    )
    update_meeting_state("WAITING_DONATED_RESPONSE", user_id)
    record_interaction_time(user_id)

    yield (
      _donated_phone,
      (
        f"Olá, {donated_name}! 👋\n\n"
        f"Temos uma reunião com {received_name} prevista para **{date_display}**.\n\n"
        f"Escolha um dos horários abaixo ou informe outro de sua preferência "
        f"(ex: *amanhã*, *dia 29*, *às 13:00*, *de manhã*):\n\n"
        + "\n".join(slots)
        + "\n\nCaso não queira agendar, basta dizer."
      ),
    )
    return

  # ── WAITING_DONATED_RESPONSE ───────────────────────────────────────────
  elif current_status == "WAITING_DONATED_RESPONSE":
    # Check for no-response timeout
    if check_timeout(user_id, NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("DONATED_NO_RESPONSE", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        _donated_phone,
        "⏰ O mentor não respondeu a tempo. O caso foi encaminhado para intervenção humana.",
      )
      return

    # Ask LLM to extract the slot or detect rejection
    enriched = (
      f"Base meeting_date: {meeting_date_iso}. "
      f"Today's date: {datetime.now().isoformat()}. "
      f"User Input: {message}"
    )
    langfuse = langfuse_client
    with langfuse.start_as_current_observation(
      as_type="span",
      name="meeting-workflow",
      user_id=user_id,
      session_id=user_id,
    ):
      run_response = slot_extractor_agent.run(enriched)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)
    selected_slot = _parse_extracted(
      extracted, "selected_date_time", default=None
    )

    if is_rejected:
      update_meeting_state("DONATED_REJECTED_SLOTS", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        _donated_phone,
        "Entendido, o mentor optou por não agendar. O caso foi encaminhado para intervenção humana.",
      )
      return

    if selected_slot:
      update_meeting_state(
        "DONATED_SELECTED_SLOT", user_id, selection=selected_slot
      )
      update_meeting_state("WAITING_RECEIVED_RESPONSE", user_id)
      record_interaction_time(user_id)

      # Format the slot nicely for the confirmation message
      try:
        dt = datetime.fromisoformat(selected_slot.replace("Z", "+00:00"))
        slot_display = dt.strftime("%d/%m/%Y às %H:%M")
      except Exception:
        slot_display = selected_slot

      yield (
        _received_phone,
        (
          f"Olá, {received_name}! 👋\n\n"
          f"O mentor {donated_name} sugeriu o seguinte horário para a reunião:\n\n"
          f"📅 **{slot_display}**\n\n"
          f"Você confirma? Responda **Sim** ou **Não**."
        ),
      )
      return

    # LLM could not extract a valid slot
    yield (
      _donated_phone,
      "Não consegui identificar a data/horário informado. Poderia informar novamente? (ex: *dia 29*, *às 14h*, *amanhã de manhã*)",
    )
    return

  # ── WAITING_RECEIVED_RESPONSE ──────────────────────────────────────────
  elif current_status == "WAITING_RECEIVED_RESPONSE":
    if check_timeout(user_id, NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("RECEIVED_NO_RESPONSE", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        _received_phone,
        "⏰ O mentorado não respondeu a tempo. O caso foi encaminhado para intervenção humana.",
      )
      return

    langfuse = langfuse_client
    with langfuse.start_as_current_observation(
      as_type="span",
      name="meeting-workflow",
      user_id=user_id,
      session_id=user_id,
    ):
      run_response = confirmation_extractor_agent.run(message)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)

    if is_rejected:
      update_meeting_state("RECEIVED_REJECTED", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        _received_phone,
        f"O mentorado {received_name} não aceitou o horário sugerido. O caso foi encaminhado para intervenção humana.",
      )
      return

    # Confirmed – read selected_slot before state reset
    selected_slot = state_dict.get("selected_slot", "")
    try:
      dt = datetime.fromisoformat(selected_slot.replace("Z", "+00:00"))
      slot_display = dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
      slot_display = selected_slot or "o horário selecionado"

    confirmation_msg = (
      f"✅ Reunião agendada com sucesso!\n\n"
      f"**{donated_name}** e **{received_name}** se encontrarão em "
      f"**{slot_display}**."
    )
    update_meeting_state("RECEIVED_CONFIRMED", user_id)
    yield (_donated_phone, confirmation_msg)
    # Only notify received separately if it's a different number
    if _received_phone != _donated_phone:
      yield (_received_phone, confirmation_msg)
    return

  # ── Terminal / unknown states ──────────────────────────────────────────
  elif current_status == "HUMAN_INTERVITION_REQUIRED":
    yield (user_id, "Este atendimento já foi encerrado e encaminhado para intervenção humana.")
    return

  elif current_status == "RECEIVED_CONFIRMED":
    yield (user_id, "A reunião já foi confirmada. Nenhuma ação adicional é necessária.")
    return

  else:
    yield (user_id, f"Estado inesperado: `{current_status}`. Por favor, reinicie o fluxo.")
    return


def shutdown_workflow():
  shutdown()

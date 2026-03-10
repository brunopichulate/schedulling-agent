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
GRADIO_USER_ID = "gradio_user"

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

  if hasattr(content, field):
    return getattr(content, field, default)

  if isinstance(content, dict):
    return content.get(field, default)

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
  user_id = GRADIO_USER_ID

  state_dict = get_current_meeting_state(user_id)

  if state_dict.get("status") == "INIT" and not state_dict.get("meeting"):
    success = load_potential_meeting_into_state(MEETING_ID, user_id)
    if not success:
      yield "Nenhuma meeting com status 'Potential' foi encontrada no banco."
      return
    state_dict = get_current_meeting_state(user_id)

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
      f"Olá, {donated_name}! 👋\n\n"
      f"Temos uma reunião com {received_name} prevista para **{date_display}**.\n\n"
      f"Para agendar, envie pelo menos 2 horários disponíveis para que possamos oferecer opções ao participante.\n\n"
      f"Escolha um dos horários abaixo ou informe outro de sua preferência "
      f"(ex: *amanhã*, *dia 29*, *às 13:00*, *de manhã*):\n\n"
      + "\n".join(slots)
      + "\n\nCaso não queira agendar, basta dizer."
    )
    return

  elif current_status == "WAITING_DONATED_RESPONSE":
    if check_timeout(user_id, NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("DONATED_NO_RESPONSE", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        "⏰ O mentor não respondeu a tempo. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    enriched = (
      f"Base meeting_date: {meeting_date_iso}. "
      f"Today's date: {datetime.now().isoformat()}. "
      f"User Input: {message}"
    )
    run_response = slot_extractor_agent.run(enriched)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)
    selected_slots = _parse_extracted(
      extracted, "selected_date_times", default=[]
    )

    if is_rejected:
      update_meeting_state("DONATED_REJECTED_SLOTS", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        "Entendido, o mentor optou por não agendar. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    if selected_slots and len(selected_slots) >= 2:
      update_meeting_state(
        "DONATED_SELECTED_SLOT", user_id, selection=selected_slots
      )
      update_meeting_state("WAITING_RECEIVED_RESPONSE", user_id)
      record_interaction_time(user_id)

      formatted_slots = []
      for idx, slot in enumerate(selected_slots, 1):
        try:
          dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
          slot_display = dt.strftime("%d/%m/%Y às %H:%M")
        except Exception:
          slot_display = slot
        formatted_slots.append(f"{idx}. {slot_display}")
      
      slots_text = "\n".join(formatted_slots)

      yield (
        f"Olá, {received_name}! 👋\n\n"
        f"O mentor {donated_name} sugeriu os seguintes horários para a reunião:\n\n"
        f"{slots_text}\n\n"
        f"Qual dessas opções você prefere? (Responda com o número da opção ou o horário, ou diga se não puder em nenhum)."
      )
      return

    if selected_slots and len(selected_slots) == 1:
      yield (
        "Por favor, forneça pelo menos duas opções de horário para o mentorado escolher (ex: *segunda às 14h* ou *terça às 10h*)."
      )
      return

    yield (
      "Não consegui identificar os horários informados. "
      "Poderia informar pelo menos duas opções de horários? (ex: *dia 29 às 14h* ou *amanhã de manhã*)"
    )
    return

  elif current_status == "WAITING_RECEIVED_RESPONSE":
    if check_timeout(user_id, NO_RESPONSE_TIMEOUT_SECONDS):
      update_meeting_state("RECEIVED_NO_RESPONSE", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        "⏰ O mentorado não respondeu a tempo. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    selected_slots = state_dict.get("selected_slot", [])
    
    # Provide the LLM with the numbered list of options so it can return purely the INT index
    enriched_msg = (
      f"User Response: {message}\n\n"
      f"Available Options ({len(selected_slots)}):\n"
    )
    for idx, slot in enumerate(selected_slots, 1):
      try:
        dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
        slot_display = dt.strftime("%d/%m/%Y às %H:%M")
      except Exception:
        slot_display = slot
      enriched_msg += f"Option {idx}: {slot_display}\n"

    run_response = confirmation_extractor_agent.run(enriched_msg)
    extracted = run_response.content

    is_rejected = _parse_extracted(extracted, "is_rejected", default=False)
    selected_option_index = _parse_extracted(extracted, "selected_option_index", default=None)

    if is_rejected:
      update_meeting_state("RECEIVED_REJECTED", user_id)
      update_meeting_state("HUMAN_INTERVITION_REQUIRED", user_id)
      yield (
        f"O mentorado {received_name} não aceitou os horários sugeridos. "
        "O caso foi encaminhado para intervenção humana."
      )
      return

    if not selected_option_index or not isinstance(selected_option_index, int) or selected_option_index < 1 or selected_option_index > len(selected_slots):
      yield (
        "Não consegui identificar qual opção você escolheu. Poderia responder visualmente com o número da opção (ex: 1 ou 2) ou confirmar o horário exato desejado?",
      )
      return

    # User gave us a valid index (1-based), fetch the exact ISO string
    selected_time = selected_slots[selected_option_index - 1]

    try:
      dt = datetime.fromisoformat(selected_time.replace("Z", "+00:00"))
      slot_display = dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
      slot_display = selected_time

    update_meeting_state("RECEIVED_CONFIRMED", user_id, selection=selected_time)
    yield (
      f"✅ Reunião agendada com sucesso!\n\n"
      f"**{donated_name}** e **{received_name}** se encontrarão em "
      f"**{slot_display}**."
    )
    return

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

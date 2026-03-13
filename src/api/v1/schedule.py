import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.whatsapp import whatsapp
from src.services.state_machine_service import (
  get_current_meeting_state,
  update_meeting_state,
  load_potential_meeting_into_state,
  register_phone_numbers,
)
from src.services.whatsapp_window_service import (
  needs_template,
  update_last_conversation_time,
)
from src.workflows.whatsapp_workflow import run_meeting_workflow_with_stream

router = APIRouter()
logger = logging.getLogger(__name__)

_TERMINAL_OR_IDLE_STATES = {
  "INIT",
  "RECEIVED_CONFIRMED",
  "HUMAN_INTERVITION_REQUIRED",
}


class ScheduleRequest(BaseModel):
  meeting_id: str
  donated_phone_number: str
  received_phone_number: str


@router.post("/schedule")
async def schedule_meeting(body: ScheduleRequest):
  meeting_id = body.meeting_id
  donated_phone = body.donated_phone_number
  received_phone = body.received_phone_number

  current_state = get_current_meeting_state(donated_phone)
  current_status = current_state.get("status", "INIT")

  is_active = current_status not in _TERMINAL_OR_IDLE_STATES or (
    current_status == "INIT" and current_state.get("meeting") is not None
  )

  if is_active:
    logger.warning(
      f"Schedule rejected: donated {donated_phone} already has an active "
      f"workflow (status={current_status})"
    )
    raise HTTPException(
      status_code=409,
      detail={
        "error": "active_workflow_exists",
        "message": f"There is already an active scheduling workflow for {donated_phone}.",
        "current_status": current_status,
      },
    )
  logger.info(
    f"Schedule triggered for meeting {meeting_id}: "
    f"donated={donated_phone}, received={received_phone}"
  )

  success = load_potential_meeting_into_state(meeting_id, donated_phone)
  if not success:
     raise HTTPException(status_code=404, detail="Meeting potential not found")
  
  register_phone_numbers(donated_phone, donated_phone, received_phone)

  if needs_template(donated_phone):
    logger.info(f"24h window expired for {donated_phone} — sending hello_world template and waiting for reply")
    update_meeting_state("WAITING_FOR_TEMPLATE_REPLY", donated_phone)
    await whatsapp.send_template(donated_phone, "hello_world")
    
    return {
      "status": "ok",
      "meeting_id": meeting_id,
      "message": "Template sent. Waiting for reply before starting workflow.",
      "donated_phone_number": donated_phone,
      "received_phone_number": received_phone,
    }

  # If window is open, run workflow normally
  for recipient, message_text in run_meeting_workflow_with_stream(
    message="",
    user_id=donated_phone,
    meeting_id=meeting_id,
    donated_phone=donated_phone,
    received_phone=received_phone,
  ):
    try:
      await whatsapp.send_text_humanized(recipient, message_text)
      update_last_conversation_time(recipient)
    except Exception as e:
      logger.error(f"Failed to send WhatsApp message to {recipient}: {e}")

  return {
    "status": "ok",
    "meeting_id": meeting_id,
    "donated_phone_number": donated_phone,
    "received_phone_number": received_phone,
  }

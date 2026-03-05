import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from src.services.whatsapp import whatsapp
from src.services.state_machine_service import get_current_meeting_state
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

  for recipient, message_text in run_meeting_workflow_with_stream(
    message="",
    user_id=donated_phone,
    meeting_id=meeting_id,
    donated_phone=donated_phone,
    received_phone=received_phone,
  ):
    try:
      await whatsapp.send_text_humanized(recipient, message_text)
    except Exception as e:
      logger.error(f"Failed to send WhatsApp message to {recipient}: {e}")

  return {
    "status": "ok",
    "meeting_id": meeting_id,
    "donated_phone_number": donated_phone,
    "received_phone_number": received_phone,
  }

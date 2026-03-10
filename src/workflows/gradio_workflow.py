import logging
from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown
from src.agents.main.meeting_agents import (
    slot_extractor_agent,
    confirmation_extractor_agent,
)
from src.services.state_machine_service import (
    load_potential_meeting_into_state,
    get_current_meeting_state,
)
from src.workflows.meeting_shared.models import MeetingContext, MeetingState
from src.workflows.meeting_shared.handlers import STATE_HANDLERS, handle_unexpected_state

MEETING_ID = "6487339ae05308a6e921c993"
GRADIO_USER_ID = "gradio_user"

logger = logging.getLogger(__name__)

def create_content_workflow():
    setup()
    return Workflow(
        name="Meeting Orchestrator",
        steps=[slot_extractor_agent, confirmation_extractor_agent],
    )

def run_meeting_workflow_with_stream(message: str):
    user_id = GRADIO_USER_ID

    state_dict = get_current_meeting_state(user_id)

    if (state_dict.get("status") == "INIT" or state_dict.get("status") is None) and not state_dict.get("meeting"):
        success = load_potential_meeting_into_state(MEETING_ID, user_id)
        if not success:
            yield "Nenhuma meeting com status 'Potential' foi encontrada no banco."
            return
        state_dict = get_current_meeting_state(user_id)

    status_str = state_dict.get("status", "INIT")
    
    try:
        current_status = MeetingState(status_str)
    except ValueError:
        current_status = status_str

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

    context = MeetingContext(
        user_id=user_id,
        donated_phone=_donated_phone,
        received_phone=_received_phone,
        donated_name=donated_name,
        received_name=received_name,
        meeting_date_iso=meeting_date_iso,
        state=current_status,
        state_dict=state_dict,
    )

    handler_key = current_status.value if isinstance(current_status, MeetingState) else current_status
    handler = STATE_HANDLERS.get(handler_key, handle_unexpected_state)

    for phone, text in handler(context, message, use_bold_asterisks=False):
        yield text

def shutdown_workflow():
    shutdown()

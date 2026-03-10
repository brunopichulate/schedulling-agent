import logging
from datetime import datetime
from typing import Generator, Tuple
from opentelemetry import trace as otel_trace
from langfuse import propagate_attributes

from src.agents.main.meeting_agents import (
    slot_extractor_agent,
    confirmation_extractor_agent,
)
from src.services.state_machine_service import (
    update_meeting_state,
    record_interaction_time,
    check_timeout,
)
from src.workflows.meeting_shared.models import MeetingState, MeetingContext
from src.workflows.meeting_shared.utils import (
    build_slot_suggestions,
    format_meeting_date,
    format_slot,
    parse_extracted,
)
from src.workflows.meeting_shared.messages import (
    build_initial_message,
    build_timeout_message,
    build_rejected_message,
    build_slot_selection_message,
    build_need_more_options_message,
    build_unrecognized_options_message,
    build_unrecognized_selection_message,
    build_confirmation_message,
    build_human_intervention_message,
    build_already_confirmed_message,
    build_unexpected_state_message,
)

logger = logging.getLogger(__name__)
NO_RESPONSE_TIMEOUT_SECONDS = 30

def handle_init(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    slots = build_slot_suggestions(context.meeting_date_iso)
    date_display = (
        format_meeting_date(context.meeting_date_iso)
        if context.meeting_date_iso
        else "em aberto"
    )
    update_meeting_state(MeetingState.WAITING_DONATED_RESPONSE.value, context.user_id)
    record_interaction_time(context.user_id)

    msg = build_initial_message(
        context.donated_name,
        context.received_name,
        date_display,
        slots,
        use_bold_asterisks
    )
    yield (context.donated_phone, msg)

def handle_waiting_donated(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    if check_timeout(context.user_id, NO_RESPONSE_TIMEOUT_SECONDS):
        update_meeting_state(MeetingState.DONATED_NO_RESPONSE.value, context.user_id)
        update_meeting_state(MeetingState.HUMAN_INTERVITION_REQUIRED.value, context.user_id)
        yield (context.donated_phone, build_timeout_message("donated"))
        return

    enriched = (
        f"Base meeting_date: {context.meeting_date_iso}. "
        f"Today's date: {datetime.now().isoformat()}. "
        f"User Input: {message}"
    )
    _tracer = otel_trace.get_tracer("meeting-workflow")
    with propagate_attributes(session_id=context.user_id, user_id=context.user_id):
        with _tracer.start_as_current_span("slot-extractor") as _span:
            _span.set_attribute("input.value", enriched)
            run_response = slot_extractor_agent.run(enriched)
            _span.set_attribute("output.value", str(run_response.content))
    extracted = run_response.content

    is_rejected = parse_extracted(extracted, "is_rejected", default=False)
    selected_slots = parse_extracted(extracted, "selected_date_times", default=[])

    if is_rejected:
        update_meeting_state(MeetingState.DONATED_REJECTED_SLOTS.value, context.user_id)
        update_meeting_state(MeetingState.HUMAN_INTERVITION_REQUIRED.value, context.user_id)
        yield (context.donated_phone, build_rejected_message("donated"))
        return

    if selected_slots and len(selected_slots) >= 2:
        update_meeting_state(MeetingState.DONATED_SELECTED_SLOT.value, context.user_id, selection=selected_slots)
        update_meeting_state(MeetingState.WAITING_RECEIVED_RESPONSE.value, context.user_id)
        record_interaction_time(context.user_id)

        formatted_slots = []
        for idx, slot in enumerate(selected_slots, 1):
            formatted_slots.append(f"{idx}. {format_slot(slot)}")
        
        slots_text = "\n".join(formatted_slots)

        yield (
            context.received_phone,
            build_slot_selection_message(context.received_name, context.donated_name, slots_text)
        )
        return

    if selected_slots and len(selected_slots) == 1:
        yield (context.donated_phone, build_need_more_options_message())
        return

    yield (context.donated_phone, build_unrecognized_options_message())

def handle_waiting_received(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    if check_timeout(context.user_id, NO_RESPONSE_TIMEOUT_SECONDS):
        update_meeting_state(MeetingState.RECEIVED_NO_RESPONSE.value, context.user_id)
        update_meeting_state(MeetingState.HUMAN_INTERVITION_REQUIRED.value, context.user_id)
        yield (context.received_phone, build_timeout_message("received"))
        return

    selected_slots = context.state_dict.get("selected_slot", [])
    
    enriched_msg = (
        f"User Response: {message}\n\n"
        f"Available Options ({len(selected_slots)}):\n"
    )
    for idx, slot in enumerate(selected_slots, 1):
        enriched_msg += f"Option {idx}: {format_slot(slot)}\n"

    _tracer = otel_trace.get_tracer("meeting-workflow")
    with propagate_attributes(session_id=context.user_id, user_id=context.user_id):
        with _tracer.start_as_current_span("confirmation-extractor") as _span:
            _span.set_attribute("input.value", enriched_msg)
            run_response = confirmation_extractor_agent.run(enriched_msg)
            _span.set_attribute("output.value", str(run_response.content))
    extracted = run_response.content

    is_rejected = parse_extracted(extracted, "is_rejected", default=False)
    selected_option_index = parse_extracted(extracted, "selected_option_index", default=None)

    if is_rejected:
        update_meeting_state(MeetingState.RECEIVED_REJECTED.value, context.user_id)
        update_meeting_state(MeetingState.HUMAN_INTERVITION_REQUIRED.value, context.user_id)
        yield (context.received_phone, build_rejected_message("received", context.received_name))
        return

    if not selected_option_index or not isinstance(selected_option_index, int) or selected_option_index < 1 or selected_option_index > len(selected_slots):
        yield (context.received_phone, build_unrecognized_selection_message())
        return

    selected_time = selected_slots[selected_option_index - 1]
    slot_display = format_slot(selected_time)

    update_meeting_state(MeetingState.RECEIVED_CONFIRMED.value, context.user_id, selection=selected_time)
    
    confirmation_msg = build_confirmation_message(
        context.donated_name, 
        context.received_name, 
        slot_display, 
        use_bold_asterisks
    )

    yield (context.donated_phone, confirmation_msg)
    if context.received_phone != context.donated_phone:
        yield (context.received_phone, confirmation_msg)

def handle_human_intervention_required(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    yield (context.user_id, build_human_intervention_message())

def handle_received_confirmed(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    yield (context.user_id, build_already_confirmed_message())

def handle_unexpected_state(context: MeetingContext, message: str, use_bold_asterisks: bool = True) -> Generator[Tuple[str, str], None, None]:
    yield (context.user_id, build_unexpected_state_message(context.state.value if isinstance(context.state, MeetingState) else context.state))

STATE_HANDLERS = {
    MeetingState.INIT.value: handle_init,
    MeetingState.WAITING_DONATED_RESPONSE.value: handle_waiting_donated,
    MeetingState.WAITING_RECEIVED_RESPONSE.value: handle_waiting_received,
    MeetingState.HUMAN_INTERVITION_REQUIRED.value: handle_human_intervention_required,
    MeetingState.RECEIVED_CONFIRMED.value: handle_received_confirmed,
}

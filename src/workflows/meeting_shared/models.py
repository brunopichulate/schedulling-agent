from enum import Enum
from dataclasses import dataclass

class MeetingState(str, Enum):
    INIT = "INIT"
    WAITING_FOR_TEMPLATE_REPLY = "WAITING_FOR_TEMPLATE_REPLY"
    WAITING_DONATED_RESPONSE = "WAITING_DONATED_RESPONSE"
    WAITING_RECEIVED_RESPONSE = "WAITING_RECEIVED_RESPONSE"
    DONATED_NO_RESPONSE = "DONATED_NO_RESPONSE"
    RECEIVED_NO_RESPONSE = "RECEIVED_NO_RESPONSE"
    DONATED_REJECTED_SLOTS = "DONATED_REJECTED_SLOTS"
    RECEIVED_REJECTED = "RECEIVED_REJECTED"
    HUMAN_INTERVITION_REQUIRED = "HUMAN_INTERVITION_REQUIRED"
    RECEIVED_CONFIRMED = "RECEIVED_CONFIRMED"
    DONATED_SELECTED_SLOT = "DONATED_SELECTED_SLOT"

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

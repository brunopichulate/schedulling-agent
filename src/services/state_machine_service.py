from datetime import datetime
from typing import Dict, Any, Optional

from src.services.meetings_service import get_meeting_by_id

# State keyed by user_id (phone number)
MEETING_STATES: Dict[str, Dict[str, Any]] = {}

VALID_STATES = [
  "INIT",
  "WAITING_DONATED_RESPONSE",
  "DONATED_REJECTED_SLOTS",
  "DONATED_NO_RESPONSE",
  "DONATED_SELECTED_SLOT",
  "WAITING_RECEIVED_RESPONSE",
  "RECEIVED_REJECTED",
  "RECEIVED_NO_RESPONSE",
  "RECEIVED_CONFIRMED",
  "HUMAN_INTERVITION_REQUIRED",
]


def _get_or_init_state(user_id: str) -> Dict[str, Any]:
  """Returns existing state for user_id, or initializes a fresh one."""
  if user_id not in MEETING_STATES:
    MEETING_STATES[user_id] = {
      "status": "INIT",
      "meeting": None,
      "donated": None,
      "received": None,
      "selected_slot": None,
      "last_interaction_time": None,
    }
  return MEETING_STATES[user_id]


def load_potential_meeting_into_state(meeting_id: str, user_id: str) -> bool:
  """
  Looks for a meeting by ID, extracts the attendees (Donated and Received),
  and initializes the meeting state for the given user.

  Returns:
      bool: True if the meeting was successfully loaded, False otherwise
  """
  state = _get_or_init_state(user_id)

  meeting = get_meeting_by_id(meeting_id)
  if not meeting:
    return False

  attendees = meeting.get("attendees", [])

  donated = next(
    (att for att in attendees if att.get("role") == "Donated"), None
  )
  received = next(
    (att for att in attendees if att.get("role") == "Received"), None
  )

  if not donated or not received:
    return False

  state["meeting"] = meeting
  state["donated"] = donated
  state["received"] = received

  return True


def record_interaction_time(user_id: str) -> None:
  """Records the current time as the last interaction time for a user."""
  state = _get_or_init_state(user_id)
  state["last_interaction_time"] = datetime.now()


def check_timeout(user_id: str, seconds: int = 30) -> bool:
  """
  Checks if the time elapsed since the last interaction exceeds the given threshold.

  Args:
      user_id: The user's phone number.
      seconds: The timeout threshold in seconds (default: 30).

  Returns:
      True if the timeout has been exceeded, False otherwise.
  """
  state = _get_or_init_state(user_id)
  last = state.get("last_interaction_time")
  if last is None:
    return False
  elapsed = (datetime.now() - last).total_seconds()
  return elapsed > seconds


def update_meeting_state(
  new_state: str, user_id: str, selection: Optional[str] = None
) -> Dict[str, Any]:
  """
  Transitions the meeting state to a new status for a given user.

  Valid states:
  INIT, WAITING_DONATED_RESPONSE, DONATED_REJECTED_SLOTS,
  DONATED_NO_RESPONSE, DONATED_SELECTED_SLOT, WAITING_RECEIVED_RESPONSE,
  RECEIVED_REJECTED, RECEIVED_NO_RESPONSE, RECEIVED_CONFIRMED,
  HUMAN_INTERVITION_REQUIRED

  Args:
      new_state: The state to transition to.
      user_id: The user's phone number.
      selection: The ISO date-time string of the selected slot (used in DONATED_SELECTED_SLOT).

  Returns:
      Dict with the updated state info.
  """
  state = _get_or_init_state(user_id)
  state["status"] = new_state

  if selection and new_state == "DONATED_SELECTED_SLOT":
    state["selected_slot"] = selection

  terminal_states = [
    "RECEIVED_CONFIRMED",
    "RECEIVED_REJECTED",
    "HUMAN_INTERVITION_REQUIRED",
  ]

  if new_state in terminal_states:
    state_snapshot = state.copy()

    # Reset state for this user after terminal state
    MEETING_STATES[user_id] = {
      "status": "INIT",
      "meeting": None,
      "donated": None,
      "received": None,
      "selected_slot": None,
      "last_interaction_time": None,
    }

    return {"status_updated_to": new_state, "final_state": state_snapshot}

  return {"status_updated_to": new_state, "current_state": state}


def get_current_meeting_state(user_id: str) -> Dict[str, Any]:
  """
  Retrieves the current state of the meeting workflow for a given user.

  Returns:
      Dict: A copy of the current state dict.
  """
  return _get_or_init_state(user_id).copy()

from datetime import datetime
from typing import Dict, Any, Optional
from src.services.meetings_service import get_meeting_by_id

MEETING_STATE: Dict[str, Any] = {
  "status": "INIT",
  "meeting": None,
  "donated": None,
  "received": None,
  "selected_slot": None,
  "last_interaction_time": None,
}

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


def load_potential_meeting_into_state(meeting_id: str) -> bool:
  """
  Looks for a meeting by ID, extracts the attendees (Donated and Received),
  and initializes the meeting state.

  Returns:
      bool: True if the meeting was successfully loaded, False otherwise
  """
  global MEETING_STATE

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

  MEETING_STATE["meeting"] = meeting
  MEETING_STATE["donated"] = donated
  MEETING_STATE["received"] = received

  return True


def record_interaction_time() -> None:
  """Records the current time as the last interaction time."""
  global MEETING_STATE
  MEETING_STATE["last_interaction_time"] = datetime.now()


def check_timeout(seconds: int = 30) -> bool:
  """
  Checks if the time elapsed since the last interaction exceeds the given threshold.

  Args:
      seconds: The timeout threshold in seconds (default: 30).

  Returns:
      True if the timeout has been exceeded, False otherwise.
  """
  last = MEETING_STATE.get("last_interaction_time")
  if last is None:
    return False
  elapsed = (datetime.now() - last).total_seconds()
  return elapsed > seconds


def update_meeting_state(
  new_state: str, selection: Optional[str] = None
) -> Dict[str, Any]:
  """
  Transitions the global meeting state to a new status.

  Valid states:
  INIT, WAITING_DONATED_RESPONSE, DONATED_REJECTED_SLOTS,
  DONATED_NO_RESPONSE, DONATED_SELECTED_SLOT, WAITING_RECEIVED_RESPONSE,
  RECEIVED_REJECTED, RECEIVED_NO_RESPONSE, RECEIVED_CONFIRMED,
  HUMAN_INTERVITION_REQUIRED

  Args:
      new_state: The state to transition to.
      selection: The ISO date-time string of the selected slot (used in DONATED_SELECTED_SLOT).

  Returns:
      Dict with the updated state info.
  """
  global MEETING_STATE
  MEETING_STATE["status"] = new_state

  if selection and new_state == "DONATED_SELECTED_SLOT":
    MEETING_STATE["selected_slot"] = selection

  terminal_states = [
    "RECEIVED_CONFIRMED",
    "RECEIVED_REJECTED",
    "HUMAN_INTERVITION_REQUIRED",
  ]

  if new_state in terminal_states:
    state_snapshot = MEETING_STATE.copy()

    # Reset state for the next conversation
    MEETING_STATE.clear()
    MEETING_STATE.update(
      {
        "status": "INIT",
        "meeting": None,
        "donated": None,
        "received": None,
        "selected_slot": None,
        "last_interaction_time": None,
      }
    )

    return {"status_updated_to": new_state, "final_state": state_snapshot}

  return {"status_updated_to": new_state, "current_state": MEETING_STATE}


def get_current_meeting_state() -> Dict[str, Any]:
  """
  Retrieves the current state of the meeting workflow.

  Returns:
      Dict: A copy of the current state dict.
  """
  return MEETING_STATE.copy()

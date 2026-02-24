import json
from src.services.mentor_service import find_potential_meetings

MEETING_STATE = {
  "status": "INIT",
  "meeting": None,
  "donated": None,
  "received": None,
  "selected_slot": None,
}

def check_potential_meetings_tool() -> str:
  """
  Looks for a meeting in 'Potential' status, extracts the attendees (Donated and Received),
  and initializes the meeting state. This should be called when the workflow status is INIT.

  Returns:
      str: A JSON string containing the meeting details or an error message if not found.
  """
  global MEETING_STATE

  meeting = find_potential_meetings()
  if not meeting:
    return json.dumps({"error": "No meetings with 'Potential' status found."})

  attendees = meeting.get("attendees", [])

  donated = next(
    (att for att in attendees if att.get("role") == "Donated"), None
  )
  received = next(
    (att for att in attendees if att.get("role") == "Received"), None
  )

  if not donated or not received:
    return json.dumps(
      {
        "error": "Found a meeting, but it is missing Donated or Received roles."
      }
    )

  MEETING_STATE["meeting"] = meeting
  MEETING_STATE["donated"] = donated
  MEETING_STATE["received"] = received

  return json.dumps(
    {"success": True, "meeting": {"donated": donated, "received": received}},
    default=str,
  )


def update_meeting_state_tool(new_state: str, selection: str = None) -> str:
  """
  Updates the global/shared state of the meeting workflow.
  Valid states are:
  INIT -> GENERATING_DONATED_SLOTS -> WAITING_DONATED_RESPONSE ->
  DONATED_SELECTED_SLOT -> CONTACTING_RECEIVED -> WAITING_RECEIVED_RESPONSE ->
  RECEIVED_CONFIRMED (or RECEIVED_REJECTED)

  Args:
      new_state (str): The state to transition to.
      selection (str, optional): The time slot selected or the confirmation response.

  Returns:
      str: Confirmation that the state transitioned, and any relevant state dumps.
  """
  global MEETING_STATE
  MEETING_STATE["status"] = new_state

  if selection and new_state == "DONATED_SELECTED_SLOT":
    MEETING_STATE["selected_slot"] = selection

  if new_state in ["RECEIVED_CONFIRMED", "RECEIVED_REJECTED"]:
    # We can clear state after completion
    state_snapshot = MEETING_STATE.copy()
    MEETING_STATE = {
      "status": "INIT",
      "meeting": None,
      "donated": None,
      "received": None,
      "selected_slot": None,
    }
    return json.dumps(
      {"status_updated_to": new_state, "final_state": state_snapshot},
      default=str,
    )

  return json.dumps(
    {"status_updated_to": new_state, "current_state": MEETING_STATE},
    default=str,
  )


def get_current_meeting_state_tool() -> str:
  """
  Retrieves the current state of the meeting workflow so the agent knows what to do next.

  Returns:
      str: A JSON string with the current state.
  """
  state_payload = MEETING_STATE.copy()
  return json.dumps(state_payload, default=str)

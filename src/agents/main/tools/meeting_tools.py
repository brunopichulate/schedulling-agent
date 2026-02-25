import json
from src.services.state_machine_service import (
  update_meeting_state,
  get_current_meeting_state,
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
  result = update_meeting_state(new_state, selection)
  return json.dumps(result, default=str)


def get_current_meeting_state_tool() -> str:
  """
  Retrieves the current state of the meeting workflow so the agent knows what to do next.

  Returns:
      str: A JSON string with the current state.
  """
  state_payload = get_current_meeting_state()
  return json.dumps(state_payload, default=str)

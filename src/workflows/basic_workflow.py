from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown
from src.agents.main.my_agents import meeting_orchestrator, get_instructions_for_state
import json
from src.agents.main.tools.meeting_tools import (
  get_current_meeting_state_tool,
  load_potential_meeting_into_state,
)


def create_content_workflow():
  setup()

  return Workflow(name="Content Creation", steps=[meeting_orchestrator])


def run_meeting_workflow_with_stream(message: str):
  state_payload = get_current_meeting_state_tool()
  state_dict = json.loads(state_payload)

  if state_dict.get("status") == "INIT" and not state_dict.get("meeting"):
    success = load_potential_meeting_into_state()
    if not success:
      yield "Nenhuma meeting potencial encontrada no momento."
      return
    state_payload = get_current_meeting_state_tool()
    state_dict = json.loads(state_payload)

  # Set only the instructions relevant to the current state
  current_status = state_dict.get("status", "INIT")
  meeting_orchestrator.instructions = get_instructions_for_state(current_status)

  enriched_message = f"State: {state_payload}\\nUser Input: {message}"

  for event in meeting_orchestrator.run(enriched_message, stream=True):
    if hasattr(event, "content") and event.content:
      yield event.content


def shutdown_workflow():
  shutdown()

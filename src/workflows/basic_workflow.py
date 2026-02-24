from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown
from src.agents.main.my_agents import meeting_orchestrator
from src.agents.main.tools.meeting_tools import get_current_meeting_state_tool


def create_content_workflow():
  setup()

  return Workflow(name="Content Creation", steps=[meeting_orchestrator])


def run_meeting_workflow_with_stream(message: str):
  state_payload = get_current_meeting_state_tool()
  enriched_message = f"State: {state_payload}\\nUser Input: {message}"

  for event in meeting_orchestrator.run(enriched_message, stream=True):
    if hasattr(event, "content") and event.content:
      yield event.content


def shutdown_workflow():
  shutdown()

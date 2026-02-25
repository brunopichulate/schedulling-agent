from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from .tools.meeting_tools import (
  update_meeting_state_tool,
)

BASE_INSTRUCTION = (
  "You are an AI Orchestrator responsible for a meeting state-machine. "
  "DO NOT be conversational. Trust the user's input. "
  "Do NOT ask them to confirm their choice. "
  "Look inside 'donated' and 'received' objects in the State to find their 'name'."
)

STATE_INSTRUCTIONS = {
  "INIT": (
    "Call `update_meeting_state_tool(new_state='WAITING_DONATED_RESPONSE')`. "
    "Then output EXACTLY this text replacing bracketed variables with info from State: "
    "'Olá [donated_name], escolha um horário:\\n1. Manhã - 09:00\\n2. Tarde - 14:00\\n3. Noite - 19:00'. "
    "STOP and wait for the user."
  ),
  "WAITING_DONATED_RESPONSE": (
    "The user's input IS the selection. Map their choice to a full slot string. "
    "First, call `update_meeting_state_tool(new_state='DONATED_SELECTED_SLOT', selection=mapped_slot)`. "
    "Second, call `update_meeting_state_tool(new_state='WAITING_RECEIVED_RESPONSE')`. "
    "Third, output EXACTLY this text replacing bracketed variables: "
    "'Olá [received_name], o mentor [donated_name] sugeriu o horário: [selected_slot]. Você aceita? (Sim/Não)'. "
    "STOP and wait for the NEXT user message."
  ),
  "WAITING_RECEIVED_RESPONSE": (
    "The user's input is their Yes/No. "
    "If Yes/Sim, call `update_meeting_state_tool(new_state='RECEIVED_CONFIRMED')` "
    "and output EXACTLY: 'Meeting agendada com sucesso com o mentor [donated_name] as [selected_slot].'. "
    "If No/Não, call `update_meeting_state_tool(new_state='RECEIVED_REJECTED')` "
    "and output EXACTLY: 'Meeting não aceita pelo mentorado. O fluxo foi encerrado.'. STOP."
  ),
}


def get_instructions_for_state(status: str) -> list[str]:
  """Returns only the instructions relevant to the current state."""
  state_instruction = STATE_INSTRUCTIONS.get(status, "")
  return [BASE_INSTRUCTION, state_instruction] if state_instruction else [BASE_INSTRUCTION]


meeting_orchestrator = Agent(
  name="MeetingOrchestrator",
  model=OpenAIChat(
    id="gpt-4o-mini", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  tools=[update_meeting_state_tool],
  markdown=False,
  add_history_to_context=False,
)

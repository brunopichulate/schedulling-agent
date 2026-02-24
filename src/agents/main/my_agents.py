from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from .tools.meeting_tools import (
  check_potential_meetings_tool,
  update_meeting_state_tool,
)

meeting_orchestrator = Agent(
  name="MeetingOrchestrator",
  instructions=[
    "You are an AI Orchestrator responsible for a state-machine. DO NOT be conversational.",
    "The current state will be provided in the user's message as 'State: ...'. Use it to determine your next action.",
    "If status == 'INIT': Call `check_potential_meetings_tool`. Then call `update_meeting_state_tool(new_state='WAITING_DONATED_RESPONSE')`. Finally, output EXACTLY this text replacing variables with state info: 'Olá {donated_name}, escolha um horário:\\n1. Manhã - 09:00\\n2. Tarde - 14:00\\n3. Noite - 19:00'. STOP and wait for the user.",
    "If status == 'WAITING_DONATED_RESPONSE': The user's input IS the selection. Map their choice to the full slot string based on available hints. First, call `update_meeting_state_tool(new_state='DONATED_SELECTED_SLOT', selection=mapped_slot)`. Second, call `update_meeting_state_tool(new_state='WAITING_RECEIVED_RESPONSE')`. Third, output EXACTLY this text: 'Olá {received_name}, o mentor {donated_name} sugeriu o horário: {selected_slot}. Você aceita? (Sim/Não)'. STOP and wait for the NEXT user message.",
    "If status == 'WAITING_RECEIVED_RESPONSE': The user's input is their Yes/No. If Yes/Sim, call `update_meeting_state_tool(new_state='RECEIVED_CONFIRMED')` and output EXACTLY: 'Meeting agendada com sucesso com o mentor {donated_name} as {selected_slot}.'. If No/Não, call `update_meeting_state_tool(new_state='RECEIVED_REJECTED')` and output EXACTLY: 'Meeting não aceita pelo mentorado. O fluxo foi encerrado.'. STOP.",
    "CRITICAL: Trust the user's input. Do NOT ask them to confirm their choice. Never wrap output in ```.",
  ],
  model=OpenAIChat(
    id="gpt-4o-mini", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  tools=[check_potential_meetings_tool, update_meeting_state_tool],
  markdown=True,
  add_history_to_context=True,
)

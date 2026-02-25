from pydantic import BaseModel, Field
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings


class ExtractedSlot(BaseModel):
  is_rejected: bool = Field(
    description="True if the user rejected the suggestions, False otherwise."
  )
  selected_date_time: Optional[str] = Field(
    default=None,
    description="The selected date and time in ISO format (YYYY-MM-DDTHH:MM:SS.000+00:00). Null if rejected.",
  )


class ExtractedConfirmation(BaseModel):
  is_rejected: bool = Field(
    description="True if the user rejected or said 'no', False if they confirmed/said 'yes'."
  )


slot_extractor_agent = Agent(
  name="SlotExtractorAgent",
  model=OpenAIChat(
    id="gpt-4o-mini", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  output_schema=ExtractedSlot,
  instructions=[
    "Você é um assistente que analisa a INTENÇÃO do usuário em português do Brasil (com ou sem acentos, linguagem informal).",
    "Existem apenas dois tipos de intenção possíveis:",
    "",
    "INTENÇÃO: AGENDAR — o usuário quer marcar um horário. Exemplos de pistas:",
    "  - Mencionou um número de 1 a 3 (opções do menu: 1=09:00, 2=14:00, 3=19:00)",
    "  - Mencionou um horário (ex: '19h', '17:00', 'as 19:00', 'às 9h', 'de manhã', 'à tarde')",
    "  - Mencionou um dia ou data (ex: 'dia 29', 'amanhã', '29/06', '29/06/2023')",
    "  - Qualquer combinação de data e/ou hora",
    "  → Nesse caso: is_rejected=False. Extraia/construa selected_date_time em YYYY-MM-DDTHH:MM:SS.000+00:00.",
    "    - Se o usuário deu data+hora completas, use-as exatamente.",
    "    - Se deu só hora, use a data do base meeting_date.",
    "    - Se escolheu opção 1/2/3, use a data do base meeting_date com 09:00/14:00/19:00.",
    "    - Se deu referência relativa (amanhã, dia 29), complete com o base meeting_date como referência.",
    "",
    "INTENÇÃO: RECUSAR — o usuário não quer agendar. Exemplos de pistas:",
    "  - Respostas negativas como 'não', 'nao', 'n', 'nope', 'cancelar', 'desisto', 'não quero', 'nao quero'",
    "  - Qualquer mensagem de recusa sem mencionar data ou horário",
    "  → Nesse caso: is_rejected=True, selected_date_time=null.",
    "",
    "Se a intenção for ambígua e não houver data/hora detectável e não for recusa clara, retorne is_rejected=False e selected_date_time=null.",
  ],
  markdown=False,
  add_history_to_context=False,
)

confirmation_extractor_agent = Agent(
  name="ConfirmationExtractorAgent",
  model=OpenAIChat(
    id="gpt-4o-mini", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  output_schema=ExtractedConfirmation,
  instructions=[
    "You are an AI assistant that extracts a simple confirmation from a user's message.",
    "If the user says 'yes', 'sim', 'ok', 'aceito', etc., set is_rejected to False.",
    "If the user says 'no', 'não', 'recusar', 'cancelar', etc., set is_rejected to True.",
  ],
  markdown=False,
  add_history_to_context=False,
)

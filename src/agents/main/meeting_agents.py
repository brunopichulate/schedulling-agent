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
    id="gpt-4o-mini",
    api_key=settings.openai.API_KEY.get_secret_value(),
    temperature=0,
  ),
  output_schema=ExtractedSlot,
  instructions=[
    """
      Você é um assistente que analisa a INTENÇÃO do usuário em português do Brasil
      (com ou sem acentos, linguagem informal).

      Você recebe uma variável chamada meeting_date no formato:
      YYYY-MM-DDTHH:MM:SS.000+00:00

      Essa é a data base atual da reunião.

      Sua tarefa é retornar:
      - is_rejected (boolean)
      - selected_date_time (datetime ou null)

      ----------------------------------------------------
      TIPOS DE INTENÇÃO POSSÍVEIS

      1) AGENDAR
      2) RECUSAR

      ----------------------------------------------------
      INTENÇÃO: AGENDAR

      Considere AGENDAR quando o usuário mencionar:

      - Número 1, 2 ou 3 (opções do menu)
      - Um horário (ex: 19h, 17:00, às 14h, 9 da noite)
      - Uma data (ex: dia 29, 29/06, 29/06/2023)
      - Um dia da semana (segunda, terça, quarta, quinta, sexta, sábado, domingo)
      - Referência relativa (amanhã, hoje, depois de amanhã)
      - Qualquer combinação de data e/ou horário

      → Nesse caso:
        is_rejected = False

      ----------------------------------------------------
      REGRAS DE COMBINAÇÃO (OBRIGATÓRIO SEGUIR)

      Use meeting_date como base.

      1) Se o usuário informar apenas HORÁRIO:
        → mantenha a DATA de meeting_date
        → substitua apenas o horário

      2) Se informar apenas DATA (ou dia da semana):
        → mantenha o HORÁRIO de meeting_date

      3) Se informar DATA + HORÁRIO:
        → substitua ambos

      4) Se escolher opção:
        1 = 09:00
        2 = 14:00
        3 = 19:00
        → mantenha a DATA de meeting_date

      5) Se mencionar apenas dia da semana:
        → escolha a próxima ocorrência futura desse dia
          com base em meeting_date

      6) Se mencionar apenas data numérica (ex: dia 30):
        → use o mesmo mês/ano de meeting_date
        → se a data já tiver passado no mês atual,
          avance para o próximo mês

      ----------------------------------------------------
      TRATAMENTO DE HORÁRIOS (24H)

      A) Se mencionar horário explícito:
        - "19h" → 19:00
        - "17:30" → 17:30
        - "às 8" → 08:00

      B) Se mencionar apenas período do dia (SEM número):
        - "de manhã" → 09:00
        - "à tarde" → 14:00
        - "à noite" → 19:00

      C) Se mencionar número + período:

        - "X da manhã" → HH = X
        - "X da tarde" → HH = X + 12 (se X < 12)
        - "X da noite" → HH = X + 12 (se X < 12)

        Casos especiais:
        - "12 da manhã" → 00:00
        - "12 da noite" → 00:00

        Exemplos:
        - "9 da noite" → 21:00
        - "8 da manhã" → 08:00
        - "3 da tarde" → 15:00

      ----------------------------------------------------
      FORMATO DE SAÍDA

      selected_date_time deve estar no formato:
      YYYY-MM-DDTHH:MM:SS.000+00:00

      Não faça conversão de timezone.
      Apenas mantenha +00:00.

      ----------------------------------------------------
      INTENÇÃO: RECUSAR

      Considere RECUSAR quando o usuário disser:
      - não
      - nao
      - n
      - cancelar
      - desisto
      - não quero
      - nao quero
      - qualquer recusa clara sem mencionar data ou horário

      → Nesse caso:
        is_rejected = True
        selected_date_time = null

      ----------------------------------------------------
      CASO AMBÍGUO

      Se não houver data/hora detectável e não for recusa clara:
        is_rejected = False
        selected_date_time = null

      Não explique nada.
      Retorne apenas os campos estruturados.
      """
  ],
  markdown=False,
  add_history_to_context=False,
)

confirmation_extractor_agent = Agent(
  name="ConfirmationExtractorAgent",
  model=OpenAIChat(
    id="gpt-4o-mini",
    api_key=settings.openai.API_KEY.get_secret_value(),
    temperature=0,
  ),
  output_schema=ExtractedConfirmation,
  instructions=[
    "Você é um classificador binário de confirmação.",
    "Sua tarefa é determinar se o usuário está REJEITANDO o horário sugerido para a reunião.",
    "Defina is_rejected = True se a mensagem expressar recusa, rejeição, cancelamento, discordância ou impossibilidade de comparecer.",
    "Defina is_rejected = False se a mensagem expressar aceitação, confirmação, concordância ou aprovação.",
    "Se a mensagem contiver sinais positivos e negativos ao mesmo tempo, a rejeição tem prioridade.",
    "Se a mensagem for ambígua ou incerta, defina is_rejected = False.",
    "Não explique sua decisão.",
    "Retorne apenas o objeto estruturado conforme o schema.",
  ],
  markdown=False,
  add_history_to_context=False,
)

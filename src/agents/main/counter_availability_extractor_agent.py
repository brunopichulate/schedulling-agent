import logging
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from src.core.langfuse import get_prompt

logger = logging.getLogger(__name__)

_FALLBACK_PROMPT = """Você extrai disponibilidade quando um participante rejeita horários propostos e oferece alternativas.

has_counter_proposal=true quando o usuário sugere janelas de disponibilidade próprias:
- "não posso nesses dias, mas posso segunda ou quarta de tarde"
- "esses horários não funcionam, tenho disponibilidade só sextas"
- "prefiro de manhã, pode ser terça ou quinta"
- "só consigo na semana que vem, de preferência manhã"
- "pode ser segunda às 10h ou quarta às 15h"

has_counter_proposal=false quando rejeita sem alternativa:
- "não posso em nenhum desses"
- "infelizmente esses horários não servem"
- "não tenho disponibilidade"
- "quero cancelar"
- "não consigo"

Extraia as janelas como o usuário as descreveu, em português, sem converter para ISO datetime.
Retorne JSON com has_counter_proposal e available_windows."""


class ExtractedAvailability(BaseModel):
    has_counter_proposal: bool = Field(
        description="True se o usuário propõe janelas de disponibilidade próprias."
    )
    available_windows: list[str] = Field(
        default_factory=list,
        description="Janelas em linguagem natural. Ex: ['segunda 14h-16h', 'sexta manhã']",
    )


try:
    _prompt_obj = get_prompt(prompt_name="counter_availability_extractor_agent_prompt")
    _instructions = [_prompt_obj.prompt]
except Exception:
    logger.warning(
        "Langfuse prompt 'counter_availability_extractor_agent_prompt' not found. Using fallback."
    )
    _instructions = [_FALLBACK_PROMPT]

counter_availability_extractor_agent = Agent(
    name="CounterAvailabilityExtractorAgent",
    model=OpenAIChat(
        id="gpt-4o-mini",
        api_key=settings.openai.API_KEY.get_secret_value(),
        temperature=0,
    ),
    output_schema=ExtractedAvailability,
    instructions=_instructions,
    markdown=False,
    add_history_to_context=False,
)

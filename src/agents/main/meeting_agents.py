from pydantic import BaseModel, Field
from typing import Optional
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from src.core.langfuse import get_prompt


class ExtractedSlot(BaseModel):
  is_rejected: bool = Field(
    description="True if the user rejected the suggestions, False otherwise."
  )
  selected_date_times: list[str] = Field(
    default_factory=list,
    description="The selected dates and times in ISO format (YYYY-MM-DDTHH:MM:SS.000+00:00). Empty if rejected or if less than 2 options were provided.",
  )


class ExtractedConfirmation(BaseModel):
  is_rejected: bool = Field(
    description="True if the user rejected or said 'no', False if they confirmed/said 'yes'."
  )
  selected_option_index: Optional[int] = Field(
    default=None,
    description="The integer index (1, 2, 3...) of the option chosen by the user. Null if rejected."
  )


_slot_extractor_prompt = get_prompt(prompt_name="slot_extractor_agent_prompt")

slot_extractor_agent = Agent(
  name="SlotExtractorAgent",
  model=OpenAIChat(
    id="gpt-4o-mini",
    api_key=settings.openai.API_KEY.get_secret_value(),
    temperature=0,
  ),
  output_schema=ExtractedSlot,
  instructions=[_slot_extractor_prompt.prompt],
  markdown=False,
  add_history_to_context=False,
)

_confirmation_extractor_prompt = get_prompt(
  prompt_name="confirmation_extractor_agent_prompt"
)

confirmation_extractor_agent = Agent(
  name="ConfirmationExtractorAgent",
  model=OpenAIChat(
    id="gpt-4o-mini",
    api_key=settings.openai.API_KEY.get_secret_value(),
    temperature=0,
  ),
  output_schema=ExtractedConfirmation,
  instructions=[_confirmation_extractor_prompt.prompt],
  markdown=False,
  add_history_to_context=False,
)

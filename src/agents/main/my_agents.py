from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from .tools.mentor_tools import search_mentor_tool


researcher = Agent(
  name="MentorAssistant",
  role="You are a professional assistant specialized in providing concise information about mentors stored in the system database.",
  model=OpenAIChat(
    id="gpt-4o", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  tools=[search_mentor_tool],
  markdown=True,
)

writer = Agent(
  name="Writer",
  role="Write a clear, engaging article based on the research",
  model=OpenAIChat(
    id="gpt-4o", api_key=settings.openai.API_KEY.get_secret_value()
  ),
  markdown=True,
)

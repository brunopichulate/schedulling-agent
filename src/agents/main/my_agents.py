from agno.agent import Agent
from agno.models.openai import OpenAIChat
from src.core.config import settings
from .tools.test_tool import count_words


researcher = Agent(
    name="Researcher",
    role="Find relevant information about the topic",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=settings.openai.API_KEY.get_secret_value()
    ),
    tools=[count_words],
    markdown=True,
)

writer = Agent(
    name="Writer",
    role="Write a clear, engaging article based on the research",
    model=OpenAIChat(
        id="gpt-4o",
        api_key=settings.openai.API_KEY.get_secret_value()
    ),
    markdown=True,
)

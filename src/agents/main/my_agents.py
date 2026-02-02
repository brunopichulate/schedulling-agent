from agno.agent import Agent
from agno.models.openai import OpenAIChat
from .tools.test_tool import count_words

researcher = Agent(
    name="Researcher",
    role="Find relevant information about the topic",
    model=OpenAIChat(id="gpt-4o"),
    tools=[count_words],
    markdown=True,
)

writer = Agent(
    name="Writer",
    role="Write a clear, engaging article based on the research",
    model=OpenAIChat(id="gpt-4o"),
    markdown=True,
)

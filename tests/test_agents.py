from src.agents.main.my_agents import researcher, writer


def test_researcher_agent_initialization():
  assert researcher.name == "Researcher"
  assert researcher.role == "Find relevant information about the topic"
  assert researcher.markdown is True


def test_writer_agent_initialization():
  assert writer.name == "Writer"
  assert writer.role == "Write a clear, engaging article based on the research"
  assert writer.markdown is True

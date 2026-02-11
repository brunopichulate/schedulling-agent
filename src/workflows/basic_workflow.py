from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown, get_prompt
from src.core.config import settings
from src.agents.main.my_agents import researcher, writer


def apply_agent_prompts():
  researcher_prompt = get_prompt(
    prompt_name=settings.prompt.RESEARCHER.NAME,
    prompt_label=settings.prompt.RESEARCHER.LABEL,
  )
  if researcher_prompt:
    researcher.instructions = researcher_prompt.compile()

  writer_prompt = get_prompt(
    prompt_name=settings.prompt.WRITER.NAME,
    prompt_label=settings.prompt.WRITER.LABEL,
  )
  if writer_prompt:
    writer.instructions = writer_prompt.compile()


def create_content_workflow():
  setup()
  apply_agent_prompts()

  return Workflow(name="Content Creation", steps=[researcher, writer])


def run_workflow_with_stream(topic: str):
  # Use the Unified/Researcher agent directly
  for event in researcher.run(topic, stream=True):
      if hasattr(event, "content") and event.content:
          yield event.content


def shutdown_workflow():
  shutdown()

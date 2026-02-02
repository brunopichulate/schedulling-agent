from agno.workflow import Workflow
from src.core.langfuse import setup, shutdown, get_prompt

setup()

from src.agents.main.my_agents import researcher, writer

try:
    researcher_prompt = get_prompt(prompt_name="researcher-instructions")
    if researcher_prompt:
        researcher.instructions = researcher_prompt.compile()
except Exception:
    pass

content_workflow = Workflow(
    name="Content Creation",
    steps=[researcher, writer]
)

if __name__ == "__main__":
    try:
        content_workflow.print_response("Research the benefits of exercise and write a short article about it.", stream=True)
    finally:
        shutdown()


import gradio as gr
from src.workflows.basic_workflow import (
  run_workflow_with_stream,
  create_content_workflow,
  shutdown_workflow,
)

create_content_workflow()


def generate_content(topic):
  for chunk in run_workflow_with_stream(topic):
    yield chunk


iface = gr.Interface(
  fn=generate_content,
  inputs=gr.Textbox(lines=2, placeholder="Enter any topic"),
  outputs=gr.Markdown(label="Result"),
  title="Agno Content Workflow (Streaming)",
  description="Researcher → tool → Writer (streaming)",
)

if __name__ == "__main__":
  try:
    iface.launch()
  finally:
    shutdown_workflow()

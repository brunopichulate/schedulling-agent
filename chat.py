import gradio as gr
from src.workflows.basic_workflow import (
    run_workflow_with_stream,
    create_content_workflow,
    shutdown_workflow,
)

# Initialize workflow once
create_content_workflow()


def generate_content(topic):
    """
    Streams the response properly by accumulating chunks
    so Gradio does not render token-by-token.
    """
    full_response = ""

    for chunk in run_workflow_with_stream(topic):
        if chunk:
            full_response += chunk
            yield full_response


iface = gr.Interface(
    fn=generate_content,
    inputs=gr.Textbox(
        lines=2,
        placeholder="Enter any topic or ask about a mentor"
    ),
    outputs=gr.Markdown(label="Result"),
    title="Agno Endeavor Workflow",
    description="Searches info about person on db",
)


if __name__ == "__main__":
    try:
        iface.launch()
    finally:
        shutdown_workflow()

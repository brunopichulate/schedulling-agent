import gradio as gr
from src.workflows.basic_workflow import content_workflow

def generate_content(topic):
    response = content_workflow.run(message=topic, stream=False)
    
    if hasattr(response, 'content'):
        return response.content
    return str(response)

iface = gr.Interface(
    fn=generate_content,
    inputs=gr.Textbox(lines=2, placeholder="Enter a topic (e.g., 'The future of AI')"),
    outputs=gr.Markdown(label="Generated Article"),
    title="Agno Content Creation Workflow",
    description="Enter a topic, and the Researcher agent will find info, then the Writer agent will write an article."
)

if __name__ == "__main__":
    iface.launch()

import gradio as gr
from src.workflows.basic_workflow import (
  run_meeting_workflow_with_stream,
  create_content_workflow,
  shutdown_workflow,
)

create_content_workflow()

with gr.Blocks() as iface:
  gr.Markdown("# Meeting Orchestrator Agent")
  gr.Markdown(
    "Envie qualquer mensagem para iniciar o fluxo. O agente gerenciará o status da meeting via ferramentas."
  )

  chatbot = gr.Chatbot(height=500)
  msg = gr.Textbox(
    placeholder="Envie qualquer mensagem...", label="Sua mensagem"
  )

  state = gr.State([])

  def user_action(user_message, history):
    new_history = history + [{"role": "user", "content": user_message}]
    return "", new_history

  def bot_action(user_message, history):
    history.append({"role": "assistant", "content": "..."})
    yield history, history

    full_response = ""
    try:
      for chunk in run_meeting_workflow_with_stream(user_message):
        if chunk:
          full_response += chunk
          history[-1]["content"] = full_response
          yield history, history
    except Exception as e:
      history[-1]["content"] = f"Ocorreu um erro: {str(e)}"
      yield history, history

  msg.submit(user_action, [msg, state], [msg, state], queue=False).then(
    bot_action, [msg, state], [chatbot, state]
  )


if __name__ == "__main__":
  try:
    iface.launch()
  finally:
    shutdown_workflow()

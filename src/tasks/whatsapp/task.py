import logging
import asyncio
from src.core.celery import celery_app
from src.services.whatsapp import whatsapp
from src.services.state_machine_service import get_current_meeting_state
from src.workflows.whatsapp_workflow import run_meeting_workflow_with_stream

from .schemas import (
  WhatsAppMessageAdapter,
  WhatsAppMessage,
  TextMessage,
)

logger = logging.getLogger(__name__)


async def _process_whatsapp_message(message: WhatsAppMessage):
  logger.info(
    f"Processing WhatsApp message from {message.from_}: {message.model_dump_json()}"
  )

  from_number = message.from_

  try:
    await whatsapp.send_typing_indicator(message.id)
  except Exception as e:
    logger.warning(f"Failed to send typing indicator: {e}")

  match message:
    case TextMessage(text=text_content):
      user_text = text_content.body
      logger.info(f"Text from {from_number}: {user_text}")

      # Check if this user has an active meeting workflow.
      # WhatsApp webhook delivers numbers without '+', but the schedule
      # request stores them with '+'. Try both variants.
      active_states = {
        "WAITING_DONATED_RESPONSE",
        "WAITING_RECEIVED_RESPONSE",
      }
      state = get_current_meeting_state(from_number)
      workflow_user_id = from_number
      if state.get("status") not in active_states:
        # Try with '+' prefix
        state = get_current_meeting_state("+" + from_number)
        if state.get("status") in active_states:
          workflow_user_id = "+" + from_number

      if state.get("status") in active_states:
        # Route through the meeting workflow
        for recipient, response_text in run_meeting_workflow_with_stream(
          message=user_text,
          user_id=workflow_user_id,
        ):
          try:
            await whatsapp.send_text_humanized(recipient, response_text)
          except Exception as e:
            logger.error(
              f"Failed to send workflow response to {recipient}: {e}"
            )
      else:
        # No active workflow – send the default fixed reply
        await whatsapp.send_text_humanized(
          from_number,
          "Esse canal é apenas para agendamentos, caso tenha alguma outra dúvida ou sugestão, fale diretamente com o seu principal ponto de contato na Endeavor.",
        )

      logger.info(f"Finished processing message ID {message.id} from {from_number}")

    case _:
      logger.info(f"Unsupported message type: {message.type}")
      await whatsapp.send_text_humanized(
        from_number, "Desculpe, no momento suporto apenas mensagens de texto."
      )


@celery_app.task(bind=True, ignore_result=True)
def process_whatsapp_message(self, message_data: dict, phone_number_id: str):
  """
  Celery task to process WhatsApp messages.
  """
  logger.info(f"Task started for {phone_number_id}")
  try:
    message: WhatsAppMessage = WhatsAppMessageAdapter.validate_python(
      message_data
    )

    asyncio.run(_process_whatsapp_message(message))

  except Exception as e:
    logger.error(f"Error processing message task: {e}", exc_info=True)
    # Maybe retry? self.retry(exc=e)

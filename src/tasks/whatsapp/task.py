import logging
import asyncio
from src.core.celery import celery_app
from src.services.whatsapp import whatsapp

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

  to = message.from_

  try:
    await whatsapp.send_typing_indicator(message.id)
  except Exception as e:
    logger.warning(f"Failed to send typing indicator: {e}")

  match message:
    case TextMessage(text=text_content):
      logger.info(f"Text: {text_content.body}")

      await whatsapp.send_text_humanized(
        to,
        "Esse canal é apenas para agendamentos, caso tenha alguma outra dúvida ou sugestão, fale diretamente com o seu principal ponto de contato na Endeavor.",
      )
      logger.info(f"Sent fixed reply to {to}")

    case _:
      logger.info(f"Unsupported message type: {message.type}")
      await whatsapp.send_text_humanized(
        to, "Desculpe, no momento suporto apenas mensagens de texto."
      )

  logger.info(f"Finished processing message ID {message.id} from {to}")


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

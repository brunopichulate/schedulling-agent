# src/tasks/whatsapp/task.py
import logging
import asyncio
from src.core.celery import celery_app
from src.workflows.basic_workflow import run_workflow_with_stream
from src.services.whatsapp import whatsapp

from .schemas import (
  WhatsAppMessageAdapter,
  WhatsAppMessage,
  TextMessage,
)

logger = logging.getLogger(__name__)

def run_sync_workflow(topic: str) -> str:
    """Helper to run the sync generator workflow and get final result."""
    final_response = ""
    for text in run_workflow_with_stream(topic):
        final_response = text
    return final_response

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

            try:
                reply = await asyncio.to_thread(run_sync_workflow, text_content.body)
                
                if reply:
                    await whatsapp.send_text_humanized(to, reply)
                    logger.info(f"Sent reply to {to}")
                else:
                    logger.warning(f"Empty workflow response for {to}")
                    await whatsapp.send_text_humanized(to, "Desculpe, não consegui gerar uma resposta.")

            except Exception as e:
                logger.error(f"Error running workflow: {e}", exc_info=True)
                await whatsapp.send_text_humanized(to, "Ocorreu um erro ao processar sua mensagem.")

        case _:
            logger.info(f"Unsupported message type: {message.type}")
            await whatsapp.send_text_humanized(
                to,
                "Desculpe, no momento suporto apenas mensagens de texto."
            )

    logger.info(f"Finished processing message ID {message.id} from {to}")


@celery_app.task(bind=True, ignore_result=True)
def process_whatsapp_message(self, message_data: dict, phone_number_id: str):
    """
    Celery task to process WhatsApp messages.
    """
    logger.info(f"Task started for {phone_number_id}")
    try:
        message: WhatsAppMessage = WhatsAppMessageAdapter.validate_python(message_data)
        
        asyncio.run(_process_whatsapp_message(message))
        
    except Exception as e:
        logger.error(f"Error processing message task: {e}", exc_info=True)
        # Maybe retry? self.retry(exc=e)

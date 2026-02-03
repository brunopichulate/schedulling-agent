from fastapi import APIRouter, Request

from src.tasks.whatsapp.task import process_whatsapp_message
from src.tasks.whatsapp.schemas import WhatsAppWebhook
from src.core.config import settings

router = APIRouter()


@router.get("/webhook")
def verify_webhook(request: Request):
  mode = request.query_params.get("hub.mode")
  token = request.query_params.get("hub.verify_token")
  challenge = request.query_params.get("hub.challenge")

  if (
    mode == "subscribe"
    and challenge
    and token == settings.meta.VERIFY_TOKEN.get_secret_value()
  ):
    return int(challenge)

  return {"error": "invalid"}


@router.post("/webhook")
async def whatsapp_webhook(request: Request):
  payload = await request.json()

  # Validate
  webhook = WhatsAppWebhook(**payload)

  # Extract messages and enqueue
  for entry in webhook.entry:
    for change in entry.changes:
      if change.value.messages:
        for message in change.value.messages:
          # Send to Celery
          process_whatsapp_message.delay(
            message, change.value.metadata.phone_number_id
          )

  return {"status": "ok"}

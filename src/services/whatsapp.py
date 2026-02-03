import httpx
import logging

logger = logging.getLogger(__name__)

class MediaDownloadResult:
    """Result from downloading WhatsApp media."""
    def __init__(self, data: bytes, mime_type: str, filename: str):
        self.data = data
        self.mime_type = mime_type
        self.filename = filename
        
class WhatsAppService:
  def __init__(self, access_token: str, phone_number_id: str):
    self.access_token = access_token
    self.phone_number_id = phone_number_id
    self.base_url = (
      f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    )
    self.headers = {
      "Authorization": f"Bearer {self.access_token}",
      "Content-Type": "application/json",
    }

  async def send_typing_indicator(self, message_id: str) -> dict:
  """Send typing indicator or mark message as read"""
  payload = {
    "messaging_product": "whatsapp",
    "status": "read",
    "message_id": message_id,
    "typing_indicator": {"type": "text"},
  }

  async with httpx.AsyncClient() as client:
    try:
      response = await client.post(
        self.base_url, json=payload, headers=self.headers, timeout=10.0
      )
      response.raise_for_status()
      return response.json()
    except httpx.HTTPStatusError as e:
      logger.error(
        f"Error sending typing indicator to msg {message_id}: {e.response.text}"
      )
      raise e
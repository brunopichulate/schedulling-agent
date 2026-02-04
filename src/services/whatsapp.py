# src/services/whatsapp.py
import httpx
import logging
import asyncio
import random
import mimetypes
import numpy as np
from src.core.config import settings

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

  async def send_text_humanized(
    self, to: str, reply: str, delay: list[float] = [0.5, 1.5]
  ) -> list[str]:
    """Send a text message with humanized delay"""
    # Split by double newlines first (paragraphs)
    paragraphs = [p.strip() for p in reply.split("\n\n") if p.strip()]

    # If no double newlines, fall back to single newlines but group smartly
    if len(paragraphs) == 1:
      lines = [line.strip() for line in reply.split("\n") if line.strip()]

      # Group lines into logical chunks (numbered lists, bullet points, etc.)
      paragraphs = []
      current_chunk = []

      for line in lines:
        current_chunk.append(line)

        # Split after numbered items (1., 2., etc.)
        # Or after bullet points that seem complete
        # Or every 3-4 lines to avoid huge blocks
        if (
          line[0].isdigit()
          and ". " in line[:4]  # Numbered list item
          or line.startswith(("- ", "• "))  # Bullet point
          or len(current_chunk) >= 3  # Max 3 lines per chunk
        ):
          paragraphs.append("\n".join(current_chunk))
          current_chunk = []

      if current_chunk:
        paragraphs.append("\n".join(current_chunk))

    # Determine number of messages (2-4, but not more than paragraphs)
    num_messages = min(random.randint(2, 4), len(paragraphs))

    # Split paragraphs into chunks
    chunks = np.array_split(paragraphs, num_messages)

    # Join chunks with double newline for breathing room
    message_parts = ["\n\n".join(chunk) for chunk in chunks]

    # Send each part with delay
    sent_messages = []
    for msg in message_parts:
      send_task = asyncio.create_task(self.send_text(to, msg))
      sleep_task = asyncio.create_task(asyncio.sleep(random.uniform(*delay)))

      results = await asyncio.gather(send_task, sleep_task)
      sent_messages.append(results[0])

    return message_parts

  async def send_text(self, to: str, text: str) -> dict:
    """Send a text message"""
    # Log message preview for debugging (truncated)
    preview = text[:200] + "..." if len(text) > 200 else text
    logger.debug(f"Sending message to {to}: {preview}")

    payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": to,
      "type": "text",
      "text": {"body": text},
    }

    async with httpx.AsyncClient() as client:
      try:
        response = await client.post(
          self.base_url,
          json=payload,
          headers=self.headers,
        )
        response.raise_for_status()
        return response.json()
      except httpx.HTTPStatusError as e:
        logger.error(f"Error sending text message to {to}: {e.response.text}")
        logger.error(f"Message content that failed: {preview}")
        raise e

  async def send_image(
    self, to: str, image_id: str, caption: str | None = None
  ) -> dict:
    """Send an image message"""
    payload = {
      "messaging_product": "whatsapp",
      "recipient_type": "individual",
      "to": to,
      "type": "image",
      "image": {"id": image_id, **({"caption": caption} if caption else {})},
    }

    async with httpx.AsyncClient() as client:
      response = await client.post(
        self.base_url,
        json=payload,
        headers=self.headers,
      )
      response.raise_for_status()
      return response.json()

  async def send_template(
    self,
    to: str,
    template_name: str,
    language_code: str = "en_US",
    components: list[dict] | None = None,
  ) -> dict:
    """Send a template message

    Args:
        to: Phone number to send to (with country code, no + sign)
        template_name: Name of the approved template
        language_code: Language code (default: en_US)
        components: List of component dicts for template (body, buttons, header, etc.)
                   Example for body: [{"type": "body", "parameters": [{"type": "text", "text": "123456"}]}]
                   Example with button: [
                     {"type": "body", "parameters": [{"type": "text", "text": "123456"}]},
                     {"type": "button", "sub_type": "url", "index": 0, "parameters": [{"type": "text", "text": "code123"}]}
                   ]
    """
    template_payload = {
      "name": template_name,
      "language": {"code": language_code},
    }

    # Add components if provided
    if components:
      template_payload["components"] = components

    to_without_plus = to.replace("+", "")

    payload = {
      "messaging_product": "whatsapp",
      "to": to_without_plus,
      "type": "template",
      "template": template_payload,
    }

    async with httpx.AsyncClient() as client:
      response = await client.post(
        self.base_url,
        json=payload,
        headers=self.headers,
      )

      if response.status_code != 200:
        logger.error(
          f"Error sending template message to {to}: {response.text}"
        )
        raise Exception(
          f"Error sending template message to {to}: {response.text}"
        )

      data = response.json()

      logger.info(f"Template message sent to {to}: {data}")

      return data

  async def download_media(self, media_id: str) -> MediaDownloadResult:
    """
    Download media content by media ID with content type.

    Returns:
        MediaDownloadResult with data, mime_type, and filename
    """
    media_url = f"https://graph.facebook.com/v22.0/{media_id}"

    async with httpx.AsyncClient() as client:
      # Step 1: Get media URL and metadata
      response = await client.get(
        media_url,
        headers={"Authorization": f"Bearer {self.access_token}"},
      )
      response.raise_for_status()
      media_info = response.json()

      download_url = media_info.get("url")
      if not download_url:
        raise ValueError("Media URL not found in response")

      # Extract metadata
      mime_type = media_info.get("mime_type", "application/octet-stream")

      # Generate filename from media_id and mime_type
      # Use custom mapping for audio to ensure Whisper compatibility
      audio_extensions = {
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
        "audio/mp3": ".mp3",
        "audio/mp4": ".m4a",
        "audio/m4a": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/aac": ".aac",
        "audio/wav": ".wav",
        "audio/wave": ".wav",
        "audio/x-wav": ".wav",
        "audio/webm": ".webm",
        "audio/flac": ".flac",
      }

      # Extract base mime type without codec info (e.g., "audio/ogg; codecs=opus" -> "audio/ogg")
      base_mime_type = mime_type.split(";")[0].strip().lower()

      if base_mime_type in audio_extensions:
        extension = audio_extensions[base_mime_type]
      else:
        extension = mimetypes.guess_extension(base_mime_type) or ""

      filename = f"{media_id}{extension}"

      # Step 2: Download media content
      media_response = await client.get(
        download_url,
        headers={"Authorization": f"Bearer {self.access_token}"},
      )
      media_response.raise_for_status()

      return MediaDownloadResult(
        data=media_response.content, mime_type=mime_type, filename=filename
      )


whatsapp = WhatsAppService(
  access_token=settings.meta.ACCESS_TOKEN.get_secret_value(),
  phone_number_id=settings.meta.PHONE_NUMBER_ID,
)

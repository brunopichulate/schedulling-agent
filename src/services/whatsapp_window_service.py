# src/services/whatsapp_window_service.py
"""
Tracks the last time a message was exchanged with a WhatsApp phone number.

WhatsApp enforces a 24-hour messaging window: if more than 24 hours have
passed since the last user-initiated message, outbound messages MUST start
with an approved template. This module provides helpers to:

  - update the timestamp whenever a message is sent/received
  - check whether a template must be sent before the next outbound message
"""

import logging
from datetime import datetime, timedelta

import redis

from src.core.config import settings

logger = logging.getLogger(__name__)

# Shared Redis client (same pattern as state_machine_service)
_redis = redis.from_url(settings.redis.URL, decode_responses=True)

# WhatsApp's window is exactly 24 hours; we store with a 25-hour TTL so the
# key naturally expires shortly after the window does.
_WINDOW_HOURS = 24
_TTL_SECONDS = int(timedelta(hours=_WINDOW_HOURS + 1).total_seconds())


def _key(phone: str) -> str:
  # Normalise: strip leading '+' so "+55..." and "55..." map to the same key.
  return f"wa_last_conv:{phone.lstrip('+')}"


def get_last_conversation_time(phone: str) -> datetime | None:
  """Return the last recorded conversation time for *phone*, or None."""
  raw = _redis.get(_key(phone))
  if raw is None:
    return None
  try:
    return datetime.fromisoformat(raw)
  except (ValueError, TypeError):
    logger.warning(f"[wa_window] Invalid timestamp for {phone}: {raw!r}")
    return None


def update_last_conversation_time(phone: str) -> None:
  """Record *now* as the last conversation time for *phone*."""
  now_iso = datetime.now().isoformat()
  _redis.set(_key(phone), now_iso, ex=_TTL_SECONDS)
  logger.debug(f"[wa_window] Updated last conv time for {phone}: {now_iso}")


def needs_template(phone: str) -> bool:
  """
  Return True if an outbound message to *phone* must be preceded by a
  template (i.e. no conversation on record OR last conversation was >24 h ago).
  """
  last = get_last_conversation_time(phone)
  if last is None:
    logger.info(
      f"[wa_window] No conversation record for {phone} — template required"
    )
    return True
  elapsed = datetime.now() - last
  if elapsed > timedelta(hours=_WINDOW_HOURS):
    logger.info(
      f"[wa_window] Window expired for {phone} "
      f"(last: {last.isoformat()}, elapsed: {elapsed}) — template required"
    )
    return True
  return False

import json
import logging
from datetime import datetime, date
from typing import Dict, Any, Optional

import redis

from src.core.config import settings
from src.services.meetings_service import get_meeting_by_id

logger = logging.getLogger(__name__)


class _MongoEncoder(json.JSONEncoder):
  """JSON encoder that handles types common in MongoDB documents."""

  def default(self, obj):
    if isinstance(obj, (datetime, date)):
      return obj.isoformat()
    # bson ObjectId or similar – fall back to str
    try:
      return str(obj)
    except Exception:
      return super().default(obj)


# Redis client – shared across all processes (FastAPI + Celery workers)
_redis = redis.from_url(settings.redis.URL, decode_responses=True)

STATE_TTL_SECONDS = 60 * 60 * 24  # 24 hours

VALID_STATES = [
  "INIT",
  "WAITING_FOR_TEMPLATE_REPLY",
  "WAITING_DONATED_RESPONSE",
  "DONATED_REJECTED_SLOTS",
  "DONATED_NO_RESPONSE",
  "DONATED_SELECTED_SLOT",
  "WAITING_RECEIVED_RESPONSE",
  "RECEIVED_REJECTED",
  "RECEIVED_NO_RESPONSE",
  "RECEIVED_CONFIRMED",
  "HUMAN_INTERVITION_REQUIRED",
]

_EMPTY_STATE: Dict[str, Any] = {
  "status": "INIT",
  "meeting": None,
  "donated": None,
  "received": None,
  "donated_phone": None,
  "received_phone": None,
  "selected_slot": None,
  "last_interaction_time": None,
}


def _key(user_id: str) -> str:
  return f"meeting_state:{user_id}"


def _load(user_id: str) -> Dict[str, Any]:
  """Load state from Redis. Returns empty state dict if not found."""
  raw = _redis.get(_key(user_id))
  if raw is None:
    return dict(_EMPTY_STATE)
  try:
    return json.loads(raw)
  except (json.JSONDecodeError, TypeError):
    return dict(_EMPTY_STATE)


def _save(user_id: str, state: Dict[str, Any]) -> None:
  """Persist state to Redis with TTL."""
  _redis.set(
    _key(user_id),
    json.dumps(state, cls=_MongoEncoder),
    ex=STATE_TTL_SECONDS,
  )


def _delete(user_id: str) -> None:
  """Remove state from Redis."""
  _redis.delete(_key(user_id))


def _get_or_init_state(user_id: str) -> Dict[str, Any]:
  """Returns existing state for user_id, or initializes a fresh one."""
  state = _load(user_id)
  # If it was a fresh empty state make sure it's persisted
  if _redis.get(_key(user_id)) is None:
    _save(user_id, state)
  return state


def load_potential_meeting_into_state(meeting_id: str, user_id: str) -> bool:
  """
  Looks for a meeting by ID, extracts the attendees (Donated and Received),
  and initializes the meeting state for the given user.

  Returns:
      bool: True if the meeting was successfully loaded, False otherwise
  """
  state = _get_or_init_state(user_id)

  meeting = get_meeting_by_id(meeting_id)
  if not meeting:
    return False

  attendees = meeting.get("attendees", [])

  donated = next(
    (att for att in attendees if att.get("role") == "Donated"), None
  )
  received = next(
    (att for att in attendees if att.get("role") == "Received"), None
  )

  if not donated or not received:
    return False

  state["meeting"] = meeting
  state["donated"] = donated
  state["received"] = received

  _save(user_id, state)
  return True


def register_phone_numbers(
  user_id: str, donated_phone: str, received_phone: str
) -> None:
  """Stores the phone numbers of donated and received in the meeting state."""
  state = _get_or_init_state(user_id)
  state["donated_phone"] = donated_phone
  state["received_phone"] = received_phone
  _save(user_id, state)


def record_interaction_time(user_id: str) -> None:
  """Records the current time as the last interaction time for a user."""
  state = _get_or_init_state(user_id)
  state["last_interaction_time"] = datetime.now().isoformat()
  _save(user_id, state)


def check_timeout(user_id: str, seconds: int = 30) -> bool:
  """
  Checks if the time elapsed since the last interaction exceeds the given threshold.

  Args:
      user_id: The user's phone number.
      seconds: The timeout threshold in seconds (default: 30).

  Returns:
      True if the timeout has been exceeded, False otherwise.
  """
  state = _get_or_init_state(user_id)
  last_str = state.get("last_interaction_time")
  if last_str is None:
    return False
  try:
    last = datetime.fromisoformat(last_str)
    elapsed = (datetime.now() - last).total_seconds()
    return elapsed > seconds
  except (ValueError, TypeError):
    return False


def update_meeting_state(
  new_state: str, user_id: str, selection: Optional[str] = None
) -> Dict[str, Any]:
  """
  Transitions the meeting state to a new status for a given user.

  Valid states:
  INIT, WAITING_FOR_TEMPLATE_REPLY, WAITING_DONATED_RESPONSE, DONATED_REJECTED_SLOTS,
  DONATED_NO_RESPONSE, DONATED_SELECTED_SLOT, WAITING_RECEIVED_RESPONSE,
  RECEIVED_REJECTED, RECEIVED_NO_RESPONSE, RECEIVED_CONFIRMED,
  HUMAN_INTERVITION_REQUIRED

  Args:
      new_state: The state to transition to.
      user_id: The user's phone number.
      selection: The ISO date-time string of the selected slot (used in DONATED_SELECTED_SLOT).

  Returns:
      Dict with the updated state info.
  """
  state = _get_or_init_state(user_id)
  state["status"] = new_state

  if selection and new_state == "DONATED_SELECTED_SLOT":
    state["selected_slot"] = selection

  terminal_states = [
    "RECEIVED_CONFIRMED",
    "RECEIVED_REJECTED",
    "HUMAN_INTERVITION_REQUIRED",
  ]

  if new_state in terminal_states:
    state_snapshot = dict(state)
    # Reset state for this user after terminal state
    _save(user_id, dict(_EMPTY_STATE))
    return {"status_updated_to": new_state, "final_state": state_snapshot}

  _save(user_id, state)
  return {"status_updated_to": new_state, "current_state": state}


def get_current_meeting_state(user_id: str) -> Dict[str, Any]:
  """
  Retrieves the current state of the meeting workflow for a given user.

  Returns:
      Dict: A copy of the current state dict.
  """
  return _get_or_init_state(user_id)

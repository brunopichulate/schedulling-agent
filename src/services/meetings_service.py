from typing import Optional, Dict, Any
from src.core.database import get_database
from bson.objectid import ObjectId


def get_meeting_by_id(meeting_id: str) -> Optional[Dict[str, Any]]:
  """
  Searches for a meeting by its ID in the 'meeting' collection.
  """
  db = get_database()
  collection = db["meeting"]

  try:
    # Try to parse string to ObjectId if it's a valid hex string
    if ObjectId.is_valid(meeting_id):
      meeting = collection.find_one({"_id": ObjectId(meeting_id)}, {"_id": 0})
      if meeting:
        return meeting
  except ImportError:
    pass

  # Fallback to searching by string in '_id' or 'id'
  meeting = collection.find_one({"_id": meeting_id}, {"_id": 0})
  if not meeting:
    meeting = collection.find_one({"id": meeting_id}, {"_id": 0})

  return meeting

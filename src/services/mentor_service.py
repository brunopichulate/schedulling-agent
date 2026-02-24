from typing import Optional, Dict, Any
from src.core.database import get_database


def find_potential_meetings() -> Optional[Dict[str, Any]]:
  """
  Searches for a meeting with 'Potential' status in the 'meeting' collection.
  """
  db = get_database()
  collection = db["meeting"]

  meeting = collection.find_one({"status": "Potential"}, {"_id": 0})

  return meeting

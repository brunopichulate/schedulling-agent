from pymongo import MongoClient
from src.core.config import settings

_client = None


def get_database():
  global _client

  if _client is None:
    _client = MongoClient(settings.mongodb.URL)

  return _client["matching"]

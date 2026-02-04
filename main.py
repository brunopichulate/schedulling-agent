import logging
import uvicorn
from fastapi.concurrency import asynccontextmanager
from src.api import create_app

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter
from src.core.config import settings
from src.core.langfuse import shutdown

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app):
  """Manage application startup and shutdown events."""

  logger.info("application_startup")
  redis_connection = redis.from_url(
    settings.redis.URL, encoding="utf-8", decode_responses=True,
  )
  await FastAPILimiter.init(redis_connection)

  yield

  # Shutdown
  logger.info("application_shutdown")
  await redis_connection.close()
  shutdown()


app = create_app(lifespan=lifespan)

if __name__ == "__main__":
  uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

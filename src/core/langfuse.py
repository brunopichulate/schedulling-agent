import logging
from langfuse import observe, Langfuse, get_client
from langfuse.model import TextPromptClient
from openinference.instrumentation.agno import AgnoInstrumentor
from src.core.config import settings

langfuse_client = Langfuse(
  public_key=settings.langfuse.PUBLIC_KEY.get_secret_value(),
  secret_key=settings.langfuse.SECRET_KEY.get_secret_value(),
  host=settings.langfuse.HOST,
)

logger = logging.getLogger(__name__)


def setup():
  if not langfuse_client:
    logger.warning("Langfuse credentials not found. Skipping setup.")
    return

  logger.info("Setting up Langfuse...")
  langfuse_client.auth_check()

  AgnoInstrumentor().instrument()

  logger.info("Langfuse setup complete")


def get_prompt(
  *, prompt_name: str, prompt_label: str | None = "production"
) -> TextPromptClient:
  if not langfuse_client:
    logger.warning("Langfuse client not initialized. Returning None.")
    return None
  return langfuse_client.get_prompt(
    prompt_name, label=prompt_label, cache_ttl_seconds=60
  )


def shutdown():
  if not langfuse_client:
    return
  logger.info("Shutting down Langfuse...")
  langfuse_client.flush()
  langfuse_client.shutdown()
  logger.info("Langfuse shut down complete")


__all__ = ["observe", "get_client", "langfuse_client"]

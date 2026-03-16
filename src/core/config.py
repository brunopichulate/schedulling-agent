import logging
import os
import sys
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import BaseModel, SecretStr, ValidationError

from src.core.otel import init_otel
from src.core.logger import init_logging, update_level

logger = logging.getLogger(__name__)


class MetaSettings(BaseModel):
  VERIFY_TOKEN: SecretStr
  APP_SECRET: SecretStr
  APP_ID: str
  ACCESS_TOKEN: SecretStr
  PHONE_NUMBER_ID: str


class OpenAISettings(BaseModel):
  API_KEY: SecretStr


class LangfuseSettings(BaseModel):
  SECRET_KEY: SecretStr
  PUBLIC_KEY: SecretStr
  HOST: str


class RedisSettings(BaseModel):
  URL: str = "redis://localhost:6379/0"


class OtelSettings(BaseModel):
  ENDPOINTS: str = ""
  ENABLE: bool = False


class PromptConfig(BaseModel):
  NAME: str
  LABEL: str


class PromptSettings(BaseModel):
  WRITER: PromptConfig
  RESEARCHER: PromptConfig


class LoggerSettings(BaseModel):
  LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


class MongoDBSettings(BaseModel):
  URL: str


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
    env_file=".env",
    extra="ignore",
    env_file_encoding="utf-8",
    env_nested_delimiter="__",
    case_sensitive=False,
  )

  # ENV: Literal['dev', 'staging', 'prod', 'test'] = 'dev'

  langfuse: LangfuseSettings
  openai: OpenAISettings
  prompt: PromptSettings | None = None
  log: LoggerSettings
  otel: OtelSettings
  redis: RedisSettings
  meta: MetaSettings
  mongodb: MongoDBSettings

  # Agent behavior
  no_response_timeout_seconds: int = 172800  # 48h — override with NO_RESPONSE_TIMEOUT_SECONDS in .env


def load_settings():
  """Load settings before initializing logging and telemetry."""
  is_test = os.getenv("PYTEST_VERSION")
  env_file = ".env.test" if is_test else ".env"

  try:
    logger.info(f"Loading configuration from {env_file}...")
    settings = Settings.model_validate({}, context={"env_file": env_file})

    logger.info("Settings loaded successfully")
    return settings
  except ValidationError as e:
    logger.error("Settings validation failed:")
    for error in e.errors():
      field_path = " -> ".join(str(loc) for loc in error["loc"])
      logger.error(f"  Field '{field_path}': {error['msg']}")

    logger.error("Please check your environment variables and configuration.")
    sys.exit(1)
  except Exception as e:
    logger.error(f"Unexpected error loading settings: {e}")
    sys.exit(1)


# Load settings with proper error handling
settings = load_settings()

# Initialize logging and telemetry
logger_provider = init_otel(
  otel_endpoints=settings.otel.ENDPOINTS, enable=settings.otel.ENABLE
)
init_logging(settings.log.LEVEL, logger_provider=logger_provider)
update_level(settings.log.LEVEL)

logger.info("Configuration initialization completed")

import os
import logging
import base64
from langfuse import observe, Langfuse
from langfuse.model import TextPromptClient
from dotenv import load_dotenv
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import SimpleSpanProcessor
from opentelemetry import trace
from openinference.instrumentation.agno import AgnoInstrumentor

load_dotenv()

LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST")

if LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY:
    langfuse_client = Langfuse(
        public_key=LANGFUSE_PUBLIC_KEY,
        secret_key=LANGFUSE_SECRET_KEY,
        host=LANGFUSE_HOST,
    )
else:
    langfuse_client = None

logger = logging.getLogger(__name__)


def setup():
    if not langfuse_client:
        logger.warning("Langfuse credentials not found. Skipping setup.")
        return

    logger.info("Setting up Langfuse...")
    langfuse_client.auth_check()

    auth_str = f"{LANGFUSE_PUBLIC_KEY}:{LANGFUSE_SECRET_KEY}"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    headers = {"Authorization": f"Basic {auth_b64}"}

    trace_provider = TracerProvider()
    trace_provider.add_span_processor(
        SimpleSpanProcessor(OTLPSpanExporter(
            endpoint=f"{LANGFUSE_HOST}/api/public/otel",
            headers=headers
        ))
    )
    trace.set_tracer_provider(trace_provider)

    AgnoInstrumentor().instrument()

    logger.info("Langfuse setup complete")


def get_prompt(
    *, prompt_name: str, prompt_label: str | None = "production"
) -> TextPromptClient:
    if not langfuse_client:
        logger.warning("Langfuse client not initialized. Returning None.")
        return None
    return langfuse_client.get_prompt(prompt_name, label=prompt_label, cache_ttl_seconds=60)


def shutdown():
    if not langfuse_client:
        return
    logger.info("Shutting down Langfuse...")
    langfuse_client.flush()
    langfuse_client.shutdown()
    logger.info("Langfuse shut down complete")


__all__ = ["observe"]

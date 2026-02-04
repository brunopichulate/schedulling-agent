import os
from opentelemetry import trace
from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.http.metric_exporter import (
  OTLPMetricExporter,
)
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http._log_exporter import (
  OTLPLogExporter,
)
from opentelemetry.exporter.otlp.proto.http.trace_exporter import (
  OTLPSpanExporter,
)
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry import _logs as logs_api


def init_otel(
  otel_endpoints: str, enable: bool = False
) -> LoggerProvider | None:
  if not enable:
    return None

  trace_provider = TracerProvider()
  logger_provider = LoggerProvider()

  metric_readers = []

  for endpoint in otel_endpoints.split(","):
    endpoint = endpoint.strip()

    if not endpoint:
      continue

    exporter = OTLPSpanExporter(endpoint=f"{endpoint}/v1/traces")
    trace_provider.add_span_processor(BatchSpanProcessor(exporter))

    metric_exporter = OTLPMetricExporter(endpoint=f"{endpoint}/v1/metrics")
    reader = PeriodicExportingMetricReader(metric_exporter)
    metric_readers.append(reader)

    log_exporter = OTLPLogExporter(endpoint=f"{endpoint}/v1/logs")
    logger_provider.add_log_record_processor(
      BatchLogRecordProcessor(log_exporter)
    )

  trace.set_tracer_provider(trace_provider)
  if metric_readers and not os.getenv("PYTEST_VERSION"):
    meter_provider = MeterProvider(metric_readers=metric_readers)
    metrics.set_meter_provider(meter_provider)
  logs_api.set_logger_provider(logger_provider)
  return logger_provider

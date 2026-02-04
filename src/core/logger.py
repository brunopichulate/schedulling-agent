import logging
import sys

from colorama import Fore, Style, init
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs import LoggingHandler
from opentelemetry.instrumentation.logging import LoggingInstrumentor

init(autoreset=True)


class ColorFormatter(logging.Formatter):
  COLORS = {
    logging.DEBUG: Fore.BLUE,
    logging.INFO: Fore.GREEN,
    logging.WARNING: Fore.YELLOW,
    logging.ERROR: Fore.RED,
    logging.CRITICAL: Fore.MAGENTA + Style.BRIGHT,
  }

  def format(self, record):
    # trace_id e span_id já podem vir do LoggingInstrumentor
    trace_id = getattr(record, "otelTraceID", "0" * 32)
    span_id = getattr(record, "otelSpanID", "0" * 16)

    service_name = getattr(record, "otelServiceName", "unknown-service")

    log_color = self.COLORS.get(record.levelno, "")

    message = super().format(record)

    return (
      f"[{Fore.CYAN}{self.formatTime(record, self.datefmt)}{Style.RESET_ALL}] "
      f"[{log_color}{record.levelname:<8}{Style.RESET_ALL}] "  # Usa <8 para alinhar os níveis
      f"[{Fore.BLUE}{service_name}{Style.RESET_ALL}] "
      f"[{Fore.YELLOW}{record.module:<20}{Style.RESET_ALL}] "
      f"[trace_id={Fore.MAGENTA}{trace_id}{Style.RESET_ALL}] "
      f"[span_id={Fore.LIGHTBLACK_EX}{span_id}{Style.RESET_ALL}] "
      f"{message}"
    )


class SuppressDetachFilter(logging.Filter):
  def filter(self, record: logging.LogRecord) -> bool:
    if "Failed to detach context" in record.getMessage():
      return False  # não loga
    return True


def init_logging(
  level: str = "INFO", logger_provider: LoggerProvider | None = None
):
  """Inicializa a configuração raiz do logging com o handler e formatter customizados."""
  handler = logging.StreamHandler(sys.stdout)

  formatter = ColorFormatter(datefmt="%Y-%m-%d %H:%M:%S UTC%z")
  handler.setFormatter(formatter)

  handlers = [handler]

  if logger_provider is not None:
    otelHandler = LoggingHandler(
      level=logging.getLevelNamesMapping().get(level, logging.INFO),
      logger_provider=logger_provider,
    )
    handlers.append(otelHandler)

  logging.basicConfig(
    level=level,
    handlers=handlers,
    force=True,
  )

  logging.getLogger("opentelemetry.context").addFilter(SuppressDetachFilter())

  LoggingInstrumentor().instrument(set_logging_format=False)


def update_level(level: str = "INFO"):
  root_logger = logging.getLogger()
  root_logger.setLevel(level)
  logging.getLogger(__name__).info(f"Nível de log atualizado para {level}")

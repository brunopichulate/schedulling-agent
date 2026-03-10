import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def format_meeting_date(value) -> str:
    """Formats a date (datetime object or ISO string) to humanized Portuguese."""
    _WEEKDAYS = [
        "segunda-feira",
        "terça-feira",
        "quarta-feira",
        "quinta-feira",
        "sexta-feira",
        "sábado",
        "domingo",
    ]
    _MONTHS = [
        "",
        "janeiro",
        "fevereiro",
        "março",
        "abril",
        "maio",
        "junho",
        "julho",
        "agosto",
        "setembro",
        "outubro",
        "novembro",
        "dezembro",
    ]
    try:
        if isinstance(value, datetime):
            dt = value
        else:
            normalized = str(value).strip().replace(" ", "T").replace("Z", "+00:00")
            dt = datetime.fromisoformat(normalized)
        weekday = _WEEKDAYS[dt.weekday()]
        month = _MONTHS[dt.month]
        return (
            f"{weekday}, {dt.day} de {month} de {dt.year} às {dt.strftime('%H:%M')}"
        )
    except Exception:
        return str(value)

def build_slot_suggestions(iso_date: str) -> list[str]:
    """
    Builds three time slot suggestions relative to the base meeting_date:
    morning (09:00), afternoon (14:00), and evening (19:00) of the same day.
    """
    try:
        if isinstance(iso_date, datetime):
            dt = iso_date
        else:
            normalized = (
                str(iso_date).strip().replace(" ", "T").replace("Z", "+00:00")
            )
            dt = datetime.fromisoformat(normalized)
        date_str = dt.strftime("%d/%m/%Y")
        return [
            f"1. Manhã   – {date_str} 09:00",
            f"2. Tarde   – {date_str} 14:00",
            f"3. Noite   – {date_str} 19:00",
        ]
    except Exception:
        return [
            "1. Manhã   – 09:00",
            "2. Tarde   – 14:00",
            "3. Noite   – 19:00",
        ]

def parse_extracted(content, field: str, default=None):
    """
    Safely extracts a field from the LLM response content.
    Handles Pydantic models, dicts, and raw JSON strings.
    """
    logger.debug(
        "[SlotExtractor] content type=%s, value=%r",
        type(content).__name__,
        content,
    )

    if hasattr(content, field):
        return getattr(content, field, default)

    if isinstance(content, dict):
        return content.get(field, default)

    if isinstance(content, str):
        try:
            data = json.loads(content)
            return data.get(field, default)
        except (json.JSONDecodeError, AttributeError):
            pass

    return default

def format_slot(slot: str) -> str:
    try:
        dt = datetime.fromisoformat(slot.replace("Z", "+00:00"))
        return dt.strftime("%d/%m/%Y às %H:%M")
    except Exception:
        return slot

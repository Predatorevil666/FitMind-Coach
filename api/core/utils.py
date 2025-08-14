"""Утилиты для API FitMind Coach."""

from datetime import datetime, timezone


def get_utc_now() -> datetime:
    """
    Получить текущее время в UTC.

    Returns:
        datetime: Текущее время в UTC с информацией о временной зоне.
    """
    return datetime.now(timezone.utc)


def format_datetime(dt: datetime) -> str:
    """
    Форматировать datetime в строку ISO 8601.

    Args:
        dt: Объект datetime для форматирования.

    Returns:
        str: Строка в формате ISO 8601.
    """
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.isoformat()


def parse_datetime(dt_str: str) -> datetime:
    """
    Преобразовать строку ISO 8601 в объект datetime.

    Args:
        dt_str: Строка в формате ISO 8601.

    Returns:
        datetime: Объект datetime с информацией о временной зоне.
    """
    dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt

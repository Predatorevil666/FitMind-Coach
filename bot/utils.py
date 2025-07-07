"""Утилиты для бота FitMind Coach."""

import re

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from bot.constants import WORKOUT_TYPES


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
    if dt_str.endswith("Z"):
        dt_str = dt_str[:-1] + "+00:00"

    # Парсим дату
    dt = datetime.fromisoformat(dt_str)

    # Если нет timezone информации, добавляем UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)

    return dt


def format_date_for_display(dt: datetime) -> str:
    """
    Форматировать дату для отображения пользователю.

    Args:
        dt: Объект datetime.

    Returns:
        str: Строка в формате ДД.ММ.ГГГГ.
    """
    return dt.strftime("%d.%m.%Y")


def parse_date_from_text(text: str) -> Optional[datetime]:
    """
    Извлечь дату из текста.

    Args:
        text: Текст, содержащий дату.

    Returns:
        Optional[datetime]: Объект datetime или None, если дата не найдена.
    """
    pattern = r"(\d{1,2})[\.\/](\d{1,2})(?:[\.\/](\d{2,4}))?"
    date_match = re.search(pattern, text)

    if date_match:
        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year_group = date_match.group(3)
        year = int(year_group) if year_group else datetime.now().year
        if year < 100:
            year += 2000

        try:
            dt = datetime(year, month, day, tzinfo=timezone.utc)
            return dt
        except ValueError:
            return None

    return None


def count_workouts_this_week(workouts: list[dict[str, Any]]) -> int:
    """
    Подсчитывает количество тренировок за текущую неделю.

    Args:
        workouts: Список тренировок из API

    Returns:
        int: Количество тренировок за текущую неделю
    """
    if not workouts:
        return 0

    now = get_utc_now()
    # Начало недели (понедельник)
    week_start = now - timedelta(days=now.weekday())
    week_start = week_start.replace(hour=0, minute=0, second=0, microsecond=0)

    # Конец недели (воскресенье)
    week_end = week_start + timedelta(days=6, hours=23, minutes=59, seconds=59)

    count = 0
    for workout in workouts:
        try:
            workout_date_str = workout.get("date", "")
            workout_date = parse_datetime(workout_date_str)

            if week_start <= workout_date <= week_end:
                count += 1
        except (ValueError, TypeError):
            # Пропускаем тренировки с некорректной датой
            continue

    return count


def pluralize_workouts(count: int) -> str:
    """
    Правильное склонение слова "тренировка" в зависимости от числа.

    Args:
        count: Количество тренировок

    Returns:
        str: Правильно склоненная форма слова
    """
    if count % 10 == 1 and count % 100 != 11:
        return "тренировка"
    elif count % 10 in [2, 3, 4] and count % 100 not in [12, 13, 14]:
        return "тренировки"
    else:
        return "тренировок"


def format_workout_count(count: int) -> str:
    """
    Форматирует количество тренировок с правильным склонением.

    Args:
        count: Количество тренировок

    Returns:
        str: Отформатированная строка с количеством и склонением
    """
    return f"{count} {pluralize_workouts(count)}"


def parse_workout_data(
    text: str,
) -> tuple[Optional[str], Optional[int], Optional[int], Optional[datetime]]:
    """
    Извлечь данные о тренировке из текста.

    Args:
        text: Текст с информацией о тренировке.

    Returns:
        Tuple: (тип, длительность, интенсивность, дата).
    """
    text = text.lower()

    # Ищем тип тренировки
    workout_type = None
    for key in WORKOUT_TYPES:
        if key in text:
            workout_type = WORKOUT_TYPES[key]
            break

    # Ищем длительность
    duration_match = re.search(r"(\d+)\s*(?:мин|минут)", text)
    if not duration_match:
        duration_match = re.search(r"(\d+)", text)

    duration = int(duration_match.group(1)) if duration_match else None

    # Ищем интенсивность
    intensity_pattern = r"(?:интенсивность|уровень)\s*[:-]?\s*(\d+)"
    intensity_match = re.search(intensity_pattern, text)
    if not intensity_match:
        intensity_match = re.search(r"(?<!\d)([1-9]|10)(?!\d)", text)

    intensity = int(intensity_match.group(1)) if intensity_match else None

    # Ищем дату
    date = parse_date_from_text(text)

    return workout_type, duration, intensity, date

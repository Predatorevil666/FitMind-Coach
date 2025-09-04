"""Утилиты для бота FitMind Coach."""

import asyncio
import os
import random
import re

from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Optional, Union

import aiohttp
import jinja2

from aiogram.types import Message, User

from bot.config import (
    MISTRAL_API_KEY,
    MISTRAL_MAX_RETRIES,
    MISTRAL_MAX_WAIT,
    MISTRAL_MIN_WAIT,
    MISTRAL_MODEL,
    MISTRAL_TIMEOUT,
)
from bot.constants import ACTIVITY_MULTIPLIERS, MET_VALUES, WORKOUT_TYPES
from bot.logger import logger


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


def get_user_id(user_or_message: Any) -> Union[int, str]:
    """
    Безопасно получает ID пользователя из объекта User или Message.

    Args:
        user_or_message: Объект User или Message

    Returns:
        int или str: ID пользователя или строка "неизвестный"
    """
    if isinstance(user_or_message, Message):
        user = user_or_message.from_user
    elif isinstance(user_or_message, User):
        user = user_or_message
    else:
        user = None

    return user.id if user else "неизвестный"


async def retry_async(
    func: Callable,
    max_retries: int = 3,
    min_wait: float = 0.5,
    max_wait: float = 4.0,
    timeout: float = 30.0,
) -> Any:
    """
    Выполняет асинхронную функцию с механизмом повторных попыток и таймаутом.

    Args:
        func: Асинхронная функция для выполнения
        max_retries: Максимальное количество повторных попыток
        min_wait: Минимальное время ожидания между попытками (в секундах)
        max_wait: Максимальное время ожидания между попытками (в секундах)
        timeout: Максимальное время выполнения функции (в секундах)

    Returns:
        Результат выполнения функции
    """
    retries = 0
    last_exception: Optional[Exception] = None

    while retries <= max_retries:
        try:
            # Выполняем функцию с таймаутом
            return await asyncio.wait_for(func(), timeout=timeout)
        except asyncio.TimeoutError:
            last_exception = asyncio.TimeoutError(
                f"Запрос превысил таймаут в {timeout} секунд"
            )
        except Exception as e:
            last_exception = e

        retries += 1
        if retries > max_retries:
            break

        # Экспоненциальный откат с случайным компонентом
        wait_time = min(max_wait, min_wait * (2 ** (retries - 1)))
        # Добавляем случайность (jitter) для предотвращения "грозди запросов"
        wait_time = wait_time * (0.8 + 0.4 * random.random())

        logger.warning(
            f"Попытка {retries} не удалась. "
            f"Повторная попытка через {wait_time:.2f} секунд..."
        )
        await asyncio.sleep(wait_time)

    # Если все попытки не удались, выбрасываем последнее исключение
    raise last_exception


# Настройка окружения Jinja2
def get_template_env() -> jinja2.Environment:
    """
    Создает и возвращает окружение Jinja2 для загрузки шаблонов.

    Returns:
        jinja2.Environment: Окружение Jinja2
    """
    template_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "bot",
        "templates",
    )
    logger.debug(f"Путь к директории шаблонов: {template_dir}")
    return jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        trim_blocks=True,
        lstrip_blocks=True,
    )


class MistralClient:
    """Клиент для работы с Mistral API."""

    _instance = None
    _template_env = None

    def __new__(cls):
        """Реализация паттерна Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)

            # Проверка API ключа
            if not MISTRAL_API_KEY or len(MISTRAL_API_KEY) < 10:
                logger.error("Невалидный API ключ Mistral")
                raise ValueError("Невалидный API ключ Mistral")

            cls._template_env = get_template_env()

            # Логируем успешную инициализацию
            logger.info(
                f"MistralClient инициализирован с моделью {MISTRAL_MODEL}"
            )

        return cls._instance

    async def get_advice(
        self, query: str, user_data: Optional[dict[str, Any]] = None
    ) -> str:
        """
        Получить персонализированный совет от Mistral AI
        на основе данных пользователя.

        Args:
            query: Запрос пользователя
            user_data: Словарь с данными пользователя
                (профиль, тренировки, питание, анализы)
                {
                    'profile': dict[str, Any],
                    'workouts': list[dict[str, Any]],
                    'meals': list[dict[str, Any]],
                    'lab_results': list[dict[str, Any]]
                }

        Returns:
            str: Ответ от модели
        """
        if user_data is None:
            user_data = {}

        try:
            logger.debug(f"Получен запрос: {query}")
            logger.debug(f"Данные пользователя: {user_data}")

            # Загружаем шаблон
            template_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                "bot",
                "templates",
            )
            logger.debug(f"Путь к директории шаблонов: {template_dir}")

            # Проверяем существование директории
            if not os.path.exists(template_dir):
                logger.error(
                    f"Директория шаблонов не существует: {template_dir}"
                )
                return "Извините, произошла ошибка при обработке запроса."

            # Проверяем существование файла шаблона
            template_path = os.path.join(template_dir, "prompts", "advice.j2")
            if not os.path.exists(template_path):
                logger.error(f"Файл шаблона не существует: {template_path}")
                return "Извините, произошла ошибка при обработке запроса."

            # Создаем окружение Jinja2 напрямую
            jinja_env = jinja2.Environment(
                loader=jinja2.FileSystemLoader(template_dir),
                trim_blocks=True,
                lstrip_blocks=True,
            )

            template = jinja_env.get_template("prompts/advice.j2")

            # Заполняем шаблон данными
            context = {
                "query": query,
                "profile": user_data.get("profile"),
                "workouts": user_data.get("workouts"),
                "meals": user_data.get("meals"),
                "lab_results": user_data.get("lab_results"),
            }

            prompt = template.render(**context)

            logger.debug(
                f"Сгенерирован промпт для Mistral API: {prompt[:100]}..."
            )

            # Используем прямой запрос к API вместо SDK
            async def make_api_request():
                url = "https://api.mistral.ai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {MISTRAL_API_KEY}",
                    "Content-Type": "application/json",
                }

                data = {
                    "model": MISTRAL_MODEL,
                    "messages": [{"role": "user", "content": prompt}],
                }

                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url, headers=headers, json=data
                    ) as response:
                        if response.status != 200:
                            error_text = await response.text()
                            raise Exception(
                                f"API вернул статус {response.status}: "
                                f"{error_text}"
                            )

                        response_json = await response.json()
                        return response_json["choices"][0]["message"][
                            "content"
                        ]

            # Выполняем запрос с retry и таймаутом
            response = await retry_async(
                make_api_request,
                max_retries=MISTRAL_MAX_RETRIES,
                min_wait=MISTRAL_MIN_WAIT,
                max_wait=MISTRAL_MAX_WAIT,
                timeout=MISTRAL_TIMEOUT,
            )
            return response
        except Exception as e:
            logger.error(f"Ошибка при запросе к Mistral API: {e}")
            # Более подробное логирование для диагностики
            logger.error(
                f"Детали запроса: model={MISTRAL_MODEL}, "
                f"API_KEY={MISTRAL_API_KEY[:5]}***"
            )
            return (
                "Извините, в данный момент я не могу предоставить совет. "
                "Пожалуйста, попробуйте позже."
            )


# Создаем глобальный экземпляр клиента Mistral
mistral_client = MistralClient()


def calculate_bmr(
    weight: float, height: float, age: int, gender: str = "male"
) -> float:
    """
    Рассчитать базовый метаболизм (BMR) по формуле Harris-Benedict.

    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст в годах
        gender: Пол ("male" или "female")

    Returns:
        float: Базовый метаболизм в ккал/день
    """
    if gender.lower() == "female":
        # BMR для женщин (Harris-Benedict)
        bmr = 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    else:
        # BMR для мужчин (Harris-Benedict)
        bmr = 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)

    return round(bmr, 1)


def calculate_calories_for_workout(
    weight: float,
    height: float,
    age: int,
    workout_type: str,
    duration_minutes: int,
    gender: str = "male",
) -> int:
    """
    Рассчитать потраченные калории на тренировке с учётом BMR.

    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст в годах
        workout_type: Тип тренировки
        duration_minutes: Продолжительность в минутах
        gender: Пол ("male" или "female")

    Returns:
        int: Потраченные калории
    """
    met = MET_VALUES.get(workout_type, 5.0)

    # Формула: калории = MET × вес(кг) × время(часы)
    calories = met * weight * (duration_minutes / 60)

    return round(calories)


def calculate_daily_calories(
    weight: float,
    height: float,
    age: int,
    activity_level: str = "moderate",
    gender: str = "male",
) -> int:
    """
    Рассчитать дневную потребность в калориях.

    Args:
        weight: Вес в кг
        height: Рост в см
        age: Возраст в годах
        activity_level: Уровень активности ("low", "moderate", "high")
        gender: Пол ("male" или "female")

    Returns:
        int: Дневная потребность в калориях
    """
    bmr = calculate_bmr(weight, height, age, gender)

    multiplier = ACTIVITY_MULTIPLIERS.get(activity_level, 1.55)
    daily_calories = bmr * multiplier

    return round(daily_calories)

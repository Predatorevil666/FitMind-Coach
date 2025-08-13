"""
Модуль для централизованного управления роутерами бота.
Содержит функцию для регистрации всех роутеров в диспетчере.
"""

from aiogram import Dispatcher

from bot.handlers.advice import router as advice_router
from bot.handlers.auth import router as auth_router
from bot.handlers.common import router as common_router
from bot.handlers.lab import router as lab_router
from bot.handlers.meal import router as meal_router
from bot.handlers.profile import router as profile_router
from bot.handlers.start import router as start_router
from bot.handlers.stats import router as stats_router
from bot.handlers.workout import router as workout_router
from bot.middleware import auth_middleware


def setup_routers(dp: Dispatcher) -> None:
    """
    Регистрирует все роутеры в диспетчере.

    Args:
        dp: Экземпляр диспетчера
    """
    # Добавляем middleware для проверки авторизации
    dp.message.outer_middleware(auth_middleware)

    # Регистрируем роутеры в порядке приоритета
    dp.include_router(auth_router)  # Авторизация должна быть первой
    dp.include_router(profile_router)  # Затем профиль
    dp.include_router(start_router)  # Затем стартовые команды
    dp.include_router(advice_router)  # Роутер для советов
    dp.include_router(workout_router)  # Тренировки
    dp.include_router(lab_router)  # Лабораторные данные (высокий приоритет)
    dp.include_router(meal_router)  # Питание (низкий приоритет)
    dp.include_router(stats_router)  # Статистика
    dp.include_router(common_router)  # Общие обработчики должны последние

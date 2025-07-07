import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from bot.api_client import UserAPIClient, _api_client
from bot.config import TG_TOKEN
from bot.handlers.auth import router as auth_router
from bot.handlers.common import router as common_router
from bot.handlers.lab import router as lab_router
from bot.handlers.meal import router as meal_router
from bot.handlers.profile import router as profile_router
from bot.handlers.start import router as start_router
from bot.handlers.stats import router as stats_router
from bot.handlers.workout import router as workout_router
from bot.logger import logger


# Middleware для проверки авторизации
async def auth_middleware(handler, event, data):
    # Создаем персональный API клиент для пользователя
    if isinstance(event, Message) and event.from_user:
        user_api_client = UserAPIClient(event.from_user.id)
        data["api_client"] = user_api_client
    else:
        # Fallback для случаев, когда пользователь неизвестен
        data["api_client"] = _api_client

    # Получаем текущее состояние из контекста
    state = data.get("state")
    current_state = await state.get_state() if state else None

    # Пропускаем сообщения в состоянии авторизации или регистрации
    if current_state and (
        current_state.startswith("AuthForm")
        or current_state.startswith("RegisterForm")
    ):
        return await handler(event, data)

    # Пропускаем команды авторизации и регистрации
    if isinstance(event, Message):
        if event.text and (
            event.text.startswith("/start")
            or event.text.startswith("/login")
            or event.text.startswith("/register")
            or event.text.startswith("/help")
            or event.text == "❌ Отмена"
        ):
            return await handler(event, data)

        # Проверяем авторизацию для всех остальных сообщений
        user_api_client = data.get("api_client")
        if user_api_client and hasattr(user_api_client, "telegram_id"):
            # Проверяем, есть ли токен для этого пользователя
            if not _api_client.get_token(user_api_client.telegram_id):
                # Пытаемся автоматически авторизоваться по Telegram ID
                auth_success = await user_api_client.telegram_auth()
                if auth_success:
                    # Авторизация прошла успешно, продолжаем обработку
                    return await handler(event, data)

                # Авторизация не удалась или пользователь не найден
                await event.answer(
                    "⚠️ Для использования бота необходимо привязать ваш "
                    "Telegram аккаунт.\n\n"
                    "Если у вас уже есть аккаунт в системе, используйте "
                    "команду /login для привязки.\n"
                    "Для создания нового аккаунта используйте /register."
                )
                return None

    return await handler(event, data)


# Основная функция
async def main():
    # Выводим информацию о запуске
    logger.info("Запуск бота")

    # Создаем объекты бота и диспетчера с хранилищем состояний
    try:
        bot = Bot(token=TG_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Добавляем middleware для проверки авторизации
        dp.message.outer_middleware(auth_middleware)

        # Регистрируем роутеры
        dp.include_router(auth_router)  # Авторизация должна быть первой
        dp.include_router(profile_router)  # Затем профиль
        dp.include_router(start_router)  # Затем стартовые команды
        dp.include_router(workout_router)
        dp.include_router(meal_router)
        dp.include_router(lab_router)
        dp.include_router(stats_router)
        dp.include_router(
            common_router
        )  # Общие обработчики должны быть последними

        # Запускаем бота
        logger.info("Подключение к Telegram API...")
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем сессию API клиента
        await _api_client.start_session()

        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Закрываем сессию API клиента
        await _api_client.close_session()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

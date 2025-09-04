"""
Модуль с middleware для бота.
"""

from aiogram.types import Message

from bot.api_client import UserAPIClient, _api_client
from bot.constants import AUTH_REQUIRED_MSG


# Middleware для проверки авторизации
async def auth_middleware(handler, event, data):
    """
    Middleware для проверки авторизации пользователя.

    Создает API клиент для пользователя и проверяет авторизацию.
    Пропускает сообщения в определенных состояниях и команды без авторизации.
    """
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

    # Пропускаем сообщения в состоянии авторизации, регистрации или совета
    if current_state and (
        current_state.startswith("AuthForm")
        or current_state.startswith("RegisterForm")
        or current_state.startswith("AdviceForm")
    ):
        return await handler(event, data)

    # Пропускаем команды авторизации, регистрации, помощи и совета
    if isinstance(event, Message):
        if event.text and (
            event.text.startswith("/start")
            or event.text.startswith("/login")
            or event.text.startswith("/register")
            or event.text.startswith("/help")
            or event.text.startswith("/advice")
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
                await event.answer(AUTH_REQUIRED_MSG)
                return None

    return await handler(event, data)

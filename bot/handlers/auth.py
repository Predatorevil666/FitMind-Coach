from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from bot.api_client import UserAPIClient
from bot.keyboards.reply import (
    main_kb,
)

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Определение состояний для FSM
class AuthForm(StatesGroup):
    # Удалены username и password - теперь авторизация только через Telegram ID
    pass


# Определение состояний для регистрации
class RegisterForm(StatesGroup):
    username = State()


# Обработчик команды /login
@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    """Обработчик команды /login - автоматическая авторизация
    через Telegram ID."""
    # Очищаем состояние
    await state.clear()

    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer("❌ Не удалось получить ваш Telegram ID.")
        return

    user_api = get_user_api_client(telegram_id)

    # Пытаемся авторизоваться по Telegram ID
    auth_result = await user_api.telegram_auth()

    if auth_result:
        await message.answer(
            "✅ Вы успешно авторизованы!\n\n"
            "Теперь вы можете использовать все функции бота. "
            "Используйте команду /menu для доступа к основным функциям.",
            reply_markup=main_kb,
        )
    else:
        await message.answer(
            "❌ Не удалось войти в систему.\n\n"
            "Возможные причины:\n"
            "• Вы не зарегистрированы в системе\n"
            "• Проблемы с сервером\n\n"
            "Пожалуйста, зарегистрируйтесь с помощью команды /register",
            reply_markup=main_kb,
        )


# Обработчик команды /register
@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    """Обработчик команды /register."""
    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer("❌ Не удалось получить ваш Telegram ID.")
        return

    # Проверяем, не зарегистрирован ли уже пользователь
    user_api = get_user_api_client(telegram_id)

    # Пытаемся авторизоваться по Telegram ID
    auth_result = await user_api.telegram_auth()
    if auth_result:
        await message.answer(
            "✅ Вы уже зарегистрированы в системе!\n\n"
            "Можете использовать команду /menu для доступа к функциям.",
            reply_markup=main_kb,
        )
        return

    # Регистрируем пользователя автоматически
    user = message.from_user
    username = user.username or f"user_{telegram_id}"

    result = await user_api.client.register_from_telegram(
        telegram_id=telegram_id,
        username=username,
        first_name=user.first_name,
        last_name=user.last_name,
    )

    if result:
        # Автоматически авторизуемся
        auth_result = await user_api.telegram_auth()

        if auth_result:
            await message.answer(
                "✅ Добро пожаловать в FitMind Coach!\n\n"
                "Вы успешно зарегистрированы и авторизованы.\n"
                "Теперь создайте профиль с помощью команды /create_profile",
                reply_markup=main_kb,
            )
        else:
            await message.answer(
                "✅ Вы успешно зарегистрированы!\n\n"
                "Попробуйте использовать команду /start для входа в систему.",
                reply_markup=main_kb,
            )
    else:
        await message.answer(
            "❌ Не удалось зарегистрироваться.\n\n"
            "Возможные причины:\n"
            "• Вы уже зарегистрированы с этого Telegram аккаунта\n"
            "• Проблемы с сервером\n\n"
            "Попробуйте использовать команду /start",
            reply_markup=main_kb,
        )

    # Очищаем состояние
    await state.clear()


# Обработчик команды /logout
@router.message(Command("logout"))
async def cmd_logout(message: Message):
    """Обработчик команды /logout."""
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        user_api = get_user_api_client(telegram_id)
        # Отправляем запрос к API для выхода из системы
        result = await user_api.logout()

        if result:
            await message.answer(
                "✅ Вы успешно вышли из системы!",
                reply_markup=main_kb,
            )
        else:
            await message.answer(
                "❌ Не удалось выйти из системы. "
                "Возможно, вы не были авторизованы.",
                reply_markup=main_kb,
            )


# Обработчик для отмены операции
@router.message(F.text == "❌ Отмена")
async def cancel_operation(message: Message, state: FSMContext):
    """Обработчик кнопки 'Отмена'."""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await message.answer(
        "Операция отменена. Используйте /start для начала работы.",
        reply_markup=ReplyKeyboardRemove(),
    )

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
    username = State()
    password = State()


# Определение состояний для регистрации
class RegisterForm(StatesGroup):
    email = State()
    username = State()
    password = State()
    password_confirm = State()


# Обработчик команды /login
@router.message(Command("login"))
async def cmd_login(message: Message, state: FSMContext):
    """Обработчик команды /login."""
    await state.set_state(AuthForm.username)
    await message.answer(
        "Введите ваш email или имя пользователя:",
        reply_markup=ReplyKeyboardRemove(),
    )


# Обработчик для ввода имени пользователя
@router.message(AuthForm.username)
async def process_username(message: Message, state: FSMContext):
    """Обработчик ввода имени пользователя."""
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, введите корректное имя пользователя или email:",
        )
        return

    username_or_email = message.text.strip()

    # Проверяем, похоже ли это на email
    is_email = "@" in username_or_email and "." in username_or_email

    if not is_email and len(username_or_email) < 3:
        await message.answer(
            "❌ Имя пользователя должно содержать не менее 3 символов. "
            "Пожалуйста, введите корректное имя пользователя или email:",
        )
        return

    # Мы не можем надежно проверить существование пользователя через API,
    # поэтому просто переходим к запросу пароля
    await state.update_data(username=username_or_email)
    await state.set_state(AuthForm.password)
    await message.answer(
        "Введите ваш пароль:",
    )


# Обработчик для ввода пароля
@router.message(AuthForm.password)
async def process_password(message: Message, state: FSMContext):
    """Обработчик ввода пароля."""
    await state.update_data(password=message.text)

    # Получаем данные из состояния
    data = await state.get_data()

    # Получаем Telegram ID пользователя
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        user_api = get_user_api_client(telegram_id)

        # Пытаемся привязать Telegram ID к аккаунту
        link_result = await user_api.client.link_telegram(
            data["username"], data["password"], telegram_id
        )

        if link_result:
            # Привязка успешна, теперь авторизуемся по Telegram ID
            auth_result = await user_api.telegram_auth()
            if auth_result:
                await message.answer(
                    "✅ Telegram аккаунт успешно привязан и вы вошли в систему!\n"
                    "Теперь вы можете использовать бота без повторной авторизации.",
                    reply_markup=main_kb,
                )
            else:
                await message.answer(
                    "✅ Telegram аккаунт привязан, но возникла ошибка при авторизации.\n"
                    "Попробуйте команду /start снова.",
                    reply_markup=main_kb,
                )
        else:
            # Привязка не удалась, пытаемся обычную авторизацию
            result = await user_api.login(data["username"], data["password"])
            if result:
                await message.answer(
                    "✅ Вы успешно вошли в систему!\n"
                    "⚠️ Telegram аккаунт не был привязан. Возможно, он уже привязан к другому аккаунту.",
                    reply_markup=main_kb,
                )
            else:
                await message.answer(
                    "❌ Не удалось войти в систему. \n\n"
                    "Возможные причины:\n"
                    "1. Неверный пароль\n"
                    "2. Пользователь с таким email/именем не существует\n\n"
                    "Пожалуйста, проверьте данные и попробуйте снова или "
                    "зарегистрируйтесь с помощью команды /register",
                )
    else:
        await message.answer(
            "❌ Ошибка получения данных пользователя.",
            reply_markup=main_kb,
        )

    # Очищаем состояние
    await state.clear()


# Обработчик команды /register
@router.message(Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    """Обработчик команды /register."""
    await state.set_state(RegisterForm.email)
    await message.answer(
        "Начинаем процесс регистрации!\n\nВведите ваш email:",
    )


# Обработчик для ввода email
@router.message(RegisterForm.email)
async def process_email(message: Message, state: FSMContext):
    """Обработчик ввода email."""
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, введите корректный email:",
        )
        return

    email = message.text.strip()

    # Валидация email с подробными сообщениями об ошибках
    from bot.validators import validate_email

    is_valid, error_message = validate_email(email)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\nПожалуйста, введите корректный email:",
        )
        return

    await state.update_data(email=email)
    await state.set_state(RegisterForm.username)

    await message.answer(
        "Введите имя пользователя (не менее 3 символов):",
    )


# Обработчик для ввода имени пользователя при регистрации
@router.message(RegisterForm.username)
async def process_reg_username(message: Message, state: FSMContext):
    """Обработчик ввода имени пользователя при регистрации."""
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, введите имя пользователя:",
        )
        return

    username = message.text.strip()

    # Валидация имени пользователя
    from bot.validators import validate_username

    is_valid, error_message = validate_username(username)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите другое имя пользователя:",
        )
        return

    await state.update_data(username=username)
    await state.set_state(RegisterForm.password)

    await message.answer(
        "Введите пароль (не менее 8 символов):",
    )


# Обработчик для ввода пароля при регистрации
@router.message(RegisterForm.password)
async def process_reg_password(message: Message, state: FSMContext):
    """Обработчик ввода пароля при регистрации."""
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, введите пароль:",
        )
        return

    password = message.text

    # Валидация пароля
    from bot.validators import validate_password

    is_valid, error_message = validate_password(password)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\nПожалуйста, введите другой пароль:",
        )
        return

    await state.update_data(password=password)
    await state.set_state(RegisterForm.password_confirm)

    await message.answer(
        "Подтвердите пароль:",
    )


# Обработчик для подтверждения пароля
@router.message(RegisterForm.password_confirm)
async def process_password_confirm(message: Message, state: FSMContext):
    """Обработчик подтверждения пароля."""
    if not message.text:
        await message.answer(
            "❌ Пожалуйста, подтвердите пароль:",
        )
        return

    password_confirm = message.text
    data = await state.get_data()

    # Проверка совпадения паролей
    from bot.validators import validate_passwords_match

    is_valid, error_message = validate_passwords_match(
        data["password"], password_confirm
    )

    if not is_valid:
        await message.answer(
            f"❌ {error_message}. Пожалуйста, введите пароль заново:",
        )
        await state.set_state(RegisterForm.password)
        return

    # Получаем Telegram ID для создания пользовательского API клиента
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        user_api = get_user_api_client(telegram_id)

        # Отправляем запрос к API для регистрации
        result = await user_api.client.register(
            data["email"], data["username"], data["password"]
        )

        if result:
            # Автоматически входим в систему
            login_result = await user_api.login(
                data["email"], data["password"]
            )

            if login_result:
                await message.answer(
                    "✅ Вы успешно зарегистрировались и вошли в систему!\n\n"
                    "Теперь вам нужно создать профиль с помощью команды "
                    "/create_profile",
                    reply_markup=main_kb,
                )
            else:
                await message.answer(
                    "✅ Вы успешно зарегистрировались!\n\n"
                    "Теперь вы можете войти в систему с помощью команды /login",
                    reply_markup=main_kb,
                )
        else:
            await message.answer(
                "❌ Не удалось зарегистрироваться.\n\n"
                "Возможные причины:\n"
                "• Пользователь с таким email уже существует\n"
                "• Имя пользователя уже занято\n"
                "• Проблемы с сервером\n\n"
                "Попробуйте использовать другой email или имя пользователя.",
                reply_markup=main_kb,
            )
    else:
        await message.answer(
            "❌ Ошибка получения данных пользователя.",
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
                "❌ Не удалось выйти из системы. Возможно, вы не были авторизованы.",
                reply_markup=main_kb,
            )
    else:
        await message.answer(
            "❌ Ошибка получения данных пользователя.",
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

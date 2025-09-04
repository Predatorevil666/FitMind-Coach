import re

from typing import Any

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from bot.api_client import UserAPIClient, _api_client
from bot.keyboards.reply import main_kb
from bot.logger import logger

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


@router.message(CommandStart())
async def cmd_start(message: Message, **kwargs) -> None:
    """Обработчик команды /start."""
    # Получаем API клиент из middleware
    api_client = kwargs.get("api_client")
    if api_client is None and message.from_user:
        from bot.api_client import UserAPIClient

        api_client = UserAPIClient(message.from_user.id)

    user = message.from_user
    if user:
        logger.info(
            f"Получена команда /start от пользователя {user.username} "
            f"({user.id})"
        )

    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id and api_client:
        # Пытаемся авторизоваться через Telegram ID
        telegram_auth_result = await api_client.telegram_auth()
        if telegram_auth_result:
            logger.info(
                f"Пользователь {telegram_id} автоматически авторизован "
                f"через Telegram"
            )

    # Проверяем, авторизован ли пользователь и есть ли у него профиль
    if not api_client:
        await message.answer("Ошибка инициализации. Попробуйте позже.")
        return

    profile = await api_client.get_profile()

    if not profile:
        # Проверяем, авторизован ли пользователь (есть ли токен)
        if telegram_id and api_client.client.get_token(telegram_id):
            # Пользователь авторизован, но нет профиля - предлагаем
            # создать профиль
            await message.answer(
                "👋 Привет! Я FitMind Coach - твой ИИ-помощник для спорта "
                "и питания.\n\n"
                "Ты уже авторизован в системе! 🎉\n\n"
                "Для начала работы нужно создать профиль:\n"
                "▫️ Используй команду /create_profile для создания профиля\n\n"
                "Профиль содержит информацию о твоих целях, весе и уровне "
                "физической подготовки."
            )
        else:
            # Пользователь не авторизован - предлагаем регистрацию/логин
            await message.answer(
                "👋 Привет! Я FitMind Coach - твой ИИ-помощник для спорта "
                "и питания.\n\n"
                "Для начала работы тебе нужно зарегистрироваться в системе:\n"
                "▫️ Используй команду /register для регистрации\n"
                "▫️ Если у тебя уже есть аккаунт, используй /login\n\n"
                "После авторизации используй команду "
                "/create_profile для создания "
                "профиля с помощью пошаговой формы."
            )
    else:
        # Если профиль найден, показываем главное меню
        await show_menu(message, profile)


@router.message(Command("menu"))
async def cmd_menu(message: Message) -> None:
    """Обработчик команды /menu."""
    user = message.from_user
    if user:
        logger.info(
            f"Получена команда /menu от пользователя {user.username} "
            f"({user.id})"
        )

    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        # Пытаемся авторизоваться через Telegram ID
        user_api = get_user_api_client(telegram_id)
        await user_api.telegram_auth()

    # Проверяем, авторизован ли пользователь и есть ли у него профиль
    if telegram_id:
        user_api = get_user_api_client(telegram_id)
        profile = await user_api.get_profile()
    else:
        profile = None

    if not profile:
        # Проверяем, авторизован ли пользователь
        if telegram_id and _api_client.get_token(telegram_id):
            await message.answer(
                "Для доступа к меню необходимо создать профиль.\n"
                "Используйте команду /create_profile для создания профиля."
            )
        else:
            await message.answer(
                "Для доступа к меню необходимо авторизоваться.\n"
                "Используйте команду /login для входа или "
                "/register для регистрации."
            )
    else:
        await show_menu(message, profile)


async def show_menu(message: Message, profile: dict[str, Any]) -> None:
    """Показать главное меню с информацией о профиле."""
    # Формируем информацию о профиле
    weight = profile.get("weight", 0)
    target_weight = profile.get("target_weight", 0)
    weight_diff = (
        abs(target_weight - weight) if weight and target_weight else 0
    )

    # Получаем фактические тренировки для подсчета за текущую неделю
    telegram_id = message.from_user.id if message.from_user else None
    if telegram_id:
        user_api = get_user_api_client(telegram_id)
        workouts = await user_api.get_workouts(limit=100)
    else:
        workouts = []

    # Подсчитываем тренировки за текущую неделю
    from bot.utils import count_workouts_this_week, format_workout_count

    actual_workouts_this_week = count_workouts_this_week(workouts or [])

    # Формируем текст с активностью
    activity_text = (
        f"Активность: {format_workout_count(actual_workouts_this_week)} "
        f"на этой неделе"
    )

    await message.answer(
        f"🏁 *Твой профиль:*\n"
        f"Вес: {weight} кг → Цель: {target_weight} кг "
        f"(осталось {weight_diff} кг)\n"
        f"{activity_text}\n\n"
        f"🔻 *Действия:*\n"
        f"/update - Обновить данные\n"
        f"/workout - Добавить тренировку\n"
        f"/food - Добавить питание\n"
        f"/labs - Загрузить анализы\n"
        f"/advice - Получить рекомендации\n"
        f"/progress - Мой прогресс\n"
        f"/status - статус авторизации",
        parse_mode="Markdown",
        reply_markup=main_kb,
    )


@router.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help."""
    user = message.from_user
    if user:
        logger.info(
            f"Получена команда /help от пользователя {user.username} "
            f"({user.id})"
        )

    await message.answer(
        "🔍 Справка по боту FitMind Coach\n\n"
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать эту справку\n"
        "/register - зарегистрироваться\n"
        "/login - войти в аккаунт\n"
        "/workouts_count - статистика тренировок\n"
        "/status - проверить статус авторизации\n\n"
        "Разделы:\n"
        "🏋️ Тренировки - запись и отслеживание тренировок\n"
        "🥗 Питание - ведение дневника питания\n"
        "🩸 Анализы - запись результатов анализов\n"
        "👤 Профиль - управление личным профилем\n"
        "📊 Статистика - просмотр статистики и прогресса\n\n"
        "Если у вас возникли вопросы или проблемы, напишите нам на "
        "support@fitmind-coach.ru",
        reply_markup=main_kb,
    )


@router.message(F.text == "❓ Помощь")
async def help_button(message: Message) -> None:
    """Обработчик кнопки 'Помощь'."""
    await cmd_help(message)


@router.message(Command("workouts_count"))
async def cmd_workouts_count(message: Message) -> None:
    """
    Обработчик команды /workouts_count - показывает статистику тренировок.
    """
    user = message.from_user
    if user:
        logger.info(
            f"Получена команда /workouts_count "
            f"от пользователя {user.username} "
            f"({user.id})"
        )

    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        # Пытаемся авторизоваться через Telegram ID
        user_api = get_user_api_client(telegram_id)
        await user_api.telegram_auth()

        # Проверяем, авторизован ли пользователь и есть ли у него профиль
        profile = await user_api.get_profile()

        if not profile:
            await message.answer(
                "Профиль не найден. Для просмотра статистики необходимо "
                "создать профиль."
            )
            return

        # Получаем все тренировки пользователя
        workouts = await user_api.get_workouts(limit=100)
    else:
        await message.answer("Ошибка получения данных пользователя.")
        return

    if not workouts:
        await message.answer("У вас пока нет записанных тренировок.")
        return

    # Подсчитываем тренировки за текущую неделю
    from bot.utils import count_workouts_this_week, format_workout_count

    actual_workouts_this_week = count_workouts_this_week(workouts)

    # Получаем планируемое количество
    workouts_per_week = profile.get("workouts_per_week", 0)

    # Определяем статус выполнения плана
    plan_status = (
        "✅ План выполнен!"
        if actual_workouts_this_week >= workouts_per_week
        else "⏰ Продолжайте тренироваться!"
    )

    await message.answer(
        f"📊 *Статистика тренировок:*\n\n"
        f"▫️ Всего тренировок: {len(workouts)}\n"
        f"▫️ Планируется в неделю: "
        f"{int(workouts_per_week) if workouts_per_week else 0}\n"
        f"▫️ Выполнено на этой неделе: "
        f"{format_workout_count(actual_workouts_this_week)}\n\n"
        f"{plan_status}",
        parse_mode="Markdown",
        reply_markup=main_kb,
    )


@router.message(
    lambda message: (
        not message.text.startswith("/")
        and not message.from_user.is_bot
        and "цель" in message.text.lower()
        and "вес" in message.text.lower()
        and "уровень" in message.text.lower()
    )
)
async def process_profile_info(message: Message) -> None:
    """Обработчик для парсинга информации о профиле из текстового сообщения."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        return

    # Проверяем, есть ли у пользователя профиль
    user_api = get_user_api_client(telegram_id)
    profile = await user_api.get_profile()

    if profile:
        # Если профиль уже существует, не обрабатываем сообщение
        # как создание профиля
        return

    if not message.text:
        return

    text = message.text.lower()

    # Парсим информацию о профиле
    goal_match = re.search(r"цель:?\s*([а-яА-Я\s]+)", text)
    weight_match = re.search(r"вес:?\s*(\d+)", text)
    target_match = re.search(r"цель:?\s*(\d+)", text)
    level_match = re.search(r"уровень:?\s*([а-яА-Я\s]+)", text)

    if not all([goal_match, weight_match, target_match, level_match]):
        await message.answer(
            "Не удалось распознать все данные профиля. "
            "Пожалуйста, используйте формат:\n"
            '"Цель: [цель], Вес: [число], Цель: [число], '
            'Уровень: [уровень]"\n\n'
            'Например: "Цель: похудеть, Вес: 85, Цель: 75, '
            'Уровень: любитель"\n\n'
            "Или используйте команду /register для регистрации через форму."
        )
        return

    if goal_match and weight_match and target_match and level_match:
        goal = goal_match.group(1).strip()
        weight = float(weight_match.group(1))
        target_weight = float(target_match.group(1))
        level = level_match.group(1).strip()

        # Преобразуем текстовые значения в соответствующие значения для API
        goal_map = {
            "похудеть": "weight_loss",
            "набрать массу": "muscle_gain",
            "подготовка к марафону": "endurance",
            "здоровье": "health",
        }

        api_goal = goal_map.get(goal, "other")

        # Создаем профиль через API
        profile_data = {
            "weight": weight,
            "target_weight": target_weight,
            "goal": api_goal,
            "workouts_per_week": 3,  # Значение по умолчанию
        }

        # Сначала регистрируем пользователя с временными данными
        # В реальном приложении нужно было бы запросить email и пароль
        user = message.from_user
        if user:
            user_data = {
                "email": f"user_{user.id}@example.com",
                "username": f"user_{user.id}",
                "password": "temporary_password",
            }

            # Регистрируем пользователя и создаем профиль
            reg_result = await user_api.client.register(
                user_data["email"],
                user_data["username"],
                user_data["password"],
            )

            if reg_result:
                # Авторизуемся
                login_result = await user_api.login(
                    user_data["email"], user_data["password"]
                )

                if login_result:
                    # Создаем профиль
                    profile_result = await user_api.create_profile(
                        profile_data
                    )

                    if profile_result:
                        await message.answer(
                            "✅ Профиль успешно создан!\n\n"
                            f"Цель: {goal}\n"
                            f"Текущий вес: {weight} кг\n"
                            f"Целевой вес: {target_weight} кг\n"
                            f"Уровень: {level}\n\n"
                            "Теперь вы можете использовать все функции бота. "
                            "Используйте /menu для доступа к меню.",
                            reply_markup=main_kb,
                        )
                    else:
                        await message.answer(
                            "❌ Не удалось создать профиль. "
                            "Пожалуйста, попробуйте позже."
                        )
                else:
                    await message.answer(
                        "❌ Не удалось авторизоваться. "
                        "Пожалуйста, попробуйте позже."
                    )
            else:
                await message.answer(
                    "❌ Не удалось зарегистрироваться. "
                    "Пожалуйста, используйте команду /register."
                )


@router.message(Command("status"))
async def cmd_status(message: Message) -> None:
    """Обработчик команды /status - показывает статус авторизации."""
    user = message.from_user
    if user:
        logger.info(
            f"Получена команда /status от пользователя {user.username} "
            f"({user.id})"
        )

    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if telegram_id:
        # Пытаемся авторизоваться через Telegram ID
        user_api = get_user_api_client(telegram_id)
        telegram_auth_result = await user_api.telegram_auth()
        if telegram_auth_result:
            logger.info(
                f"Пользователь {telegram_id} "
                f"автоматически авторизован через Telegram"
            )

        # Проверяем токен
        has_token = bool(user_api.client.get_token(telegram_id))

        # Проверяем профиль
        profile = await user_api.get_profile()
        has_profile = bool(profile)
    else:
        has_token = False
        has_profile = False

    # Формируем сообщение о статусе
    status_text = "🔍 *Статус авторизации:*\n\n"

    if telegram_id:
        status_text += f"📱 Telegram ID: {telegram_id}\n"

    if has_token:
        status_text += "✅ Авторизован: Да\n"
    else:
        status_text += "❌ Авторизован: Нет\n"

    if has_profile:
        status_text += "✅ Профиль: Создан\n"
    else:
        status_text += "❌ Профиль: Не создан\n"

    status_text += "\n"

    if not has_token:
        status_text += "💡 Для авторизации используйте:\n"
        status_text += "▫️ /login - если у вас есть аккаунт\n"
        status_text += "▫️ /register - для создания нового аккаунта\n"
    elif not has_profile:
        status_text += "💡 Для создания профиля используйте:\n"
        status_text += "▫️ /create_profile - создать профиль\n"
    else:
        status_text += "🎉 Всё готово! Можете пользоваться ботом."

    await message.answer(
        status_text,
        parse_mode="Markdown",
        reply_markup=main_kb,
    )

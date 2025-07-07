from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup

from bot.api_client import UserAPIClient
from bot.keyboards.reply import (
    cancel_kb,
    main_kb,
    profile_kb,
)
from bot.utils import format_workout_count

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Определение состояний для создания профиля
class ProfileForm(StatesGroup):
    goal = State()
    weight = State()
    target_weight = State()
    level = State()


# Определение состояний для редактирования профиля
class EditProfileForm(StatesGroup):
    goal = State()
    weight = State()
    target_weight = State()
    level = State()


# Определение состояний для выборочного редактирования профиля
class EditSingleFieldForm(StatesGroup):
    field_selection = State()
    goal = State()
    weight = State()
    target_weight = State()
    level = State()


# Обработчик команды /update
@router.message(Command("update"))
async def cmd_update(message: Message, state: FSMContext) -> None:
    """Обработчик команды /update."""
    # Перенаправляем на редактирование профиля
    await edit_profile(message, state)


# Обработчик команды /profile
@router.message(Command("profile"))
async def cmd_profile(message: Message) -> None:
    """Обработчик команды /profile."""
    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer(
            "Для доступа к профилю необходимо авторизоваться.\n"
            "Используйте команду /login для входа или "
            "/register для регистрации."
        )
        return

    # Получаем API клиент для пользователя
    user_api_client = get_user_api_client(telegram_id)
    # Пытаемся авторизоваться через Telegram ID
    await user_api_client.telegram_auth()
    # Проверяем, авторизован ли пользователь
    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Для доступа к профилю необходимо авторизоваться.\n"
            "Используйте команду /login для входа или "
            "/register для регистрации."
        )
        return

    await message.answer(
        "👤 Управление профилем",
        reply_markup=profile_kb,
    )


# Обработчик кнопки 'Профиль'
@router.message(F.text == "👤 Профиль")
async def profile_button(message: Message) -> None:
    """Обработчик кнопки 'Профиль'."""
    await cmd_profile(message)


# Обработчик кнопки 'Просмотреть профиль'
@router.message(F.text == "👁️ Просмотреть профиль")
async def view_profile(message: Message) -> None:
    """Обработчик кнопки 'Просмотреть профиль'."""
    # Сначала пытаемся авторизоваться через Telegram ID, если он есть
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer(
            "Профиль не найден. Используйте команду /create_profile для создания."
        )
        return

    # Получаем API клиент для пользователя
    user_api_client = get_user_api_client(telegram_id)
    # Пытаемся авторизоваться через Telegram ID
    await user_api_client.telegram_auth()

    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Профиль не найден. Используйте команду /create_profile для создания."
        )
        return

    # Получаем данные профиля
    weight = profile.get("weight", 0)  # Используем правильное поле weight
    target_weight = profile.get("target_weight", 0)
    goal = profile.get("goal", "")

    # Получаем фактические тренировки для подсчета за текущую неделю
    workouts = await user_api_client.get_workouts(
        limit=100
    )  # Получаем больше для точного подсчета

    # Подсчитываем тренировки за текущую неделю
    from bot.utils import count_workouts_this_week

    actual_workouts_this_week = count_workouts_this_week(workouts or [])

    # Преобразуем значения для отображения
    goal_map = {
        "weight_loss": "Похудение",
        "muscle_gain": "Набор массы",
        "endurance": "Выносливость",
        "health": "Здоровье",
        "other": "Другое",
    }

    goal_display = goal_map.get(goal, "Не указано")

    await message.answer(
        f"👤 *Ваш профиль:*\n\n"
        f"▫️ Цель: {goal_display}\n"
        f"▫️ Текущий вес: {weight} кг\n"
        f"▫️ Целевой вес: {target_weight} кг\n"
        f"▫️ На этой неделе: {format_workout_count(actual_workouts_this_week)}\n\n"
        f"Для редактирования профиля нажмите '✏️ Редактировать профиль'",
        parse_mode="Markdown",
        reply_markup=profile_kb,
    )


# Обработчик кнопки 'Редактировать профиль'
@router.message(F.text == "✏️ Редактировать профиль")
async def edit_profile(message: Message, state: FSMContext) -> None:
    """Обработчик кнопки 'Редактировать профиль'."""
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer("Ошибка авторизации.")
        return

    # Получаем API клиент для пользователя
    user_api_client = get_user_api_client(telegram_id)
    # Проверяем, авторизован ли пользователь
    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Профиль не найден. Используйте команду /create_profile для создания."
        )
        return

    # Получаем текущие данные профиля
    current_goal = profile.get("goal", "")
    current_weight = profile.get(
        "weight", 0
    )  # Используем правильное поле weight
    current_target_weight = profile.get("target_weight", 0)
    current_workouts_per_week = profile.get("workouts_per_week", 0)

    # Получаем фактические тренировки для подсчета за текущую неделю
    workouts = await user_api_client.get_workouts(limit=100)

    # Подсчитываем тренировки за текущую неделю
    from bot.utils import count_workouts_this_week

    actual_workouts_this_week = count_workouts_this_week(workouts or [])

    # Преобразуем значения для отображения
    goal_map = {
        "weight_loss": "Похудение",
        "muscle_gain": "Набор массы",
        "endurance": "Выносливость",
        "health": "Здоровье",
        "other": "Другое",
    }

    current_goal_display = goal_map.get(current_goal, "Не указано")

    # Сохраняем текущие данные в состоянии
    await state.update_data(
        current_goal=current_goal,
        current_weight=current_weight,
        current_target_weight=current_target_weight,
        current_workouts_per_week=current_workouts_per_week,
    )

    # Создаем клавиатуру для выбора поля для редактирования
    edit_field_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Изменить цель"),
                KeyboardButton(text="Изменить текущий вес"),
            ],
            [
                KeyboardButton(text="Изменить целевой вес"),
                KeyboardButton(text="Изменить уровень"),
            ],
            [
                KeyboardButton(text="Изменить всё"),
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите, что хотите изменить",
    )

    await state.set_state(EditSingleFieldForm.field_selection)
    await message.answer(
        f"Выберите, что вы хотите изменить в профиле:\n\n"
        f"Текущие данные:\n"
        f"▫️ Цель: {current_goal_display}\n"
        f"▫️ Текущий вес: {current_weight} кг\n"
        f"▫️ Целевой вес: {current_target_weight} кг\n"
        f"▫️ На этой неделе: {format_workout_count(actual_workouts_this_week)}",
        reply_markup=edit_field_kb,
    )


# Обработчик выбора поля для редактирования
@router.message(EditSingleFieldForm.field_selection)
async def process_field_selection(message: Message, state: FSMContext) -> None:
    """Обработчик выбора поля для редактирования."""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Редактирование профиля отменено.",
            reply_markup=profile_kb,
        )
        return

    if message.text == "Изменить всё":
        # Переходим к полному редактированию профиля
        await full_edit_profile(message, state)
        return

    # Создаем клавиатуры для разных полей
    goal_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Похудение"),
                KeyboardButton(text="Набор массы"),
            ],
            [
                KeyboardButton(text="Выносливость"),
                KeyboardButton(text="Здоровье"),
            ],
            [
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите цель",
    )

    level_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Начинающий"),
                KeyboardButton(text="Любитель"),
            ],
            [
                KeyboardButton(text="Продвинутый"),
                KeyboardButton(text="Профессионал"),
            ],
            [
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите уровень",
    )

    # Определяем, какое поле редактируем
    if message.text == "Изменить цель":
        await state.set_state(EditSingleFieldForm.goal)
        await message.answer(
            "Выберите вашу цель:",
            reply_markup=goal_kb,
        )
    elif message.text == "Изменить текущий вес":
        await state.set_state(EditSingleFieldForm.weight)
        await message.answer(
            "Введите ваш текущий вес (в кг):",
            reply_markup=cancel_kb,
        )
    elif message.text == "Изменить целевой вес":
        await state.set_state(EditSingleFieldForm.target_weight)
        await message.answer(
            "Введите ваш целевой вес (в кг):",
            reply_markup=cancel_kb,
        )
    elif message.text == "Изменить уровень":
        await state.set_state(EditSingleFieldForm.level)
        await message.answer(
            "Выберите ваш уровень подготовки:",
            reply_markup=level_kb,
        )
    else:
        # Получаем клавиатуру из предыдущей функции
        data = await state.get_data()
        current_goal = data.get("current_goal", "")
        current_weight = data.get("current_weight", 0)
        current_target_weight = data.get("current_target_weight", 0)

        goal_map = {
            "weight_loss": "Похудение",
            "muscle_gain": "Набор массы",
            "endurance": "Выносливость",
            "health": "Здоровье",
            "other": "Другое",
        }

        current_goal_display = goal_map.get(current_goal, "Не указано")

        # Пересоздаем клавиатуру
        edit_field_kb = ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Изменить цель"),
                    KeyboardButton(text="Изменить текущий вес"),
                ],
                [
                    KeyboardButton(text="Изменить целевой вес"),
                    KeyboardButton(text="Изменить уровень"),
                ],
                [
                    KeyboardButton(text="Изменить всё"),
                    KeyboardButton(text="❌ Отмена"),
                ],
            ],
            resize_keyboard=True,
            input_field_placeholder="Выберите, что хотите изменить",
        )

        # Получаем фактические тренировки для подсчета за текущую неделю
        telegram_id = message.from_user.id if message.from_user else None
        if telegram_id:
            user_api_client = get_user_api_client(telegram_id)
            workouts = await user_api_client.get_workouts(limit=100)

            # Подсчитываем тренировки за текущую неделю
            from bot.utils import count_workouts_this_week

            actual_workouts_this_week = count_workouts_this_week(
                workouts or []
            )
        else:
            actual_workouts_this_week = 0

        await message.answer(
            "Пожалуйста, выберите один из предложенных вариантов.\n\n"
            f"Текущие данные:\n"
            f"▫️ Цель: {current_goal_display}\n"
            f"▫️ Текущий вес: {current_weight} кг\n"
            f"▫️ Целевой вес: {current_target_weight} кг\n"
            f"▫️ На этой неделе: {format_workout_count(actual_workouts_this_week)}",
            reply_markup=edit_field_kb,
        )


# Вспомогательная функция для перехода к полному редактированию профиля
async def full_edit_profile(message: Message, state: FSMContext) -> None:
    """Переход к полному редактированию профиля."""
    # Создаем клавиатуру для выбора цели
    goal_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Похудение"),
                KeyboardButton(text="Набор массы"),
            ],
            [
                KeyboardButton(text="Выносливость"),
                KeyboardButton(text="Здоровье"),
            ],
            [
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите цель",
    )

    # Получаем данные из состояния
    data = await state.get_data()

    # Преобразуем значения для отображения
    goal_map = {
        "weight_loss": "Похудение",
        "muscle_gain": "Набор массы",
        "endurance": "Выносливость",
        "health": "Здоровье",
        "other": "Другое",
    }

    current_goal_display = goal_map.get(
        data.get("current_goal", ""), "Не указано"
    )

    await state.set_state(EditProfileForm.goal)
    await message.answer(
        f"Редактирование профиля\n\n"
        f"Текущие данные:\n"
        f"▫️ Цель: {current_goal_display}\n"
        f"▫️ Текущий вес: {data.get('current_weight', 0)} кг\n"
        f"▫️ Целевой вес: {data.get('current_target_weight', 0)} кг\n\n"
        f"Шаг 1/4: Выберите вашу цель:",
        reply_markup=goal_kb,
    )


# Обработчик выбора цели при выборочном редактировании
@router.message(EditSingleFieldForm.goal)
async def process_single_goal(message: Message, state: FSMContext) -> None:
    """Обработчик выбора цели при выборочном редактировании."""
    if not message.text:
        await message.answer(
            "Пожалуйста, выберите цель из предложенных вариантов."
        )
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Редактирование профиля отменено.",
            reply_markup=profile_kb,
        )
        return

    # Преобразуем текст в значение для API
    goal_map = {
        "Похудение": "weight_loss",
        "Набор массы": "muscle_gain",
        "Выносливость": "endurance",
        "Здоровье": "health",
    }

    goal = goal_map.get(message.text, "other")

    # Получаем текущие данные профиля
    profile = await get_user_api_client(message.from_user.id).get_profile()

    if not profile:
        await message.answer(
            "Профиль не найден. Используйте команду /create_profile для создания."
        )
        await state.clear()
        return

    # Создаем данные для обновления, сохраняя остальные поля
    profile_data = {
        "weight": profile.get("weight", 0),
        "target_weight": profile.get("target_weight", 0),
        "goal": goal,  # Обновляем только цель
        "workouts_per_week": profile.get("workouts_per_week", 0),
    }

    # Отправляем запрос к API для обновления профиля
    profile_result = await get_user_api_client(
        message.from_user.id
    ).update_profile(profile_data)

    if profile_result:
        await message.answer(
            f"✅ Цель успешно обновлена на '{message.text}'!",
            reply_markup=main_kb,  # Возвращаем в главное меню
        )
    else:
        await message.answer(
            "❌ Не удалось обновить профиль. Возможно, вы не авторизованы.",
            reply_markup=main_kb,  # Возвращаем в главное меню
        )

    await state.clear()


# Обработчик ввода веса при выборочном редактировании
@router.message(EditSingleFieldForm.weight)
async def process_single_weight(message: Message, state: FSMContext) -> None:
    """Обработчик ввода веса при выборочном редактировании."""
    if not message.text:
        await message.answer("Пожалуйста, введите ваш текущий вес.")
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Редактирование профиля отменено.",
            reply_markup=profile_kb,
        )
        return

    try:
        weight = float(message.text.replace(",", "."))
        if weight <= 0 or weight > 300:
            await message.answer(
                "Пожалуйста, введите корректный вес (от 1 до 300 кг):"
            )
            return

        # Получаем текущие данные профиля
        profile = await get_user_api_client(message.from_user.id).get_profile()

        if not profile:
            await message.answer(
                "Профиль не найден. Используйте команду /create_profile для создания."
            )
            await state.clear()
            return

        # Создаем данные для обновления, сохраняя остальные поля
        profile_data = {
            "weight": weight,  # Обновляем только вес
            "target_weight": profile.get("target_weight", 0),
            "goal": profile.get("goal", ""),
            "workouts_per_week": profile.get("workouts_per_week", 0),
        }

        # Отправляем запрос к API для обновления профиля
        profile_result = await get_user_api_client(
            message.from_user.id
        ).update_profile(profile_data)

        if profile_result:
            await message.answer(
                f"✅ Текущий вес успешно обновлен на {weight} кг!",
                reply_markup=main_kb,  # Возвращаем в главное меню
            )
        else:
            await message.answer(
                "❌ Не удалось обновить профиль. Возможно, вы не авторизованы.",
                reply_markup=main_kb,  # Возвращаем в главное меню
            )

        await state.clear()
    except ValueError:
        await message.answer(
            "Пожалуйста, введите число (например, 75.5):",
            reply_markup=cancel_kb,
        )


# Обработчик ввода целевого веса при выборочном редактировании
@router.message(EditSingleFieldForm.target_weight)
async def process_single_target_weight(
    message: Message, state: FSMContext
) -> None:
    """Обработчик ввода целевого веса при выборочном редактировании."""
    if not message.text:
        await message.answer("Пожалуйста, введите ваш целевой вес.")
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Редактирование профиля отменено.",
            reply_markup=profile_kb,
        )
        return

    # Валидация целевого веса
    from bot.validators import validate_weight

    is_valid, error_message, target_weight = validate_weight(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректный целевой вес:"
        )
        return

        # Получаем текущие данные профиля
        profile = await get_user_api_client(message.from_user.id).get_profile()

        if not profile:
            await message.answer(
                "Профиль не найден. Используйте команду /create_profile для создания."
            )
            await state.clear()
            return

        # Создаем данные для обновления, сохраняя остальные поля
        profile_data = {
            "weight": profile.get("weight", 0),
            "target_weight": target_weight,  # Обновляем только целевой вес
            "goal": profile.get("goal", ""),
            "workouts_per_week": profile.get("workouts_per_week", 0),
        }

        # Отправляем запрос к API для обновления профиля
        profile_result = await get_user_api_client(
            message.from_user.id
        ).update_profile(profile_data)

        if profile_result:
            await message.answer(
                f"✅ Целевой вес успешно обновлен на {target_weight} кг!",
                reply_markup=main_kb,  # Возвращаем в главное меню
            )
        else:
            await message.answer(
                "❌ Не удалось обновить профиль. Возможно, вы не авторизованы.",
                reply_markup=main_kb,  # Возвращаем в главное меню
            )

        await state.clear()


# Обработчик выбора уровня при выборочном редактировании
@router.message(EditSingleFieldForm.level)
async def process_single_level(message: Message, state: FSMContext) -> None:
    """Обработчик выбора уровня при выборочном редактировании."""
    if not message.text:
        await message.answer(
            "Пожалуйста, выберите уровень из предложенных вариантов."
        )
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Редактирование профиля отменено.",
            reply_markup=profile_kb,
        )
        return

    # Преобразуем текст в значение для API
    level_map = {
        "Начинающий": 1,
        "Любитель": 2,
        "Продвинутый": 3,
        "Профессионал": 5,
    }

    workouts_per_week = level_map.get(message.text, 3)

    # Получаем текущие данные профиля
    profile = await get_user_api_client(message.from_user.id).get_profile()

    if not profile:
        await message.answer(
            "Профиль не найден. Используйте команду /create_profile для создания."
        )
        await state.clear()
        return

    # Создаем данные для обновления, сохраняя остальные поля
    profile_data = {
        "weight": profile.get("weight", 0),
        "target_weight": profile.get("target_weight", 0),
        "goal": profile.get("goal", ""),
        "workouts_per_week": int(
            workouts_per_week
        ),  # Преобразуем в целое число
    }

    # Отправляем запрос к API для обновления профиля
    profile_result = await get_user_api_client(
        message.from_user.id
    ).update_profile(profile_data)

    if profile_result:
        await message.answer(
            f"✅ Уровень подготовки успешно обновлен на '{message.text}'!",
            reply_markup=main_kb,  # Возвращаем в главное меню
        )
    else:
        await message.answer(
            "❌ Не удалось обновить профиль. Возможно, вы не авторизованы.",
            reply_markup=main_kb,  # Возвращаем в главное меню
        )

    await state.clear()


# Обработчик команды /create_profile
@router.message(Command("create_profile"))
async def cmd_create_profile(message: Message, state: FSMContext) -> None:
    """Обработчик команды /create_profile."""
    telegram_id = message.from_user.id if message.from_user else None

    if not telegram_id:
        await message.answer("Ошибка авторизации.")
        return

    # Получаем API клиент для пользователя
    user_api_client = get_user_api_client(telegram_id)
    profile = await user_api_client.get_profile()

    if profile:
        await message.answer(
            "У вас уже есть профиль. Используйте команду /profile для просмотра."
        )
        return

    # Создаем клавиатуру для выбора цели
    goal_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Похудение"),
                KeyboardButton(text="Набор массы"),
            ],
            [
                KeyboardButton(text="Выносливость"),
                KeyboardButton(text="Здоровье"),
            ],
            [
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите цель",
    )

    await state.set_state(ProfileForm.goal)
    await message.answer(
        "Давайте создадим ваш профиль!\n\nШаг 1/4: Выберите вашу цель:",
        reply_markup=goal_kb,
    )


# Обработчик выбора цели
@router.message(ProfileForm.goal)
async def process_goal(message: Message, state: FSMContext) -> None:
    """Обработчик выбора цели."""
    if not message.text:
        await message.answer(
            "Пожалуйста, выберите цель из предложенных вариантов."
        )
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Создание профиля отменено.",
            reply_markup=main_kb,
        )
        return

    # Преобразуем текст в значение для API
    goal_map = {
        "Похудение": "weight_loss",
        "Набор массы": "muscle_gain",
        "Выносливость": "endurance",
        "Здоровье": "health",
    }

    goal = goal_map.get(message.text, "other")
    await state.update_data(goal=goal)
    await state.set_state(ProfileForm.weight)

    await message.answer(
        "Шаг 2/4: Введите ваш текущий вес (в кг):",
        reply_markup=cancel_kb,
    )


# Обработчик ввода текущего веса
@router.message(ProfileForm.weight)
async def process_weight(message: Message, state: FSMContext) -> None:
    """Обработчик ввода текущего веса."""
    if not message.text:
        await message.answer("Пожалуйста, введите ваш текущий вес.")
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Создание профиля отменено.",
            reply_markup=main_kb,
        )
        return

    # Валидация веса
    from bot.validators import validate_weight

    is_valid, error_message, weight = validate_weight(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\nПожалуйста, введите корректный вес:"
        )
        return

    await state.update_data(weight=weight)
    await state.set_state(ProfileForm.target_weight)

    await message.answer(
        "Шаг 3/4: Введите ваш целевой вес (в кг):",
        reply_markup=cancel_kb,
    )


# Обработчик ввода целевого веса
@router.message(ProfileForm.target_weight)
async def process_target_weight(message: Message, state: FSMContext) -> None:
    """Обработчик ввода целевого веса."""
    if not message.text:
        await message.answer("Пожалуйста, введите ваш целевой вес.")
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Создание профиля отменено.",
            reply_markup=main_kb,
        )
        return

    # Валидация целевого веса
    from bot.validators import validate_weight

    is_valid, error_message, target_weight = validate_weight(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректный целевой вес:"
        )
        return

    await state.update_data(target_weight=target_weight)
    await state.set_state(ProfileForm.level)

    # Создаем клавиатуру для выбора уровня
    level_kb = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="Начинающий"),
                KeyboardButton(text="Любитель"),
            ],
            [
                KeyboardButton(text="Продвинутый"),
                KeyboardButton(text="Профессионал"),
            ],
            [
                KeyboardButton(text="❌ Отмена"),
            ],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите уровень",
    )

    await message.answer(
        "Шаг 4/4: Выберите ваш уровень подготовки:",
        reply_markup=level_kb,
    )


# Обработчик выбора уровня
@router.message(ProfileForm.level)
async def process_level(message: Message, state: FSMContext) -> None:
    """Обработчик выбора уровня."""
    if not message.text:
        await message.answer(
            "Пожалуйста, выберите уровень из предложенных вариантов."
        )
        return

    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Создание профиля отменено.",
            reply_markup=main_kb,
        )
        return

    # Преобразуем текст в значение для API
    level_map = {
        "Начинающий": 1,
        "Любитель": 2,
        "Продвинутый": 3,
        "Профессионал": 5,
    }

    workouts_per_week = level_map.get(message.text, 3)
    await state.update_data(workouts_per_week=workouts_per_week)

    # Получаем все данные из состояния
    data = await state.get_data()

    # Создаем профиль через API
    profile_data = {
        "weight": data["weight"],
        "target_weight": data["target_weight"],
        "goal": data["goal"],
        "workouts_per_week": data["workouts_per_week"],
    }

    # Отображаем цель в понятном виде
    goal_display_map = {
        "weight_loss": "Похудение",
        "muscle_gain": "Набор массы",
        "endurance": "Выносливость",
        "health": "Здоровье",
        "other": "Другое",
    }
    goal_display = goal_display_map.get(data["goal"], "Не указано")

    # Отправляем запрос к API для создания профиля
    profile_result = await get_user_api_client(
        message.from_user.id
    ).create_profile(profile_data)

    if profile_result:
        await message.answer(
            "✅ Профиль успешно создан!\n\n"
            f"▫️ Цель: {goal_display}\n"
            f"▫️ Текущий вес: {data['weight']} кг\n"
            f"▫️ Целевой вес: {data['target_weight']} кг\n"
            f"▫️ Уровень: {message.text}\n\n"
            "Теперь вы можете использовать все функции бота.",
            reply_markup=main_kb,
        )
    else:
        await message.answer(
            "❌ Не удалось создать профиль. Возможно, вы не авторизованы.\n"
            "Используйте команду /login для входа или "
            "/register для регистрации.",
            reply_markup=main_kb,
        )

    # Очищаем состояние
    await state.clear()


# Обработчик кнопки 'Назад'
@router.message(F.text == "🔙 Назад")
async def back_to_main(message: Message) -> None:
    """Обработчик кнопки 'Назад'."""
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_kb,
    )

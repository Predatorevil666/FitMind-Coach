from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.api_client import UserAPIClient
from bot.constants import (
    CALORIES_PER_MIN,
    SPECIFIC_EXERCISES,
    TEMPLATE_WORKOUTS,
    WORKOUT_TYPE_DISPLAY,
)
from bot.keyboards.reply import (
    main_kb,
    workout_form_kb,
    workout_kb,
    workout_template_kb,
    workout_type_kb,
)
from bot.utils import (
    format_datetime,
    get_utc_now,
    parse_datetime,
    parse_workout_data,
)

# Создаем роутер для обработчиков тренировок
router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Определяем состояния для формы добавления тренировки
class WorkoutForm(StatesGroup):
    """Форма для добавления тренировки."""

    name = State()
    type = State()
    duration = State()
    calories = State()
    notes = State()


# Обработчик команды /workout
@router.message(Command("workout"))
async def cmd_workout(message: Message):
    """Обработчик команды /workout."""
    await workouts_menu(message)


# Обработчик для распознавания тренировки из текста
@router.message(
    lambda message: not message.text.startswith("/")
    and not message.text.startswith("💪")
    and not message.text.startswith("🏃")
    and not message.text.startswith("🦵")
    and not message.text.startswith("🏋️")
    and not message.text.startswith("🫁")
    and not message.text.startswith("🧘")
    and not message.text.startswith("🤸")
    and any(
        keyword in message.text.lower()
        for keyword in ["силовая", "кардио", "йога", "мин", "минут"]
    )
)
async def parse_workout_text(message: Message):
    """Парсинг данных о тренировке из текстового сообщения."""
    # Используем функцию для парсинга данных о тренировке
    if message.text:
        workout_type, duration, intensity, workout_date = parse_workout_data(
            message.text
        )

        # Если тип не определен, пытаемся определить его по ключевым словам
        if not workout_type:
            text_lower = message.text.lower()
            if "силовая" in text_lower:
                workout_type = "strength"
            elif "кардио" in text_lower:
                workout_type = "cardio"
            elif "йога" in text_lower:
                workout_type = "flexibility"
            elif "растяжка" in text_lower:
                workout_type = "flexibility"
            elif "ног" in text_lower:
                workout_type = "strength"
            elif "рук" in text_lower:
                workout_type = "strength"
            elif "спин" in text_lower:
                workout_type = "strength"
            elif "груд" in text_lower:
                workout_type = "strength"

        if not workout_type:
            await message.answer(
                "Не удалось определить тип тренировки. "
                "Пожалуйста, укажите тип явно."
            )
            return

        if not duration:
            await message.answer(
                "Не удалось определить продолжительность тренировки. "
                "Пожалуйста, укажите продолжительность в минутах."
            )
            return

        # Если интенсивность не указана, используем среднюю (5)
        intensity = intensity or 5

        # Если дата не указана, используем текущую
        workout_date = workout_date or get_utc_now()

        # Рассчитываем примерные калории на основе типа, длительности
        # и интенсивности
        base_calories = CALORIES_PER_MIN.get(workout_type, 5) * duration
        intensity_factor = intensity / 5  # Нормализуем интенсивность
        calories = int(base_calories * intensity_factor)

        # Формируем данные для API
        # Пытаемся извлечь конкретное упражнение из текста
        text_lower = message.text.lower()
        specific_exercise = None

        # Ищем конкретные упражнения
        for exercise in SPECIFIC_EXERCISES:
            if exercise in text_lower:
                specific_exercise = exercise.capitalize()
                break

        # Формируем название тренировки
        if specific_exercise:
            workout_name = specific_exercise
        else:
            workout_name = f"{workout_type.capitalize()} тренировка"

        workout_data = {
            "name": workout_name,
            "type": workout_type,
            "duration_minutes": duration,
            "calories_burned": calories,
            "notes": message.text,
            "date": format_datetime(workout_date),
        }

        # Отправляем запрос к API
        telegram_id = message.from_user.id if message.from_user else None
        if not telegram_id:
            await message.answer("Ошибка авторизации.")
            return

        user_api_client = get_user_api_client(telegram_id)
        result = await user_api_client.create_workout(workout_data)

        if result:
            # Получаем отображаемое название типа тренировки
            workout_type_display = WORKOUT_TYPE_DISPLAY.get(
                workout_type, "Тренировка"
            )

            await message.answer(
                f"✅ Добавлена тренировка: {workout_type_display}\n"
                f"Продолжительность: {duration} мин\n"
                f"Калории: {calories}"
            )
        else:
            await message.answer(
                "❌ Не удалось добавить тренировку. "
                "Пожалуйста, попробуйте позже."
            )


# Обработчик для кнопки "Тренировки"
@router.message(F.text == "🏋️ Тренировки")
async def workouts_menu(message: Message):
    """Обработчик кнопки 'Тренировки'."""
    await message.answer(
        "🏋️ Меню тренировок\n\nВыберите действие:",
        reply_markup=workout_kb,
    )


# Обработчик для кнопки "Назад" в меню тренировок
@router.message(F.text == "🔙 Назад")
async def back_to_main_menu(message: Message):
    """Обработчик кнопки 'Назад'."""
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_kb,
    )


# Обработчик для кнопки "Мои тренировки"
@router.message(F.text == "📋 Мои тренировки")
async def list_workouts(message: Message):
    """Обработчик кнопки 'Мои тренировки'."""
    # Получаем список тренировок
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=workout_kb,
        )
        return

    await message.answer("Запрашиваю список тренировок...")
    user_api_client = get_user_api_client(telegram_id)
    workouts = await user_api_client.get_workouts(limit=10)

    if not workouts:
        await message.answer(
            "У вас пока нет добавленных тренировок.",
            reply_markup=workout_kb,
        )
        return

    # Отладочное сообщение
    await message.answer(f"Получено тренировок: {len(workouts)}")

    # Формируем сообщение со списком тренировок
    workouts_text = "📋 *Ваши последние тренировки:*\n\n"

    for workout in workouts:
        workout_date = parse_datetime(workout["date"]).strftime("%d.%m.%Y")

        # Определяем эмодзи для типа тренировки
        type_emoji = "🔄"
        if workout["type"] == "strength":
            type_emoji = "💪"
        elif workout["type"] == "cardio":
            type_emoji = "🏃"
        elif workout["type"] == "flexibility":
            type_emoji = "🧘"
        elif workout["type"] == "hiit":
            type_emoji = "⚡"

        # Получаем калории, если они есть
        calories = workout.get("calories_burned")
        calories_text = f"🔥 {calories} ккал" if calories else "🔥 не указано"

        # Формируем описание тренировки
        workout_description = workout["name"]

        # Если есть заметки с деталями упражнений, добавляем их
        notes = workout.get("notes", "").strip()
        if notes and notes != "-" and len(notes) > 10:
            # Ограничиваем длину заметок для краткого отображения
            if len(notes) > 50:
                notes_short = notes[:47] + "..."
            else:
                notes_short = notes
            workout_description = f"{workout['name']}: {notes_short}"

        workouts_text += (
            f"*{workout_date}*: {type_emoji} {workout_description}\n"
            f"⏱ {workout['duration_minutes']} мин, {calories_text}\n\n"
        )

    await message.answer(
        workouts_text, reply_markup=workout_kb, parse_mode="Markdown"
    )


# Обработчик для кнопки "Добавить тренировку"
@router.message(F.text == "➕ Добавить тренировку")
async def add_workout_start(message: Message, state: FSMContext):
    """Обработчик кнопки 'Добавить тренировку'."""
    # Отладочное сообщение
    await message.answer("Запуск формы добавления тренировки...")

    # Устанавливаем состояние формы
    await state.set_state(WorkoutForm.name)

    # Отправляем сообщение с клавиатурой шаблонов
    await message.answer(
        "Выберите название тренировки или введите своё:",
        reply_markup=workout_template_kb,
    )


# Обработчик для шаблонных тренировок
@router.message(lambda message: message.text in TEMPLATE_WORKOUTS.keys())
async def process_template_workout(message: Message, state: FSMContext):
    """Обработчик для шаблонных тренировок."""
    # Получаем название и тип из словаря
    workout_name = message.text
    workout_type = TEMPLATE_WORKOUTS[workout_name]

    # Очищаем название от эмодзи для сохранения
    clean_name = workout_name
    emoji_list = ["💪", "🏃", "🦵", "🏋️", "🫁", "🧘", "🤸"]
    if clean_name and len(clean_name) >= 2:
        for emoji in emoji_list:
            if clean_name.startswith(emoji):
                clean_name = clean_name[len(emoji) :].strip()
                break

    # Сохраняем данные
    await state.set_state(WorkoutForm.duration)
    await state.update_data(name=clean_name, type=workout_type)

    # Получаем отображаемое название типа
    workout_type_display = WORKOUT_TYPE_DISPLAY.get(workout_type, "Другая")

    # Переходим к вводу продолжительности
    await message.answer(
        f"Тип тренировки определен: {workout_type_display}\n\n"
        "Введите продолжительность тренировки в минутах (только число):\n"
        "Используйте кнопку 🔙 Назад для возврата к выбору тренировки.",
        reply_markup=workout_form_kb,
    )


# Обработчик для ввода названия тренировки
@router.message(WorkoutForm.name)
async def process_workout_name(message: Message, state: FSMContext):
    """Обработчик ввода названия тренировки."""
    if not message.text:
        await message.answer("Пожалуйста, введите название тренировки.")
        return

    # Обрабатываем кнопку "Назад"
    if message.text == "🔙 Назад":
        await state.clear()
        await message.answer(
            "Возвращаемся в меню тренировок.",
            reply_markup=workout_kb,
        )
        return

    if message.text == "✏️ Своё название":
        # Если пользователь выбрал "Своё название", просим ввести его вручную
        await message.answer(
            "Введите название тренировки:",
            reply_markup=workout_form_kb,
        )
        return

    # Сохраняем оригинальное название
    original_name = message.text

    # Очищаем название от эмодзи для сохранения
    workout_name = original_name

    # Удаляем эмодзи и пробел после него, если они есть
    emoji_list = ["💪", "🏃", "🦵", "🏋️", "🫁", "🧘", "🤸"]
    if workout_name and len(workout_name) >= 2:
        for emoji in emoji_list:
            if workout_name.startswith(emoji):
                workout_name = workout_name[len(emoji) :].strip()
                break

    # Сохраняем название тренировки
    await state.update_data(name=workout_name)

    # Определяем тип тренировки по названию
    workout_type = None

    # Преобразуем название в нижний регистр для сравнения
    name_lower = original_name.lower()

    # Прямое сопоставление названий с типами
    if "силовая" in name_lower:
        workout_type = "strength"
    elif "кардио" in name_lower:
        workout_type = "cardio"
    elif "тренировка ног" in name_lower:
        workout_type = "strength"
    elif "тренировка рук" in name_lower:
        workout_type = "strength"
    elif "тренировка спины" in name_lower:
        workout_type = "strength"
    elif "тренировка груди" in name_lower:
        workout_type = "strength"
    elif "йога" in name_lower:
        workout_type = "flexibility"
    elif "растяжка" in name_lower:
        workout_type = "flexibility"

    # Если тип не определен, спрашиваем у пользователя
    if not workout_type:
        await state.set_state(WorkoutForm.type)
        await message.answer(
            "Выберите тип тренировки:\n"
            "Используйте кнопку 🔙 Назад для возврата к выбору названия.",
            reply_markup=workout_type_kb,
        )
        return

    # Сохраняем тип тренировки
    await state.update_data(type=workout_type)

    # Получаем отображаемое название типа
    workout_type_display = WORKOUT_TYPE_DISPLAY.get(workout_type, "Другая")

    # Переходим к вводу продолжительности
    await state.set_state(WorkoutForm.duration)
    await message.answer(
        f"Тип тренировки определен: {workout_type_display}\n\n"
        "Введите продолжительность тренировки в минутах (только число):\n"
        "Используйте кнопку 🔙 Назад для возврата к выбору тренировки.",
        reply_markup=workout_form_kb,
    )


# Обработчик для выбора типа тренировки
@router.message(WorkoutForm.type)
async def process_workout_type(message: Message, state: FSMContext):
    """Обработчик выбора типа тренировки."""
    workout_types = {
        "💪 Силовая": "strength",
        "🏃 Кардио": "cardio",
        "🧘 Гибкость": "flexibility",
        "⚡ HIIT": "hiit",
        "🔄 Другое": "other",
    }

    if message.text == "🔙 Назад":
        await state.set_state(WorkoutForm.name)
        await message.answer(
            "Выберите название тренировки или введите своё:",
            reply_markup=workout_template_kb,
        )
        return

    if message.text in workout_types:
        await state.update_data(type=workout_types[message.text])
        await state.set_state(WorkoutForm.duration)

        await message.answer(
            "Введите продолжительность тренировки в минутах (только число):",
            reply_markup=workout_form_kb,
        )
    else:
        await message.answer(
            "Пожалуйста, выберите тип тренировки из предложенных вариантов.",
            reply_markup=workout_type_kb,
        )


# Обработчик для ввода продолжительности тренировки
@router.message(WorkoutForm.duration)
async def process_workout_duration(message: Message, state: FSMContext):
    """Обработчик ввода продолжительности тренировки."""
    # Обрабатываем кнопку "Назад"
    if message.text == "🔙 Назад":
        # Возвращаемся к выбору типа тренировки
        await state.set_state(WorkoutForm.name)
        await message.answer(
            "Выберите название тренировки:",
            reply_markup=workout_template_kb,
        )
        return

    # Валидация длительности тренировки
    from bot.validators import validate_duration

    if not message.text:
        await message.answer(
            "Пожалуйста, введите продолжительность тренировки."
        )
        return

    is_valid, error_message, duration = validate_duration(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректную продолжительность в минутах:"
        )
        return

    # Отладочное сообщение
    await message.answer(f"Получена продолжительность: {duration} минут")

    # Сохраняем продолжительность
    await state.update_data(duration_minutes=duration)

    # Переходим к вводу сожженных калорий
    await state.set_state(WorkoutForm.calories)
    await message.answer(
        "Введите количество сожженных калорий (только число):\n"
        "Если не знаете, введите 0.\n"
        "Используйте кнопку 🔙 Назад для возврата к вводу продолжительности.",
        reply_markup=workout_form_kb,
    )


# Обработчик для ввода калорий
@router.message(WorkoutForm.calories)
async def process_workout_calories(message: Message, state: FSMContext):
    """Обработчик ввода калорий."""
    if message.text == "🔙 Назад":
        await state.set_state(WorkoutForm.duration)
        await message.answer(
            "Введите продолжительность тренировки в минутах (только число):",
            reply_markup=workout_form_kb,
        )
        return

    # Проверяем входные данные
    if not message.text:
        await message.answer(
            "Пожалуйста, введите количество калорий.",
            reply_markup=workout_form_kb,
        )
        return

    # Позволяем ввод 0 для случаев, когда калории неизвестны
    if message.text.strip() == "0":
        await state.update_data(calories=None)
        await state.set_state(WorkoutForm.notes)
        await message.answer(
            "Введите заметки о тренировке "
            "(упражнения, веса, подходы и т.д.):\n"
            "Если нет заметок, отправьте '-'",
            reply_markup=workout_form_kb,
        )
        return

    # Валидация калорий
    from bot.validators import validate_calories

    is_valid, error_message, calories = validate_calories(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректное количество калорий:",
            reply_markup=workout_form_kb,
        )
        return

    await state.update_data(calories=calories)
    await state.set_state(WorkoutForm.notes)

    await message.answer(
        "Введите заметки о тренировке "
        "(упражнения, веса, подходы и т.д.):\n"
        "Если нет заметок, отправьте '-'",
        reply_markup=workout_form_kb,
    )


# Обработчик для ввода заметок
@router.message(WorkoutForm.notes)
async def process_workout_notes(message: Message, state: FSMContext):
    """Обработчик ввода заметок о тренировке."""
    if message.text == "🔙 Назад":
        await state.set_state(WorkoutForm.calories)
        await message.answer(
            "Введите количество сожженных калорий "
            "(только число, можно примерно):\n"
            "Если не знаете, введите 0.",
            reply_markup=workout_form_kb,
        )
        return

    # Сохраняем заметки о тренировке
    notes = message.text if message.text else ""
    await state.update_data(notes=notes)

    # Получаем все данные из состояния
    data = await state.get_data()

    # Формируем данные для API
    workout_data = {
        "name": data["name"],
        "type": data["type"],
        "duration_minutes": data["duration_minutes"],
        "calories_burned": data["calories"],
        "notes": data.get("notes", ""),
        "date": format_datetime(get_utc_now()),
    }

    # Отправляем запрос к API
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=workout_kb,
        )
        await state.clear()
        return

    user_api_client = get_user_api_client(telegram_id)
    result = await user_api_client.create_workout(workout_data)

    if result:
        # Получаем отображаемое название типа тренировки
        workout_type_display = WORKOUT_TYPE_DISPLAY.get(
            data["type"], "Тренировка"
        )

        await message.answer(
            f"✅ Добавлена тренировка: {data['name']}\n"
            f"Тип: {workout_type_display}\n"
            f"Продолжительность: {data['duration_minutes']} мин\n"
            f"Калории: {data['calories']}",
            reply_markup=workout_kb,  # Возвращаем в меню тренировок
        )
    else:
        await message.answer(
            "❌ Не удалось добавить тренировку. Пожалуйста, попробуйте позже.",
            reply_markup=workout_kb,  # Возвращаем в меню тренировок
        )

    # Очищаем состояние
    await state.clear()

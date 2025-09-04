import re

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.api_client import UserAPIClient
from bot.constants import MEAL_TYPE_DISPLAY, MESSAGES
from bot.keyboards.reply import (
    cancel_kb,
    main_kb,
    meal_kb,
    meal_type_kb,
)
from bot.utils import format_datetime, get_utc_now

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Определение состояний для FSM
class MealForm(StatesGroup):
    name = State()
    type = State()
    calories = State()
    protein = State()
    fat = State()
    carbs = State()
    notes = State()


# Обработчик команды /food
@router.message(Command("food"))
async def cmd_food(message: Message):
    """Обработчик команды /food."""
    await message.answer(
        "➡️ Выбери вариант:\n"
        '1. Ввести вручную: "Овсянка 100г"\n'
        "2. Отправить фото чека/этикетки\n"
        "3. Синхронизировать с MyFitnessPal\n\n"
        "Для ручного ввода просто отправь название продукта и вес, например:\n"
        '"Овсянка 100г"',
        reply_markup=cancel_kb,
    )


# Обработчик для парсинга данных о питании из текста
@router.message(
    lambda message: not message.text.startswith("/")
    and re.search(r"\d+\s*(?:г|гр|g)\b", message.text.lower())
    and not any(
        medical_term in message.text.lower()
        for medical_term in [
            "гемоглобин",
            "холестерин",
            "глюкоза",
            "лейкоциты",
            "эритроциты",
            "ферритин",
            "кортизол",
        ]
    )
)
async def parse_food_text(message: Message):
    """Парсинг данных о питании из текстового сообщения."""
    text = message.text.lower()

    # Ищем название продукта и вес
    weight_match = re.search(r"(\d+)\s*(?:г|гр|g)\b", text)

    if not weight_match:
        await message.answer(
            "Не удалось распознать вес продукта. Пожалуйста, "
            'укажите вес в граммах, например: "Овсянка 100г"',
            reply_markup=meal_kb,
        )
        return

    weight = int(weight_match.group(1))

    # Получаем название продукта (всё, что идет до веса)
    food_name_match = re.search(r"^(.+?)(?:\d+\s*(?:г|гр|g))", text)
    food_name = (
        food_name_match.group(1).strip() if food_name_match else "Продукт"
    )

    # Рассчитываем примерные значения питательных веществ на основе базы данных
    # В реальном приложении здесь был бы запрос к базе данных продуктов
    # Для демонстрации используем примерные значения для овсянки
    calories_per_100g = 389
    protein_per_100g = 13
    fat_per_100g = 7
    carbs_per_100g = 66

    # Если это овсянка, используем реальные значения, иначе примерные
    if "овсян" in text:
        calories = int(calories_per_100g * weight / 100)
        protein = round(protein_per_100g * weight / 100, 1)
        fat = round(fat_per_100g * weight / 100, 1)
        carbs = round(carbs_per_100g * weight / 100, 1)
    else:
        # Примерные значения для других продуктов
        calories = int(weight * 2)  # Примерно 200 ккал на 100г
        protein = round(weight * 0.1, 1)  # Примерно 10г белка на 100г
        fat = round(weight * 0.05, 1)  # Примерно 5г жира на 100г
        carbs = round(weight * 0.2, 1)  # Примерно 20г углеводов на 100г

    # Формируем данные для API
    meal_data = {
        "food_name": food_name.capitalize(),
        "meal_type": "other",
        "quantity": weight,
        "unit": "г",
        "calories": calories,
        "protein_g": protein,
        "fat_g": fat,
        "carbs_g": carbs,
        "date": format_datetime(get_utc_now()),
    }

    # Отправляем запрос к API
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=main_kb,
        )
        return

    user_api_client = get_user_api_client(telegram_id)
    result = await user_api_client.create_meal(meal_data)

    if result:
        await message.answer(
            MESSAGES["meal_added"].format(
                weight=weight,
                name=food_name,
                calories=calories,
                protein=protein,
                fat=fat,
                carbs=carbs,
            ),
            reply_markup=main_kb,
        )
    else:
        await message.answer(
            MESSAGES["meal_not_added"],
            reply_markup=main_kb,
        )


# Обработчик для кнопки "Питание"
@router.message(F.text == "🥗 Питание")
async def meals_menu(message: Message):
    """Обработчик кнопки 'Питание'."""
    await message.answer(
        "📋 Раздел питания\n\n"
        "Здесь вы можете добавлять приемы пищи и просматривать историю.",
        reply_markup=meal_kb,
    )


# Обработчик для кнопки "Добавить прием пищи"
@router.message(F.text == "➕ Добавить прием пищи")
async def add_meal(message: Message, state: FSMContext):
    """Обработчик кнопки 'Добавить прием пищи'."""
    await state.set_state(MealForm.name)
    await message.answer(
        "Введите название продукта или блюда:",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода названия приема пищи
@router.message(MealForm.name)
async def process_meal_name(message: Message, state: FSMContext):
    """Обработчик ввода названия приема пищи."""
    await state.update_data(name=message.text)
    await state.set_state(MealForm.type)

    await message.answer(
        "Выберите тип приема пищи:",
        reply_markup=meal_type_kb,
    )


# Обработчик для выбора типа приема пищи
@router.message(MealForm.type)
async def process_meal_type(message: Message, state: FSMContext):
    """Обработчик выбора типа приема пищи."""
    meal_types = {
        "🍳 Завтрак": "breakfast",
        "🥪 Обед": "lunch",
        "🍲 Ужин": "dinner",
        "🍎 Перекус": "snack",
        "🔄 Другое": "other",
    }

    if message.text in meal_types:
        await state.update_data(type=meal_types[message.text])
        await state.set_state(MealForm.calories)

        await message.answer(
            "Введите калорийность в ккал (только число):",
            reply_markup=cancel_kb,
        )
    else:
        await message.answer(
            "Пожалуйста, выберите тип приема пищи из предложенных вариантов.",
            reply_markup=meal_type_kb,
        )


# Обработчик для ввода калорий
@router.message(MealForm.calories)
async def process_meal_calories(message: Message, state: FSMContext):
    """Обработчик ввода калорий."""
    # Валидация калорий
    from bot.validators import validate_calories

    if not message.text:
        await message.answer(
            "Пожалуйста, введите количество калорий.",
            reply_markup=cancel_kb,
        )
        return

    is_valid, error_message, calories = validate_calories(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректное количество калорий:",
            reply_markup=cancel_kb,
        )
        return

    await state.update_data(calories=calories)
    await state.set_state(MealForm.protein)

    await message.answer(
        "Введите количество белка в граммах (только число):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода белка
@router.message(MealForm.protein)
async def process_meal_protein(message: Message, state: FSMContext):
    """Обработчик ввода белка."""
    # Валидация белков
    from bot.validators import validate_macronutrient

    if not message.text:
        await message.answer(
            "Пожалуйста, введите количество белка.",
            reply_markup=cancel_kb,
        )
        return

    is_valid, error_message, protein = validate_macronutrient(
        message.text, "Белки"
    )

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректное количество белка:",
            reply_markup=cancel_kb,
        )
        return

    await state.update_data(protein_g=protein)
    await state.set_state(MealForm.fat)

    await message.answer(
        "Введите количество жиров в граммах (только число):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода жиров
@router.message(MealForm.fat)
async def process_meal_fat(message: Message, state: FSMContext):
    """Обработчик ввода жиров."""
    # Валидация жиров
    from bot.validators import validate_macronutrient

    if not message.text:
        await message.answer(
            "Пожалуйста, введите количество жиров.",
            reply_markup=cancel_kb,
        )
        return

    is_valid, error_message, fat = validate_macronutrient(message.text, "Жиры")

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректное количество жиров:",
            reply_markup=cancel_kb,
        )
        return

    await state.update_data(fat_g=fat)
    await state.set_state(MealForm.carbs)

    await message.answer(
        "Введите количество углеводов в граммах (только число):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода углеводов
@router.message(MealForm.carbs)
async def process_meal_carbs(message: Message, state: FSMContext):
    """Обработчик ввода углеводов."""
    # Валидация углеводов
    from bot.validators import validate_macronutrient

    if not message.text:
        await message.answer(
            "Пожалуйста, введите количество углеводов.",
            reply_markup=cancel_kb,
        )
        return

    is_valid, error_message, carbs = validate_macronutrient(
        message.text, "Углеводы"
    )

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\n"
            "Пожалуйста, введите корректное количество углеводов:",
            reply_markup=cancel_kb,
        )
        return

    await state.update_data(carbs_g=carbs)
    await state.set_state(MealForm.notes)

    await message.answer(
        "Введите заметки о приеме пищи (например, состав блюда):\n"
        "Если нет заметок, отправьте '-'",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода заметок
@router.message(MealForm.notes)
async def process_meal_notes(message: Message, state: FSMContext):
    """Обработчик ввода заметок."""
    notes = None if message.text == "-" else message.text
    await state.update_data(notes=notes)

    # Получаем все данные из состояния
    data = await state.get_data()

    # Формируем данные для API
    meal_data = {
        "food_name": data["name"],
        "meal_type": data["type"],
        "calories": data["calories"],
        "protein_g": data["protein_g"],
        "fat_g": data["fat_g"],
        "carbs_g": data["carbs_g"],
        "notes": data.get("notes"),
        "date": format_datetime(get_utc_now()),
    }

    # Отправляем запрос к API
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=meal_kb,
        )
        await state.clear()
        return

    user_api_client = get_user_api_client(telegram_id)
    result = await user_api_client.create_meal(meal_data)

    if result:
        # Получаем отображаемое название типа приема пищи
        meal_type_display = MEAL_TYPE_DISPLAY.get(data["type"], "Прием пищи")

        await message.answer(
            f"✅ {meal_type_display} успешно добавлен!\n\n"
            f"Название: {data['name']}\n"
            f"Калории: {data['calories']} ккал\n"
            f"Белки: {data['protein_g']} г\n"
            f"Жиры: {data['fat_g']} г\n"
            f"Углеводы: {data['carbs_g']} г",
            reply_markup=meal_kb,
        )
    else:
        await message.answer(
            MESSAGES["meal_not_added"],
            reply_markup=meal_kb,
        )

    # Очищаем состояние
    await state.clear()


# Обработчик для кнопки "Мои приемы пищи"
@router.message(F.text == "📋 Мои приемы пищи")
async def list_meals(message: Message):
    """Обработчик кнопки 'Мои приемы пищи'."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=meal_kb,
        )
        return

    # Получаем список приемов пищи
    user_api_client = get_user_api_client(telegram_id)
    meals = await user_api_client.get_meals(limit=5)

    if not meals:
        await message.answer(
            "У вас пока нет добавленных приемов пищи.",
            reply_markup=meal_kb,
        )
        return

    # Формируем сообщение со списком приемов пищи
    meals_text = "📋 Ваши последние приемы пищи:\n\n"

    for meal in meals:
        # Преобразуем тип приема пищи в читаемый формат
        meal_type = MEAL_TYPE_DISPLAY.get(meal.get("meal_type"), "Другое")

        # Форматируем дату
        meal_date = (
            meal["date"].split("T")[0] if "T" in meal["date"] else meal["date"]
        )

        meals_text += (
            f"• {meal_date}: {meal.get('food_name', 'Блюдо')}\n"
            f"  Тип: {meal_type}, {meal.get('calories', 0)} ккал\n"
            f"  БЖУ: {meal.get('protein_g', 0)}г / "
            f"{meal.get('fat_g', 0)}г / {meal.get('carbs_g', 0)}г\n\n"
        )

    await message.answer(meals_text, reply_markup=meal_kb)

import re

from typing import cast

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message

from bot.api_client import UserAPIClient
from bot.constants import LAB_REFERENCES, LAB_STATUS, MESSAGES
from bot.keyboards.reply import (
    cancel_kb,
    lab_kb,
    main_kb,
)
from bot.utils import format_datetime, get_utc_now

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Определение состояний для FSM
class LabForm(StatesGroup):
    name = State()
    value = State()
    unit = State()
    reference_min = State()
    reference_max = State()
    date = State()
    notes = State()


# Обработчик команды /labs
@router.message(Command("labs"))
async def cmd_labs(message: Message):
    """Обработчик команды /labs."""
    await message.answer(
        "➡️ Прикрепи PDF/фото анализа или введи данные вручную:\n\n"
        "Формат:\n"
        "[Показатель] [Значение] [Ед.изм]\n\n"
        "✅ Пример:\n"
        '"гемоглобин 148 г/л"',
        reply_markup=cancel_kb,
    )


# Обработчик для парсинга данных анализа из текста
@router.message(
    lambda message: not message.text.startswith("/")
    and any(
        keyword in message.text.lower()
        for keyword in ["гемоглобин", "холестерин", "глюкоза", "лейкоциты"]
    )
)
async def parse_lab_text(message: Message, state: FSMContext):
    """Парсинг данных анализа из текстового сообщения."""
    text = message.text.lower()

    # Ищем показатель в тексте
    lab_name = None
    for key in LAB_REFERENCES:
        if key in text:
            lab_name = key
            break

    if not lab_name:
        await message.answer(
            "Не удалось распознать показатель анализа.\n"
            "Пожалуйста, используйте формат:\n"
            '"[Показатель] [Значение] [Ед.изм]"\n\n'
            'Например: "гемоглобин 148 г/л"',
            reply_markup=lab_kb,
        )
        return

    # Ищем значение (число после названия показателя)
    # Ищем число, которое может быть окружено пробелами
    # и может содержать запятую или точку
    value_match = re.search(rf"{lab_name}\s*(\d+(?:[,.]\d+)?)", text)

    if not value_match:
        await message.answer(
            "Не удалось распознать значение показателя.\n"
            "Пожалуйста, используйте формат:\n"
            '"[Показатель] [Значение] [Ед.изм]"\n\n'
            'Например: "гемоглобин 148 г/л"',
            reply_markup=lab_kb,
        )
        return

    # Преобразуем значение в число
    value_str = value_match.group(1).replace(",", ".")
    value = float(value_str)

    # Получаем единицу измерения и референсные значения
    unit = LAB_REFERENCES[lab_name]["unit"]
    ref_min = LAB_REFERENCES[lab_name]["min"]
    ref_max = LAB_REFERENCES[lab_name]["max"]

    # Определяем статус значения (норма, повышен, понижен)
    if value < cast(float, ref_min):
        status = LAB_STATUS["low"]
    elif value > cast(float, ref_max):
        status = LAB_STATUS["high"]
    else:
        status = LAB_STATUS["normal"]

    # Формируем данные для API
    lab_data = {
        "test_type": lab_name.capitalize(),
        "date": format_datetime(get_utc_now()),
        "notes": f"Статус: {status}",
        "results": {
            "value": value,
            "unit": unit,
            "reference_min": ref_min,
            "reference_max": ref_max,
            "status": status,
        },
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
    result = await user_api_client.create_lab_result(lab_data)

    if result:
        # Очищаем состояние FSM после успешного добавления
        await state.clear()

        await message.answer(
            MESSAGES["lab_added"].format(
                name=lab_name.capitalize(),
                value=value,
                unit=unit,
                status=status,
                min=ref_min,
                max=ref_max,
            ),
            reply_markup=main_kb,
        )
    else:
        await message.answer(
            MESSAGES["lab_not_added"],
            reply_markup=main_kb,
        )


# Обработчик для кнопки "Анализы"
@router.message(F.text == "🩸 Анализы")
async def labs_menu(message: Message):
    """Обработчик кнопки 'Анализы'."""
    await message.answer(
        "📋 Раздел анализов\n\n"
        "Здесь вы можете добавлять результаты "
        "анализов и просматривать историю.",
        reply_markup=lab_kb,
    )


# Обработчик для кнопки "Назад" в меню анализов
@router.message(F.text == "🔙 Назад")
async def back_to_main_menu(message: Message):
    """Обработчик кнопки 'Назад'."""
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_kb,
    )


# Обработчик для кнопки "Добавить анализ"
@router.message(F.text == "➕ Добавить анализ")
async def add_lab(message: Message, state: FSMContext):
    """Обработчик кнопки 'Добавить анализ'."""
    await state.set_state(LabForm.name)
    await message.answer(
        "Введите название показателя анализа (например, 'Гемоглобин'):",
        reply_markup=cancel_kb,
    )


# Обработчик для отмены операции
@router.message(F.text == "❌ Отмена")
async def cancel_operation(message: Message, state: FSMContext):
    """Обработчик кнопки 'Отмена'."""
    current_state = await state.get_state()
    if current_state is not None:
        await state.clear()

    await message.answer(
        "Операция отменена.",
        reply_markup=lab_kb,
    )


# Обработчик для ввода названия показателя
@router.message(LabForm.name)
async def process_lab_name(message: Message, state: FSMContext):
    """Обработчик ввода названия показателя."""
    await state.update_data(name=message.text)
    await state.set_state(LabForm.value)

    await message.answer(
        "Введите значение показателя (только число):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода значения показателя
@router.message(LabForm.value)
async def process_lab_value(message: Message, state: FSMContext):
    """Обработчик ввода значения показателя."""
    # Валидация значения анализа
    from bot.validators import validate_lab_value

    if not message.text:
        await message.answer(
            "Пожалуйста, введите значение показателя.",
            reply_markup=cancel_kb,
        )
        return

    is_valid, error_message, value = validate_lab_value(message.text)

    if not is_valid:
        await message.answer(
            f"❌ {error_message}\n\nПожалуйста, введите корректное значение:",
            reply_markup=cancel_kb,
        )
        return

    await state.update_data(value=value)
    await state.set_state(LabForm.unit)

    await message.answer(
        "Введите единицу измерения (например, 'г/л', 'ммоль/л'):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода единицы измерения
@router.message(LabForm.unit)
async def process_lab_unit(message: Message, state: FSMContext):
    """Обработчик ввода единицы измерения."""
    await state.update_data(unit=message.text)
    await state.set_state(LabForm.reference_min)

    await message.answer(
        "Введите нижнюю границу референсных значений (например, '4.0'):",
        reply_markup=cancel_kb,
    )


# Обработчик для ввода нижней границы референсных значений
@router.message(LabForm.reference_min)
async def process_lab_reference_min(message: Message, state: FSMContext):
    """Обработчик ввода нижней границы референсных значений."""
    try:
        ref_min = float(message.text.replace(",", "."))
        await state.update_data(reference_min=ref_min)
        await state.set_state(LabForm.reference_max)

        await message.answer(
            "Введите верхнюю границу референсных значений (например, '5.5'):",
            reply_markup=cancel_kb,
        )
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число.",
            reply_markup=cancel_kb,
        )


# Обработчик для ввода верхней границы референсных значений
@router.message(LabForm.reference_max)
async def process_lab_reference_max(message: Message, state: FSMContext):
    """Обработчик ввода верхней границы референсных значений."""
    try:
        ref_max = float(message.text.replace(",", "."))
        await state.update_data(reference_max=ref_max)
        await state.set_state(LabForm.notes)

        await message.answer(
            "Введите заметки к анализу (например, 'Сдан натощак'):\n"
            "Если нет заметок, отправьте '-'",
            reply_markup=cancel_kb,
        )
    except ValueError:
        await message.answer(
            "Пожалуйста, введите корректное число.",
            reply_markup=cancel_kb,
        )


# Обработчик для ввода заметок
@router.message(LabForm.notes)
async def process_lab_notes(message: Message, state: FSMContext):
    """Обработчик ввода заметок."""
    notes = None if message.text == "-" else message.text
    await state.update_data(notes=notes)

    # Получаем все данные из состояния
    data = await state.get_data()

    # Определяем статус значения (норма, повышен, понижен)
    value = data["value"]
    ref_min = data["reference_min"]
    ref_max = data["reference_max"]

    if value < cast(float, ref_min):
        status = LAB_STATUS["low"]
    elif value > cast(float, ref_max):
        status = LAB_STATUS["high"]
    else:
        status = LAB_STATUS["normal"]

    # Добавляем статус к заметкам
    if data.get("notes"):
        notes = f"{data['notes']}. Статус: {status}"
    else:
        notes = f"Статус: {status}"

    # Формируем данные для API
    lab_data = {
        "test_type": data["name"],
        "date": format_datetime(get_utc_now()),
        "notes": notes,
        "results": {
            "value": data["value"],
            "unit": data["unit"],
            "reference_min": data["reference_min"],
            "reference_max": data["reference_max"],
            "status": status,
        },
    }

    # Отправляем запрос к API
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=lab_kb,
        )
        await state.clear()
        return

    user_api_client = get_user_api_client(telegram_id)
    result = await user_api_client.create_lab_result(lab_data)

    if result:
        await message.answer(
            f"✅ Анализ успешно добавлен!\n\n"
            f"Показатель: {data['name']}\n"
            f"Значение: {data['value']} {data['unit']}\n"
            f"Референсные значения: {ref_min}-{ref_max}\n"
            f"Статус: {status}",
            reply_markup=lab_kb,
        )
    else:
        await message.answer(
            MESSAGES["lab_not_added"],
            reply_markup=lab_kb,
        )

    # Очищаем состояние
    await state.clear()


# Обработчик для кнопки "Мои анализы"
@router.message(F.text == "📋 Мои анализы")
async def list_lab_results(message: Message):
    """Обработчик кнопки 'Мои анализы'."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=lab_kb,
        )
        return

    # Получаем список результатов анализов
    user_api_client = get_user_api_client(telegram_id)
    labs = await user_api_client.get_lab_results(limit=10)

    if not labs:
        await message.answer(
            "У вас пока нет добавленных результатов анализов.",
            reply_markup=lab_kb,
        )
        return

    # Формируем сообщение со списком анализов
    lab_list = "📋 Ваши последние результаты анализов:\n\n"

    for lab in labs:
        results = lab.get("results", {})
        value = results.get("value", "N/A")
        unit = results.get("unit", "")
        ref_min = results.get("reference_min")
        ref_max = results.get("reference_max")

        ref_range = (
            f" (норма: {ref_min}-{ref_max})"
            if ref_min is not None and ref_max is not None
            else ""
        )
        lab_list += f"• {lab['test_type']}: {value} {unit}{ref_range}\n"

    await message.answer(lab_list, reply_markup=lab_kb)

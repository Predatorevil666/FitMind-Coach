from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.handlers.advice import cmd_advice
from bot.keyboards.reply import (
    lab_kb,
    main_kb,
    meal_kb,
    profile_kb,
    workout_kb,
)
from bot.logger import logger
from bot.utils import get_user_id

router = Router()

# Словарь для определения, какую клавиатуру показывать при отмене операции
SECTION_KEYBOARDS = {
    "meal": meal_kb,
    "workout": workout_kb,
    "lab": lab_kb,
    "profile": profile_kb,
}


# Обработчик для кнопки "Назад" в любом разделе
@router.message(F.text == "🔙 Назад")
async def back_to_main_menu(message: Message):
    """Обработчик кнопки 'Назад'."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} вернулся в главное меню")
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_kb,
    )


# Обработчик для кнопки "Тренировки" в главном меню
@router.message(F.text == "🏋️‍♂️ Тренировки")
async def workout_button(message: Message):
    """Обработчик кнопки 'Тренировки'."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} перешел в раздел тренировок")
    await message.answer(
        "Раздел тренировок. Выберите действие:",
        reply_markup=workout_kb,
    )


# Обработчик для кнопки "Питание" в главном меню
@router.message(F.text == "🍽 Питание")
async def meal_button(message: Message):
    """Обработчик кнопки 'Питание'."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} перешел в раздел питания")
    await message.answer(
        "Раздел питания. Выберите действие:",
        reply_markup=meal_kb,
    )


# Обработчик для кнопки "Лабораторные данные" в главном меню
@router.message(F.text == "🔬 Лабораторные данные")
async def lab_button(message: Message):
    """Обработчик кнопки 'Лабораторные данные'."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} перешел в раздел лабораторных данных")
    await message.answer(
        "Раздел лабораторных данных. Выберите действие:",
        reply_markup=lab_kb,
    )


# Обработчик для кнопки "Получить совет" в главном меню
@router.message(F.text == "💡 Получить совет")
async def advice_button(message: Message, state: FSMContext):
    """Обработчик кнопки 'Получить совет'."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} нажал кнопку 'Получить совет'")
    await cmd_advice(message, state=state)


# Обработчик для отмены операции
@router.message(F.text == "❌ Отмена")
async def cancel_operation(message: Message, state: FSMContext):
    """Обработчик кнопки 'Отмена'."""
    current_state = await state.get_state()
    if current_state is not None:
        # Определяем, из какого раздела была вызвана отмена
        section = None
        if "Meal" in current_state:
            section = "meal"
        elif "Workout" in current_state:
            section = "workout"
        elif "Lab" in current_state:
            section = "lab"
        elif "Profile" in current_state:
            section = "profile"

        # Очищаем состояние
        await state.clear()

        # Выбираем соответствующую клавиатуру
        keyboard = SECTION_KEYBOARDS.get(section or "", main_kb)

        user_id = get_user_id(message)
        logger.info(
            f"Пользователь {user_id} отменил операцию в разделе {section}"
        )
        await message.answer(
            "Операция отменена.",
            reply_markup=keyboard,
        )
    else:
        await message.answer(
            "Нет активных операций для отмены.",
            reply_markup=main_kb,
        )

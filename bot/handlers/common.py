from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from bot.keyboards.reply import (
    lab_kb,
    main_kb,
    meal_kb,
    profile_kb,
    workout_kb,
)
from bot.logger import logger

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
    logger.info(f"Пользователь {message.from_user.id} вернулся в главное меню")
    await message.answer(
        "Вы вернулись в главное меню.",
        reply_markup=main_kb,
    )


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
        keyboard = SECTION_KEYBOARDS.get(section, main_kb)

        logger.info(
            f"Пользователь {message.from_user.id} отменил операцию в разделе {
                section
            }"
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

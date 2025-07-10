from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from bot.api_client import UserAPIClient
from bot.keyboards.reply import main_kb
from bot.logger import logger
from bot.utils import get_user_id, mistral_client

router = Router()


class AdviceForm(StatesGroup):
    """Состояния для получения совета."""

    waiting_for_query = State()


@router.message(Command("advice"))
async def cmd_advice(message: Message, state: FSMContext):
    """Обработчик команды /advice."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} запросил совет")
    await message.answer(
        "Какой совет вы хотели бы получить? Опишите ваш вопрос о фитнесе, "
        "питании или здоровом образе жизни.",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AdviceForm.waiting_for_query)


@router.message(AdviceForm.waiting_for_query)
async def process_advice_query(message: Message, state: FSMContext):
    """Обработчик запроса совета."""
    query = message.text or ""
    user_id = get_user_id(message)

    logger.info(
        f"=== QUERY PROCESSING === Получен запрос от {user_id}: {query}"
    )

    if query == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Запрос совета отменен.",
            reply_markup=main_kb,
        )
        return

    # Отправляем сообщение о том, что запрос обрабатывается
    processing_msg = await message.answer(
        "🔍 Анализирую данные... Это займет 60-90 секунд."
    )

    try:
        logger.info("=== USING MISTRAL === Отправляю запрос к Mistral API")

        # Получаем данные пользователя из API
        user_data: dict[str, Any] = {}

        if message.from_user:
            # Создаем API клиент для пользователя
            api_client = UserAPIClient(message.from_user.id)

            # Получаем профиль пользователя
            profile = await api_client.get_profile()
            if profile:
                user_data["profile"] = profile

                # Получаем тренировки пользователя
                workouts = await api_client.get_workouts()
                if workouts:
                    user_data["workouts"] = workouts

                # Получаем питание пользователя
                meals = await api_client.get_meals()
                if meals:
                    user_data["meals"] = meals

                # Получаем лабораторные данные пользователя
                lab_results = await api_client.get_lab_results()
                if lab_results:
                    user_data["lab_results"] = lab_results

        logger.info(f"Отправляю запрос к Mistral API: {query}")
        # Получаем совет от Mistral AI с учетом данных пользователя
        advice = await mistral_client.get_advice(query, user_data)

        # Очищаем состояние
        await state.clear()

        # Отправляем совет
        await message.answer(
            f"💡 <b>Персонализированный совет:</b>\n\n{advice}",
            parse_mode="HTML",
            reply_markup=main_kb,
        )

        # Сокращаем запрос для логирования
        query_preview = (
            query[:30] + "..." if query and len(query) > 30 else query
        )
        logger.info(
            f"=== SUCCESS === Пользователь {user_id} "
            f"получил совет по запросу: {query_preview}"
        )
    except Exception as e:
        logger.error(f"=== ERROR === Ошибка при получении совета: {e}")
        await message.answer(
            "Извините, произошла ошибка при обработке вашего запроса. "
            "Пожалуйста, попробуйте позже.",
            reply_markup=main_kb,
        )
        await state.clear()
    finally:
        # Удаляем сообщение о обработке
        await processing_msg.delete()

import re

from typing import Any

from aiogram import Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, ReplyKeyboardRemove

from bot.api_client import UserAPIClient
from bot.keyboards.reply import main_kb
from bot.logger import logger
from bot.utils import mistral_client


def get_user_id(message: Message) -> int:
    """Получить ID пользователя из сообщения."""
    return message.from_user.id if message.from_user else 0


def clean_html_tags(text: str) -> str:
    """
    Очищает HTML-тэги и проблемные символы для безопасной отправки в Telegram.

    Args:
        text: Текст с HTML-тэгами

    Returns:
        Очищенный текст
    """
    # Убираем все HTML-тэги
    text = re.sub(r"<[^>]+>", "", text)

    # Убираем HTML-сущности
    text = text.replace("&lt;", "<")
    text = text.replace("&gt;", ">")
    text = text.replace("&amp;", "&")
    text = text.replace("&quot;", '"')
    text = text.replace("&#39;", "'")

    # Убираем лишние пробелы и переносы строк
    text = re.sub(r"\n\s*\n", "\n\n", text)  # Убираем множественные переносы
    text = re.sub(r" +", " ", text)  # Убираем множественные пробелы
    text = text.strip()

    return text


def split_long_message(text: str, max_length: int = 3500) -> list[str]:
    """
    Разбивает длинное сообщение на части, не превышающие max_length.

    Args:
        text: Текст для разбиения
        max_length: Максимальная длина части (по умолчанию 3500)

    Returns:
        Список частей сообщения
    """
    if len(text) <= max_length:
        return [text]

    parts = []
    current_part = ""

    # Сначала пробуем разбить по абзацам (двойной перенос строки)
    paragraphs = text.split("\n\n")

    for paragraph in paragraphs:
        # Если добавление абзаца превысит лимит
        paragraph_length = len(current_part) + len(paragraph) + 2
        if paragraph_length > max_length:
            if current_part:
                parts.append(current_part.strip())
                current_part = paragraph
            else:
                # Если один абзац слишком длинный, разбиваем по предложениям
                sentences = re.split(r"(?<=[.!?])\s+", paragraph)
                for sentence in sentences:
                    sentence_length = len(current_part) + len(sentence) + 1
                    if sentence_length > max_length:
                        if current_part:
                            parts.append(current_part.strip())
                            current_part = sentence
                        else:
                            # Если одно предложение слишком длинное,
                            #  разбиваем по словам
                            words = sentence.split()
                            for word in words:
                                word_length = len(current_part) + len(word) + 1
                                if word_length > max_length:
                                    if current_part:
                                        parts.append(current_part.strip())
                                        current_part = word
                                    else:
                                        # Если одно слово слишком длинное,
                                        #  обрезаем
                                        parts.append(word[:max_length])
                                        current_part = word[max_length:]
                                else:
                                    current_part += (
                                        " " + word if current_part else word
                                    )
                    else:
                        current_part += (
                            " " + sentence if current_part else sentence
                        )
        else:
            current_part += "\n\n" + paragraph if current_part else paragraph

    # Добавляем последнюю часть
    if current_part.strip():
        parts.append(current_part.strip())

    return parts


class AdviceForm(StatesGroup):
    """Состояния для формы запроса совета."""

    waiting_for_query = State()


router = Router()


@router.message(Command("advice"))
async def cmd_advice(message: Message, state: FSMContext):
    """Обработчик команды /advice."""
    user_id = get_user_id(message)
    logger.info(f"Пользователь {user_id} запросил совет")
    await message.answer(
        "🤖 Какой совет вы хотели бы получить?\n\n"
        "Опишите ваш вопрос о фитнесе, питании или здоровом образе жизни.\n\n"
        "📏 Лимиты:\n"
        "• До 5000 символов - быстрая обработка\n"
        "• До 8000 символов - может потребоваться больше времени\n"
        "• Свыше 8000 символов - разбейте на части\n\n"
        "💡 Совет: Конкретные вопросы дают лучшие ответы!",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(AdviceForm.waiting_for_query)


@router.message(AdviceForm.waiting_for_query)
async def process_advice_query(message: Message, state: FSMContext):
    """Обработчик запроса совета."""
    query = message.text or ""
    user_id = get_user_id(message)

    logger.info(
        f"=== QUERY PROCESSING === Получен запрос от {user_id}: "
        f"{query[:100]}..."
    )

    if query == "❌ Отмена":
        await state.clear()
        await message.answer(
            "Запрос совета отменен.",
            reply_markup=main_kb,
        )
        return

    # Проверяем длину запроса
    if len(query) > 8000:  # Увеличиваем лимит до 8000 символов
        await message.answer(
            "⚠️ Ваш запрос слишком длинный (больше 8000 символов).\n\n"
            "💡 Рекомендации:\n"
            "• Разбейте вопрос на части\n"
            "• Задайте несколько коротких вопросов\n"
            "• Сократите текст, оставив главное\n\n"
            "Попробуйте снова с более коротким запросом.",
            reply_markup=main_kb,
        )
        await state.clear()
        return
    elif len(query) > 5000:  # Предупреждение для длинных запросов
        await message.answer(
            "⚠️ Ваш запрос довольно длинный. "
            "Обработка может занять больше времени.\n"
            "🕐 Ожидайте ответ в течение 2-3 минут..."
        )

    # Отправляем сообщение о том, что запрос обрабатывается
    processing_msg = await message.answer(
        "🤖 Обрабатываю ваш запрос, пожалуйста, подождите..."
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

        # Очищаем HTML-тэги из ответа
        advice = clean_html_tags(advice)

        # Очищаем состояние
        await state.clear()

        # Разбиваем длинное сообщение на части
        message_parts = split_long_message(advice)

        # Отправляем первую часть с заголовком
        if message_parts:
            first_part = message_parts[0]
            await message.answer(
                f"💡 Персонализированный совет:\n\n{first_part}",
                reply_markup=main_kb if len(message_parts) == 1 else None,
            )

            # Отправляем остальные части
            for i, part in enumerate(message_parts[1:], 2):
                is_last = i == len(message_parts)
                await message.answer(
                    part,
                    reply_markup=main_kb if is_last else None,
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

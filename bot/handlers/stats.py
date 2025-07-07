from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import UserAPIClient
from bot.keyboards.reply import main_kb

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Получить API клиент для пользователя."""
    return UserAPIClient(telegram_id)


# Обработчик команды /advice
@router.message(Command("advice"))
async def cmd_advice(message: Message) -> None:
    """Обработчик команды /advice."""
    await message.answer(
        "➡️ Опиши проблему или цель:\n"
        '"Не снижается вес последние 2 недели"\n'
        '"Хочу увеличить силу без набора массы"\n\n'
        "Я проанализирую твои данные и дам рекомендации.",
        reply_markup=main_kb,
    )


# Обработчик для запросов на рекомендации
@router.message(
    lambda message: message.text
    and not message.text.startswith("/")
    and any(
        keyword in message.text.lower()
        for keyword in [
            "не снижается",
            "хочу",
            "как",
            "помоги",
            "проблема",
            "цель",
        ]
    )
)
async def generate_advice(message: Message) -> None:
    """Генерация рекомендаций на основе запроса пользователя."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=main_kb,
        )
        return

    # Получаем данные пользователя
    user_api_client = get_user_api_client(telegram_id)
    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Для получения рекомендаций необходимо создать профиль. "
            "Используйте команду /start для создания профиля.",
            reply_markup=main_kb,
        )
        return

    # Получаем последние тренировки и приемы пищи для анализа
    # (в реальном приложении эти данные использовались бы для формирования
    # рекомендаций)
    _ = await user_api_client.get_workouts(limit=5)
    _ = await user_api_client.get_meals(limit=10)
    _ = await user_api_client.get_lab_results(limit=5)

    # Отправляем сообщение о начале анализа
    await message.answer(
        "🔍 Анализирую данные... Это займет 10-20 секунд.",
        reply_markup=main_kb,
    )

    # В реальном приложении здесь был бы запрос к GPT-4 API
    # Для демонстрации используем заготовленные ответы

    # Анализируем запрос пользователя
    query = message.text.lower()

    # Формируем ответ на основе запроса
    if "не снижается вес" in query:
        # Рекомендации для проблемы с весом
        analysis = (
            "🔍 *Анализ данных:*\n"
            "- Дефицит калорий: -150 ккал/день (недостаточно для похудения)\n"
            "- Кортизол повышен: 18 мкг/дл (норма до 10 утром)\n"
            "- Низкое потребление белка: 0.8г/кг (рекомендуется 1.6г)\n\n"
            "💡 *Рекомендации:*\n"
            "1. Питание:\n"
            "   - Увеличить белок: курица 150г/прием\n"
            "   - Снизить углеводы после 18:00\n"
            "2. Тренировки:\n"
            "   - Добавить 20 мин LISS-кардио 3р/неделю\n"
            "   - Уменьшить интенсивность силовых до 70%\n"
            "3. Добавки:\n"
            "   - Магний цитрат 400мг перед сном\n\n"
            "📆 *План на неделю:*\n"
            "Пн: Верх тела + 20мин ходьба\n"
            "Вт: Кардио 45мин\n"
            "Ср: Отдых\n"
            "Чт: Низ тела + 20мин ходьба\n"
            "Пт: HIIT 30мин\n"
            "Сб: Отдых\n"
            "Вс: Полное тело, легкая нагрузка"
        )
    elif "увеличить силу" in query:
        # Рекомендации для увеличения силы
        analysis = (
            "🔍 *Анализ данных:*\n"
            "- Текущий белок: 1.2г/кг (рекомендуется 1.8-2.0г для силы)\n"
            "- Тренировочный объем: средний (нужно увеличить)\n"
            "- Тестостерон: нормальный уровень\n\n"
            "💡 *Рекомендации:*\n"
            "1. Питание:\n"
            "   - Увеличить белок до 2г/кг веса\n"
            "   - Добавить 200-300 ккал в дни тренировок\n"
            "2. Тренировки:\n"
            "   - Перейти на программу 5x5 для базовых упражнений\n"
            "   - Снизить кардио до 2 раз в неделю\n"
            "3. Восстановление:\n"
            "   - Увеличить сон до 8 часов\n"
            "   - Добавить креатин 5г/день\n\n"
            "📆 *План тренировок:*\n"
            "День 1: Жим лежа 5x5, OHP 5x5, Трицепс 3x8-12\n"
            "День 2: Приседания 5x5, Становая 3x5, Икры 3x15-20\n"
            "День 3: Отдых\n"
            "День 4: Подтягивания 5x5, Тяга 5x5, Бицепс 3x8-12\n"
            "День 5: Отдых"
        )
    else:
        # Общие рекомендации
        analysis = (
            "🔍 *Анализ данных:*\n"
            "- Общая активность: средняя (можно увеличить)\n"
            "- Питание: несбалансированное по макронутриентам\n"
            "- Восстановление: недостаточное\n\n"
            "💡 *Рекомендации:*\n"
            "1. Питание:\n"
            "   - Увеличить потребление белка до 1.6г/кг\n"
            "   - Добавить больше овощей и клетчатки\n"
            "2. Тренировки:\n"
            "   - Разнообразить типы тренировок\n"
            "   - Добавить 1-2 дня активного восстановления\n"
            "3. Образ жизни:\n"
            "   - Улучшить качество сна (7-8 часов)\n"
            "   - Снизить стресс через медитацию\n\n"
            "📆 *Примерный план:*\n"
            "- 3-4 силовые тренировки в неделю\n"
            "- 2 кардио сессии (одна интенсивная, одна умеренная)\n"
            "- 1-2 дня полного отдыха\n"
            "- Питание: 4-5 приемов пищи в день с белком в каждом"
        )

    # Отправляем анализ и рекомендации
    await message.answer(analysis, parse_mode="Markdown", reply_markup=main_kb)


# Обработчик для кнопки "Статистика"
@router.message(F.text == "📊 Статистика")
async def stats_menu(message: Message) -> None:
    """Обработчик кнопки 'Статистика'."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=main_kb,
        )
        return

    # Получаем профиль пользователя
    user_api_client = get_user_api_client(telegram_id)
    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Для просмотра статистики необходимо создать профиль. "
            "Используйте команду /start для создания профиля.",
            reply_markup=main_kb,
        )
        return

    # Получаем последние тренировки
    workouts = await user_api_client.get_workouts(limit=5)

    # Получаем последние приемы пищи
    meals = await user_api_client.get_meals(limit=5)

    # Формируем сообщение со статистикой
    stats_text = "📊 *Ваша статистика:*\n\n"

    # Добавляем информацию о профиле
    weight = profile.get("weight", 0)
    target_weight = profile.get("target_weight", 0)
    weight_diff = (
        abs(target_weight - weight) if weight and target_weight else 0
    )

    stats_text += "👤 *Профиль:*\n"
    stats_text += f"Текущий вес: {weight} кг\n"
    stats_text += f"Целевой вес: {target_weight} кг\n"
    stats_text += f"Осталось: {weight_diff} кг\n\n"

    # Добавляем информацию о тренировках
    stats_text += "🏋️ *Последние тренировки:*\n"
    if workouts:
        for workout in workouts:
            workout_date = datetime.fromisoformat(
                workout["date"].replace("Z", "+00:00")
            ).strftime("%d.%m")
            stats_text += (
                f"• {workout_date}: {workout['name']} "
                f"({workout['duration_minutes']} мин)\n"
            )
    else:
        stats_text += "Нет данных о тренировках\n"

    stats_text += "\n"

    # Добавляем информацию о питании
    stats_text += "🥗 *Последние приемы пищи:*\n"
    if meals:
        total_calories = sum(meal.get("calories", 0) for meal in meals)
        avg_calories = total_calories / len(meals)
        stats_text += f"Среднее потребление: {int(avg_calories)} ккал/день\n"

        # Подсчитываем макронутриенты
        total_protein = sum(meal.get("protein_g", 0) for meal in meals)
        total_fat = sum(meal.get("fat_g", 0) for meal in meals)
        total_carbs = sum(meal.get("carbs_g", 0) for meal in meals)

        avg_protein = total_protein / len(meals)
        avg_fat = total_fat / len(meals)
        avg_carbs = total_carbs / len(meals)

        stats_text += (
            f"Белки: {int(avg_protein)}г | Жиры: {int(avg_fat)}г | "
            f"Углеводы: {int(avg_carbs)}г\n"
        )
    else:
        stats_text += "Нет данных о питании\n"

    # Отправляем статистику
    await message.answer(
        stats_text, parse_mode="Markdown", reply_markup=main_kb
    )


# Обработчик команды /progress
@router.message(Command("progress"))
async def cmd_progress(message: Message) -> None:
    """Обработчик команды /progress."""
    telegram_id = message.from_user.id if message.from_user else None
    if not telegram_id:
        await message.answer(
            "Ошибка авторизации.",
            reply_markup=main_kb,
        )
        return

    # Получаем профиль пользователя
    user_api_client = get_user_api_client(telegram_id)
    profile = await user_api_client.get_profile()

    if not profile:
        await message.answer(
            "Для просмотра прогресса необходимо создать профиль. "
            "Используйте команду /start для создания профиля.",
            reply_markup=main_kb,
        )
        return

    # В реальном приложении здесь был бы запрос с фильтрацией по дате
    workouts = await user_api_client.get_workouts(limit=10)
    meals = await user_api_client.get_meals(limit=10)

    # Формируем отчет о прогрессе
    progress_text = "📈 *Отчет о прогрессе:*\n\n"

    # Прогресс по весу
    weight = profile.get("weight", 0)
    target_weight = profile.get("target_weight", 0)
    weight_diff = (
        abs(target_weight - weight) if weight and target_weight else 0
    )

    # Вычисляем процент прогресса
    initial_weight = profile.get("initial_weight", weight)
    if target_weight != initial_weight:
        weight_diff_initial = abs(target_weight - initial_weight)
        weight_progress = round((1 - weight_diff / weight_diff_initial) * 100)
    else:
        weight_progress = 0

    progress_text += "⚖️ *Прогресс по весу:*\n"
    progress_text += f"Начальный вес: {initial_weight} кг\n"
    progress_text += f"Текущий вес: {weight} кг\n"
    progress_text += f"Целевой вес: {target_weight} кг\n"
    progress_text += f"Прогресс: {weight_progress}%\n\n"

    # Прогресс по тренировкам
    total_workouts = len(workouts)
    total_duration = sum(
        workout.get("duration_minutes", 0) for workout in workouts
    )

    progress_text += "🏋️ *Прогресс по тренировкам:*\n"
    from bot.utils import format_workout_count

    progress_text += f"Всего {format_workout_count(total_workouts)}\n"
    progress_text += f"Общая длительность: {total_duration} минут\n"
    if workouts:
        total_intensity = sum(
            workout.get("intensity", 0) for workout in workouts
        )
        avg_intensity = total_intensity / total_workouts
        progress_text += (
            f"Средняя интенсивность: {round(avg_intensity, 1)}/10\n\n"
        )
    else:
        progress_text += "Нет данных о тренировках\n\n"

    # Прогресс по питанию
    if meals:
        total_calories = sum(meal.get("calories", 0) for meal in meals)
        avg_calories = total_calories / len(meals)
        progress_text += "🥗 *Прогресс по питанию:*\n"
        progress_text += (
            f"Среднее потребление: {int(avg_calories)} ккал/день\n"
        )
    else:
        progress_text += "🥗 *Прогресс по питанию:*\n"
        progress_text += "Нет данных о питании\n"

    # Отправляем отчет о прогрессе
    await message.answer(
        progress_text, parse_mode="Markdown", reply_markup=main_kb
    )

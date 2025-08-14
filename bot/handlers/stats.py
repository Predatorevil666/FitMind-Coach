from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.api_client import UserAPIClient
from bot.keyboards.reply import main_kb

router = Router()


def get_user_api_client(telegram_id: int) -> UserAPIClient:
    """Создать API клиент для пользователя."""
    return UserAPIClient(telegram_id)


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
    workouts = await user_api_client.get_workouts(limit=5) or []

    # Получаем последние приемы пищи
    meals = await user_api_client.get_meals(limit=5) or []

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
    workouts = await user_api_client.get_workouts(limit=10) or []
    meals = await user_api_client.get_meals(limit=10) or []

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

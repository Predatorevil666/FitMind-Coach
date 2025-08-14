"""Константы для API FitMind Coach."""

# Настройки безопасности
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 дней
ALGORITHM = "HS256"
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 30  # 30 дней

# Настройки базы данных
DEFAULT_ITEMS_LIMIT = 100
DEFAULT_ITEMS_OFFSET = 0

# Настройки пользователей
PASSWORD_MIN_LENGTH = 8
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 50

# Настройки профиля
DEFAULT_GOAL = "other"
DEFAULT_WORKOUTS_PER_WEEK = 3

# Настройки тренировок
WORKOUT_TYPES = [
    "strength",
    "cardio",
    "flexibility",
    "hiit",
    "other",
]

# Настройки питания
MEAL_TYPES = [
    "breakfast",
    "lunch",
    "dinner",
    "snack",
    "other",
]

# Настройки анализов
DEFAULT_LAB_UNIT = "единиц"

# Сообщения об ошибках
ERROR_MESSAGES = {
    "user_exists_email": "Пользователь с таким email уже существует",
    "user_exists_username": "Пользователь с таким именем уже существует",
    "user_not_found": "Пользователь не найден",
    "profile_exists": "У пользователя уже есть профиль",
    "profile_not_found": "Профиль не найден",
    "workout_not_found": "Тренировка не найдена",
    "meal_not_found": "Прием пищи не найден",
    "lab_not_found": "Результат анализа не найден",
    "incorrect_credentials": "Неверный email или пароль",
    "inactive_user": "Пользователь неактивен",
    "not_authenticated": "Не аутентифицирован",
    "not_authorized": "Недостаточно прав",
}

"""Константы для бота FitMind Coach."""

# Типы тренировок
WORKOUT_TYPES = {
    "силовая": "strength",
    "кардио": "cardio",
    "йога": "flexibility",
    "hiit": "hiit",
    "другое": "other",
}

# Отображаемые названия типов тренировок
WORKOUT_TYPE_DISPLAY = {
    "strength": "Силовая",
    "cardio": "Кардио",
    "flexibility": "Гибкость/Йога",
    "hiit": "HIIT",
    "other": "Другое",
}

# Калории, сжигаемые за минуту по типам тренировок
CALORIES_PER_MIN = {
    "strength": 5,
    "cardio": 8,
    "flexibility": 3,
    "hiit": 10,
    "other": 5,
}

# Типы целей
GOAL_MAP = {
    "похудеть": "weight_loss",
    "набрать массу": "muscle_gain",
    "подготовка к марафону": "endurance",
    "здоровье": "health",
    "другое": "other",
}

# Отображаемые названия целей
GOAL_DISPLAY = {
    "weight_loss": "Похудение",
    "muscle_gain": "Набор массы",
    "endurance": "Подготовка к марафону",
    "health": "Здоровье",
    "other": "Другое",
}

# Уровни активности
ACTIVITY_LEVELS = {
    "малоподвижный": "sedentary",
    "слабо активный": "lightly_active",
    "умеренно активный": "moderately_active",
    "очень активный": "very_active",
    "экстремально активный": "extremely_active",
}

# Отображаемые названия уровней активности
ACTIVITY_DISPLAY = {
    "sedentary": "Малоподвижный",
    "lightly_active": "Слабо активный",
    "moderately_active": "Умеренно активный",
    "very_active": "Очень активный",
    "extremely_active": "Экстремально активный",
}

# Типы приемов пищи
MEAL_TYPES = {
    "завтрак": "breakfast",
    "обед": "lunch",
    "ужин": "dinner",
    "перекус": "snack",
    "другое": "other",
}

# Отображаемые названия типов приемов пищи
MEAL_TYPE_DISPLAY = {
    "breakfast": "Завтрак",
    "lunch": "Обед",
    "dinner": "Ужин",
    "snack": "Перекус",
    "other": "Другое",
}

# Референсные значения для анализов
LAB_REFERENCES = {
    "гемоглобин": {"unit": "г/л", "min": 130, "max": 160},
    "холестерин": {"unit": "ммоль/л", "min": 3.5, "max": 5.2},
    "глюкоза": {"unit": "ммоль/л", "min": 3.9, "max": 5.8},
    "лейкоциты": {"unit": "10^9/л", "min": 4, "max": 9},
    "эритроциты": {"unit": "10^12/л", "min": 4.0, "max": 5.1},
    "ферритин": {"unit": "мкг/л", "min": 20, "max": 250},
    "кортизол": {"unit": "мкг/дл", "min": 5, "max": 23},
}

# Статусы значений анализов
LAB_STATUS = {
    "low": "понижен",
    "normal": "норма",
    "high": "повышен",
}

# Шаблоны сообщений
MESSAGES = {
    # Общие сообщения
    "operation_cancelled": "Операция отменена.",
    "back_to_main": "Вы вернулись в главное меню.",
    "no_active_operations": "Нет активных операций для отмены.",
    # Сообщения для профиля
    "profile_not_found": (
        "Профиль не найден. Пожалуйста, создайте профиль сначала."
    ),
    "profile_created": (
        "✅ Профиль успешно создан!\n\n"
        "Теперь вы можете использовать все функции бота."
    ),
    # Сообщения для тренировок
    "workout_added": (
        "✅ Тренировка добавлена: {type} ({duration} мин) | {calories} ккал"
    ),
    "workout_not_added": (
        "❌ Не удалось добавить тренировку. "
        "Пожалуйста, проверьте данные и попробуйте снова."
    ),
    # Сообщения для питания
    "meal_added": (
        "🍎 {weight}г {name}: {calories} ккал | "
        "Б:{protein}г Ж:{fat}г У:{carbs}г"
    ),
    "meal_not_added": (
        "❌ Не удалось добавить прием пищи. "
        "Пожалуйста, проверьте данные и попробуйте снова."
    ),
    # Сообщения для анализов
    "lab_added": ("🩸 {name}: {value} {unit} ({status}, норма {min}-{max})"),
    "lab_not_added": (
        "❌ Не удалось добавить результат анализа. "
        "Пожалуйста, проверьте данные и попробуйте снова."
    ),
}

# Сообщения для авторизации
AUTH_REQUIRED_MSG = (
    "⚠️ Для использования бота необходимо привязать ваш "
    "Telegram аккаунт.\n\n"
    "Если у вас уже есть аккаунт в системе, используйте "
    "команду /login для привязки.\n"
    "Для создания нового аккаунта используйте /register."
)

AUTH_ERROR_MSG = "Ошибка авторизации."

PROFILE_ACCESS_ERROR_MSG = (
    "Для доступа к профилю необходимо авторизоваться.\n"
    "Используйте команду /login для входа или "
    "/register для регистрации."
)

# Сообщения для профиля (дополнительные)
PROFILE_NOT_FOUND_MSG = (
    "Профиль не найден. Используйте команду /create_profile для создания."
)
PROFILE_EXISTS_MSG = (
    "У вас уже есть профиль. Используйте команду /profile для просмотра."
)
UPDATE_FAILED_MSG = (
    "❌ Не удалось обновить профиль. Возможно, вы не авторизованы."
)

# Ограничения для валидации
MIN_AGE = 16
MAX_AGE = 100
MIN_HEIGHT = 100  # см
MAX_HEIGHT = 250  # см
MIN_WEIGHT = 30  # кг
MAX_WEIGHT = 300  # кг
MIN_DURATION = 1  # минуты
MAX_DURATION = 300  # минуты
MIN_CALORIES = 1
MAX_CALORIES = 2000

# Ограничения для валидаторов
MAX_EMAIL_LENGTH = 254
MAX_USERNAME_LENGTH = 50
MAX_PASSWORD_LENGTH = 128
MIN_VALIDATOR_WEIGHT = 1.0
MAX_VALIDATOR_WEIGHT = 300.0
MIN_VALIDATOR_CALORIES = 1
MAX_VALIDATOR_CALORIES = 10000
MAX_NUTRIENT_VALUE = 1000.0
MAX_WORKOUT_DURATION = 600  # минуты
MIN_INTENSITY = 1
MAX_INTENSITY = 10
MAX_LAB_VALUE = 99999.0
MIN_VALIDATOR_AGE = 10
MAX_VALIDATOR_AGE = 120
MIN_VALIDATOR_HEIGHT = 50.0
MAX_VALIDATOR_HEIGHT = 250.0
MIN_WEEKLY_WORKOUTS = 0.5
MAX_WEEKLY_WORKOUTS = 14.0

# MET коэффициенты для расчёта калорий
MET_VALUES = {
    "strength": 6.0,
    "cardio": 8.0,
    "flexibility": 2.5,
    "hiit": 12.0,
    "other": 5.0,
}

# Множители активности для расчёта дневных калорий
ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.2,
    "lightly_active": 1.375,
    "moderately_active": 1.55,
    "very_active": 1.725,
    "extremely_active": 1.9,
}

# Шаблоны тренировок
WORKOUT_TEMPLATES = {
    "💪 Силовая тренировка": "strength",
    "🏃 Кардио тренировка": "cardio",
    "🦵 Тренировка ног": "strength",
    "💪 Тренировка рук": "strength",
    "🏋️ Тренировка спины": "strength",
    "🫁 Тренировка груди": "strength",
    "🧘 Йога": "flexibility",
    "🤸 Растяжка": "flexibility",
}

TEMPLATE_WORKOUTS = {
    "💪 Силовая тренировка": "strength",
    "🏃 Кардио тренировка": "cardio",
    "🧘 Йога": "flexibility",
    "🦵 Тренировка ног": "strength",
    "🏋️ Тренировка рук": "strength",
    "🫁 Тренировка спины": "strength",
    "🤸 Тренировка груди": "strength",
}

# Эмодзи для типов тренировок
WORKOUT_TYPE_EMOJI = {
    "strength": "💪",
    "cardio": "🏃",
    "flexibility": "🧘",
    "hiit": "⚡",
    "other": "🔄",
}

# Специфические упражнения
SPECIFIC_EXERCISES = [
    "жим лежа",
    "приседания",
    "становая тяга",
    "подтягивания",
    "отжимания",
    "планка",
    "бег",
    "ходьба",
    "велосипед",
    "плавание",
    "йога",
    "растяжка",
    "пресс",
    "берпи",
]

# Сообщения для тренировок
WORKOUT_SECTION_MSG = "Раздел тренировок. Выберите действие:"
WORKOUT_MENU_MSG = "🏋️ Меню тренировок\n\nВыберите действие:"
ADD_WORKOUT_MSG = "Запуск формы добавления тренировки..."
NO_WORKOUTS_MSG = "У вас пока нет добавленных тренировок."
WORKOUT_LIST_HEADER = "📋 *Ваши последние тренировки:*\n\n"
SELECT_WORKOUT_NAME_MSG = "Выберите название тренировки или введите своё:"
ENTER_WORKOUT_NAME_MSG = "Введите название тренировки:"
SELECT_WORKOUT_TYPE_MSG = (
    "Выберите тип тренировки:\n"
    "Используйте кнопку 🔙 Назад для возврата к выбору названия."
)
ENTER_DURATION_MSG = (
    "Введите продолжительность тренировки в минутах (только число):"
)
ENTER_CALORIES_MSG = (
    "Введите количество сожженных калорий (только число):\n"
    "Если не знаете, введите 0.\n"
    "Используйте кнопку 🔙 Назад для возврата к вводу продолжительности."
)
ENTER_NOTES_MSG = (
    "Введите заметки о тренировке (упражнения, веса, подходы и т.д.):\n"
    "Если нет заметок, отправьте '-'"
)
WORKOUT_ADD_ERROR_MSG = (
    "❌ Не удалось добавить тренировку. Пожалуйста, попробуйте позже."
)

# Сообщения для статистики
STATS_HEADER = "📊 *Ваша статистика:*\n\n"
PROGRESS_HEADER = "📈 *Отчет о прогрессе:*\n\n"
LAST_WORKOUTS_HEADER = "🏋️ *Последние тренировки:*\n"
LAST_MEALS_HEADER = "🥗 *Последние приемы пищи:*\n"
WEIGHT_PROGRESS_HEADER = "⚖️ *Прогресс по весу:*\n"
WORKOUT_PROGRESS_HEADER = "🏋️ *Прогресс по тренировкам:*\n"
MEAL_PROGRESS_HEADER = "🥗 *Прогресс по питанию:*\n"
NO_WORKOUT_DATA_MSG = "Нет данных о тренировках"
NO_MEAL_DATA_MSG = "Нет данных о питании"

# Сообщения для общих действий
BACK_TO_MAIN_MENU_MSG = "Вы вернулись в главное меню."
NUTRITION_SECTION_MSG = "Раздел питания. Выберите действие:"
LAB_SECTION_MSG = "Раздел лабораторных данных. Выберите действие:"

# Кнопки и метки
BUTTON_WORKOUTS = "🏋️‍♂️ Тренировки"
BUTTON_NUTRITION = "🍎 Питание"
BUTTON_STATS = "📊 Статистика"
BUTTON_LAB_DATA = "🔬 Лабораторные данные"
BUTTON_PROFILE = "👤 Профиль"
BUTTON_ADVICE = "💡 Получить совет"
BUTTON_BACK = "🔙 Назад"
BUTTON_CANCEL = "❌ Отмена"
BUTTON_ADD_WORKOUT = "➕ Добавить тренировку"
BUTTON_MY_WORKOUTS = "📋 Мои тренировки"
BUTTON_VIEW_PROFILE = "👁️ Просмотреть профиль"
BUTTON_EDIT_PROFILE = "✏️ Редактировать профиль"
BUTTON_CUSTOM_NAME = "✏️ Своё название"

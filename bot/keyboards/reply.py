from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏋️‍♂️ Тренировки"),
            KeyboardButton(text="🍽 Питание"),
        ],
        [
            KeyboardButton(text="🔬 Лабораторные данные"),
            KeyboardButton(text="📊 Статистика"),
        ],
        [
            KeyboardButton(text="👤 Профиль"),
            KeyboardButton(text="💡 Получить совет"),
        ],
    ],
    resize_keyboard=True,
)

# Клавиатура для раздела тренировок
workout_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Добавить тренировку"),
            KeyboardButton(text="📋 Мои тренировки"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

# Клавиатура для раздела питания
meal_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Добавить прием пищи"),
            KeyboardButton(text="📋 Мои приемы пищи"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

# Клавиатура для раздела анализов
lab_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="➕ Добавить анализ"),
            KeyboardButton(text="📋 Мои анализы"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

# Клавиатура для раздела профиля
profile_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="✏️ Редактировать профиль"),
            KeyboardButton(text="👁️ Просмотреть профиль"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие",
)

# Клавиатура для отмены операции
cancel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Нажмите для отмены",
)

# Типы тренировок
workout_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💪 Силовая"),
            KeyboardButton(text="🏃 Кардио"),
        ],
        [
            KeyboardButton(text="🧘 Гибкость"),
            KeyboardButton(text="⚡ HIIT"),
        ],
        [
            KeyboardButton(text="🔄 Другое"),
            KeyboardButton(text="❌ Отмена"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите тип тренировки",
)

# Клавиатура для процесса добавления тренировки с кнопками отмены и возврата
workout_form_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="❌ Отмена"),
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Добавление тренировки",
)

# Шаблоны названий тренировок
workout_template_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="💪 Силовая тренировка"),
            KeyboardButton(text="🏃 Кардио тренировка"),
        ],
        [
            KeyboardButton(text="🦵 Тренировка ног"),
            KeyboardButton(text="💪 Тренировка рук"),
        ],
        [
            KeyboardButton(text="🏋️ Тренировка спины"),
            KeyboardButton(text="🫁 Тренировка груди"),
        ],
        [
            KeyboardButton(text="🧘 Йога"),
            KeyboardButton(text="🤸 Растяжка"),
        ],
        [
            KeyboardButton(text="✏️ Своё название"),
            KeyboardButton(text="❌ Отмена"),
        ],
        [
            KeyboardButton(text="🔙 Назад"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите название тренировки",
)

# Типы приемов пищи
meal_type_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🍳 Завтрак"),
            KeyboardButton(text="🥪 Обед"),
        ],
        [
            KeyboardButton(text="🍲 Ужин"),
            KeyboardButton(text="🍎 Перекус"),
        ],
        [
            KeyboardButton(text="🔄 Другое"),
            KeyboardButton(text="❌ Отмена"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите тип приема пищи",
)

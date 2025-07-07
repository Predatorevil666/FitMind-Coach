"""Валидаторы для бота FitMind Coach."""

import re


def validate_email(email: str) -> tuple[bool, str]:
    """
    Валидация email адреса.

    Args:
        email: Email адрес для проверки

    Returns:
        tuple: (is_valid, error_message)
    """
    if not email or not email.strip():
        return False, "Email не может быть пустым"

    email = email.strip()

    # Проверка длины
    if len(email) > 254:
        return False, "Email слишком длинный (максимум 254 символа)"

    # Проверка базовой структуры
    if email.count("@") != 1:
        return False, "Email должен содержать ровно один символ @"

    local, domain = email.split("@")

    # Проверка локальной части (до @)
    if not local:
        return False, "Отсутствует имя пользователя перед @"

    if len(local) > 64:
        return (
            False,
            "Имя пользователя слишком длинное (максимум 64 символа)",
        )

    # Проверка домена (после @)
    if not domain:
        return False, "Отсутствует домен после @"

    if len(domain) > 253:
        return False, "Домен слишком длинный (максимум 253 символа)"

    # Проверка регулярным выражением (упрощенная RFC-совместимая)
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Некорректный формат email адреса"

    # Проверка на двойные точки
    if ".." in email:
        return False, "Email не может содержать две точки подряд"

    # Проверка начала и конца локальной части
    if local.startswith(".") or local.endswith("."):
        return (
            False,
            "Имя пользователя не может начинаться или заканчиваться точкой",
        )

    # Проверка домена на валидность
    domain_parts = domain.split(".")
    if len(domain_parts) < 2:
        return False, "Домен должен содержать минимум одну точку"

    for part in domain_parts:
        if not part:
            return False, "Некорректный формат домена"
        if part.startswith("-") or part.endswith("-"):
            return (
                False,
                "Части домена не могут начинаться или заканчиваться дефисом",
            )

    # Проверка TLD (последняя часть домена)
    tld = domain_parts[-1].lower()
    if len(tld) < 2:
        return False, "Доменная зона должна содержать минимум 2 символа"

    if not tld.isalpha():
        return False, "Доменная зона должна содержать только буквы"

    return True, ""


def validate_username(username: str) -> tuple[bool, str]:
    """
    Валидация имени пользователя.

    Args:
        username: Имя пользователя для проверки

    Returns:
        tuple: (is_valid, error_message)
    """
    if not username or not username.strip():
        return False, "Имя пользователя не может быть пустым"

    username = username.strip()

    # Проверка длины
    if len(username) < 3:
        return (False, "Имя пользователя должно содержать не менее 3 символов")

    if len(username) > 50:
        return (False, "Имя пользователя не может быть длиннее 50 символов")

    # Проверка разрешенных символов
    if not re.match(r"^[a-zA-Z0-9._-]+$", username):
        return (
            False,
            "Имя пользователя может содержать только буквы, "
            "цифры, точки, подчеркивания и дефисы",
        )

    # Проверка, что не начинается и не заканчивается спец. символами
    if username.startswith((".", "_", "-")) or username.endswith(
        (".", "_", "-")
    ):
        return (
            False,
            "Имя пользователя не может начинаться или заканчиваться "
            "точкой, подчеркиванием или дефисом",
        )

    return True, ""


def validate_password(password: str) -> tuple[bool, str]:
    """
    Валидация пароля.

    Args:
        password: Пароль для проверки

    Returns:
        tuple: (is_valid, error_message)
    """
    if not password:
        return False, "Пароль не может быть пустым"

    # Проверка длины
    if len(password) < 8:
        return False, "Пароль должен содержать не менее 8 символов"

    if len(password) > 128:
        return False, "Пароль не может быть длиннее 128 символов"

    # Дополнительные проверки безопасности (опционально)
    has_letter = bool(re.search(r"[a-zA-Z]", password))
    has_digit = bool(re.search(r"\d", password))

    if not has_letter and not has_digit:
        return (False, "Пароль должен содержать хотя бы одну букву или цифру")

    return True, ""


def validate_float_range(
    value_str: str, min_val: float, max_val: float, field_name: str
) -> tuple[bool, str, float]:
    """
    Валидация числового значения с плавающей точкой в диапазоне.

    Args:
        value_str: Строка с числом
        min_val: Минимальное значение
        max_val: Максимальное значение
        field_name: Название поля для ошибки

    Returns:
        tuple: (is_valid, error_message, parsed_value)
    """
    if not value_str or not value_str.strip():
        return False, f"{field_name} не может быть пустым", 0.0

    try:
        # Поддержка запятой как десятичного разделителя
        value = float(value_str.strip().replace(",", "."))

        if value < min_val or value > max_val:
            return (
                False,
                f"{field_name} должно быть от {min_val} до {max_val}",
                0.0,
            )

        return True, "", value

    except ValueError:
        return (
            False,
            f"Пожалуйста, введите число для поля '{field_name}'",
            0.0,
        )


def validate_int_range(
    value_str: str, min_val: int, max_val: int, field_name: str
) -> tuple[bool, str, int]:
    """
    Валидация целого числа в диапазоне.

    Args:
        value_str: Строка с числом
        min_val: Минимальное значение
        max_val: Максимальное значение
        field_name: Название поля для ошибки

    Returns:
        tuple: (is_valid, error_message, parsed_value)
    """
    if not value_str or not value_str.strip():
        return False, f"{field_name} не может быть пустым", 0

    try:
        value = int(value_str.strip())

        if value < min_val or value > max_val:
            return (
                False,
                f"{field_name} должно быть от {min_val} до {max_val}",
                0,
            )

        return True, "", value

    except ValueError:
        return (
            False,
            f"Пожалуйста, введите целое число для поля '{field_name}'",
            0,
        )


def validate_weight(weight_str: str) -> tuple[bool, str, float]:
    """
    Валидация веса в килограммах.

    Args:
        weight_str: Строка с весом

    Returns:
        tuple: (is_valid, error_message, parsed_weight)
    """
    return validate_float_range(weight_str, 1.0, 300.0, "Вес")


def validate_calories(calories_str: str) -> tuple[bool, str, int]:
    """
    Валидация калорий.

    Args:
        calories_str: Строка с калориями

    Returns:
        tuple: (is_valid, error_message, parsed_calories)
    """
    return validate_int_range(calories_str, 1, 10000, "Калории")


def validate_macronutrient(
    value_str: str, nutrient_name: str
) -> tuple[bool, str, float]:
    """
    Валидация макронутриентов (белки, жиры, углеводы).

    Args:
        value_str: Строка со значением
        nutrient_name: Название нутриента

    Returns:
        tuple: (is_valid, error_message, parsed_value)
    """
    return validate_float_range(value_str, 0.0, 1000.0, nutrient_name)


def validate_duration(duration_str: str) -> tuple[bool, str, int]:
    """
    Валидация длительности тренировки в минутах.

    Args:
        duration_str: Строка с длительностью

    Returns:
        tuple: (is_valid, error_message, parsed_duration)
    """
    return validate_int_range(duration_str, 1, 600, "Длительность")


def validate_intensity(intensity_str: str) -> tuple[bool, str, int]:
    """
    Валидация интенсивности тренировки (1-10).

    Args:
        intensity_str: Строка с интенсивностью

    Returns:
        tuple: (is_valid, error_message, parsed_intensity)
    """
    return validate_int_range(intensity_str, 1, 10, "Интенсивность")


def validate_lab_value(value_str: str) -> tuple[bool, str, float]:
    """
    Валидация значения лабораторного анализа.

    Args:
        value_str: Строка со значением

    Returns:
        tuple: (is_valid, error_message, parsed_value)
    """
    return validate_float_range(value_str, 0.0, 99999.0, "Значение анализа")


def validate_age(age_str: str) -> tuple[bool, str, int]:
    """
    Валидация возраста.

    Args:
        age_str: Строка с возрастом

    Returns:
        tuple: (is_valid, error_message, parsed_age)
    """
    return validate_int_range(age_str, 10, 120, "Возраст")


def validate_height(height_str: str) -> tuple[bool, str, float]:
    """
    Валидация роста в сантиметрах.

    Args:
        height_str: Строка с ростом

    Returns:
        tuple: (is_valid, error_message, parsed_height)
    """
    return validate_float_range(height_str, 50.0, 250.0, "Рост")


def validate_workouts_per_week(workouts_str: str) -> tuple[bool, str, float]:
    """
    Валидация количества тренировок в неделю.

    Args:
        workouts_str: Строка с количеством тренировок

    Returns:
        tuple: (is_valid, error_message, parsed_workouts)
    """
    return validate_float_range(workouts_str, 0.5, 14.0, "Тренировок в неделю")


def validate_passwords_match(
    password: str, password_confirm: str
) -> tuple[bool, str]:
    """
    Проверка совпадения паролей.

    Args:
        password: Пароль
        password_confirm: Подтверждение пароля

    Returns:
        tuple: (is_valid, error_message)
    """
    if password != password_confirm:
        return False, "Пароли не совпадают"

    return True, ""

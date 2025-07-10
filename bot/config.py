import os

from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

# Получаем токен бота из переменных окружения
TG_TOKEN = os.getenv("TG_TOKEN")

if not TG_TOKEN:
    raise ValueError(
        "TG_TOKEN не найден в переменных окружения. Проверьте .env файл."
    )

# Получаем URL API из переменных окружения или используем значение по умолчанию
API_URL = os.getenv("API_URL", "http://localhost:8003/api/v1")

# Получаем API ключ Mistral из переменных окружения
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")

if not MISTRAL_API_KEY:
    raise ValueError(
        "MISTRAL_API_KEY не найден в переменных окружения. "
        "Проверьте .env файл."
    )

# Настройки для Mistral API
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")
MISTRAL_MAX_RETRIES = int(os.getenv("MISTRAL_MAX_RETRIES", "2"))
MISTRAL_TIMEOUT = float(os.getenv("MISTRAL_TIMEOUT", "60.0"))
MISTRAL_MIN_WAIT = float(os.getenv("MISTRAL_MIN_WAIT", "1.0"))
MISTRAL_MAX_WAIT = float(os.getenv("MISTRAL_MAX_WAIT", "5.0"))

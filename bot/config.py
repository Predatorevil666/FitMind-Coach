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

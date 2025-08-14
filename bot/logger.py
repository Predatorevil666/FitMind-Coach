import logging

from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logger(name="bot_logger"):
    """
    Настройка логирования с выводом в файл и консоль
    """
    # Создаем директорию для логов, если она не существует
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Настраиваем логгер
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Форматирование логов
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Обработчик для вывода в файл с ротацией
    # Максимальный размер файла 10MB, хранить до 5 файлов
    file_handler = RotatingFileHandler(
        logs_dir / "bot.log",
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Обработчик для вывода в консоль
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Добавляем обработчики к логгеру
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


# Создаем и экспортируем глобальный логгер
logger = setup_logger()

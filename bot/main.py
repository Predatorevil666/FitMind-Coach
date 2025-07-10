import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from bot.api_client import _api_client
from bot.config import TG_TOKEN
from bot.logger import logger
from bot.routers import setup_routers


# Основная функция
async def main():
    # Выводим информацию о запуске
    logger.info("Запуск бота")

    # Создаем объекты бота и диспетчера с хранилищем состояний
    try:
        bot = Bot(token=TG_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(storage=storage)

        # Настраиваем роутеры
        setup_routers(dp)

        # Запускаем бота
        logger.info("Подключение к Telegram API...")
        await bot.delete_webhook(drop_pending_updates=True)

        # Запускаем сессию API клиента
        await _api_client.start_session()

        # Запускаем поллинг
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        # Закрываем сессию API клиента
        await _api_client.close_session()
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

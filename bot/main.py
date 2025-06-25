import asyncio

from aiogram import Bot, Dispatcher

from bot.config import TG_TOKEN
from bot.handlers.start import router as start_router
from bot.logger import logger


# Основная функция
async def main():
    # Выводим информацию о запуске
    logger.info("Запуск бота")

    # Создаем объекты бота и диспетчера
    try:
        bot = Bot(token=TG_TOKEN)
        dp = Dispatcher()

        # Регистрируем роутер
        dp.include_router(start_router)

        # Запускаем бота
        logger.info("Подключение к Telegram API...")
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")

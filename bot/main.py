from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from prometheus_client import start_http_server

import os
from dotenv import load_dotenv, dotenv_values

from routers import router


load_dotenv()

# Инициализируем бот и диспатчер
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())


# Запуск сервера метрик при старте
async def on_startup():
    start_http_server(4321)  # Метрики будут доступны на http://bot:4321/metrics


async def main() -> None:
    await on_startup()

    dp.include_router(router)

    print('Bot started!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
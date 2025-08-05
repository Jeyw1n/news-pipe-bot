from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio

import os
from dotenv import load_dotenv, dotenv_values

from routers import router


load_dotenv()

# Инициализируем бот и диспатчер
bot = Bot(token=os.getenv("BOT_TOKEN"), default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())


async def main() -> None:

    dp.include_router(router)

    print('Bot started!')
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"An error occurred: {e}")
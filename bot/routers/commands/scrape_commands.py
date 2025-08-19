from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from loguru import logger

from scrapers import scrape_posts

from metrics_client import MESSAGES_RECEIVED

router = Router(name=__name__)

@router.message(Command('scrape'))
async def start_command(message: Message) -> None:

    # Увеличиваем счетчик сообщений
    MESSAGES_RECEIVED.inc()

    await message.answer(text="Парсинг начался!")
    posts = scrape_posts()
    for i in posts:
        print("перебор сгенерированных постов")
        try:
            if len(i) > 1000:
                print(i)
                continue
            await message.answer(text=i)
        except Exception as ex:
            logger.error(f"Ошибка отправки обработанного текста: {ex}")
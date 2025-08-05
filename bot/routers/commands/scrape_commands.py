from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

from scrapers import scrape_posts

router = Router(name=__name__)

@router.message(Command('/scrape'))
async def start_command(message: Message) -> None:
    await message.answer(text="Парсинг начался!")
    posts = scrape_posts()
    for i in posts:
        print(i)

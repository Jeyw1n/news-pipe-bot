__all__ = ("router", )
from aiogram import Router
from .scrape_commands import router as scrape_router
router = Router(name=__name__)
router.include_router(scrape_router)
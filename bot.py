import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
import database as db
from handlers import private, group_menu, moderation


async def main():
    logging.basicConfig(level=logging.INFO)

    if not BOT_TOKEN or BOT_TOKEN == "8551854797:AAE5AehzgsWiq4bt2d-DawEDX4qFtVg8HnA":
        raise RuntimeError(
            "Не задан BOT_TOKEN. Укажите его в config.py или переменной окружения BOT_TOKEN."
        )

    await db.init_db()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(private.router)
    dp.include_router(group_menu.router)
    dp.include_router(moderation.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

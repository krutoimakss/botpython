from aiogram import Bot
from aiogram.types import Message


async def is_chat_admin(bot: Bot, chat_id: int, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id, user_id)
    except Exception:
        return False
    return member.status in ("creator", "administrator")


def count_emojis(text: str) -> int:
    """Простой подсчёт эмодзи в строке по диапазонам unicode."""
    if not text:
        return 0
    count = 0
    for ch in text:
        code = ord(ch)
        if (
            0x1F300 <= code <= 0x1FAFF
            or 0x2600 <= code <= 0x27BF
            or 0x2190 <= code <= 0x21FF
            or 0x2B00 <= code <= 0x2BFF
            or code in (0x2764, 0x2705, 0x274C)
        ):
            count += 1
    return count

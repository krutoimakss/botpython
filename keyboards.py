from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def start_keyboard(bot_username: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🐣 Добавить",
        url=f"https://t.me/{bot_username}?startgroup=true",
    )
    builder.button(text="❔ Что умеет этот бот", callback_data="about")
    builder.adjust(1)
    return builder.as_markup()


def main_menu_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="Запрещённые слова", callback_data="menu_words")
    builder.button(text="Лимит эмодзи", callback_data="menu_emoji")
    builder.button(text="Уничтожение 18+", callback_data="menu_nsfw")
    builder.button(text="Антирейд", callback_data="menu_antiraid")
    builder.adjust(1)
    return builder.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="⬅️ Назад", callback_data="menu_back")
    return builder.as_markup()

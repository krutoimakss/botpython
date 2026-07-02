from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import texts
from keyboards import start_keyboard

router = Router(name="private")


@router.message(CommandStart(), F.chat.type == "private")
async def cmd_start(message: Message, bot: Bot):
    me = await bot.get_me()
    await message.answer(
        texts.START_TEXT,
        reply_markup=start_keyboard(me.username),
    )


@router.callback_query(F.data == "about")
async def cb_about(call: CallbackQuery):
    await call.answer()
    await call.message.answer(texts.ABOUT_TEXT)

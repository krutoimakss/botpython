import time
from collections import defaultdict, deque

from aiogram import Router, F, Bot
from aiogram.types import Message, ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, JOIN_TRANSITION

import texts
import database as db
from config import (
    RAID_JOIN_WINDOW_SECONDS,
    RAID_JOIN_THRESHOLD,
    FLOOD_WINDOW_SECONDS,
    FLOOD_MESSAGE_THRESHOLD,
)
from utils import count_emojis

router = Router(name="moderation")

# Внутрипроцессная память для антирейда/антифлуда.
# Для промышленного использования лучше вынести в Redis.
_join_events: dict[int, deque] = defaultdict(deque)
_message_events: dict[tuple[int, int], deque] = defaultdict(deque)


def _is_nsfw_media(message: Message) -> bool:
    """
    Заглушка определения 18+ контента.
    Точная классификация NSFW требует внешнего сервиса компьютерного зрения
    (например, Google Cloud Vision SafeSearch, AWS Rekognition и т.п.).
    Здесь как эвристика используется флаг "спойлер" у фото/видео,
    которым в Telegram чаще всего помечают деликатный контент.
    Замените эту функцию на вызов реального модератора контента при необходимости.
    """
    if message.has_media_spoiler:
        return True
    return False


@router.my_chat_member()
async def on_bot_added_to_chat(event: ChatMemberUpdated, bot: Bot):
    """Срабатывает, когда бота добавляют/удаляют/меняют его права в чате."""
    if event.chat.type not in ("group", "supergroup"):
        return
    old_status = event.old_chat_member.status
    new_status = event.new_chat_member.status
    just_added = old_status in ("left", "kicked") and new_status in (
        "member",
        "administrator",
    )
    if not just_added:
        return

    settings = await db.get_chat_settings(event.chat.id)
    text = texts.WELCOME_IN_GROUP.format(
        antiraid="on" if settings["antiraid"] else "off",
        emoji_limit="on" if settings["emoji_limit_enabled"] else "off",
    )
    await bot.send_message(event.chat.id, text)

    # Пытаемся написать тому, кто добавил бота (владельцу/админу).
    inviter = event.from_user
    if inviter:
        try:
            await bot.send_message(inviter.id, texts.OWNER_DM_TEXT)
        except Exception:
            # Пользователь мог не запускать бота в личке (/start) — тогда написать нельзя.
            pass


@router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def on_member_join(event: ChatMemberUpdated, bot: Bot):
    """Антирейд: массовое вступление участников за короткое время."""
    settings = await db.get_chat_settings(event.chat.id)
    if not settings["antiraid"]:
        return

    now = time.monotonic()
    events = _join_events[event.chat.id]
    events.append(now)
    while events and now - events[0] > RAID_JOIN_WINDOW_SECONDS:
        events.popleft()

    if len(events) >= RAID_JOIN_THRESHOLD:
        # Похоже на рейд: ограничиваем только что вступившего пользователя.
        try:
            await bot.restrict_chat_member(
                chat_id=event.chat.id,
                user_id=event.new_chat_member.user.id,
                permissions={
                    "can_send_messages": False,
                    "can_send_media_messages": False,
                    "can_send_other_messages": False,
                },
            )
            await bot.send_message(
                event.chat.id,
                "🛡️ Обнаружен рейд (массовое вступление). "
                "Новые участники временно ограничены в правах.",
            )
        except Exception:
            pass


@router.message(F.chat.type.in_({"group", "supergroup"}))
async def moderate_message(message: Message, bot: Bot):
    """Основная модерация сообщений: запрещённые слова, лимит эмодзи, 18+."""
    if message.from_user and message.from_user.is_bot:
        return

    settings = await db.get_chat_settings(message.chat.id)

    # --- Антифлуд (часть антирейда) ---
    if settings["antiraid"] and message.from_user:
        key = (message.chat.id, message.from_user.id)
        now = time.monotonic()
        events = _message_events[key]
        events.append(now)
        while events and now - events[0] > FLOOD_WINDOW_SECONDS:
            events.popleft()
        if len(events) >= FLOOD_MESSAGE_THRESHOLD:
            try:
                await message.delete()
            except Exception:
                pass
            try:
                await bot.restrict_chat_member(
                    chat_id=message.chat.id,
                    user_id=message.from_user.id,
                    permissions={"can_send_messages": False},
                )
                await message.answer(
                    f"🛡️ {message.from_user.full_name} заблокирован(а) за флуд."
                )
            except Exception:
                pass
            return

    # --- Запрещённые слова ---
    if message.text or message.caption:
        content = (message.text or message.caption or "").lower()
        banned_words = await db.get_banned_words(message.chat.id)
        for word in banned_words:
            if word in content:
                try:
                    await message.delete()
                except Exception:
                    pass
                await message.answer(
                    f"⚠️ {message.from_user.full_name}, ваше сообщение удалено "
                    f"за использование запрещённого слова."
                )
                return

    # --- Лимит эмодзи ---
    if settings["emoji_limit_enabled"] and message.text:
        emoji_count = count_emojis(message.text)
        if emoji_count > settings["emoji_limit"]:
            try:
                await message.delete()
            except Exception:
                pass
            await message.answer(
                f"⚠️ {message.from_user.full_name}, превышен лимит эмодзи "
                f"({emoji_count} > {settings['emoji_limit']})."
            )
            return

    # --- 18+ контент ---
    has_media = any(
        [message.photo, message.video, message.sticker, message.animation]
    )
    if has_media and not settings["nsfw_allowed"] and _is_nsfw_media(message):
        try:
            await message.delete()
        except Exception:
            pass
        try:
            await bot.restrict_chat_member(
                chat_id=message.chat.id,
                user_id=message.from_user.id,
                permissions={"can_send_messages": False},
            )
        except Exception:
            pass
        await message.answer(
            f"🔞 {message.from_user.full_name} замьючен(а) за 18+ контент, "
            f"сообщение удалено."
      )

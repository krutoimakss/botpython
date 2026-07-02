import aiosqlite
from config import DB_PATH

_CREATE_CHATS = """
CREATE TABLE IF NOT EXISTS chats (
    chat_id INTEGER PRIMARY KEY,
    antiraid INTEGER NOT NULL DEFAULT 1,
    emoji_limit_enabled INTEGER NOT NULL DEFAULT 0,
    emoji_limit INTEGER NOT NULL DEFAULT 0,
    nsfw_allowed INTEGER NOT NULL DEFAULT 0
);
"""

_CREATE_WORDS = """
CREATE TABLE IF NOT EXISTS banned_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chat_id INTEGER NOT NULL,
    word TEXT NOT NULL
);
"""


async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(_CREATE_CHATS)
        await db.execute(_CREATE_WORDS)
        await db.commit()


async def ensure_chat(chat_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO chats (chat_id) VALUES (?)", (chat_id,)
        )
        await db.commit()


async def get_chat_settings(chat_id: int) -> dict:
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT * FROM chats WHERE chat_id = ?", (chat_id,)
        )
        row = await cursor.fetchone()
        return dict(row)


async def set_antiraid(chat_id: int, enabled: bool):
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chats SET antiraid = ? WHERE chat_id = ?",
            (1 if enabled else 0, chat_id),
        )
        await db.commit()


async def set_emoji_limit(chat_id: int, limit: int):
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chats SET emoji_limit = ?, emoji_limit_enabled = 1 WHERE chat_id = ?",
            (limit, chat_id),
        )
        await db.commit()


async def set_emoji_limit_enabled(chat_id: int, enabled: bool):
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chats SET emoji_limit_enabled = ? WHERE chat_id = ?",
            (1 if enabled else 0, chat_id),
        )
        await db.commit()


async def set_nsfw_allowed(chat_id: int, allowed: bool):
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE chats SET nsfw_allowed = ? WHERE chat_id = ?",
            (1 if allowed else 0, chat_id),
        )
        await db.commit()


async def add_banned_word(chat_id: int, word: str):
    await ensure_chat(chat_id)
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO banned_words (chat_id, word) VALUES (?, ?)",
            (chat_id, word.lower()),
        )
        await db.commit()


async def get_banned_words(chat_id: int) -> list[str]:
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT word FROM banned_words WHERE chat_id = ?", (chat_id,)
        )
        rows = await cursor.fetchall()
        return [r[0] for r in rows]

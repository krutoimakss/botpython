import os

# Токен бота, полученный у @BotFather.
# Можно задать через переменную окружения BOT_TOKEN,
# либо просто вписать строкой ниже.
BOT_TOKEN = os.getenv("BOT_TOKEN", "8551854797:AAE5AehzgsWiq4bt2d-DawEDX4qFtVg8HnA")

# Имя пользователя бота без @ (нужно для кнопки "Добавить").
# Если оставить пустым - бот подставит его сам при старте через getMe().
BOT_USERNAME = os.getenv("BOT_USERNAME", "ShutUpWordBot")

# Путь к файлу базы данных SQLite
DB_PATH = os.getenv("DB_PATH", "clanbot.db")

# Настройки антирейда (защита от массового вступления ботов/спамеров)
RAID_JOIN_WINDOW_SECONDS = 10   # окно времени
RAID_JOIN_THRESHOLD = 5         # сколько вступлений за окно считается рейдом

# Настройки антифлуда (защита от спама сообщениями)
FLOOD_WINDOW_SECONDS = 5
FLOOD_MESSAGE_THRESHOLD = 6

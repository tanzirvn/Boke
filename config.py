# config.py
import os

# Telegram bot token (replace or set as environment variable in Replit)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "8077611794:AAHIAxN80HzsNGkfh8UCuUe5Sd52zMv63_A")

# Admin IDs (comma separated) -> replace with your Telegram user id(s)
ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "7507787272").split(",")]

# OpenAI API key for AI chat (replace or set as env var)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

# Database file
DB_PATH = os.getenv("DB_PATH", "bot_database.sqlite3")

# Scheduler settings
TIMEZONE = os.getenv("TIMEZONE", "Asia/Dhaka")

# Other settings
BOT_NAME = os.getenv("BOT_NAME", "AdvancedKeywordBot")
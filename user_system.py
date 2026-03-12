# user_system.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext
from utils import register_user, is_admin
from keyword_system import list_keywords, get_keyword
from database import get_conn

WELCOME_TEXT = """Assalamu Alaikum 👋
Welcome to the bot. Use /help to see commands.
"""

def start_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    register_user(user)
    update.message.reply_text(WELCOME_TEXT)

def help_handler(update: Update, context: CallbackContext):
    kb = [
        [InlineKeyboardButton("Contact Admin", callback_data="contact_admin")],
        [InlineKeyboardButton("Language", callback_data="set_lang")]
    ]
    update.message.reply_text("/start - Start\n/help - This menu\nYou can type keywords to get auto replies.", reply_markup=InlineKeyboardMarkup(kb))

def profile_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT rank, points FROM users WHERE user_id = ?", (user.id,))
    row = c.fetchone()
    conn.close()
    rank = row[0] if row else 0
    points = row[1] if row else 0
    msg = f"User: {user.full_name}\nID: {user.id}\nUsername: @{user.username if user.username else 'N/A'}\nRank: {rank}\nPoints: {points}"
    update.message.reply_text(msg)
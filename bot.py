# bot.py
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ChatAction
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler
from config import TELEGRAM_TOKEN, ADMIN_IDS, BOT_NAME
import database
from user_system import start_handler, help_handler, profile_handler
from chat_system import message_ai_handler
from group_system import on_member_join, on_member_left, message_filter_handler
from keyword_system import get_keyword, list_keywords
from admin_system import broadcast_message, add_admin, remove_admin
from auto_system import start_scheduler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def unknown(update: Update, context: CallbackContext):
    update.message.reply_text("Sorry, I didn't understand that. Use /help.")

def handle_text(update: Update, context: CallbackContext):
    text = update.message.text or ""
    # first run group filters
    message_filter_handler(update, context)

    # register user
    from utils import register_user
    register_user(update.effective_user)

    # keyword system: exact match first
    kw = get_keyword(text.strip().lower())
    if kw:
        ktype = kw['type']
        if ktype == "text":
            update.message.reply_text(kw['content'], parse_mode="HTML")
            return
        # other types (media, buttons) - basic support
        if ktype == "buttons":
            # extras expected as JSON {buttons:[{text:,url:}]}
            extras = kw.get('extras') or {}
            buttons = []
            for b in extras.get('buttons', []):
                if b.get('url'):
                    buttons.append([InlineKeyboardButton(b.get('text','Open'), url=b.get('url'))])
            update.message.reply_text(kw['content'] or " ", reply_markup=InlineKeyboardMarkup(buttons))
            return
        if ktype == "ai_chat":
            # forward to AI
            message_ai_handler(update, context)
            return

    # fallback: if message starts with /ai or mentions bot -> AI reply
    if text.startswith("/ai") or BOT_NAME.lower() in text.lower():
        message_ai_handler(update, context)
        return

    # optionally reply that no keyword found
    # update.message.reply_text("No keyword matched. Use /help or contact admin.")

def start_bot():
    database.init_db()
    updater = Updater(token=TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Commands
    dp.add_handler(CommandHandler("start", start_handler))
    dp.add_handler(CommandHandler("help", help_handler))
    dp.add_handler(CommandHandler("profile", profile_handler))
    # Admin commands (simple)
    def cmd_broadcast(update: Update, context: CallbackContext):
        if int(update.effective_user.id) not in ADMIN_IDS:
            update.message.reply_text("Unauthorized.")
            return
        text = " ".join(context.args)
        res = broadcast_message(updater.bot, text)
        update.message.reply_text(f"Broadcast sent to approx {res} users.")

    dp.add_handler(CommandHandler("broadcast", cmd_broadcast))
    dp.add_handler(CommandHandler("addadmin", lambda u,c: add_admin(int(c.args[0]), u.effective_user.id) or u.message.reply_text("Added."), pass_args=True))

    # Group events
    dp.add_handler(MessageHandler(Filters.status_update.new_chat_members, on_member_join))
    dp.add_handler(MessageHandler(Filters.status_update.left_chat_member, on_member_left))

    # Messages
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_text))

    # Unknown
    dp.add_handler(MessageHandler(Filters.command, unknown))

    # Start scheduler
    start_scheduler(updater.bot)

    # Start polling
    updater.start_polling()
    logger.info("Bot started.")
    updater.idle()

if __name__ == "__main__":
    start_bot()
# group_system.py
from telegram import Update, ChatPermissions
from telegram.ext import CallbackContext
from database import get_conn
from utils import contains_link
import time

def on_member_join(update: Update, context: CallbackContext):
    for member in update.message.new_chat_members:
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT welcome FROM groups WHERE chat_id = ?", (update.effective_chat.id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            welcome = row[0].replace("{name}", member.full_name)
        else:
            welcome = f"Welcome {member.full_name}!"
        update.message.reply_text(welcome)

def on_member_left(update: Update, context: CallbackContext):
    user = update.message.left_chat_member
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT goodbye FROM groups WHERE chat_id = ?", (update.effective_chat.id,))
    row = c.fetchone()
    conn.close()
    if row and row[0]:
        goodbye = row[0].replace("{name}", user.full_name)
    else:
        goodbye = f"{user.full_name} left the group."
    update.message.reply_text(goodbye)

# Simple anti-link
def message_filter_handler(update: Update, context: CallbackContext):
    text = update.message.text or ""
    chat_id = update.effective_chat.id
    user = update.effective_user
    if contains_link(text):
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT link_block FROM groups WHERE chat_id = ?", (chat_id,))
        row = c.fetchone()
        conn.close()
        if row and row[0]:
            try:
                update.message.delete()
            except:
                pass
            update.message.reply_text(f"Links are not allowed, {user.first_name}.")
            return

# Simple mute/unmute using chat permissions
def mute_user(chat, user_id, until_seconds=60*60):
    try:
        chat.restrict_member(user_id, permissions=ChatPermissions(can_send_messages=False), timeout=until_seconds)
        return True
    except Exception as e:
        return False

def unmute_user(chat, user_id):
    try:
        chat.restrict_member(user_id, permissions=ChatPermissions(
            can_send_messages=True,
            can_send_media_messages=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True
        ))
        return True
    except Exception as e:
        return False
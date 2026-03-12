# chat_system.py
import os
import openai
from config import OPENAI_API_KEY
from telegram import Update
from telegram.ext import CallbackContext
from utils import register_user

openai.api_key = OPENAI_API_KEY

def ai_reply(prompt, max_tokens=256):
    # Simple wrapper using ChatCompletion GPT-3.5 / GPT-4 style
    try:
        resp = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role":"user","content": prompt}],
            max_tokens=max_tokens,
            temperature=0.7,
        )
        text = resp.choices[0].message.content.strip()
        return text
    except Exception as e:
        return "Sorry, AI service is not available right now."

def message_ai_handler(update: Update, context: CallbackContext):
    user = update.effective_user
    register_user(user)
    text = update.message.text
    # optional: if user mentions bot or /ai command
    if not text:
        return
    update.message.chat.send_action(action="typing")
    reply = ai_reply(text)
    update.message.reply_text(reply)
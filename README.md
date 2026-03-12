# Advanced Telegram Keyword + Chat Bot (Python)

## Overview
This project is an advanced, modular Telegram bot built in Python with:
- Keyword reply system (text, media, buttons)
- Admin features (add/edit/delete keywords, broadcast)
- Group moderation (welcome, link block, mute)
- AI Chat integration (OpenAI)
- Scheduler (APScheduler)
- SQLite database

## Setup (Replit)
1. Create a new Replit (Python).
2. Add the files above to the repl.
3. In Secrets (Environment variables), set:
   - `TELEGRAM_TOKEN`
   - `OPENAI_API_KEY`
   - `ADMIN_IDS` (comma separated ids)
4. Install requirements (Replit installs from requirements.txt automatically).
5. Run `bot.py`.

## Notes
- Make sure the bot is admin in groups for moderation actions.
- For media keyword replies & advanced button types extend `keyword_system`.
- Scheduler accepts cron expressions stored in DB (minute hour day month dow).
- Keep OpenAI usage within quota and add error handling for robustness.
# auto_system.py
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from database import get_conn
import atexit
from config import TIMEZONE

scheduler = BackgroundScheduler(timezone=TIMEZONE)

def load_scheduled_posts(bot):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, chat_id, content, cron, is_enabled FROM scheduled_posts WHERE is_enabled = 1")
    rows = c.fetchall()
    for r in rows:
        pid, chat_id, content, cron, enabled = r
        try:
            # Example cron stored as "0 9 * * *" -> map to cron trigger parts
            parts = cron.split()
            if len(parts) == 5:
                minute, hour, day, month, dow = parts
                trigger = CronTrigger(minute=minute, hour=hour, day=day, month=month, day_of_week=dow)
                scheduler.add_job(lambda c=content, cid=chat_id: bot.send_message(chat_id=cid, text=c, parse_mode="HTML"), trigger=trigger, id=str(pid))
        except Exception as e:
            print("Failed to schedule:", e)
    conn.close()

def start_scheduler(bot):
    scheduler.start()
    load_scheduled_posts(bot)
    atexit.register(lambda: scheduler.shutdown())
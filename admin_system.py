# admin_system.py
import json
import time
import shutil
from database import get_conn
from utils import is_admin
from keyword_system import add_keyword, edit_keyword, delete_keyword, list_keywords, get_keyword

# -----------------------------
# Admin Management
# -----------------------------
def add_admin(user_id: int, added_by: int) -> bool:
    """Add a new admin to the bot"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?,?)", (user_id, added_by))
    conn.commit()
    conn.close()
    return True

def remove_admin(user_id: int) -> bool:
    """Remove an existing admin"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("DELETE FROM admins WHERE user_id = ?", (user_id,))
    changed = c.rowcount
    conn.commit()
    conn.close()
    return changed > 0

def list_admins() -> list:
    """Return list of all admins"""
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT user_id, added_by, added_at FROM admins")
    rows = c.fetchall()
    conn.close()
    return rows

# -----------------------------
# Keyword Management
# -----------------------------
def admin_add_keyword(admin_id: int, keyword: str, ktype: str, content: str,
                      category: str = None, extras: dict = None, restricted: bool = False) -> bool:
    """
    Admin adds keyword with type: text/media/buttons/command/ai_chat
    extras: dictionary for buttons, media file_id, multi-replies
    restricted: if True, only admin can trigger this keyword
    """
    if not is_admin(admin_id):
        return False
    data = extras.copy() if extras else {}
    data['restricted'] = restricted
    return add_keyword(keyword, ktype, content, admin_id, category, data)

def admin_edit_keyword(admin_id: int, keyword: str, **fields) -> bool:
    """
    Edit keyword. Fields: type, content, category, extras, restricted
    """
    if not is_admin(admin_id):
        return False
    if 'restricted' in fields:
        fields['extras'] = fields.get('extras', {})
        fields['extras']['restricted'] = fields.pop('restricted')
    return edit_keyword(keyword, **fields)

def admin_delete_keyword(admin_id: int, keyword: str) -> bool:
    if not is_admin(admin_id):
        return False
    return delete_keyword(keyword)

def admin_list_keywords(admin_id: int, limit: int = 100) -> list:
    """Return recent keywords"""
    if not is_admin(admin_id):
        return []
    return list_keywords(limit)

# -----------------------------
# Keyword Statistics
# -----------------------------
def keyword_usage_stats(keyword: str) -> dict:
    """Return keyword usage stats from stats table"""
    kw = get_keyword(keyword)
    if not kw:
        return {}
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM stats WHERE keyword_id = ?", (kw['id'],))
    count = c.fetchone()[0]
    c.execute("SELECT user_id, COUNT(*) FROM stats WHERE keyword_id = ? GROUP BY user_id", (kw['id'],))
    user_stats = c.fetchall()
    conn.close()
    return {
        'keyword': keyword,
        'total_triggered': count,
        'user_stats': user_stats
    }

# -----------------------------
# Broadcast Messages
# -----------------------------
def broadcast_message(bot, text: str, admins_only: bool = False) -> int:
    """
    Send message to all users or only admins
    Returns number of successful deliveries
    """
    conn = get_conn()
    c = conn.cursor()
    if admins_only:
        c.execute("SELECT user_id FROM admins")
    else:
        c.execute("SELECT user_id FROM users WHERE is_banned = 0")
    recipients = [r[0] for r in c.fetchall()]
    conn.close()
    successes = 0
    for uid in recipients:
        try:
            bot.send_message(chat_id=uid, text=text, parse_mode="HTML")
            successes += 1
        except Exception:
            continue
    return successes

# -----------------------------
# Ban / Unban Users
# -----------------------------
def ban_user(admin_id: int, user_id: int) -> bool:
    if not is_admin(admin_id):
        return False
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 1 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

def unban_user(admin_id: int, user_id: int) -> bool:
    if not is_admin(admin_id):
        return False
    conn = get_conn()
    c = conn.cursor()
    c.execute("UPDATE users SET is_banned = 0 WHERE user_id = ?", (user_id,))
    conn.commit()
    conn.close()
    return True

# -----------------------------
# Database Backup / Clear
# -----------------------------
def backup_database(out_path: str) -> bool:
    """Backup the SQLite DB to specified path"""
    from config import DB_PATH
    try:
        shutil.copyfile(DB_PATH, out_path)
        return True
    except Exception:
        return False

def clear_database(admin_id: int) -> bool:
    """Clear all DB tables (use carefully)"""
    if not is_admin(admin_id):
        return False
    conn = get_conn()
    c = conn.cursor()
    tables = ["keywords", "users", "admins", "groups", "warns", "stats", "scheduled_posts"]
    for t in tables:
        c.execute(f"DELETE FROM {t}")
    conn.commit()
    conn.close()
    return True

# -----------------------------
# Auto Message Scheduler (basic helper)
# -----------------------------
def schedule_message(admin_id: int, chat_id: int, content: str, cron_expr: str) -> bool:
    """Store a scheduled message in DB for auto_system to pick up"""
    if not is_admin(admin_id):
        return False
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT INTO scheduled_posts (chat_id, content, cron, is_enabled) VALUES (?,?,?,1)",
              (chat_id, content, cron_expr))
    conn.commit()
    conn.close()
    return True

# -----------------------------
# Keyword Category / Multi-Reply
# -----------------------------
def get_keywords_by_category(category: str) -> list:
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, keyword, type, content FROM keywords WHERE category = ?", (category,))
    rows = c.fetchall()
    conn.close()
    return rows

def add_multi_reply(admin_id: int, keyword: str, replies: list) -> bool:
    """
    Add multiple replies to a single keyword.
    replies: list of dicts, e.g. [{"type":"text","content":"Hello"},{"type":"photo","content":"file_id"}]
    """
    if not is_admin(admin_id):
        return False
    kw = get_keyword(keyword)
    if not kw:
        return False
    extras = kw.get('extras') or {}
    extras['multi'] = replies
    return edit_keyword(keyword, extras=extras)
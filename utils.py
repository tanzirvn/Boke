# utils.py
import re
from database import get_conn
from config import ADMIN_IDS

URL_REGEX = re.compile(r'(https?://\S+|t.me/\S+)', re.IGNORECASE)

def is_admin(user_id):
    try:
        return int(user_id) in ADMIN_IDS
    except:
        return False

def register_user(user):
    conn = get_conn()
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name, last_name) VALUES (?,?,?,?)",
              (user.id, user.username, user.first_name, user.last_name))
    conn.commit()
    conn.close()

def parse_command_args(text):
    # returns list of args after command or splitted by newline
    if not text:
        return []
    parts = text.split(maxsplit=1)
    if len(parts) == 1:
        return []
    return parts[1].strip().split()

def contains_link(text):
    return bool(URL_REGEX.search(text or ""))
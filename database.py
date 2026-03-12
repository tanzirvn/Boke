# database.py
import sqlite3
from contextlib import closing
from config import DB_PATH

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        # users
        c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            language TEXT,
            rank INTEGER DEFAULT 0,
            points INTEGER DEFAULT 0,
            is_banned INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # keywords
        c.execute('''
        CREATE TABLE IF NOT EXISTS keywords (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword TEXT,
            type TEXT,
            content TEXT,
            extras TEXT,
            admin_id INTEGER,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # admins
        c.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            user_id INTEGER PRIMARY KEY,
            added_by INTEGER,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # groups
        c.execute('''
        CREATE TABLE IF NOT EXISTS groups (
            chat_id INTEGER PRIMARY KEY,
            welcome TEXT,
            goodbye TEXT,
            anti_spam_enabled INTEGER DEFAULT 0,
            bad_words TEXT,
            link_block INTEGER DEFAULT 0,
            media_only INTEGER DEFAULT 0,
            slow_mode_seconds INTEGER DEFAULT 0
        );
        ''')
        # warns
        c.execute('''
        CREATE TABLE IF NOT EXISTS warns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            user_id INTEGER,
            reason TEXT,
            count INTEGER DEFAULT 1,
            last_warn TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # statistics (keyword usage)
        c.execute('''
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            keyword_id INTEGER,
            user_id INTEGER,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        # scheduled posts
        c.execute('''
        CREATE TABLE IF NOT EXISTS scheduled_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER,
            content TEXT,
            cron TEXT,
            is_enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        ''')
        conn.commit()

def get_conn():
    return sqlite3.connect(DB_PATH)
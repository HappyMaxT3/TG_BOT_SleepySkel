import sqlite3

def init_db():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            sleep_start TEXT,
            sleep_end TEXT
        )
        """)
        conn.commit()

def save_user_name(user_id, name):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, name)
        VALUES (?, ?)
        """, (user_id, name))
        conn.commit()

def get_user_name(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def save_sleep_start(user_id, sleep_start):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET sleep_start = ? WHERE user_id = ?
        """, (sleep_start, user_id))
        conn.commit()

def save_sleep_end(user_id, sleep_end):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE users SET sleep_end = ? WHERE user_id = ?
        """, (sleep_end, user_id))
        conn.commit()

def get_sleep_end(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sleep_end FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def get_sleep_start(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT sleep_start FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

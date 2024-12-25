import sqlite3

def init_db():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        # Создаём таблицу пользователей
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)
        # Создаём таблицу истории сна
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS sleep_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            sleep_start TEXT,
            sleep_end TEXT,
            sleep_duration TEXT,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
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

def save_sleep_event(user_id, sleep_start, sleep_end, sleep_duration):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sleep_history (user_id, sleep_start, sleep_end, sleep_duration)
        VALUES (?, ?, ?, ?)
        """, (user_id, sleep_start, sleep_end, sleep_duration))
        conn.commit()

def get_sleep_history(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_start, sleep_end, sleep_duration FROM sleep_history
        WHERE user_id = ?
        ORDER BY id DESC
        """, (user_id,))
        return cursor.fetchall()

def get_last_sleep_event(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_start, sleep_end FROM sleep_history
        WHERE user_id = ?
        ORDER BY id DESC LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        return result if result else (None, None)

def save_sleep_start(user_id, sleep_start):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sleep_history (user_id, sleep_start)
        VALUES (?, ?)
        """, (user_id, sleep_start))
        conn.commit()

def get_sleep_start(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_start FROM sleep_history
        WHERE user_id = ? AND sleep_end IS NULL
        ORDER BY id DESC
        LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

def save_sleep_end(user_id, sleep_end, sleep_duration):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE sleep_history
        SET sleep_end = ?, sleep_duration = ?
        WHERE user_id = ? AND sleep_end IS NULL
        """, (sleep_end, sleep_duration, user_id))
        conn.commit()

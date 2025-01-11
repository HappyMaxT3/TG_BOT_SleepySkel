import sqlite3
from datetime import datetime, timedelta

def init_db():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            name TEXT
        )
        """)
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
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            review_text TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(user_id)
        )
        """)
        conn.commit()

def get_all_user_ids():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users")
        user_ids = [row[0] for row in cursor.fetchall()]
    return user_ids

def add_sleep_history(user_id, sleep_start, sleep_end, sleep_duration):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO sleep_history (user_id, sleep_start, sleep_end, sleep_duration) 
        VALUES (?, ?, ?, ?)
        """, (user_id, sleep_start, sleep_end, sleep_duration))
        conn.commit()

def add_feedback(user_id, review_text):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        INSERT INTO reviews (user_id, review_text) 
        VALUES (?, ?)
        """, (user_id, review_text))
        conn.commit()

def clean_old_sleep_data():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        fifteen_days_ago = (datetime.now() - timedelta(days=15)).strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
        DELETE FROM sleep_history
        WHERE sleep_start < ?
        """, (fifteen_days_ago,))
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

def get_sleep_history_last_7_days(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        query = """
        SELECT sleep_start, sleep_end, sleep_duration
        FROM sleep_history
        WHERE user_id = ? AND sleep_start >= ?
        ORDER BY sleep_start DESC
        """
        cursor.execute(query, (user_id, week_ago))
        results = cursor.fetchall()

    return [(row[0], row[1], row[2]) for row in results]

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

def convert_duration_to_minutes(duration):
    duration = duration.replace(" H ", ":").replace(" Min", "").strip()
    hours, minutes = map(int, duration.split(':'))
    return hours * 60 + minutes


def get_average_sleep_duration_last_7_days(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_duration FROM sleep_history
        WHERE user_id = ? AND sleep_duration IS NOT NULL
        ORDER BY id DESC
        LIMIT 7
        """, (user_id,))
        durations = cursor.fetchall()
        durations = [convert_duration_to_minutes(d[0]) for d in durations]
        if durations:
            return round(sum(durations) / len(durations), 2)
        return 0

def get_total_sleep_duration_last_7_days(user_id):
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_duration FROM sleep_history
        WHERE user_id = ? AND sleep_duration IS NOT NULL
        ORDER BY id DESC
        LIMIT 7
        """, (user_id,))
        durations = cursor.fetchall()
        durations = [convert_duration_to_minutes(d[0]) for d in durations]
        return round(sum(durations), 2)

def get_anonymous_average_sleep():
    with sqlite3.connect("bot.db") as conn:
        cursor = conn.cursor()
        cursor.execute("""
        SELECT sleep_duration FROM sleep_history
        WHERE sleep_duration IS NOT NULL
        """)
        durations = cursor.fetchall()
        durations = [convert_duration_to_minutes(d[0]) for d in durations]
        if durations:
            return round(sum(durations) / len(durations), 2)
        return 0
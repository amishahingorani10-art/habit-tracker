import sqlite3
from datetime import date

DB_NAME = "habits.db"


def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)


def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            last_done TEXT,
            streak INTEGER DEFAULT 0
        )
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits (id)
        )
        """
    )
    try:
        cursor.execute("ALTER TABLE habits ADD COLUMN created_date TEXT")
    except sqlite3.OperationalError:
        pass
    conn.commit()
    conn.close()

def add_habit(name):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO habits (name, last_done, streak, created_date) VALUES (?, NULL, 0, ?)",
            (name, date.today().isoformat()),
        )
        conn.commit()
    except sqlite3.IntegrityError:
        pass
    finally:
        conn.close()


def get_all_habits():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, last_done, streak, created_date FROM habits ORDER BY id")
    rows = cursor.fetchall()
    conn.close()

    habits = []
    for row in rows:
        habits.append({
            "id": row[0], "name": row[1], "last_done": row[2],
            "streak": row[3], "created_date": row[4]
        })
    return habits


def delete_habit(habit_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    cursor.execute("DELETE FROM completions WHERE habit_id = ?", (habit_id,))
    conn.commit()
    conn.close()


def is_done_today(last_done_str):
    if last_done_str is None:
        return False
    last_done = date.fromisoformat(last_done_str)
    return last_done == date.today()


def mark_done(habit_id, current_last_done, current_streak):
    today = date.today()

    if current_last_done is None:
        new_streak = 1
    else:
        last_done = date.fromisoformat(current_last_done)
        gap = (today - last_done).days
        if gap == 0:
            new_streak = current_streak
        elif gap == 1:
            new_streak = current_streak + 1
        else:
            new_streak = 1

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE habits SET last_done = ?, streak = ? WHERE id = ?",
        (today.isoformat(), new_streak, habit_id),
    )
    cursor.execute(
        "INSERT OR IGNORE INTO completions (habit_id, date) VALUES (?, ?)",
        (habit_id, today.isoformat()),
    )
    conn.commit()
    conn.close()


def unmark_today(habit_id, current_last_done, current_streak):
    conn = get_connection()
    cursor = conn.cursor()
    new_streak = max(current_streak - 1, 0)
    cursor.execute(
        "UPDATE habits SET last_done = NULL, streak = ? WHERE id = ?",
        (new_streak, habit_id),
    )
    cursor.execute(
        "DELETE FROM completions WHERE habit_id = ? AND date = ?",
        (habit_id, date.today().isoformat()),
    )
    conn.commit()
    conn.close()


def get_month_completions(habit_id, year, month):
    conn = get_connection()
    cursor = conn.cursor()
    month_prefix = f"{year}-{month:02d}"
    cursor.execute(
        "SELECT date FROM completions WHERE habit_id = ? AND date LIKE ?",
        (habit_id, f"{month_prefix}-%"),
    )
    rows = cursor.fetchall()
    conn.close()

    completed_days = set()
    for row in rows:
        day_number = int(row[0].split("-")[2])
        completed_days.add(day_number)
    return completed_days
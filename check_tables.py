import database
import sqlite3

database.init_db()

conn = sqlite3.connect("habits.db")
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print(cursor.fetchall())
conn.close()
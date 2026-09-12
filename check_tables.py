import sqlite3
from datetime import date

conn = sqlite3.connect("habits.db")
conn.execute("UPDATE habits SET created_date = ? WHERE created_date IS NULL", (date.today().isoformat(),))
conn.commit()
conn.close()
print("Backfilled.")
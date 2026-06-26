import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "adhd.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS focus_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    duration INTEGER
)
""")

conn.commit()
conn.close()

print("focus_log table created successfully!")

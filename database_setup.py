import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "..", "adhd.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    task TEXT,
    status TEXT,
    priority TEXT,
    created_date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS focus_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    duration INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS task_quiz_scores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT,
    score INTEGER,
    date TEXT
)
""")

conn.commit()
conn.close()

print("Database setup completed successfully!")

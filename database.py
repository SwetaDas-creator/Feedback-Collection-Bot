import sqlite3

def get_connection():
    return sqlite3.connect("feedback.db", check_same_thread=False)

def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nps INTEGER,
        csat INTEGER,
        ces INTEGER,
        comment TEXT,
        sentiment TEXT,
        is_fraud INTEGER
    )
    """)

    conn.commit()
    conn.close()

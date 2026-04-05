import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "app.db"

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            created_at TEXT NOT NULL,
            final_score REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS interview_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_index INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            user_answer TEXT,
            score REAL,
            strengths TEXT,
            weaknesses TEXT,
            advice TEXT,
            FOREIGN KEY(interview_id) REFERENCES interviews(id)
        );
        """
    )

    conn.commit()
    conn.close()
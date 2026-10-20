import sqlite3
import config


def get_connection():
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT,
                google_id TEXT UNIQUE,
                email TEXT
            )
        """)
        # Migrate existing databases that predate google_id / email columns
        for column, definition in [("google_id", "TEXT UNIQUE"), ("email", "TEXT")]:
            try:
                conn.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
            except Exception:
                pass  # column already exists
        conn.commit()

import uuid

from database import get_connection


def create_user(username, password_hash):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash) VALUES (?, ?)",
            (username, password_hash),
        )
        conn.commit()


def get_user_by_username(username):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()


def username_exists(username):
    return get_user_by_username(username) is not None


def get_user_by_google_id(google_id):
    with get_connection() as conn:
        return conn.execute(
            "SELECT * FROM users WHERE google_id = ?", (google_id,)
        ).fetchone()


def create_oauth_user(username, google_id, email):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO users (username, password_hash, google_id, email) VALUES (?, NULL, ?, ?)",
            (username, google_id, email),
        )
        conn.commit()


def generate_unique_username(base):
    if not username_exists(base):
        return base
    return f"{base}_{uuid.uuid4().hex[:6]}"

import sqlite3
from contextlib import contextmanager
from pathlib import Path

DATABASE_PATH = Path(__file__).with_name("conversations.sqlite3")
MAX_HISTORY_MESSAGES = 20


@contextmanager
def connect():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS user_profiles (
            user_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
        """
    )
    try:
        with connection:
            yield connection
    finally:
        connection.close()


def get_history(user_id):
    # Conversation context is limited so requests do not grow forever
    with connect() as connection:
        rows = connection.execute(
            "SELECT role, content FROM messages "
            "WHERE user_id = ? ORDER BY id DESC LIMIT ?",
            (user_id, MAX_HISTORY_MESSAGES),
        ).fetchall()

    rows.reverse()
    return [{"role": role, "content": content} for role, content in rows]


def add_exchange(user_id, user_message, assistant_message):
    with connect() as connection:
        connection.executemany(
            "INSERT INTO messages (user_id, role, content) VALUES (?, ?, ?)",
            [
                (user_id, "user", user_message),
                (user_id, "assistant", assistant_message),
            ],
        )
        message_ids = connection.execute(
            "SELECT id FROM messages WHERE user_id = ? ORDER BY id",
            (user_id,),
        ).fetchall()
        extra_count = len(message_ids) - MAX_HISTORY_MESSAGES
        if extra_count > 0:
            old_ids = [(user_id, row[0]) for row in message_ids[:extra_count]]
            connection.executemany(
                "DELETE FROM messages WHERE user_id = ? AND id = ?",
                old_ids,
            )


def clear_history(user_id):
    with connect() as connection:
        connection.execute("DELETE FROM messages WHERE user_id = ?", (user_id,))


def get_name(user_id):
    with connect() as connection:
        row = connection.execute(
            "SELECT name FROM user_profiles WHERE user_id = ?",
            (user_id,),
        ).fetchone()

    if row is None:
        return None
    return row[0]


def save_name(user_id, name):
    name = name.strip()
    if not name or len(name) > 80 or "\n" in name or "\r" in name:
        raise ValueError("Name must be 1 to 80 characters on one line")

    # Keep the profile separate so trimming or resetting chat history cannot remove it
    with connect() as connection:
        connection.execute(
            "INSERT INTO user_profiles (user_id, name) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET name = excluded.name",
            (user_id, name),
        )

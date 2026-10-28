#Manages SQLite storage

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "data" / "users.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def initialize_database():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                external_id INTEGER PRIMARY KEY,
                full_name TEXT NOT NULL,
                email TEXT NOT NULL,
                city TEXT,
                phone TEXT
            )
        """)

    print("Database initialized successfully.")



def upsert_users(users):
    """
    Insert new users or update existing users.
    Returns the number of records processed.
    """

    query = """
        INSERT INTO users (
            external_id,
            full_name,
            email,
            city,
            phone
        )
        VALUES (?, ?, ?, ?, ?)

        ON CONFLICT(external_id)
        DO UPDATE SET
            full_name = excluded.full_name,
            email = excluded.email,
            city = excluded.city,
            phone = excluded.phone
    """

    records = [
        (
            user["external_id"],
            user["full_name"],
            user["email"],
            user["city"],
            user["phone"]
        )
        for user in users
    ]

    with get_connection() as connection:
        connection.executemany(query, records)

    return len(records)



def get_user_count():
    with get_connection() as connection:
        cursor = connection.execute(
            "SELECT COUNT(*) FROM users"
        )
        return cursor.fetchone()[0]


def get_all_users():
    with get_connection() as connection:
        connection.row_factory = sqlite3.Row

        cursor = connection.execute("""
            SELECT external_id, full_name, email, city, phone
            FROM users
            ORDER BY external_id
        """)

        return [dict(row) for row in cursor.fetchall()]

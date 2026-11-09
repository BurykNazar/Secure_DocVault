"""Схема бази даних.

Таблиці створюються під час старту, повторний запуск нічого не змінює.
Сіль зберігається окремою колонкою, як вимагає методичка; вона також
входить до самого bcrypt-хеша.
"""

from __future__ import annotations

from .engine import session

USERS = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT    UNIQUE NOT NULL,
    email         TEXT    UNIQUE NOT NULL,
    password_hash TEXT    NOT NULL,
    salt          TEXT    NOT NULL,
    role          TEXT    DEFAULT 'user',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active     INTEGER DEFAULT 1
)
"""

# owner_id зв'язує коментар із користувачем: вибірка й зміни завжди
# фільтруються за власником, тому чужі записи недоступні.
COMMENTS = """
CREATE TABLE IF NOT EXISTS comments (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    owner_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      TEXT    NOT NULL,
    body       TEXT    NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def install() -> None:
    with session() as connection:
        connection.execute(USERS)
        connection.execute(COMMENTS)

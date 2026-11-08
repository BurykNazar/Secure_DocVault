"""Схема бази даних.

Таблиця створюється один раз під час старту, повторний запуск нічого
не змінює. Сіль зберігається окремою колонкою, як вимагає методичка;
вона також входить до самого bcrypt-хеша.
"""

from __future__ import annotations

from .engine import session

DDL = """
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


def install() -> None:
    with session() as connection:
        connection.execute(DDL)

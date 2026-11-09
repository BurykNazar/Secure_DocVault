"""Схема бази даних.

Таблиці створюються під час старту, повторний запуск нічого не змінює.
"""

from __future__ import annotations

from .engine import session
from .signing_tables import install as install_signing

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

DOCUMENTS = """
CREATE TABLE IF NOT EXISTS documents (
    id                TEXT    PRIMARY KEY,
    owner_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    original_filename TEXT    NOT NULL,
    stored_filename   TEXT    NOT NULL UNIQUE,
    content_type      TEXT,
    size_bytes        INTEGER NOT NULL,
    encrypted_size    INTEGER NOT NULL,
    sha256            TEXT    NOT NULL,
    created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

DOCUMENT_COMMENTS = """
CREATE TABLE IF NOT EXISTS document_comments (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    document_id TEXT    NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    author_id   INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       TEXT    NOT NULL,
    body        TEXT    NOT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def install() -> None:
    with session() as connection:
        for ddl in (USERS, DOCUMENTS, DOCUMENT_COMMENTS):
            connection.execute(ddl)
    install_signing()

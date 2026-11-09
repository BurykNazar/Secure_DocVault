"""Таблиці ключів і підписів ЕЦП."""

from __future__ import annotations

from .engine import session

SIGNING_KEYS = """
CREATE TABLE IF NOT EXISTS user_signing_keys (
    user_id               INTEGER PRIMARY KEY
                          REFERENCES users(id) ON DELETE CASCADE,
    algorithm             TEXT    NOT NULL,
    public_key_pem        TEXT    NOT NULL,
    private_key_encrypted TEXT    NOT NULL,
    key_fingerprint       TEXT    NOT NULL,
    created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

DOCUMENT_SIGNATURES = """
CREATE TABLE IF NOT EXISTS document_signatures (
    document_id           TEXT    PRIMARY KEY
                          REFERENCES documents(id) ON DELETE CASCADE,
    signer_id             INTEGER NOT NULL
                          REFERENCES users(id) ON DELETE CASCADE,
    algorithm             TEXT    NOT NULL,
    signature_b64         TEXT    NOT NULL,
    public_key_fingerprint TEXT   NOT NULL,
    signed_at             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""


def install() -> None:
    with session() as connection:
        for ddl in (SIGNING_KEYS, DOCUMENT_SIGNATURES):
            connection.execute(ddl)

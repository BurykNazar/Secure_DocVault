"""AES-256-GCM для файлів сховища.

Контейнер: [12 байт IV] + [16 байт Tag] + [шифротекст]. AAD прив'язує
контейнер до документа й власника, тому підміна файлів між записами
теж призводить до InvalidTag.
"""

from __future__ import annotations

import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..settings import settings

NONCE_SIZE = 12
TAG_SIZE = 16

KEY = bytes.fromhex(settings.file_key)
if len(KEY) != 32:
    raise RuntimeError("VAULT_FILE_KEY має бути 64 hex-символи (256 біт)")


def associated(doc_id: str, owner_id: int) -> bytes:
    return f"docvault|v1|{doc_id}|{owner_id}".encode("utf-8")


def encrypt(data: bytes, aad: bytes) -> bytes:
    nonce = os.urandom(NONCE_SIZE)
    sealed = AESGCM(KEY).encrypt(nonce, data, aad)
    tag, ciphertext = sealed[-TAG_SIZE:], sealed[:-TAG_SIZE]
    return nonce + tag + ciphertext


def decrypt(blob: bytes, aad: bytes) -> bytes:
    if len(blob) < NONCE_SIZE + TAG_SIZE:
        raise ValueError("Пошкоджений або занадто короткий шифроконтейнер")
    nonce = blob[:NONCE_SIZE]
    tag = blob[NONCE_SIZE:NONCE_SIZE + TAG_SIZE]
    ciphertext = blob[NONCE_SIZE + TAG_SIZE:]
    return AESGCM(KEY).decrypt(nonce, ciphertext + tag, aad)

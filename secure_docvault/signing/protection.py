"""Шифрування приватного ключа ЕЦП на сервері."""

from __future__ import annotations

import base64
import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..settings import settings

NONCE_SIZE = 12
TAG_SIZE = 16
AAD = b"docvault|signing-key|v1"

KEY = bytes.fromhex(settings.signing_key)
if len(KEY) != 32:
    raise RuntimeError("VAULT_SIGNING_KEY має бути 64 hex-символи (256 біт)")


def encrypt_pem(pem: str) -> str:
    nonce = os.urandom(NONCE_SIZE)
    sealed = AESGCM(KEY).encrypt(nonce, pem.encode("utf-8"), AAD)
    return base64.b64encode(nonce + sealed).decode("ascii")


def decrypt_pem(token: str) -> str:
    try:
        raw = base64.b64decode(token.encode("ascii"), validate=True)
    except (ValueError, UnicodeEncodeError) as exc:
        raise ValueError("Пошкоджений зашифрований приватний ключ") from exc

    if len(raw) < NONCE_SIZE + TAG_SIZE:
        raise ValueError("Пошкоджений зашифрований приватний ключ")

    nonce, sealed = raw[:NONCE_SIZE], raw[NONCE_SIZE:]
    try:
        plaintext = AESGCM(KEY).decrypt(nonce, sealed, AAD)
    except InvalidTag as exc:
        raise ValueError("Не вдалося розшифрувати приватний ключ") from exc
    return plaintext.decode("utf-8")

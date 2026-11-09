"""Керування ключами ЕЦП і підписування документів."""

from __future__ import annotations

from ..transport.errors import InternalFailure, ValidationRejected
from . import keys, protection, repository

MIN_PASSPHRASE = 8
MAX_PASSPHRASE = 128


def _info(row: dict) -> dict:
    return {
        "algorithm": row["algorithm"],
        "fingerprint": row["key_fingerprint"],
        "public_key_pem": row["public_key_pem"],
        "created_at": row.get("created_at"),
    }


def ensure_key(user_id: int) -> dict:
    existing = repository.get_key(user_id)
    if existing:
        return existing

    private_key, public_key = keys.generate_keypair()
    saved = repository.save_key(
        user_id=user_id,
        algorithm=keys.ALGORITHM,
        public_key_pem=keys.serialize_public_key(public_key),
        private_key_encrypted=protection.encrypt_pem(
            keys.serialize_private_key(private_key)
        ),
        key_fingerprint=keys.fingerprint(public_key),
    )
    if not saved:
        existing = repository.get_key(user_id)
        if existing:
            return existing
        raise InternalFailure("Не вдалося зберегти ключі ЕЦП")

    created = repository.get_key(user_id)
    if not created:
        raise InternalFailure("Не вдалося прочитати ключі ЕЦП")
    return created


def find_key(user_id: int) -> dict | None:
    row = repository.get_key(user_id)
    return _info(row) if row else None


def get_key(user_id: int) -> dict:
    return _info(ensure_key(user_id))


def public_key_pem(user_id: int) -> str:
    return ensure_key(user_id)["public_key_pem"]


def _validate_passphrase(passphrase: str) -> None:
    value = (passphrase or "").strip()
    errors: list[str] = []
    if not value:
        errors.append("Парольна фраза є обов'язковою")
    elif len(value) < MIN_PASSPHRASE:
        errors.append(
            f"Парольна фраза має містити щонайменше {MIN_PASSPHRASE} символів"
        )
    if len(value) > MAX_PASSPHRASE:
        errors.append(
            f"Парольна фраза не повинна перевищувати {MAX_PASSPHRASE} символів"
        )
    if errors:
        raise ValidationRejected(errors[0], fields={"passphrase": errors})


def export_private_key(user_id: int, passphrase: str) -> str:
    _validate_passphrase(passphrase)
    row = ensure_key(user_id)
    try:
        pem = protection.decrypt_pem(row["private_key_encrypted"])
        private_key = keys.load_private_key(pem)
        return keys.serialize_private_key(private_key, passphrase)
    except ValueError as exc:
        raise InternalFailure("Не вдалося експортувати приватний ключ") from exc




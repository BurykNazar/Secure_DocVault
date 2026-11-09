"""Сценарії роботи з документами."""

from __future__ import annotations

import hashlib
import uuid

from cryptography.exceptions import InvalidTag
from fastapi import UploadFile

from ..transport.errors import (
    IntegrityViolation,
    MissingResource,
    PayloadTooLarge,
    ValidationRejected,
)
from . import repository, storage
from .filenames import safe_name


def _owner(claims: dict) -> int:
    return int(claims["sub"])


def _public(row: dict) -> dict:
    return {
        "id": row["id"],
        "original_filename": row["original_filename"],
        "content_type": row["content_type"],
        "size_bytes": row["size_bytes"],
        "created_at": row["created_at"],
    }
def list_mine(claims: dict) -> list[dict]:
    return [_public(row) for row in repository.list_for(_owner(claims))]
async def upload(file: UploadFile, claims: dict) -> dict:
    chunks: list[bytes] = []
    total = 0
    while True:
        chunk = await file.read(storage.CHUNK)
        if not chunk:
            break
        total += len(chunk)
        if total > storage.MAX_BYTES:
            raise PayloadTooLarge("Файл перевищує ліміт 10 МБ")
        chunks.append(chunk)

    if total == 0:
        raise ValidationRejected("Файл порожній")

    data = b"".join(chunks)
    owner = _owner(claims)
    filename = safe_name(file.filename)
    doc_id = str(uuid.uuid4())
    try:
        stored, encrypted_size = storage.write(doc_id, owner, data)
        repository.save(
            doc_id,
            owner,
            filename,
            stored,
            file.content_type or "application/octet-stream",
            total,
            encrypted_size,
            hashlib.sha256(data).hexdigest(),
        )
    except Exception:
        storage.remove(f"{doc_id}.enc")
        raise

    row = repository.get_for(owner, doc_id)
    assert row is not None
    return _public(row)
def download(doc_id: str, claims: dict) -> tuple[bytes, str, str]:
    owner = _owner(claims)
    row = repository.get_for(owner, doc_id)
    if row is None:
        raise MissingResource("Документ не знайдено")

    try:
        data = storage.read(doc_id, owner, row["stored_filename"])
    except InvalidTag:
        raise IntegrityViolation(
            "Цілісність порушено: AES-GCM не пройшов перевірку (InvalidTag)."
        ) from None
    except ValueError as error:
        raise IntegrityViolation(str(error)) from None

    if hashlib.sha256(data).hexdigest() != row["sha256"]:
        raise IntegrityViolation("SHA-256 розшифрованого файлу не збігається")
    return data, row["original_filename"], row["content_type"]
def delete(doc_id: str, claims: dict) -> None:
    owner = _owner(claims)
    row = repository.get_for(owner, doc_id)
    if row is None:
        raise MissingResource("Документ не знайдено")
    storage.remove(row["stored_filename"])
    repository.delete(owner, doc_id)

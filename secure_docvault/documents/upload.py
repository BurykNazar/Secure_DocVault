"""Завантаження, шифрування й підписування документа."""

from __future__ import annotations

import hashlib
import uuid

from fastapi import UploadFile

from ..signing import documents as signing
from ..transport.errors import PayloadTooLarge, ValidationRejected
from . import repository, storage
from .filenames import safe_name
from .listing import public


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
    owner = int(claims["sub"])
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
        signing.store_signature(
            doc_id, owner, signing.sign_for_user(data, owner)
        )
    except Exception:
        storage.remove(f"{doc_id}.enc")
        repository.delete(owner, doc_id)
        raise

    row = repository.get_for(owner, doc_id)
    assert row is not None
    return public(row)

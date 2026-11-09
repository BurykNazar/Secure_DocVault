"""Скачування та видалення документів."""

from __future__ import annotations

import hashlib

from cryptography.exceptions import InvalidTag

from ..signing.verification import verify_document
from ..transport.errors import (
    IntegrityViolation,
    MissingResource,
    SignatureRejected,
)
from . import repository, storage
from .filenames import disposition
from .listing import list_mine
from .upload import upload

__all__ = ["upload", "list_mine", "download", "delete"]


def download(doc_id: str, claims: dict) -> tuple[bytes, str, dict[str, str]]:
    owner = int(claims["sub"])
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

    signature = verify_document(doc_id, data)
    if signature["status"] == "invalid":
        raise SignatureRejected(
            "Цифровий підпис документа недійсний: підпис не відповідає вмісту."
        )

    headers = {
        "Content-Disposition": disposition(row["original_filename"]),
        "X-Content-SHA256": row["sha256"],
        "X-Signature-Status": (
            "Signed & Verified"
            if signature["status"] == "verified"
            else "Unsigned"
        ),
    }
    if signature["status"] == "verified":
        headers.update(
            {
                "X-Signature-Algorithm": signature["algorithm"],
                "X-Signature-Fingerprint": signature["fingerprint"],
                "X-Signer": signature.get("signer") or "",
                "X-Signed-At": signature.get("signed_at") or "",
            }
        )
    return data, row["content_type"] or "application/octet-stream", headers


def delete(doc_id: str, claims: dict) -> None:
    owner = int(claims["sub"])
    row = repository.get_for(owner, doc_id)
    if row is None:
        raise MissingResource("Документ не знайдено")
    storage.remove(row["stored_filename"])
    repository.delete(owner, doc_id)

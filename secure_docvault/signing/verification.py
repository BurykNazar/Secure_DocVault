"""Перевірка ЕЦП документа."""

from __future__ import annotations

import base64

from . import keys, repository


def signature_info(document_id: str) -> dict:
    row = repository.get_signature(document_id)
    if not row:
        return {"status": "unsigned"}
    return {
        "status": "signed",
        "algorithm": row["algorithm"],
        "signed_at": row.get("signed_at"),
        "signer": repository.username(row["signer_id"]),
        "signer_id": row["signer_id"],
        "fingerprint": row["public_key_fingerprint"],
    }


def verify_document(document_id: str, content: bytes) -> dict:
    row = repository.get_signature(document_id)
    if not row:
        return {"status": "unsigned"}

    key = repository.get_key(row["signer_id"])
    if not key:
        return {"status": "invalid", "reason": "key_missing"}

    try:
        signature = base64.b64decode(
            row["signature_b64"].encode("ascii"), validate=True
        )
        public_key = keys.load_public_key(key["public_key_pem"])
        valid = keys.verify_content(content, signature, public_key)
    except (ValueError, TypeError):
        valid = False

    if not valid:
        return {"status": "invalid", "reason": "bad_signature"}

    return {
        "status": "verified",
        "algorithm": row["algorithm"],
        "signed_at": row.get("signed_at"),
        "signer": repository.username(row["signer_id"]),
        "signer_id": row["signer_id"],
        "fingerprint": row["public_key_fingerprint"],
    }

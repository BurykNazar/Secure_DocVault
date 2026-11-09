"""Підписування документа та збереження підпису."""

from __future__ import annotations

import base64

from ..transport.errors import InternalFailure
from . import keys, protection, repository
from .service import ensure_key


def sign_for_user(content: bytes, user_id: int) -> dict:
    row = ensure_key(user_id)
    try:
        pem = protection.decrypt_pem(row["private_key_encrypted"])
        private_key = keys.load_private_key(pem)
        signature = keys.sign_content(content, private_key)
        public_key = keys.load_public_key(row["public_key_pem"])
    except ValueError as exc:
        raise InternalFailure("Не вдалося створити ЕЦП") from exc

    if not keys.verify_content(content, signature, public_key):
        raise InternalFailure("Створений ЕЦП не пройшов самоперевірку")

    return {
        "signature_b64": base64.b64encode(signature).decode("ascii"),
        "algorithm": row["algorithm"],
        "fingerprint": row["key_fingerprint"],
    }


def store_signature(document_id: str, signer_id: int, signature: dict) -> None:
    repository.save_signature(
        document_id=document_id,
        signer_id=signer_id,
        algorithm=signature["algorithm"],
        signature_b64=signature["signature_b64"],
        public_key_fingerprint=signature["fingerprint"],
    )

"""Підписування документа та блокування підробленого підпису."""

from __future__ import annotations

import base64
import os

from secure_docvault.signing.repository import get_signature, save_signature
from tests.conftest import login_token, upload_document


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_upload_signs_and_download_reports_verified(client, member):
    token = login_token(client, member["username"])
    content = b"OFFICIAL STATEMENT: APPROVED BY CHIEF SECURITY OFFICER"

    document = upload_document(client, token, "official.txt", content)
    assert document["signature"]["status"] == "signed"
    assert document["signature"]["algorithm"] == "RSA-PSS-SHA256"

    listed = client.get("/api/v1/documents", headers=auth(token)).json()
    item = listed["documents"][0]
    assert item["signature"]["signer"] == member["username"]
    assert len(item["signature"]["fingerprint"]) == 64

    response = client.get(
        f"/api/v1/documents/{document['id']}/download", headers=auth(token)
    )
    assert response.status_code == 200
    assert response.content == content
    assert response.headers["X-Signature-Status"] == "Signed & Verified"
    assert response.headers["X-Signature-Algorithm"] == "RSA-PSS-SHA256"
    assert response.headers["X-Signer"] == member["username"]
    assert len(response.headers["X-Signature-Fingerprint"]) == 64


def test_tampered_signature_is_rejected(client, member):
    token = login_token(client, member["username"])
    document = upload_document(client, token, "signed.txt", b"signed bytes")

    stored = get_signature(document["id"])
    assert stored is not None
    save_signature(
        document_id=document["id"],
        signer_id=stored["signer_id"],
        algorithm=stored["algorithm"],
        signature_b64=base64.b64encode(os.urandom(256)).decode("ascii"),
        public_key_fingerprint=stored["public_key_fingerprint"],
    )

    response = client.get(
        f"/api/v1/documents/{document['id']}/download", headers=auth(token)
    )
    assert response.status_code == 409
    assert response.json()["error"]["code"] == "signature_invalid"
    assert "підпис" in response.json()["error"]["message"].lower()

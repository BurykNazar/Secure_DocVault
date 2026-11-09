"""Цілісність, порожні файли та видалення документів."""

from __future__ import annotations

from secure_docvault.settings import settings
from tests.conftest import login_token, upload_document


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def stored_file(doc_id: str):
    return settings.data_dir / "uploads" / f"{doc_id}.enc"


def test_tampered_file_is_rejected(client, member):
    token = login_token(client, member["username"])
    document = upload_document(client, token, "secret.txt", b"top secret")
    path = stored_file(document["id"])
    blob = bytearray(path.read_bytes())
    blob[20] ^= 0xFF
    path.write_bytes(bytes(blob))

    response = client.get(
        f"/api/v1/documents/{document['id']}/download", headers=auth(token)
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "integrity_failed"


def test_empty_file_is_rejected(client, member):
    token = login_token(client, member["username"])

    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.txt", b"", "text/plain")},
        headers=auth(token),
    )

    assert response.status_code == 400


def test_delete_removes_file_and_metadata(client, member):
    token = login_token(client, member["username"])
    document = upload_document(client, token)
    path = stored_file(document["id"])

    response = client.delete(
        f"/api/v1/documents/{document['id']}", headers=auth(token)
    )

    assert response.status_code == 204
    assert not path.exists()
    assert client.get(
        "/api/v1/documents", headers=auth(token)
    ).json()["documents"] == []

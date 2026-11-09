"""Завантаження, список і скачування документів."""

from __future__ import annotations

from secure_docvault.settings import settings
from tests.conftest import form, login_token, upload_document


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def stored_file(doc_id: str):
    return settings.data_dir / "uploads" / f"{doc_id}.enc"


def test_upload_stores_encrypted_container(client, member):
    token = login_token(client, member["username"])
    data = b"CONFIDENTIAL REPORT 2026"

    document = upload_document(client, token, "report.txt", data)
    blob = stored_file(document["id"]).read_bytes()

    assert len(blob) == 12 + 16 + len(data)
    assert data not in blob
    assert document["original_filename"] == "report.txt"
    assert document["size_bytes"] == len(data)


def test_download_returns_original_bytes(client, member):
    token = login_token(client, member["username"])
    data = "Конфіденційний звіт".encode("utf-8")
    document = upload_document(client, token, "zvit.txt", data)

    response = client.get(
        f"/api/v1/documents/{document['id']}/download", headers=auth(token)
    )

    assert response.status_code == 200
    assert response.content == data
    assert "attachment" in response.headers["content-disposition"]


def test_list_returns_only_own_documents(client, member):
    token = login_token(client, member["username"])
    upload_document(client, token)
    client.post(
        "/api/v1/accounts/register",
        json=form(username="other_user", email="other@example.com"),
    )
    other = login_token(client, "other_user")

    mine = client.get("/api/v1/documents", headers=auth(token)).json()
    theirs = client.get("/api/v1/documents", headers=auth(other)).json()

    assert len(mine["documents"]) == 1
    assert theirs["documents"] == []


def test_foreign_document_is_not_visible(client, member):
    token = login_token(client, member["username"])
    document = upload_document(client, token)
    client.post(
        "/api/v1/accounts/register",
        json=form(username="other_user", email="other@example.com"),
    )
    other = login_token(client, "other_user")

    response = client.get(
        f"/api/v1/documents/{document['id']}/download", headers=auth(other)
    )

    assert response.status_code == 404


def test_waf_does_not_read_inside_multipart(client, member):
    token = login_token(client, member["username"])

    document = upload_document(
        client, token, "notes.txt", b"UNION SELECT * FROM users"
    )

    assert document["original_filename"] == "notes.txt"

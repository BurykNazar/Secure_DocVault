"""Чужі документи й коментарі недоступні."""

from __future__ import annotations

from tests.conftest import form, login_token, upload_document


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def owner_setup(client, member) -> tuple[str, str]:
    token = login_token(client, member["username"])
    document = upload_document(client, token)
    return token, document["id"]


def stranger(client) -> str:
    client.post(
        "/api/v1/accounts/register",
        json=form(username="other_user", email="other@example.com"),
    )
    return login_token(client, "other_user")


def test_foreign_comments_are_not_listed(client, member):
    _, doc_id = owner_setup(client, member)
    other = stranger(client)

    response = client.get(
        f"/api/v1/documents/{doc_id}/comments", headers=auth(other)
    )

    assert response.status_code == 404


def test_foreign_document_rejects_comment(client, member):
    _, doc_id = owner_setup(client, member)
    other = stranger(client)

    response = client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json={"title": "Злам", "comment": "текст"},
        headers=auth(other),
    )

    assert response.status_code == 404


def test_foreign_comment_cannot_be_deleted(client, member):
    token, doc_id = owner_setup(client, member)
    comment_id = client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json={"title": "Свій", "comment": "текст"},
        headers=auth(token),
    ).json()["comment"]["id"]
    other = stranger(client)

    response = client.delete(
        f"/api/v1/documents/{doc_id}/comments/{comment_id}", headers=auth(other)
    )

    assert response.status_code == 404

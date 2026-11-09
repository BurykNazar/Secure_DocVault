"""Коментарі, прив'язані до документа."""

from __future__ import annotations

from tests.conftest import login_token, upload_document


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def document_for(client, member) -> tuple[str, str]:
    token = login_token(client, member["username"])
    document = upload_document(client, token)
    return token, document["id"]


def test_comment_is_stored_sanitized(client, member):
    token, doc_id = document_for(client, member)
    payload = {
        "title": "<b>Звіт</b>",
        "comment": "<script>alert('XSS')</script>",
    }

    response = client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json=payload,
        headers=auth(token),
    )

    assert response.status_code == 201
    item = response.json()["comment"]
    assert item["title"] == "Звіт"
    assert item["comment"] == "alert('XSS')"


def test_comments_are_listed_for_document(client, member):
    token, doc_id = document_for(client, member)
    client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json={"title": "Перший", "comment": "текст"},
        headers=auth(token),
    )

    response = client.get(
        f"/api/v1/documents/{doc_id}/comments", headers=auth(token)
    )

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 1


def test_comment_can_be_updated_and_deleted(client, member):
    token, doc_id = document_for(client, member)
    created = client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json={"title": "Старий", "comment": "було"},
        headers=auth(token),
    ).json()["comment"]

    updated = client.put(
        f"/api/v1/documents/{doc_id}/comments/{created['id']}",
        json={"title": "<b>Новий</b>", "comment": "стало"},
        headers=auth(token),
    )
    assert updated.status_code == 200
    assert updated.json()["comment"]["title"] == "Новий"

    removed = client.delete(
        f"/api/v1/documents/{doc_id}/comments/{created['id']}",
        headers=auth(token),
    )
    assert removed.status_code == 204


def test_empty_comment_after_sanitizing_is_rejected(client, member):
    token, doc_id = document_for(client, member)

    response = client.post(
        f"/api/v1/documents/{doc_id}/comments",
        json={"title": "<img src=x>", "comment": "<script></script>"},
        headers=auth(token),
    )

    assert response.status_code == 400

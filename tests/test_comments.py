"""Створення, перегляд і зміна власних коментарів."""

from __future__ import annotations

from secure_docvault.persistence import session
from tests.conftest import GOOD_PASSWORD


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def token_for(client, username: str) -> str:
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": username, "password": GOOD_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def test_comment_is_stored_already_sanitized(client, member):
    token = token_for(client, member["username"])
    payload = {
        "title": "<b>Звіт</b>",
        "comment": "<script>alert('XSS')</script><img src=x onerror=alert(1)>",
    }
    response = client.post(
        "/api/v1/comments", json=payload, headers=auth(token)
    )

    assert response.status_code == 201
    item = response.json()["comment"]
    assert item["title"] == "Звіт"
    assert item["comment"] == "alert('XSS')"
    with session() as connection:
        row = connection.execute(
            "SELECT title, body FROM comments WHERE id = ?", (item["id"],)
        ).fetchone()
    assert row["title"] == "Звіт"
    assert row["body"] == "alert('XSS')"

def test_list_returns_only_own_comments(client, member):
    token = token_for(client, member["username"])
    for index in range(2):
        client.post(
            "/api/v1/comments",
            json={"title": f"Запис {index}", "comment": "текст"},
            headers=auth(token),
        )
    response = client.get("/api/v1/comments", headers=auth(token))

    assert response.status_code == 200
    assert len(response.json()["comments"]) == 2

def test_own_comment_can_be_updated(client, member):
    token = token_for(client, member["username"])
    created = client.post(
        "/api/v1/comments",
        json={"title": "Старий", "comment": "було"},
        headers=auth(token),
    ).json()["comment"]
    response = client.put(
        f"/api/v1/comments/{created['id']}",
        json={"title": "<b>Новий</b>", "comment": "стало"},
        headers=auth(token),
    )

    assert response.status_code == 200
    assert response.json()["comment"]["title"] == "Новий"

def test_own_comment_can_be_deleted(client, member):
    token = token_for(client, member["username"])
    created = client.post(
        "/api/v1/comments",
        json={"title": "Тимчасовий", "comment": "текст"},
        headers=auth(token),
    ).json()["comment"]
    response = client.delete(
        f"/api/v1/comments/{created['id']}", headers=auth(token)
    )

    assert response.status_code == 204
    assert client.get(
        "/api/v1/comments", headers=auth(token)
    ).json()["comments"] == []

def test_empty_text_after_sanitizing_is_rejected(client, member):
    token = token_for(client, member["username"])
    response = client.post(
        "/api/v1/comments",
        json={"title": "<img src=x>", "comment": "<script></script>"},
        headers=auth(token),
    )

    assert response.status_code == 400
    fields = response.json()["error"]["fields"]
    assert "title" in fields and "comment" in fields

"""Чужі коментарі недоступні: перевірка ізоляції власників."""

from __future__ import annotations

from tests.conftest import GOOD_PASSWORD, form


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def token_for(client, username: str) -> str:
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": username, "password": GOOD_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()["access_token"]


def second_user(client) -> str:
    client.post(
        "/api/v1/accounts/register",
        json=form(username="other_user", email="other@example.com"),
    )
    return token_for(client, "other_user")


def make_comment(client, token: str) -> int:
    response = client.post(
        "/api/v1/comments",
        json={"title": "Свій", "comment": "текст"},
        headers=auth(token),
    )
    return response.json()["comment"]["id"]


def test_other_user_sees_nothing(client, member):
    owner = token_for(client, member["username"])
    make_comment(client, owner)
    stranger = second_user(client)

    response = client.get("/api/v1/comments", headers=auth(stranger))

    assert response.status_code == 200
    assert response.json()["comments"] == []


def test_foreign_comment_cannot_be_changed(client, member):
    owner = token_for(client, member["username"])
    comment_id = make_comment(client, owner)
    stranger = second_user(client)

    response = client.put(
        f"/api/v1/comments/{comment_id}",
        json={"title": "Злам", "comment": "текст"},
        headers=auth(stranger),
    )

    assert response.status_code == 404


def test_foreign_comment_cannot_be_deleted(client, member):
    owner = token_for(client, member["username"])
    comment_id = make_comment(client, owner)
    stranger = second_user(client)

    response = client.delete(
        f"/api/v1/comments/{comment_id}", headers=auth(stranger)
    )

    assert response.status_code == 404


def test_anonymous_user_cannot_add_comment(client):
    response = client.post(
        "/api/v1/comments", json={"title": "Тест", "comment": "текст"}
    )

    assert response.status_code == 401

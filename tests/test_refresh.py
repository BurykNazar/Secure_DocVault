"""Ротація refresh-токенів і захист від повторного використання."""

from __future__ import annotations

from tests.conftest import GOOD_PASSWORD


def _sign_in(client, member) -> dict:
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()


def _refresh(client, token: str):
    return client.post(
        "/api/v1/auth/refresh", json={"refresh_token": token}
    )


def test_refresh_returns_a_new_pair(client, member):
    first = _sign_in(client, member)
    response = _refresh(client, first["refresh_token"])

    assert response.status_code == 200
    second = response.json()
    assert second["access_token"] != first["access_token"]
    assert second["refresh_token"] != first["refresh_token"]

    profile = client.get(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {second['access_token']}"},
    )
    assert profile.status_code == 200


def test_reused_refresh_token_is_rejected(client, member):
    tokens = _sign_in(client, member)
    assert _refresh(client, tokens["refresh_token"]).status_code == 200

    replay = _refresh(client, tokens["refresh_token"])

    assert replay.status_code == 401
    assert replay.json()["error"]["code"] == "token_reuse"


def test_access_token_cannot_be_refreshed(client, member):
    tokens = _sign_in(client, member)
    response = _refresh(client, tokens["access_token"])

    assert response.status_code == 401
    assert "тип токена" in response.json()["error"]["message"]


def test_garbage_refresh_token_is_rejected(client, member):
    response = _refresh(client, "not-a-jwt")

    assert response.status_code == 401

"""Блокування після серії невдалих спроб."""

from __future__ import annotations

from secure_docvault.persistence import session
from secure_docvault.settings import settings
from tests.conftest import GOOD_PASSWORD, form


def read(username: str) -> dict:
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    assert row is not None
    return dict(row)


def fail_login(client, username: str):
    return client.post(
        "/api/v1/accounts/login",
        json={"username": username, "password": "WrongPass1!"},
    )


def test_account_is_blocked_after_limit(client):
    client.post("/api/v1/accounts/register", json=form())
    username = form()["username"]

    for _ in range(settings.max_failures - 1):
        assert fail_login(client, username).status_code == 401

    blocked = fail_login(client, username)
    assert blocked.status_code == 423
    assert blocked.json()["error"]["code"] == "account_blocked"

    still_blocked = client.post(
        "/api/v1/accounts/login",
        json={"username": username, "password": GOOD_PASSWORD},
    )
    assert still_blocked.status_code == 423

    row = read(username)
    assert row["failed_attempts"] == settings.max_failures
    assert row["locked_until"] is not None


def test_successful_sign_in_clears_counter(client, member):
    for _ in range(2):
        fail_login(client, member["username"])

    client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )

    assert read(member["username"])["failed_attempts"] == 0

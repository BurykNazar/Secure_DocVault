"""Сценарії створення облікового запису."""

from __future__ import annotations

from secure_docvault.persistence import session
from tests.conftest import GOOD_PASSWORD, form


def read(username: str) -> dict:
    with session() as connection:
        row = connection.execute(
            "SELECT * FROM users WHERE username = ?", (username,)
        ).fetchone()
    assert row is not None
    return dict(row)


def test_account_is_created_without_exposing_secrets(client):
    response = client.post("/api/v1/accounts/register", json=form())

    assert response.status_code == 201
    body = response.json()
    assert body["ok"] is True
    assert body["account"]["username"] == "nazar_buryk"
    assert body["account"]["role"] == "user"
    assert "password_hash" not in response.text
    assert "salt" not in body["account"]


def test_password_is_stored_as_salted_bcrypt_hash(client):
    client.post("/api/v1/accounts/register", json=form())
    row = read("nazar_buryk")

    assert row["password_hash"].startswith("$2b$")
    assert row["password_hash"] != GOOD_PASSWORD
    assert row["salt"] in row["password_hash"]
    assert (row["is_active"], row["failed_attempts"]) == (1, 0)


def test_equal_passwords_give_different_hashes(client):
    client.post("/api/v1/accounts/register", json=form())
    client.post(
        "/api/v1/accounts/register",
        json=form(username="second_user", email="second@example.com"),
    )

    first, second = read("nazar_buryk"), read("second_user")
    assert first["salt"] != second["salt"]
    assert first["password_hash"] != second["password_hash"]


def test_duplicate_username_ignores_case(client):
    client.post("/api/v1/accounts/register", json=form())

    response = client.post(
        "/api/v1/accounts/register",
        json=form(username="NAZAR_BURYK", email="other@example.com"),
    )

    assert response.status_code == 409
    assert "username" in response.json()["error"]["fields"]


def test_duplicate_email_ignores_case(client):
    client.post("/api/v1/accounts/register", json=form())

    response = client.post(
        "/api/v1/accounts/register",
        json=form(username="another_user", email="NAZAR@example.com"),
    )

    assert response.status_code == 409
    assert "email" in response.json()["error"]["fields"]


def test_weak_password_lists_every_requirement(client):
    response = client.post(
        "/api/v1/accounts/register", json=form(password="short")
    )

    assert response.status_code == 400
    body = response.json()["error"]
    assert body["code"] == "validation_failed"
    assert len(body["fields"]["password"]) >= 3


def test_invalid_name_and_email_are_reported(client):
    response = client.post(
        "/api/v1/accounts/register",
        json=form(username="1 bad", email="not-a-mail"),
    )

    assert response.status_code == 400
    fields = response.json()["error"]["fields"]
    assert "username" in fields and "email" in fields

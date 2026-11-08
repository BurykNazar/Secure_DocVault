"""Сценарії входу."""

from __future__ import annotations

from tests.conftest import GOOD_PASSWORD


def test_sign_in_succeeds(client, member):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )

    assert response.status_code == 200
    assert response.json()["account"]["username"] == "nazar_buryk"


def test_username_match_ignores_case(client, member):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": "NAZAR_BURYK", "password": GOOD_PASSWORD},
    )

    assert response.status_code == 200


def test_wrong_password_is_rejected(client, member):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": "WrongPass1!"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_credentials"


def test_unknown_account_looks_the_same(client):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": "ghost", "password": "WrongPass1!"},
    )

    assert response.status_code == 401
    assert "Невірне ім'я користувача" in response.json()["error"]["message"]


def test_empty_fields_are_validation_errors(client):
    response = client.post(
        "/api/v1/accounts/login", json={"username": "", "password": ""}
    )

    assert response.status_code == 400
    fields = response.json()["error"]["fields"]
    assert "username" in fields and "password" in fields

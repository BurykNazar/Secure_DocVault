"""Доказ стійкості до SQL-ін'єкцій."""

from __future__ import annotations

import pytest

from secure_docvault.identity import queries
from secure_docvault.persistence import session
from secure_docvault.transport.gate import reset as reset_gate
from tests.conftest import GOOD_PASSWORD, form

PAYLOADS = [
    "' OR '1'='1",
    "admin' --",
    "' UNION SELECT id, username, email, password_hash, salt FROM users --",
    "'; DROP TABLE users; --",
    '" OR ""="',
]


@pytest.mark.parametrize("payload", PAYLOADS)
def test_payload_cannot_open_a_session(client, member, payload):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": payload, "password": "WrongPass1!"},
    )

    assert response.status_code in (401, 403)
    assert response.json()["ok"] is False


@pytest.mark.parametrize("payload", PAYLOADS)
def test_repository_sees_payload_as_plain_text(client, member, payload):
    assert queries.by_username(payload) is None


def test_drop_payload_leaves_database_intact(client, member):
    client.post(
        "/api/v1/accounts/login",
        json={"username": "'; DROP TABLE users; --", "password": "x"},
    )

    with session() as connection:
        total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert total == 1

    reset_gate()
    good = client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )
    assert good.status_code == 200


def test_payload_in_signup_fields_is_rejected(client):
    name = client.post(
        "/api/v1/accounts/register", json=form(username="admin' OR '1'='1")
    )
    mail = client.post(
        "/api/v1/accounts/register", json=form(email="x' OR '1'='1@mail.com")
    )

    assert name.status_code == 403
    assert mail.status_code == 403


def test_database_stays_intact_after_attacks(client, member):
    for payload in PAYLOADS:
        client.post(
            "/api/v1/accounts/login",
            json={"username": payload, "password": "x"},
        )

    with session() as connection:
        total = connection.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    assert total == 1

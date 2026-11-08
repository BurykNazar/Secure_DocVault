"""JWT: випуск access-токена та доступ до захищеного профілю."""

from __future__ import annotations

import base64
import datetime
import json

import jwt

from secure_docvault.settings import settings
from tests.conftest import GOOD_PASSWORD


def _sign_in(client, member) -> dict:
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )
    assert response.status_code == 200
    return response.json()


def _get_profile(client, token: str):
    return client.get(
        "/api/v1/user/profile",
        headers={"Authorization": f"Bearer {token}"},
    )


def _segment(data: dict) -> str:
    raw = json.dumps(data).encode("utf-8")
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def test_login_returns_access_and_refresh_tokens(client, member):
    body = _sign_in(client, member)

    assert body["token_type"] == "bearer"
    assert body["access_token"] and body["refresh_token"]
    claims = jwt.decode(
        body["access_token"], settings.jwt_secret, algorithms=["HS256"]
    )
    assert claims["type"] == "access"
    assert claims["username"] == "nazar_buryk"
    assert claims["role"] == "user"
    assert claims["exp"] > claims["iat"]


def test_profile_requires_a_token(client):
    response = client.get("/api/v1/user/profile")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "invalid_token"


def test_profile_accepts_access_token(client, member):
    tokens = _sign_in(client, member)
    response = _get_profile(client, tokens["access_token"])

    assert response.status_code == 200
    assert response.json()["profile"]["username"] == "nazar_buryk"


def test_refresh_token_cannot_open_profile(client, member):
    tokens = _sign_in(client, member)
    response = _get_profile(client, tokens["refresh_token"])

    assert response.status_code == 401
    assert "тип токена" in response.json()["error"]["message"]


def test_tampered_payload_breaks_the_signature(client, member):
    tokens = _sign_in(client, member)
    claims = jwt.decode(tokens["access_token"], options={"verify_signature": False})
    claims["role"] = "admin"
    forged = jwt.encode(claims, "attacker-secret-key-32-bytes-long!!", algorithm="HS256")

    assert _get_profile(client, forged).status_code == 401


def test_alg_none_is_rejected(client, member):
    tokens = _sign_in(client, member)
    claims = jwt.decode(tokens["access_token"], options={"verify_signature": False})
    unsigned = f"{_segment({'alg': 'none', 'typ': 'JWT'})}.{_segment(claims)}."

    assert _get_profile(client, unsigned).status_code == 401


def test_expired_token_is_rejected(client, member):
    tokens = _sign_in(client, member)
    claims = jwt.decode(tokens["access_token"], options={"verify_signature": False})
    past = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
    claims["iat"] = past
    claims["exp"] = past
    expired = jwt.encode(claims, settings.jwt_secret, algorithm="HS256")

    response = _get_profile(client, expired)
    assert response.status_code == 401
    assert "Термін дії" in response.json()["error"]["message"]

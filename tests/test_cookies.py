"""Cookie-автентифікація та її прапорці."""

from __future__ import annotations

from secure_docvault.settings import settings
from tests.conftest import GOOD_PASSWORD


def _login(client, member):
    return client.post(
        "/api/v1/accounts/login",
        json={"username": member["username"], "password": GOOD_PASSWORD},
    )


def test_login_sets_hardened_cookie(client, member):
    response = _login(client, member)
    header = response.headers["set-cookie"].lower()

    assert "vault_access=" in header
    assert "httponly" in header
    assert "samesite=strict" in header
    assert "path=/" in header
    if settings.cookie_secure:
        assert "secure" in header


def test_profile_accepts_cookie_without_bearer(client, member):
    token = _login(client, member).json()["access_token"]

    response = client.get(
        "/api/v1/user/profile",
        headers={"Cookie": f"vault_access={token}"},
    )

    assert response.status_code == 200
    assert response.json()["profile"]["username"] == "nazar_buryk"


def test_broken_cookie_is_rejected(client):
    response = client.get(
        "/api/v1/user/profile",
        headers={"Cookie": "vault_access=not-a-jwt"},
    )

    assert response.status_code == 401

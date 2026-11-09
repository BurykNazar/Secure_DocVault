"""CORS: дозволені та сторонні Origin."""

from __future__ import annotations

PREFLIGHT = {
    "Access-Control-Request-Method": "POST",
}


def test_allowed_origin_is_echoed(client):
    response = client.options(
        "/api/v1/accounts/login",
        headers={"Origin": "http://localhost:8000", **PREFLIGHT},
    )

    assert response.headers.get("access-control-allow-origin") == (
        "http://localhost:8000"
    )


def test_foreign_origin_gets_no_permission(client):
    response = client.options(
        "/api/v1/accounts/login",
        headers={"Origin": "http://evil.example", **PREFLIGHT},
    )

    assert "access-control-allow-origin" not in response.headers

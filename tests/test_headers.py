"""Захисні HTTP-заголовки та CSP."""

from __future__ import annotations


def test_app_response_has_strict_headers(client):
    response = client.get("/")
    csp = response.headers["content-security-policy"]

    assert "script-src 'self'" in csp
    assert "unsafe-inline" not in csp
    assert "frame-ancestors 'none'" in csp
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"
    assert "max-age=31536000" in response.headers["strict-transport-security"]
    assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"


def test_reference_page_gets_its_own_csp(client):
    response = client.get("/api/docs")
    csp = response.headers["content-security-policy"]

    assert "unsafe-inline" in csp
    assert "https://cdn.jsdelivr.net" in csp


def test_api_errors_also_carry_headers(client):
    response = client.get("/api/v1/user/profile")

    assert response.status_code == 401
    assert response.headers["x-frame-options"] == "DENY"
    assert "content-security-policy" in response.headers

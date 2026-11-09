"""Санітизація XSS-пейлоадів."""

from __future__ import annotations

from secure_docvault.security.sanitizer import clean_text
from tests.conftest import GOOD_PASSWORD, form


def test_script_tag_is_removed():
    cleaned = clean_text("<script>alert('XSS')</script>")

    assert "<script" not in cleaned.lower()
    assert "alert" in cleaned  # текст лишається, але вже безпечний


def test_img_onerror_is_removed():
    assert clean_text('<img src=x onerror="alert(1)">') == ""


def test_registration_sanitizes_the_username(client):
    response = client.post(
        "/api/v1/accounts/register", json=form(username="<b>nazar</b>")
    )

    assert response.status_code == 201
    assert response.json()["account"]["username"] == "nazar"


def test_login_sanitizes_the_username(client, member):
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": "<b>nazar_buryk</b>", "password": GOOD_PASSWORD},
    )

    assert response.status_code == 200

"""Сторінка документації API (Scalar)."""

from __future__ import annotations


def test_reference_page_is_available(client):
    response = client.get("/api/docs")

    assert response.status_code == 200
    assert "Scalar" in response.text


def test_swagger_ui_is_replaced(client):
    response = client.get("/api/redoc")

    assert response.status_code == 404

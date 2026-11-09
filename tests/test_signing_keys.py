"""Генерація ключів ЕЦП, PEM-експорт і криптомодуль."""

from __future__ import annotations

import pytest
from cryptography.hazmat.primitives import serialization

from secure_docvault.signing import keys
from tests.conftest import login_token


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_key_generation_and_public_pem(client, member):
    token = login_token(client, member["username"])

    empty = client.get("/api/v1/signing/keys", headers=auth(token))
    assert empty.status_code == 200
    assert empty.json()["key"] is None

    created = client.post("/api/v1/signing/keys", headers=auth(token))
    assert created.status_code == 200
    key = created.json()["key"]
    assert key["algorithm"] == "RSA-PSS-SHA256"
    assert key["public_key_pem"].startswith("-----BEGIN PUBLIC KEY-----")

    again = client.get("/api/v1/signing/keys", headers=auth(token)).json()
    assert again["key"]["fingerprint"] == key["fingerprint"]

    pem = client.get("/api/v1/signing/keys/public", headers=auth(token))
    assert pem.status_code == 200
    assert pem.text.startswith("-----BEGIN PUBLIC KEY-----")
    assert keys.load_public_key(pem.text).key_size == 2048


def test_private_key_export_is_password_protected(client, member):
    token = login_token(client, member["username"])

    response = client.post(
        "/api/v1/signing/keys/export",
        headers=auth(token),
        json={"passphrase": "Aa1!aaaa"},
    )
    assert response.status_code == 200, response.text
    assert "BEGIN ENCRYPTED PRIVATE KEY" in response.text
    assert "BEGIN PRIVATE KEY" not in response.text

    private_key = serialization.load_pem_private_key(
        response.content, password=b"Aa1!aaaa"
    )
    assert private_key.key_size == 2048

    with pytest.raises(ValueError):
        serialization.load_pem_private_key(response.content, password=b"wrong")

    short = client.post(
        "/api/v1/signing/keys/export",
        headers=auth(token),
        json={"passphrase": "short"},
    )
    assert short.status_code == 400
    assert short.json()["error"]["fields"]["passphrase"]


def test_signature_module_detects_modified_content():
    private_key, public_key = keys.generate_keypair()
    original = b"OFFICIAL STATEMENT: APPROVED"
    signature = keys.sign_content(original, private_key)

    assert keys.verify_content(original, signature, public_key)
    assert not keys.verify_content(
        b"OFFICIAL STATEMENT: REJECTED", signature, public_key
    )

    public_pem = keys.serialize_public_key(public_key)
    private_pem = keys.serialize_private_key(private_key, "Aa1!aaaa")
    assert "BEGIN PUBLIC KEY" in public_pem
    assert "BEGIN ENCRYPTED PRIVATE KEY" in private_pem
    assert keys.load_public_key(public_pem).key_size == 2048
    assert keys.load_private_key(private_pem, "Aa1!aaaa").key_size == 2048

"""AES-256-GCM: контейнер, унікальність IV і виявлення підробки."""

from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidTag

from secure_docvault.security.vault import associated, decrypt, encrypt


def test_roundtrip():
    data = b"CONFIDENTIAL FINANCIAL REPORT 2026"
    aad = associated("doc-1", 7)

    blob = encrypt(data, aad)

    assert decrypt(blob, aad) == data


def test_container_layout_and_no_plaintext():
    data = b"SECRET DATA"
    aad = associated("doc-2", 1)

    blob = encrypt(data, aad)

    assert len(blob) == 12 + 16 + len(data)
    assert data not in blob


def test_nonce_is_unique_for_each_encryption():
    aad = associated("doc-3", 1)

    first = encrypt(b"same", aad)
    second = encrypt(b"same", aad)

    assert first != second
    assert first[:12] != second[:12]


def test_single_byte_change_raises_invalid_tag():
    aad = associated("doc-4", 1)
    blob = bytearray(encrypt(b"important", aad))
    blob[20] ^= 0xFF

    with pytest.raises(InvalidTag):
        decrypt(bytes(blob), aad)


def test_wrong_associated_data_is_rejected():
    data = b"document body"
    blob = encrypt(data, associated("doc-5", 1))

    with pytest.raises(InvalidTag):
        decrypt(blob, associated("doc-5", 2))

"""Перевірка bcrypt-модуля."""

from __future__ import annotations

import pytest

from secure_docvault.identity.hashing import BYTE_LIMIT, matches, seal


def test_roundtrip_and_service_salt_copy():
    digest, salt = seal("Dossier2026!")

    assert digest.startswith("$2b$")
    assert "Dossier2026!" not in digest
    assert salt.startswith("$2b$")
    assert salt in digest
    assert matches("Dossier2026!", digest)


def test_equal_passwords_get_different_salts():
    first, first_salt = seal("Dossier2026!")
    second, second_salt = seal("Dossier2026!")

    assert first != second
    assert first_salt != second_salt
    assert matches("Dossier2026!", first)
    assert matches("Dossier2026!", second)


def test_wrong_password_is_rejected():
    digest, _ = seal("Dossier2026!")

    assert matches("dossier2026!", digest) is False
    assert matches("", digest) is False


def test_overlong_password_is_refused_before_hashing():
    oversized = "A1!" + "a" * BYTE_LIMIT

    with pytest.raises(ValueError):
        seal(oversized)
    assert matches(oversized, "$2b$04$" + "x" * 50) is False


def test_damaged_digest_does_not_raise():
    assert matches("Dossier2026!", "not-a-bcrypt-digest") is False

"""Подання документів для API."""

from __future__ import annotations

from ..signing.verification import signature_info
from . import repository


def public(row: dict) -> dict:
    return {
        "id": row["id"],
        "original_filename": row["original_filename"],
        "content_type": row["content_type"],
        "size_bytes": row["size_bytes"],
        "created_at": row["created_at"],
        "signature": signature_info(row["id"]),
    }


def list_mine(claims: dict) -> list[dict]:
    owner = int(claims["sub"])
    return [public(row) for row in repository.list_for(owner)]

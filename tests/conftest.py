"""Спільні фікстури pytest.

Змінні оточення задаються до імпорту застосунку: конфігурація
читається один раз під час старту. Тести працюють із тимчасовою базою
й не торкаються робочих даних.
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

_TEMP = Path(tempfile.mkdtemp(prefix="docvault-tests-"))
os.environ["VAULT_DATA_DIR"] = str(_TEMP)
os.environ["VAULT_DB"] = str(_TEMP / "test.sqlite3")
os.environ["VAULT_HASH_ROUNDS"] = "4"

from fastapi.testclient import TestClient  # noqa: E402

from secure_docvault.factory import app  # noqa: E402
from secure_docvault.persistence import session  # noqa: E402
from secure_docvault.transport.gate import reset as reset_gate  # noqa: E402

GOOD_PASSWORD = "Dossier2026!"


def form(**changes: str) -> dict[str, str]:
    payload = {
        "username": "nazar_buryk",
        "email": "nazar@example.com",
        "password": GOOD_PASSWORD,
    }
    payload.update(changes)
    return payload


def login_token(client, username: str = "nazar_buryk") -> str:
    response = client.post(
        "/api/v1/accounts/login",
        json={"username": username, "password": GOOD_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def upload_document(
    client,
    token: str,
    name: str = "report.txt",
    content: bytes = b"CONFIDENTIAL REPORT",
) -> dict:
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": (name, content, "text/plain")},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 201, response.text
    return response.json()["document"]


@pytest.fixture(autouse=True)
def _clean_gate():
    """Кожен тест починається з чистими лічильниками й Greylist."""
    reset_gate()


@pytest.fixture()
def client():
    with session() as connection:
        connection.execute("DELETE FROM users")
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def member(client):
    response = client.post("/api/v1/accounts/register", json=form())
    assert response.status_code == 201, response.text
    return form()

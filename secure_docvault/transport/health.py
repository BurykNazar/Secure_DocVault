"""Службовий маршрут стану сервісу."""

from fastapi import APIRouter

from ..identity.queries import total

router = APIRouter(tags=["Службові"])


@router.get("/api/v1/status", summary="Стан сервісу")
def status() -> dict:
    return {
        "ok": True,
        "service": "Secure DocVault",
        "database": "ready",
        "accounts": total(),
    }

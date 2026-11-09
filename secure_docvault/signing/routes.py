"""HTTP-маршрути ключів ЕЦП."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel

from ..identity.guard import current_claims
from . import service

router = APIRouter(prefix="/api/v1/signing", tags=["ЕЦП"])


class ExportPayload(BaseModel):
    passphrase: str


def _pem_response(pem: str, filename: str) -> Response:
    return Response(
        content=pem,
        media_type="application/x-pem-file",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Cache-Control": "no-store",
            "Pragma": "no-cache",
        },
    )


@router.get("/keys", summary="Інформація про ключ ЕЦП")
def key_info(claims: dict = Depends(current_claims)) -> dict:
    return {"ok": True, "key": service.find_key(int(claims["sub"]))}


@router.post("/keys", summary="Створити ключі ЕЦП")
def create_keys(claims: dict = Depends(current_claims)) -> dict:
    return {"ok": True, "key": service.get_key(int(claims["sub"]))}


@router.get("/keys/public", summary="Експорт відкритого ключа")
def public_key(claims: dict = Depends(current_claims)) -> Response:
    pem = service.public_key_pem(int(claims["sub"]))
    return _pem_response(pem, "docvault-public-key.pem")


@router.post("/keys/export", summary="Експорт приватного ключа")
def export_key(
    payload: ExportPayload, claims: dict = Depends(current_claims)
) -> Response:
    pem = service.export_private_key(int(claims["sub"]), payload.passphrase)
    return _pem_response(pem, "docvault-private-key.pem")

"""HTTP-маршрути документів."""

from fastapi import APIRouter, Depends, File, Response, UploadFile, status

from ..identity.guard import current_claims
from . import service
from .filenames import disposition

router = APIRouter(prefix="/api/v1/documents", tags=["Документи"])


@router.get("", summary="Мої документи")
def list_documents(claims: dict = Depends(current_claims)) -> dict:
    return {"ok": True, "documents": service.list_mine(claims)}


@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Завантажити й зашифрувати документ",
)
async def upload_document(
    file: UploadFile = File(...), claims: dict = Depends(current_claims)
) -> dict:
    return {"ok": True, "document": await service.upload(file, claims)}


@router.get("/{doc_id}/download", summary="Скачати й розшифрувати документ")
def download_document(doc_id: str, claims: dict = Depends(current_claims)) -> Response:
    data, filename, content_type = service.download(doc_id, claims)
    return Response(
        content=data,
        media_type=content_type or "application/octet-stream",
        headers={"Content-Disposition": disposition(filename)},
    )


@router.delete(
    "/{doc_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити документ",
)
def delete_document(doc_id: str, claims: dict = Depends(current_claims)) -> None:
    service.delete(doc_id, claims)

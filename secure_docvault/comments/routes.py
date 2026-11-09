"""Маршрути коментарів до документа."""

from fastapi import APIRouter, Depends, status

from ..identity.guard import current_claims
from . import service
from .models import CommentDraft

router = APIRouter(prefix="/api/v1/documents", tags=["Коментарі"])


@router.get("/{document_id}/comments", summary="Коментарі до документа")
def list_comments(
    document_id: str, claims: dict = Depends(current_claims)
) -> dict:
    return {"ok": True, "comments": service.list_for(document_id, claims)}


@router.post(
    "/{document_id}/comments",
    status_code=status.HTTP_201_CREATED,
    summary="Додати коментар до документа",
)
def add_comment(
    document_id: str,
    draft: CommentDraft,
    claims: dict = Depends(current_claims),
) -> dict:
    return {"ok": True, "comment": service.create(document_id, claims, draft)}


@router.put("/{document_id}/comments/{comment_id}", summary="Змінити коментар")
def edit_comment(
    document_id: str,
    comment_id: int,
    draft: CommentDraft,
    claims: dict = Depends(current_claims),
) -> dict:
    return {
        "ok": True,
        "comment": service.update(document_id, comment_id, claims, draft),
    }


@router.delete(
    "/{document_id}/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити коментар",
)
def remove_comment(
    document_id: str, comment_id: int, claims: dict = Depends(current_claims)
) -> None:
    service.delete(document_id, comment_id, claims)

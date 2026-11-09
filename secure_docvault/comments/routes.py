"""Маршрути коментарів: лише власні записи."""

from fastapi import APIRouter, Depends, status

from ..identity.guard import current_claims
from ..security.sanitizer import clean_text
from . import service
from .models import CommentDraft

router = APIRouter(prefix="/api/v1/comments", tags=["Коментарі"])


@router.get("", summary="Мої коментарі")
def list_comments(claims: dict = Depends(current_claims)) -> dict:
    return {"ok": True, "comments": service.list_mine(claims)}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Додати коментар")
def add_comment(
    draft: CommentDraft, claims: dict = Depends(current_claims)
) -> dict:
    return {"ok": True, "comment": service.create(claims, draft)}


@router.put("/{comment_id}", summary="Змінити свій коментар")
def edit_comment(
    comment_id: int,
    draft: CommentDraft,
    claims: dict = Depends(current_claims),
) -> dict:
    return {"ok": True, "comment": service.update(claims, comment_id, draft)}


@router.delete(
    "/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Видалити свій коментар",
)
def remove_comment(comment_id: int, claims: dict = Depends(current_claims)) -> None:
    service.delete(claims, comment_id)


@router.post("/preview", summary="Очистити текст без збереження")
def preview(
    draft: CommentDraft, _: dict = Depends(current_claims)
) -> dict:
    return {
        "ok": True,
        "original": {"title": draft.title, "comment": draft.comment},
        "sanitized": {
            "title": clean_text(draft.title),
            "comment": clean_text(draft.comment),
        },
    }

"""Сценарії коментарів, прив'язаних до документа."""

from __future__ import annotations

from ..documents import repository as documents
from ..security.sanitizer import clean_text
from ..transport.errors import MissingResource, ValidationRejected
from . import repository
from .models import CommentDraft


def _owner(claims: dict) -> int:
    return int(claims["sub"])


def _ensure_document(document_id: str, claims: dict) -> int:
    owner = _owner(claims)
    if documents.get_for(owner, document_id) is None:
        raise MissingResource("Документ не знайдено")
    return owner


def _clean(draft: CommentDraft) -> tuple[str, str]:
    title = clean_text(draft.title)
    comment = clean_text(draft.comment)

    issues: dict[str, list[str]] = {}
    if not title:
        issues["title"] = ["Порожній заголовок після очищення"]
    if not comment:
        issues["comment"] = ["Порожній текст після очищення"]
    if issues:
        raise ValidationRejected("Текст порожній після очищення", fields=issues)

    return title, comment


def _public(row: dict) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "comment": row["body"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def list_for(document_id: str, claims: dict) -> list[dict]:
    owner = _ensure_document(document_id, claims)
    return [_public(row) for row in repository.list_for(document_id, owner)]


def create(document_id: str, claims: dict, draft: CommentDraft) -> dict:
    owner = _ensure_document(document_id, claims)
    title, comment = _clean(draft)
    return _public(repository.create(document_id, owner, title, comment))


def update(document_id: str, comment_id: int, claims: dict, draft: CommentDraft) -> dict:
    owner = _ensure_document(document_id, claims)
    title, comment = _clean(draft)
    row = repository.update(document_id, owner, comment_id, title, comment)
    if row is None:
        raise MissingResource("Коментар не знайдено")
    return _public(row)


def delete(document_id: str, comment_id: int, claims: dict) -> None:
    owner = _ensure_document(document_id, claims)
    if not repository.delete(document_id, owner, comment_id):
        raise MissingResource("Коментар не знайдено")

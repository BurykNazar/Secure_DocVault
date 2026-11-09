"""Сценарії роботи з коментарями."""

from __future__ import annotations

from ..security.sanitizer import clean_text
from ..transport.errors import MissingResource, ValidationRejected
from . import repository
from .models import CommentDraft


def _owner(claims: dict) -> int:
    try:
        return int(claims["sub"])
    except (KeyError, TypeError, ValueError):
        raise ValidationRejected("Некоректний токен") from None


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


def list_mine(claims: dict) -> list[dict]:
    return [_public(row) for row in repository.list_for(_owner(claims))]


def create(claims: dict, draft: CommentDraft) -> dict:
    title, comment = _clean(draft)
    return _public(repository.create(_owner(claims), title, comment))


def update(claims: dict, comment_id: int, draft: CommentDraft) -> dict:
    title, comment = _clean(draft)
    row = repository.update(_owner(claims), comment_id, title, comment)
    if row is None:
        raise MissingResource("Коментар не знайдено")
    return _public(row)


def delete(claims: dict, comment_id: int) -> None:
    if not repository.delete(_owner(claims), comment_id):
        raise MissingResource("Коментар не знайдено")

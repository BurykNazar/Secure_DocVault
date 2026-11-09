"""Модель коментаря."""

from pydantic import BaseModel, Field


class CommentDraft(BaseModel):
    title: str = Field(default="", max_length=200)
    comment: str = Field(default="", max_length=4000)

"""Контракти запитів доступу."""

from pydantic import BaseModel, Field


class SignUp(BaseModel):
    username: str = Field(default="", max_length=64)
    email: str = Field(default="", max_length=254)
    password: str = Field(default="", max_length=128)


class SignIn(BaseModel):
    # Поле входу навмисно без обмежень набору символів: будь-який рядок
    # безпечно потрапляє в параметризований запит.
    username: str = Field(default="", max_length=255)
    password: str = Field(default="", max_length=128)


class RefreshPayload(BaseModel):
    refresh_token: str = Field(default="", max_length=4096)

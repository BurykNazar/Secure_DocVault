"""Очищення користувацького тексту від HTML/JS.

Bleach видаляє всі теги й атрибути, залишаючи лише текст. Це закриває
Stored і Reflected XSS у місцях, де введення зберігається або
повертається клієнту.
"""

from __future__ import annotations

import bleach


def clean_text(value: str) -> str:
    if not value:
        return ""

    return bleach.clean(
        value,
        tags=[],
        attributes={},
        protocols=[],
        strip=True,
    ).strip()

"""Сигнатурний фільтр (мікро-WAF).

Перевіряються шлях, query-параметри та тіло запиту. XSS-сигнатури
навмисно не додані: такий текст очищується санітизатором ЛР №3, а не
відкидається на вході.
"""

from __future__ import annotations

import re

SIGNATURES = [
    (re.compile(r"\.\.[\\/]"), "Path Traversal"),
    (re.compile(r"(?i)\bunion\s+select\b"), "SQL Injection"),
    (re.compile(r"(?i)'\s*or\s*'1'\s*=\s*'1"), "SQL Injection"),
    (re.compile(r"(?i)\bexec(?:ute)?\s+xp_"), "SQL Injection"),
    (re.compile(r"(?i)\bdrop\s+table\b"), "SQL Injection"),
    (
        re.compile(
            r"(?i)(\|\s*(?:sh|bash)\b|cmd\.exe|/bin/(?:sh|bash)\b"
            r"|system\s*\(|\bcmd\s*=)"
        ),
        "Command Injection",
    ),
]


def inspect(path: str, query: str, body: bytes) -> str:
    """Повертає назву атаки або порожній рядок."""
    text = "\n".join((path, query, body.decode("utf-8", errors="ignore")))
    for pattern, name in SIGNATURES:
        if pattern.search(text):
            return name
    return ""

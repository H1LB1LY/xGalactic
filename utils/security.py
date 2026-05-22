"""Input sanitization and validation helpers."""

from __future__ import annotations

import re

MAX_TRANSLATION_INPUT = 4000
MAX_WEBHOOK_NAME = 80

# Strip null bytes and excessive whitespace
_CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(text: str, max_len: int = MAX_TRANSLATION_INPUT) -> str:
    """Sanitize user text before sending to Grok."""
    if not text:
        return ""
    cleaned = _CONTROL_CHARS.sub("", text)
    cleaned = cleaned.strip()
    if len(cleaned) > max_len:
        cleaned = cleaned[:max_len] + "…"
    return cleaned


def sanitize_webhook_name(name: str) -> str:
    """Discord webhook display names must be 1–80 chars."""
    if not name:
        return "xGalactic"
    cleaned = _CONTROL_CHARS.sub("", name.strip())
    return cleaned[:MAX_WEBHOOK_NAME] or "xGalactic"


def is_valid_snowflake(value: str) -> bool:
    """Basic Discord snowflake validation."""
    try:
        n = int(value)
        return 17 <= len(str(n)) <= 20 and n > 0
    except (TypeError, ValueError):
        return False

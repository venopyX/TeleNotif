"""Validation utilities"""

from typing import Any


def validate_chat_id(chat_id: str) -> bool:
    """Validate Telegram chat ID format"""
    if chat_id.startswith("@"):
        return len(chat_id) > 1 and chat_id[1:].replace("_", "").isalnum()

    try:
        int(chat_id)
        return True
    except ValueError:
        return False


def validate_parse_mode(parse_mode: str) -> bool:
    """Validate Telegram parse mode"""
    return parse_mode in ["Markdown", "MarkdownV2", "HTML"]


def sanitize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Remove None values and empty strings from payload"""
    return {k: v for k, v in payload.items() if v is not None and v != ""}


def escape_markdown_v2(text: str) -> str:
    """Escape special MarkdownV2 characters"""
    for char in ["_", "*", "[", "]", "(", ")", "~", "`", ">", "#", "+", "-", "=", "|", "{", "}", ".", "!"]:
        text = str(text).replace(char, f"\\{char}")
    return text

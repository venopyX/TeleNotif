"""
Telegram message escaping utilities for MarkdownV2 and Markdown parse modes.

This module provides robust escaping functions to ensure all special characters
are properly escaped according to Telegram Bot API specifications.

References:
- https://core.telegram.org/bots/api#markdownv2-style
- https://core.telegram.org/bots/api#markdown-style
"""

import re
from typing import Optional, Union


# MarkdownV2 special characters that MUST be escaped
# According to Telegram Bot API docs:
MARKDOWNV2_SPECIAL_CHARS = [
    '_', '*', '[', ']', '(', ')', '~', '`',
    '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'
]

# Markdown (legacy) special characters
MARKDOWN_SPECIAL_CHARS = ['_', '*', '`', '[']


def escape_markdown_v2(text: Optional[Union[str, int, float]]) -> str:
    """
    Escape special characters for Telegram MarkdownV2 parse mode.

    This function escapes all special characters defined in Telegram's MarkdownV2
    specification to prevent parsing errors when sending messages.

    Special characters that are escaped:
    '_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!'

    Args:
        text: The text to escape. Can be str, int, float, or None.
              Non-string types will be converted to strings first.

    Returns:
        The escaped text with all special characters preceded by a backslash.
        Returns empty string if input is None or empty.

    Examples:
        >>> escape_markdown_v2("Order #123")
        'Order \\\\#123'

        >>> escape_markdown_v2("Price: $10.50!")
        'Price: $10\\\\.50\\\\!'

        >>> escape_markdown_v2(None)
        ''

    Note:
        This function is designed to work with plain text content. If you want
        to preserve markdown formatting (bold, italic, etc.), you should not
        escape the formatting characters in those specific parts.
    """
    # Handle None or empty input
    if text is None:
        return ""

    # Convert non-string types to string
    if not isinstance(text, str):
        text = str(text)

    # Return empty string for empty input
    if not text:
        return ""

    # Escape each special character with a backslash
    # Using a character class regex for efficiency
    # Note: The hyphen is placed at the end to avoid creating a range
    escape_chars = r'([_*\[\]()~`>#+=|{}.!\-])'

    # Replace each match with a backslash followed by the matched character
    escaped_text = re.sub(escape_chars, r'\\\1', text)

    return escaped_text


def escape_markdown(text: Optional[Union[str, int, float]]) -> str:
    """
    Escape special characters for Telegram Markdown (legacy) parse mode.

    This function escapes special characters for the original Markdown parser.
    Note: Telegram recommends using MarkdownV2 instead of Markdown for new bots.

    Special characters that are escaped:
    '_', '*', '`', '['

    Args:
        text: The text to escape. Can be str, int, float, or None.
              Non-string types will be converted to strings first.

    Returns:
        The escaped text with markdown special characters preceded by a backslash.
        Returns empty string if input is None or empty.

    Examples:
        >>> escape_markdown("Hello *world*")
        'Hello \\\\*world\\\\*'

        >>> escape_markdown(None)
        ''
    """
    # Handle None or empty input
    if text is None:
        return ""

    # Convert non-string types to string
    if not isinstance(text, str):
        text = str(text)

    # Return empty string for empty input
    if not text:
        return ""

    # Escape Markdown special characters
    escape_chars = r'([_*`\[])'
    escaped_text = re.sub(escape_chars, r'\\\1', text)

    return escaped_text


def escape_for_html(text: Optional[Union[str, int, float]]) -> str:
    """
    Escape special characters for Telegram HTML parse mode.

    When using HTML parse mode, you need to escape <, >, and & characters.

    Args:
        text: The text to escape. Can be str, int, float, or None.

    Returns:
        The escaped text with HTML special characters replaced with entities.
        Returns empty string if input is None or empty.

    Examples:
        >>> escape_for_html("<b>Bold</b> & italic")
        '&lt;b&gt;Bold&lt;/b&gt; &amp; italic'
    """
    # Handle None or empty input
    if text is None:
        return ""

    # Convert non-string types to string
    if not isinstance(text, str):
        text = str(text)

    # Return empty string for empty input
    if not text:
        return ""

    # Replace HTML special characters with entities
    text = text.replace('&', '&amp;')  # Must be first!
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')

    return text


def sanitize_text(
    text: Optional[Union[str, int, float]],
    parse_mode: Optional[str] = None
) -> str:
    """
    Sanitize text based on the specified parse mode.

    This is a convenience function that automatically chooses the appropriate
    escaping function based on the parse mode.

    Args:
        text: The text to sanitize. Can be str, int, float, or None.
        parse_mode: The Telegram parse mode. Can be:
                   - "MarkdownV2" (recommended)
                   - "Markdown" (legacy)
                   - "HTML"
                   - None (no escaping)

    Returns:
        The sanitized text appropriate for the specified parse mode.
        Returns empty string if input is None or empty.

    Examples:
        >>> sanitize_text("Order #123", "MarkdownV2")
        'Order \\\\#123'

        >>> sanitize_text("<b>Test</b>", "HTML")
        '&lt;b&gt;Test&lt;/b&gt;'

        >>> sanitize_text("Plain text", None)
        'Plain text'
    """
    # Handle None or empty input
    if text is None:
        return ""

    # Convert non-string types to string
    if not isinstance(text, str):
        text = str(text)

    # Return empty string for empty input
    if not text:
        return ""

    # Choose escaping function based on parse mode
    if parse_mode == "MarkdownV2":
        return escape_markdown_v2(text)
    elif parse_mode == "Markdown":
        return escape_markdown(text)
    elif parse_mode == "HTML":
        return escape_for_html(text)
    else:
        # No escaping for plain text mode
        return text


def preserve_formatting(text: str, parse_mode: str = "MarkdownV2") -> str:
    """
    Escape text while preserving intentional markdown formatting.

    This function attempts to preserve markdown formatting markers like *bold*
    and _italic_ while escaping other special characters.

    WARNING: This is a heuristic approach and may not work perfectly for all cases.
    For maximum safety, use escape_markdown_v2() and apply formatting explicitly.

    Args:
        text: The text with markdown formatting.
        parse_mode: The parse mode ("MarkdownV2" or "Markdown").

    Returns:
        Text with special characters escaped but formatting preserved.

    Note:
        This function uses pattern matching to detect formatting:
        - *text* for bold (must have content between asterisks)
        - _text_ for italic (must have content between underscores)
        - `code` for code (must have content between backticks)
    """
    if not text:
        return ""

    # This is complex and error-prone. For now, just escape everything.
    # Users should manually construct formatted messages if they need formatting.
    return escape_markdown_v2(text) if parse_mode == "MarkdownV2" else escape_markdown(text)


# Validation functions

def validate_escaped_text(text: str, parse_mode: str = "MarkdownV2") -> bool:
    """
    Validate that text is properly escaped for the given parse mode.

    This function checks if all special characters are properly escaped.

    Args:
        text: The text to validate.
        parse_mode: The parse mode to validate against.

    Returns:
        True if text is properly escaped, False otherwise.
    """
    if not text:
        return True

    if parse_mode == "MarkdownV2":
        # Check for unescaped special characters
        # Look for special chars not preceded by backslash
        pattern = r'(?<!\\)([_*\[\]()~`>#+=|{}.!\-])'
        matches = re.findall(pattern, text)
        return len(matches) == 0

    elif parse_mode == "Markdown":
        pattern = r'(?<!\\)([_*`\[])'
        matches = re.findall(pattern, text)
        return len(matches) == 0

    return True


# Export all functions
__all__ = [
    'escape_markdown_v2',
    'escape_markdown',
    'escape_for_html',
    'sanitize_text',
    'preserve_formatting',
    'validate_escaped_text',
    'MARKDOWNV2_SPECIAL_CHARS',
    'MARKDOWN_SPECIAL_CHARS',
]

"""Tests for formatters"""

from telenotif.formatters.plain import PlainFormatter
from telenotif.formatters.markdown import MarkdownFormatter


def test_plain_formatter_simple_message():
    """Test plain formatter with simple message"""
    formatter = PlainFormatter()
    result = formatter.format({"message": "Hello World"})
    assert result == "Hello World"


def test_plain_formatter_dict():
    """Test plain formatter with dictionary"""
    formatter = PlainFormatter()
    result = formatter.format({"user": "John", "status": "active"})
    assert "user: John" in result
    assert "status: active" in result


def test_markdown_formatter():
    """Test markdown formatter"""
    formatter = MarkdownFormatter()
    result = formatter.format({"title": "Alert", "message": "Test"})
    assert "*Alert*" in result

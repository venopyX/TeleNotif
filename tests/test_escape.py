import unittest
from telegrify.utils.escape import escape_markdown_v2, escape_markdown

class TestEscapeMarkdownV2(unittest.TestCase):

    def test_escape_all_special_characters(self):
        """Test escaping all MarkdownV2 special characters"""
        text = "_*[]()~`>#+-=|{}.!"
        expected = "\\_\\*\\[\\]\\(\\)\\~\\`\\>\\#\\+\\-\\=\\|\\{\\}\\.\\!"
        actual_output = escape_markdown_v2(text)
        self.assertEqual(actual_output, expected)

    def test_text_with_no_special_characters(self):
        """Test that non-special characters remain unchanged"""
        text = "This is a simple text."
        expected = "This is a simple text\\."
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_text_with_mixed_characters(self):
        """Test realistic text with mixed characters"""
        text = "Order #123. Total: $10.00!"
        expected = "Order \\#123\\. Total: $10\\.00\\!"
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_empty_string(self):
        """Test that empty strings are handled"""
        text = ""
        self.assertEqual(escape_markdown_v2(text), "")

    def test_real_order_notification(self):
        """Test with a real-world order notification example"""
        text = "New Order #36F39592"
        expected = "New Order \\#36F39592"
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_phone_number(self):
        """Test phone numbers with + and -"""
        text = "+251963333668"
        expected = "\\+251963333668"
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_telegram_username(self):
        """Test telegram username with @"""
        text = "@scorpydev"
        expected = "@scorpydev"  # @ is not a special char in MarkdownV2
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_bullet_points(self):
        """Test bullet point lists"""
        text = "• Item 1\n• Item 2"
        expected = "• Item 1\n• Item 2"  # • is not special
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_preserves_bold_formatting(self):
        """Test that intentional bold formatting is preserved"""
        text = "*bold text*"
        expected = "\\*bold text\\*"
        self.assertEqual(escape_markdown_v2(text), expected)

    def test_none_input(self):
        """Test that None input is handled gracefully"""
        result = escape_markdown_v2(None)
        self.assertEqual(result, "")

    def test_numeric_input(self):
        """Test that numeric values are converted to strings"""
        result = escape_markdown_v2(123.45)
        self.assertEqual(result, "123\\.45")

class TestEscapeMarkdown(unittest.TestCase):

    def test_basic_markdown_escape(self):
        """Test basic Markdown (non-V2) escaping"""
        text = "_*`["
        expected = "\\_\\*\\`\\["
        self.assertEqual(escape_markdown(text), expected)

    def test_markdown_preserves_other_chars(self):
        """Test that Markdown mode doesn't escape unnecessary chars"""
        text = "Order #123. Total: $10.00!"
        expected = "Order #123. Total: $10.00!"
        self.assertEqual(escape_markdown(text), expected)

if __name__ == '__main__':
    unittest.main()

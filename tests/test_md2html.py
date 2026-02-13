#!/usr/bin/env python3
"""Unit tests for Markdown to HTML converter."""

import unittest
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'markdown-to-html'))

from md2html import MarkdownParser


class TestMarkdownParser(unittest.TestCase):
    """Test cases for MarkdownParser."""
    
    def setUp(self):
        self.parser = MarkdownParser()
    
    # Headers
    def test_h1(self):
        html = self.parser.parse_string("# Heading 1")
        self.assertEqual(html, "<h1>Heading 1</h1>")
    
    def test_h6(self):
        html = self.parser.parse_string("###### Heading 6")
        self.assertEqual(html, "<h6>Heading 6</h6>")
    
    def test_h7_becomes_h6(self):
        html = self.parser.parse_string("####### Too many")
        self.assertEqual(html, "<h6>Too many</h6>")
    
    # Inline formatting
    def test_bold(self):
        html = self.parser.parse_string("**bold text**")
        self.assertEqual(html, "<p><strong>bold text</strong></p>")
    
    def test_bold_underscore(self):
        html = self.parser.parse_string("__bold text__")
        self.assertEqual(html, "<p><strong>bold text</strong></p>")
    
    def test_italic(self):
        html = self.parser.parse_string("*italic text*")
        self.assertEqual(html, "<p><em>italic text</em></p>")
    
    def test_italic_underscore(self):
        html = self.parser.parse_string("_italic text_")
        self.assertEqual(html, "<p><em>italic text</em></p>")
    
    def test_bold_and_italic(self):
        html = self.parser.parse_string("***bold italic***")
        self.assertEqual(html, "<p><strong><em>bold italic</em></strong></p>")
    
    def test_inline_code(self):
        html = self.parser.parse_string("`code()`")
        self.assertEqual(html, "<p><code>code()</code></p>")
    
    # Links and images
    def test_link(self):
        html = self.parser.parse_string("[link text](https://example.com)")
        self.assertEqual(html, '<p><a href="https://example.com">link text</a></p>')
    
    def test_image(self):
        html = self.parser.parse_string("![alt text](image.png)")
        self.assertEqual(html, '<p><img alt="alt text" src="image.png"></p>')
    
    # Lists
    def test_unordered_list(self):
        md = "- Item 1\n- Item 2"
        html = self.parser.parse_string(md)
        self.assertIn("<ul>", html)
        self.assertIn("<li>Item 1</li>", html)
        self.assertIn("<li>Item 2</li>", html)
        self.assertIn("</ul>", html)
    
    def test_ordered_list(self):
        md = "1. First\n2. Second"
        html = self.parser.parse_string(md)
        self.assertIn("<ol>", html)
        self.assertIn("<li>First</li>", html)
        self.assertIn("<li>Second</li>", html)
        self.assertIn("</ol>", html)
    
    # Blockquotes
    def test_blockquote(self):
        html = self.parser.parse_string("> Quote")
        self.assertEqual(html, "<blockquote>Quote</blockquote>")
    
    # Code blocks
    def test_code_block(self):
        md = "```python\nprint('hi')\n```"
        html = self.parser.parse_string(md)
        self.assertIn("<pre>", html)
        self.assertIn("<code", html)
        self.assertIn("print('hi')", html)
        self.assertIn("</pre>", html)
    
    # Horizontal rule
    def test_horizontal_rule(self):
        html = self.parser.parse_string("---")
        self.assertEqual(html, "<hr>")
    
    # HTML escaping
    def test_html_escaping(self):
        html = self.parser.parse_string("<script>alert('xss')</script>")
        self.assertIn("&lt;script&gt;", html)
        self.assertNotIn("<script>", html)
    
    # Mixed content
    def test_mixed_content(self):
        md = """# Title

This is **bold** and *italic*.

- List item
- Another item
"""
        html = self.parser.parse_string(md)
        self.assertIn("<h1>Title</h1>", html)
        self.assertIn("<strong>bold</strong>", html)
        self.assertIn("<em>italic</em>", html)
        self.assertIn("<ul>", html)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""
    
    def setUp(self):
        self.parser = MarkdownParser()
    
    def test_empty_string(self):
        html = self.parser.parse_string("")
        self.assertEqual(html, "")
    
    def test_only_whitespace(self):
        html = self.parser.parse_string("   \n   \n   ")
        self.assertEqual(html, "")
    
    def test_multiple_empty_lines(self):
        html = self.parser.parse_string("Hello\n\n\nWorld")
        self.assertIn("<p>Hello</p>", html)
        self.assertIn("<p>World</p>", html)


if __name__ == '__main__':
    unittest.main()

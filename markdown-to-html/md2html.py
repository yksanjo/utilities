#!/usr/bin/env python3
"""
Markdown to HTML Converter
A simple parser that converts basic Markdown syntax to HTML.

Supported syntax:
- Headers (# ## ###)
- Bold (**text** or __text__)
- Italic (*text* or _text_)
- Bold+Italic (***text*** or ___text___)
- Links [text](url)
- Images ![alt](url)
- Unordered lists (- or *)
- Ordered lists (1. 2.)
- Inline code (`code`)
- Code blocks (```code```)
- Blockquotes (>)
- Horizontal rules (--- or ***)
"""

import re
import sys
from pathlib import Path


class MarkdownParser:
    """Simple Markdown to HTML parser."""
    
    def __init__(self):
        self.lines = []
        self.html_lines = []
        self.in_code_block = False
        self.code_block_content = []
        self.code_block_lang = ""
        self.in_list = False
        self.list_type = None  # 'ul' or 'ol'
        self.list_items = []
        
    def parse_file(self, filepath):
        """Parse a markdown file and return HTML."""
        path = Path(filepath)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        
        self.lines = path.read_text().split('\n')
        return self._parse_lines()
    
    def parse_string(self, markdown_text):
        """Parse a markdown string and return HTML."""
        self.lines = markdown_text.split('\n')
        return self._parse_lines()
    
    def _parse_lines(self):
        """Parse all lines and generate HTML."""
        self.html_lines = []
        self.in_code_block = False
        self.code_block_content = []
        self.code_block_lang = ""
        self.in_list = False
        self.list_type = None
        self.list_items = []
        
        for line in self.lines:
            self._process_line(line)
        
        # Close any open blocks
        self._close_code_block()
        self._close_list()
        
        return '\n'.join(self.html_lines)
    
    def _process_line(self, line):
        """Process a single line of markdown."""
        stripped = line.strip()
        
        # Handle code blocks
        if stripped.startswith('```'):
            if self.in_code_block:
                self._close_code_block()
            else:
                self._close_list()
                self.in_code_block = True
                self.code_block_lang = stripped[3:].strip()
            return
        
        if self.in_code_block:
            self.code_block_content.append(line)
            return
        
        # Handle horizontal rules
        if stripped in ('---', '***', '___'):
            self._close_list()
            self.html_lines.append('<hr>')
            return
        
        # Handle empty lines
        if not stripped:
            self._close_list()
            return
        
        # Handle headers
        if stripped.startswith('#'):
            self._close_list()
            html = self._parse_header(stripped)
            self.html_lines.append(html)
            return
        
        # Handle blockquotes
        if stripped.startswith('>'):
            self._close_list()
            html = self._parse_blockquote(stripped)
            self.html_lines.append(html)
            return
        
        # Handle list items
        list_match = self._match_list_item(stripped)
        if list_match:
            list_type, content = list_match
            if not self.in_list:
                self.in_list = True
                self.list_type = list_type
                self.list_items = []
            elif self.list_type != list_type:
                self._close_list()
                self.in_list = True
                self.list_type = list_type
            
            content = self._parse_inline(content)
            self.list_items.append(f'<li>{content}</li>')
            return
        else:
            self._close_list()
        
        # Handle regular paragraphs
        html = self._parse_inline(stripped)
        self.html_lines.append(f'<p>{html}</p>')
    
    def _parse_header(self, line):
        """Parse header syntax."""
        level = 0
        for char in line:
            if char == '#':
                level += 1
            else:
                break
        
        if level > 6:
            level = 6
        
        content = line[level:].strip()
        content = self._parse_inline(content)
        return f'<h{level}>{content}</h{level}>'
    
    def _parse_blockquote(self, line):
        """Parse blockquote syntax."""
        content = line[1:].strip()
        content = self._parse_inline(content)
        return f'<blockquote>{content}</blockquote>'
    
    def _match_list_item(self, line):
        """Check if line is a list item and return (type, content)."""
        # Unordered list
        if line.startswith('- ') or line.startswith('* '):
            return ('ul', line[2:])
        # Ordered list
        match = re.match(r'^(\d+)\.\s+(.+)$', line)
        if match:
            return ('ol', match.group(2))
        return None
    
    def _close_list(self):
        """Close any open list."""
        if self.in_list and self.list_items:
            items = '\n'.join(self.list_items)
            self.html_lines.append(f'<{self.list_type}>')
            self.html_lines.append(items)
            self.html_lines.append(f'</{self.list_type}>')
            self.in_list = False
            self.list_type = None
            self.list_items = []
    
    def _close_code_block(self):
        """Close any open code block."""
        if self.in_code_block:
            content = '\n'.join(self.code_block_content)
            # Escape HTML entities
            content = content.replace('&', '&amp;')
            content = content.replace('<', '&lt;')
            content = content.replace('>', '&gt;')
            
            lang_attr = f' class="language-{self.code_block_lang}"' if self.code_block_lang else ''
            self.html_lines.append(f'<pre><code{lang_attr}>{content}</code></pre>')
            
            self.in_code_block = False
            self.code_block_content = []
            self.code_block_lang = ""
    
    def _parse_inline(self, text):
        """Parse inline formatting (bold, italic, links, code)."""
        # Escape HTML entities first
        text = text.replace('&', '&amp;')
        text = text.replace('<', '&lt;')
        text = text.replace('>', '&gt;')
        
        # Code spans (must be first to avoid processing content inside)
        text = re.sub(r'`([^`]+)`', r'<code>\1</code>', text)
        
        # Images ![alt](url)
        text = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'<img alt="\1" src="\2">', text)
        
        # Links [text](url)
        text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
        
        # Bold + Italic
        text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'<strong><em>\1</em></strong>', text)
        text = re.sub(r'___([^_]+)___', r'<strong><em>\1</em></strong>', text)
        
        # Bold
        text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
        text = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', text)
        
        # Italic
        text = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', text)
        text = re.sub(r'_([^_]+)_', r'<em>\1</em>', text)
        
        return text


def convert_file(input_path, output_path=None):
    """Convert a markdown file to HTML."""
    parser = MarkdownParser()
    html = parser.parse_file(input_path)
    
    # Wrap in HTML document
    full_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Converted Markdown</title>
    <style>
        body {{
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        pre {{
            background: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }}
        code {{
            background: #f4f4f4;
            padding: 2px 5px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', monospace;
        }}
        blockquote {{
            border-left: 4px solid #ddd;
            margin: 0;
            padding-left: 20px;
            color: #666;
        }}
        img {{
            max-width: 100%;
        }}
    </style>
</head>
<body>
{html}
</body>
</html>'''
    
    if output_path:
        Path(output_path).write_text(full_html)
        print(f"Converted: {input_path} -> {output_path}")
    else:
        # Default output path
        input_path = Path(input_path)
        default_output = input_path.with_suffix('.html')
        default_output.write_text(full_html)
        print(f"Converted: {input_path} -> {default_output}")
    
    return full_html


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python md2html.py <input.md> [output.html]")
        print("\nExample:")
        print("  python md2html.py README.md")
        print("  python md2html.py README.md output.html")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        convert_file(input_file, output_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()

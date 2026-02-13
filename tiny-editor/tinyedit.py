#!/usr/bin/env python3
"""
TinyEdit - A terminal-based text editor

Features:
- Basic text editing
- Cursor movement (arrow keys)
- File open/save
- Simple buffer management
- Status bar showing position and filename

Controls:
- Ctrl+S: Save file
- Ctrl+Q: Quit
- Ctrl+N: New file
- Arrow keys: Move cursor
- Home: Beginning of line
- End: End of line
- Page Up/Down: Scroll
- Delete/Backspace: Delete characters

This demonstrates:
- Terminal control (raw mode)
- Buffer management
- Cursor positioning
- Screen redrawing
"""

import sys
import os
import re
import termios
import tty
import fcntl
import struct


class EditorBuffer:
    """Manages the text buffer."""
    
    def __init__(self):
        self.lines = ['']
        self.filename = None
        self.modified = False
    
    def load(self, filename):
        """Load file into buffer."""
        try:
            with open(filename, 'r') as f:
                content = f.read()
                self.lines = content.split('\n') if content else ['']
                if not self.lines:
                    self.lines = ['']
            self.filename = filename
            self.modified = False
            return True
        except FileNotFoundError:
            self.lines = ['']
            self.filename = filename
            return True
        except Exception as e:
            return False
    
    def save(self):
        """Save buffer to file."""
        if not self.filename:
            return False
        try:
            with open(self.filename, 'w') as f:
                f.write('\n'.join(self.lines))
            self.modified = False
            return True
        except Exception as e:
            return False
    
    def insert_char(self, row, col, char):
        """Insert a character at position."""
        if row >= len(self.lines):
            return
        line = self.lines[row]
        if col > len(line):
            col = len(line)
        self.lines[row] = line[:col] + char + line[col:]
        self.modified = True
    
    def delete_char(self, row, col):
        """Delete character at position."""
        if row >= len(self.lines):
            return False
        line = self.lines[row]
        if col < len(line):
            # Delete character at cursor
            self.lines[row] = line[:col] + line[col+1:]
            self.modified = True
            return True
        elif col >= len(line) and row < len(self.lines) - 1:
            # Join with next line
            self.lines[row] = line + self.lines[row + 1]
            del self.lines[row + 1]
            self.modified = True
            return True
        return False
    
    def backspace(self, row, col):
        """Handle backspace key."""
        if col > 0:
            # Delete character before cursor
            line = self.lines[row]
            self.lines[row] = line[:col-1] + line[col:]
            self.modified = True
            return row, col - 1
        elif row > 0:
            # Join with previous line
            prev_len = len(self.lines[row - 1])
            self.lines[row - 1] += self.lines[row]
            del self.lines[row]
            self.modified = True
            return row - 1, prev_len
        return row, col
    
    def insert_line(self, row, col):
        """Split line at cursor (Enter key)."""
        if row >= len(self.lines):
            self.lines.append('')
        else:
            line = self.lines[row]
            self.lines[row] = line[:col]
            self.lines.insert(row + 1, line[col:])
        self.modified = True
        return row + 1, 0
    
    def get_line(self, row):
        """Get line at row."""
        if 0 <= row < len(self.lines):
            return self.lines[row]
        return ''
    
    def get_line_count(self):
        """Get total number of lines."""
        return len(self.lines)


class Terminal:
    """Terminal control utilities."""
    
    @staticmethod
    def get_size():
        """Get terminal size."""
        try:
            import shutil
            return shutil.get_terminal_size()
        except:
            return os.terminal_size((80, 24))
    
    @staticmethod
    def clear():
        """Clear screen."""
        sys.stdout.write('\033[2J')
        sys.stdout.write('\033[H')
    
    @staticmethod
    def move_cursor(row, col):
        """Move cursor to position (1-based)."""
        sys.stdout.write(f'\033[{row};{col}H')
    
    @staticmethod
    def hide_cursor():
        """Hide cursor."""
        sys.stdout.write('\033[?25l')
    
    @staticmethod
    def show_cursor():
        """Show cursor."""
        sys.stdout.write('\033[?25h')
    
    @staticmethod
    def set_raw_mode():
        """Set terminal to raw mode."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        tty.setraw(fd)
        return old_settings
    
    @staticmethod
    def restore_mode(old_settings):
        """Restore terminal settings."""
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)


class SyntaxHighlighter:
    """Simple syntax highlighting for common languages."""
    
    # Color codes
    RESET = '\033[0m'
    KEYWORD = '\033[35m'      # Magenta
    STRING = '\033[32m'       # Green
    COMMENT = '\033[90m'      # Gray
    NUMBER = '\033[33m'       # Yellow
    FUNCTION = '\033[36m'     # Cyan
    
    # Python keywords
    PYTHON_KEYWORDS = {
        'def', 'class', 'if', 'elif', 'else', 'for', 'while', 'return',
        'import', 'from', 'as', 'try', 'except', 'finally', 'with',
        'lambda', 'yield', 'raise', 'break', 'continue', 'pass',
        'True', 'False', 'None', 'and', 'or', 'not', 'in', 'is',
        'async', 'await', 'nonlocal', 'global', 'assert', 'del'
    }
    
    # JavaScript keywords
    JS_KEYWORDS = {
        'function', 'var', 'let', 'const', 'if', 'else', 'for', 'while',
        'return', 'class', 'extends', 'super', 'this', 'new', 'try',
        'catch', 'finally', 'throw', 'switch', 'case', 'default',
        'break', 'continue', 'true', 'false', 'null', 'undefined',
        'async', 'await', 'import', 'export', 'from', 'typeof', 'in',
        'instanceof', 'of', 'yield', 'debugger'
    }
    
    # C/C++/Java keywords
    C_KEYWORDS = {
        'int', 'float', 'double', 'char', 'void', 'if', 'else', 'for',
        'while', 'do', 'return', 'break', 'continue', 'switch', 'case',
        'default', 'struct', 'typedef', 'static', 'extern', 'const',
        'sizeof', 'goto', 'union', 'enum', 'inline', 'volatile'
    }
    
    def __init__(self, filename=None):
        self.filename = filename
        self.keywords = set()
        self.is_comment = self._get_comment_func(filename)
        self._detect_language(filename)
    
    def _detect_language(self, filename):
        """Detect language from filename."""
        if not filename:
            return
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if ext in ('py', 'pyw'):
            self.keywords = self.PYTHON_KEYWORDS
        elif ext in ('js', 'jsx', 'ts', 'tsx'):
            self.keywords = self.JS_KEYWORDS
        elif ext in ('c', 'cpp', 'cc', 'cxx', 'h', 'hpp', 'java'):
            self.keywords = self.C_KEYWORDS
    
    def _get_comment_func(self, filename):
        """Get comment detection function based on language."""
        if not filename:
            return lambda line: (False, line)
        
        ext = filename.lower().split('.')[-1] if '.' in filename else ''
        
        if ext in ('py', 'pyw', 'sh', 'rb', 'yaml', 'yml'):
            # Hash comments
            return lambda line: (line.strip().startswith('#'), line)
        elif ext in ('js', 'jsx', 'ts', 'tsx', 'c', 'cpp', 'java'):
            # C-style comments (simplified)
            return lambda line: (line.strip().startswith('//'), line)
        else:
            return lambda line: (False, line)
    
    def highlight(self, line):
        """Apply syntax highlighting to a line."""
        if not self.keywords:
            return line
        
        import re
        result = []
        i = 0
        
        # Check for comment
        stripped = line.lstrip()
        is_comment = False
        if stripped.startswith('#') or stripped.startswith('//'):
            return self.COMMENT + line + self.RESET
        
        while i < len(line):
            # Try to match string literals
            if line[i] in ('"', "'"):
                quote = line[i]
                j = i + 1
                while j < len(line) and line[j] != quote:
                    if line[j] == '\\' and j + 1 < len(line):
                        j += 2
                    else:
                        j += 1
                if j < len(line):
                    j += 1
                result.append(self.STRING + line[i:j] + self.RESET)
                i = j
                continue
            
            # Try to match numbers
            if line[i].isdigit():
                j = i
                while j < len(line) and (line[j].isdigit() or line[j] == '.'):
                    j += 1
                result.append(self.NUMBER + line[i:j] + self.RESET)
                i = j
                continue
            
            # Try to match keywords and identifiers
            if line[i].isalpha() or line[i] == '_':
                j = i
                while j < len(line) and (line[j].isalnum() or line[j] == '_'):
                    j += 1
                word = line[i:j]
                if word in self.keywords:
                    result.append(self.KEYWORD + word + self.RESET)
                else:
                    result.append(word)
                i = j
                continue
            
            # Try to match function calls (identifier followed by '(')
            if line[i] == '(' and result:
                # Check if previous token is an identifier
                prev = result[-1]
                if prev and prev[0].isalpha():
                    # Extract any ANSI codes and the word
                    plain = re.sub(r'\033\[[0-9;]*m', '', prev)
                    if plain and plain[0].isalpha() and plain not in self.keywords:
                        result[-1] = self.FUNCTION + prev + self.RESET
            
            result.append(line[i])
            i += 1
        
        return ''.join(result)


class Editor:
    """Main editor class."""
    
    def __init__(self):
        self.buffer = EditorBuffer()
        self.cursor_row = 0
        self.cursor_col = 0
        self.scroll_row = 0
        self.scroll_col = 0
        self.term_rows = 24
        self.term_cols = 80
        self.message = ""
        self.message_time = 0
        self.running = True
        self.highlighter = None
    
    def open_file(self, filename):
        """Open a file."""
        if filename:
            if self.buffer.load(filename):
                self.message = f"Opened: {filename}"
                self.highlighter = SyntaxHighlighter(filename)
            else:
                self.message = f"Error opening: {filename}"
        else:
            self.buffer.filename = None
            self.message = "New file"
            self.highlighter = None
    
    def save_file(self):
        """Save current file."""
        if not self.buffer.filename:
            # For simplicity, use a default name
            self.buffer.filename = "untitled.txt"
        if self.buffer.save():
            self.message = f"Saved: {self.buffer.filename}"
        else:
            self.message = "Error saving file"
    
    def get_status_bar(self):
        """Generate status bar text."""
        filename = self.buffer.filename or "[No Name]"
        modified = "[+]" if self.buffer.modified else ""
        pos = f"{self.cursor_row + 1}:{self.cursor_col + 1}"
        
        left = f" {filename} {modified}"
        right = f"{pos} "
        
        padding = self.term_cols - len(left) - len(right)
        if padding < 0:
            padding = 0
        
        return left + " " * padding + right
    
    def draw(self):
        """Draw the editor screen."""
        Terminal.clear()
        
        # Get terminal size
        size = Terminal.get_size()
        self.term_rows = size.lines
        self.term_cols = size.columns
        
        # Calculate visible area (reserve 2 lines for status)
        visible_rows = self.term_rows - 2
        visible_cols = self.term_cols
        
        # Adjust scroll to keep cursor visible
        if self.cursor_row < self.scroll_row:
            self.scroll_row = self.cursor_row
        elif self.cursor_row >= self.scroll_row + visible_rows:
            self.scroll_row = self.cursor_row - visible_rows + 1
        
        if self.cursor_col < self.scroll_col:
            self.scroll_col = self.cursor_col
        elif self.cursor_col >= self.scroll_col + visible_cols:
            self.scroll_col = self.cursor_col - visible_cols + 1
        
        # Draw visible lines
        for i in range(visible_rows):
            row = self.scroll_row + i
            Terminal.move_cursor(i + 1, 1)
            
            if row < self.buffer.get_line_count():
                line = self.buffer.get_line(row)
                # Show portion of line based on horizontal scroll
                visible = line[self.scroll_col:self.scroll_col + visible_cols]
                # Apply syntax highlighting
                if self.highlighter:
                    visible = self.highlighter.highlight(visible)
                sys.stdout.write(visible)
        
        # Draw status bar
        status = self.get_status_bar()
        Terminal.move_cursor(self.term_rows - 1, 1)
        sys.stdout.write('\033[7m')  # Reverse video
        sys.stdout.write(status[:self.term_cols].ljust(self.term_cols))
        sys.stdout.write('\033[0m')  # Normal video
        
        # Draw message line
        Terminal.move_cursor(self.term_rows, 1)
        if self.message:
            sys.stdout.write(self.message[:self.term_cols])
        
        # Position cursor
        screen_row = self.cursor_row - self.scroll_row + 1
        screen_col = self.cursor_col - self.scroll_col + 1
        Terminal.move_cursor(screen_row, screen_col)
        
        sys.stdout.flush()
    
    def move_cursor(self, delta_row, delta_col):
        """Move cursor by delta."""
        new_row = self.cursor_row + delta_row
        new_col = self.cursor_col + delta_col
        
        # Clamp row
        if new_row < 0:
            new_row = 0
        if new_row >= self.buffer.get_line_count():
            new_row = self.buffer.get_line_count() - 1
        
        # Clamp col to line length
        line_len = len(self.buffer.get_line(new_row))
        if new_col > line_len:
            new_col = line_len
        if new_col < 0:
            new_col = 0
        
        self.cursor_row = new_row
        self.cursor_col = new_col
    
    def handle_key(self, key):
        """Handle a key press."""
        # Ctrl+Q = Quit
        if key == '\x11':
            if self.buffer.modified:
                self.message = "Unsaved changes! Ctrl+Q again to quit"
                self.buffer.modified = False  # Hack: toggle to detect second press
            else:
                self.running = False
            return
        
        # Ctrl+S = Save
        if key == '\x13':
            self.save_file()
            return
        
        # Ctrl+N = New
        if key == '\x0e':
            self.buffer = EditorBuffer()
            self.cursor_row = 0
            self.cursor_col = 0
            self.scroll_row = 0
            self.scroll_col = 0
            self.message = "New file"
            return
        
        # Arrow keys (escape sequences)
        if key.startswith('\x1b['):
            seq = key[2:]
            if seq == 'A':  # Up
                self.move_cursor(-1, 0)
            elif seq == 'B':  # Down
                self.move_cursor(1, 0)
            elif seq == 'C':  # Right
                self.move_cursor(0, 1)
            elif seq == 'D':  # Left
                self.move_cursor(0, -1)
            elif seq == 'H':  # Home
                self.cursor_col = 0
            elif seq == 'F':  # End
                self.cursor_col = len(self.buffer.get_line(self.cursor_row))
            elif seq == '5~':  # Page Up
                self.move_cursor(-(self.term_rows - 2), 0)
            elif seq == '6~':  # Page Down
                self.move_cursor(self.term_rows - 2, 0)
            elif seq == '3~':  # Delete
                self.buffer.delete_char(self.cursor_row, self.cursor_col)
            return
        
        # Backspace
        if key in ('\x7f', '\x08'):
            if self.cursor_row > 0 or self.cursor_col > 0:
                self.cursor_row, self.cursor_col = self.buffer.backspace(
                    self.cursor_row, self.cursor_col
                )
            return
        
        # Enter
        if key in ('\r', '\n'):
            self.cursor_row, self.cursor_col = self.buffer.insert_line(
                self.cursor_row, self.cursor_col
            )
            return
        
        # Tab
        if key == '\t':
            self.buffer.insert_char(self.cursor_row, self.cursor_col, ' ' * 4)
            self.cursor_col += 4
            return
        
        # Printable characters
        if len(key) == 1 and 32 <= ord(key) <= 126:
            self.buffer.insert_char(self.cursor_row, self.cursor_col, key)
            self.cursor_col += 1
    
    def read_key(self):
        """Read a key from stdin."""
        key = sys.stdin.read(1)
        
        # Handle escape sequences
        if key == '\x1b':
            # Read more characters for escape sequence
            seq = sys.stdin.read(1)
            if seq == '[':
                # CSI sequence - read until we get a letter or ~
                seq2 = ''
                while True:
                    ch = sys.stdin.read(1)
                    seq2 += ch
                    if ch.isalpha() or ch == '~':
                        break
                return '\x1b[' + seq2
            else:
                return '\x1b' + seq
        
        return key
    
    def run(self):
        """Main editor loop."""
        old_settings = Terminal.set_raw_mode()
        Terminal.hide_cursor()
        
        try:
            while self.running:
                self.draw()
                key = self.read_key()
                self.handle_key(key)
        finally:
            Terminal.show_cursor()
            Terminal.restore_mode(old_settings)
            Terminal.clear()
            print("TinyEdit - Goodbye!")


def main():
    """Main entry point."""
    filename = sys.argv[1] if len(sys.argv) > 1 else None
    
    editor = Editor()
    editor.open_file(filename)
    editor.run()


if __name__ == '__main__':
    main()

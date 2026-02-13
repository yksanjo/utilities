# TinyEdit

A terminal-based text editor demonstrating buffers and terminal control.

## Features

- **Basic editing**: Insert, delete, backspace characters
- **Cursor movement**: Arrow keys, Home, End, Page Up/Down
- **File operations**: Open, Save, New file
- **Buffer management**: In-memory text storage
- **Viewport scrolling**: Handle files larger than screen
- **Syntax highlighting**: Python, JavaScript, C/C++/Java support

## Usage

```bash
# Open a file
python tinyedit.py filename.txt

# Start with new file
python tinyedit.py
```

## Controls

| Key | Action |
|-----|--------|
| Ctrl+S | Save file |
| Ctrl+Q | Quit (press twice if unsaved) |
| Ctrl+N | New file |
| ↑↓←→ | Move cursor |
| Home | Beginning of line |
| End | End of line |
| PgUp/PgDn | Scroll up/down |
| Delete | Delete character at cursor |
| Backspace | Delete character before cursor |
| Enter | Insert new line |
| Tab | Insert 4 spaces |

## Architecture

### Buffer (`EditorBuffer`)
- Stores text as a list of strings (lines)
- Handles insertions, deletions, and line splits
- Tracks modification status

### Terminal (`Terminal`)
- Manages terminal raw mode
- Handles screen clearing and cursor positioning
- Gets terminal dimensions

### Editor (`Editor`)
- Coordinates buffer and display
- Handles keyboard input
- Manages viewport scrolling
- Renders status bar

## How It Works

1. **Raw Mode**: Terminal is put in raw mode to receive individual keystrokes
2. **Event Loop**: Read key → Update buffer → Redraw screen
3. **Double Buffering**: The screen is cleared and redrawn on each change
4. **Viewport**: Only visible portion of file is rendered
5. **Scrolling**: Scroll position adjusts to keep cursor visible

## Supported Languages for Syntax Highlighting

- **Python** (.py): Keywords, strings, comments, numbers, functions
- **JavaScript/TypeScript** (.js, .jsx, .ts, .tsx)
- **C/C++** (.c, .cpp, .h, .hpp)
- **Java** (.java)

## Limitations

- No search/replace
- No undo/redo
- Fixed tab width (4 spaces)
- No line wrapping

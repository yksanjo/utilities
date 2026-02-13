# Utilities Collection

Three simple utilities built from scratch to understand core concepts.

## Quick Commands

```bash
make test     # Run all unit tests
make demo     # Run demos of all utilities
make clean    # Clean generated files
make install  # Install dependencies (pytest)
```

---

## 1. Markdown to HTML Converter

A simple parser demonstrating text parsing and transformation.

```bash
cd markdown-to-html
python md2html.py example.md
```

**Concepts**: Tokenization, recursive descent parsing, HTML generation

**Features**:
- Headers (# ## ###)
- Bold, italic, combined formatting
- Links and images
- Unordered and ordered lists
- Code blocks and inline code
- Blockquotes
- Horizontal rules
- HTML escaping

---

## 2. Mini-Git

A simplified Git clone demonstrating version control internals.

```bash
cd mini-git
python minigit.py init
python minigit.py add file.txt
python minigit.py commit -m "Initial commit"
python minigit.py log
python minigit.py diff      # Show changes
```

**Concepts**: Content-addressable storage, DAG of commits, staging area

**Features**:
- `init`: Initialize repository
- `add`: Stage files
- `commit`: Create commits with parent pointers
- `log`: View commit history
- `diff`: Show file differences with color output
- `status`: Check repository status

---

## 3. TinyEdit

A terminal-based text editor demonstrating buffers and terminal control.

```bash
cd tiny-editor
python tinyedit.py [filename]
```

**Concepts**: Terminal raw mode, buffer management, screen redrawing, syntax highlighting

**Features**:
- Full terminal control (raw mode)
- Cursor movement (arrows, Home, End, PgUp, PgDn)
- File open/save
- **Syntax highlighting** for Python, JavaScript, C/C++, Java
- Scrollable viewport
- Status bar

| Key | Action |
|-----|--------|
| Ctrl+S | Save |
| Ctrl+Q | Quit |
| Ctrl+N | New file |

---

## File Structure

```
utilities/
├── README.md
├── Makefile                  # Easy commands
├── .github/workflows/ci.yml  # GitHub Actions CI
├── tests/
│   ├── test_md2html.py       # Unit tests
│   └── test_minigit.py
├── markdown-to-html/
│   ├── md2html.py
│   └── example.md
├── mini-git/
│   ├── minigit.py
│   └── README.md
└── tiny-editor/
    ├── tinyedit.py
    └── README.md
```

---

## CI/CD

This repository uses GitHub Actions to automatically:
- Run unit tests on Python 3.8-3.12
- Test the markdown converter
- Test mini-git operations

See `.github/workflows/ci.yml`

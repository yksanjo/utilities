# Utilities Collection

Three simple utilities built from scratch to understand core concepts.

## 1. Markdown to HTML Converter

A simple parser demonstrating text parsing and transformation.

```bash
cd markdown-to-html
python md2html.py example.md
```

**Concepts**: Tokenization, recursive descent parsing, HTML generation

---

## 2. Mini-Git

A simplified Git clone demonstrating version control internals.

```bash
cd mini-git
python minigit.py init
python minigit.py add file.txt
python minigit.py commit -m "Initial commit"
python minigit.py log
```

**Concepts**: Content-addressable storage, DAG of commits, staging area

---

## 3. TinyEdit

A terminal-based text editor demonstrating buffers and terminal control.

```bash
cd tiny-editor
python tinyedit.py
```

**Concepts**: Terminal raw mode, buffer management, screen redrawing

---

## Quick Test

Run all examples:

```bash
# Markdown converter
cd markdown-to-html
python md2html.py example.md

# Mini-git demo
cd ../mini-git
mkdir -p /tmp/minigit-test && cd /tmp/minigit-test
python ~/utilities/mini-git/minigit.py init
echo "Hello" > test.txt
python ~/utilities/mini-git/minigit.py add test.txt
python ~/utilities/mini-git/minigit.py commit -m "Test"
python ~/utilities/mini-git/minigit.py log
```

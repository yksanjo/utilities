# Mini-Git

A simplified Git clone to understand version control internals.

## Concepts Demonstrated

- **Content-addressable storage**: Files are stored by their SHA-1 hash
- **Staging area (index)**: Files are staged before committing
- **Commit objects**: Contain tree SHA, parent SHA, author, timestamp, message
- **Tree objects**: Represent directory structure
- **Parent pointers**: Form a linked list of commits

## Usage

```bash
# Initialize a repository
python minigit.py init

# Stage files
python minigit.py add file.txt

# Commit changes
python minigit.py commit -m "Initial commit"

# View history
python minigit.py log

# Show differences
python minigit.py diff          # Show all changes
python minigit.py diff file.txt # Show changes to specific file

# Check status
python minigit.py status
```

## How It Works

### Object Storage

Objects are stored in `.minigit/objects/XX/YYYY...` where `XX` is the first 2 characters
of the SHA-1 hash and `YYYY...` is the rest.

Types of objects:
- **blob**: File content
- **tree**: Directory listing (mode, type, SHA, filename)
- **commit**: Commit metadata (tree, parent, author, message)

### The Index (Staging Area)

The `.minigit/index` file is a JSON file mapping filenames to blob SHAs.

### HEAD

`.minigit/HEAD` contains a reference like `ref: refs/heads/master`,
which points to the current branch file containing the latest commit SHA.

## Example Session

```bash
$ python minigit.py init
Initialized empty Mini-Git repository in /path/to/project/.minigit

$ echo "Hello World" > hello.txt
$ python minigit.py add hello.txt
Added: hello.txt

$ python minigit.py commit -m "First commit"
[a1b2c3d] First commit

$ python minigit.py log
commit a1b2c3d...
Author: User <user@example.com>
Date:   2024-01-15 10:30:00

    First commit
```

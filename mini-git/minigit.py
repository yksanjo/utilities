#!/usr/bin/env python3
"""
Mini-Git: A simplified Git clone to understand version control internals.

Implements:
- init: Initialize a new repository
- add: Stage files for commit
- commit: Create a snapshot of staged files
- log: View commit history
- status: Check repository status

This demonstrates core Git concepts:
- Content-addressable storage (SHA-1 hashing)
- Staging area (index)
- Commit objects with parent pointers
- Tree objects for directory structure
"""

import hashlib
import json
import os
import sys
import time
from pathlib import Path
from datetime import datetime


class MiniGit:
    """A simplified Git implementation."""
    
    def __init__(self, path='.'):
        self.repo_path = Path(path).resolve()
        self.minigit_dir = self.repo_path / '.minigit'
        self.objects_dir = self.minigit_dir / 'objects'
        self.refs_dir = self.minigit_dir / 'refs'
        self.head_file = self.minigit_dir / 'HEAD'
        self.index_file = self.minigit_dir / 'index'
    
    def init(self):
        """Initialize a new minigit repository."""
        if self.minigit_dir.exists():
            print(f"Reinitialized existing Mini-Git repository in {self.minigit_dir}")
            return
        
        # Create directory structure
        self.minigit_dir.mkdir()
        self.objects_dir.mkdir()
        (self.minigit_dir / 'refs' / 'heads').mkdir(parents=True)
        
        # Initialize HEAD to point to master (no commit yet)
        self.head_file.write_text('ref: refs/heads/master\n')
        
        # Create empty index
        self.index_file.write_text('{}')
        
        print(f"Initialized empty Mini-Git repository in {self.minigit_dir}")
    
    def _hash_object(self, content, obj_type='blob'):
        """
        Create a SHA-1 hash of content and store it.
        Returns the hash (like git hash-object).
        """
        # Store as: type\0content
        if isinstance(content, str):
            content = content.encode('utf-8')
        
        header = f"{obj_type}\0".encode('utf-8')
        full_content = header + content
        
        sha = hashlib.sha1(full_content).hexdigest()
        
        # Store in objects directory (first 2 chars as subdir)
        obj_dir = self.objects_dir / sha[:2]
        obj_dir.mkdir(exist_ok=True)
        obj_file = obj_dir / sha[2:]
        obj_file.write_bytes(full_content)
        
        return sha
    
    def _read_object(self, sha):
        """Read an object by its SHA-1 hash."""
        if len(sha) < 3:
            return None
        
        obj_file = self.objects_dir / sha[:2] / sha[2:]
        if not obj_file.exists():
            return None
        
        content = obj_file.read_bytes()
        # Split header and content
        null_idx = content.index(b'\0')
        obj_type = content[:null_idx].decode('utf-8')
        data = content[null_idx + 1:]
        
        return obj_type, data
    
    def _get_current_commit(self):
        """Get the SHA of the current commit (HEAD)."""
        if not self.head_file.exists():
            return None
        
        head_content = self.head_file.read_text().strip()
        if head_content.startswith('ref: '):
            ref_path = self.minigit_dir / head_content[5:]
            if ref_path.exists():
                return ref_path.read_text().strip()
            return None
        return head_content
    
    def _set_current_commit(self, sha):
        """Update HEAD to point to a new commit."""
        head_content = self.head_file.read_text().strip()
        if head_content.startswith('ref: '):
            ref_path = self.minigit_dir / head_content[5:]
            ref_path.write_text(sha + '\n')
    
    def _read_index(self):
        """Read the staging area (index)."""
        if not self.index_file.exists():
            return {}
        return json.loads(self.index_file.read_text())
    
    def _write_index(self, index):
        """Write the staging area."""
        self.index_file.write_text(json.dumps(index, indent=2))
    
    def add(self, filepath):
        """Stage a file for commit."""
        if not self.minigit_dir.exists():
            print("Not a minigit repository. Run 'minigit init' first.")
            return
        
        path = self.repo_path / filepath
        if not path.exists():
            print(f"Error: pathspec '{filepath}' did not match any files")
            return
        
        if path.is_dir():
            print(f"Error: '{filepath}' is a directory (directories not yet supported)")
            return
        
        # Read file and create blob object
        content = path.read_bytes()
        sha = self._hash_object(content, 'blob')
        
        # Add to index
        index = self._read_index()
        index[filepath] = sha
        self._write_index(index)
        
        print(f"Added: {filepath}")
    
    def commit(self, message):
        """Create a commit with staged changes."""
        if not self.minigit_dir.exists():
            print("Not a minigit repository. Run 'minigit init' first.")
            return
        
        index = self._read_index()
        if not index:
            print("Nothing to commit (empty index)")
            return
        
        # Create tree object from index
        tree_entries = []
        for filepath, sha in sorted(index.items()):
            tree_entries.append(f"100644 blob {sha}\t{filepath}")
        tree_content = '\n'.join(tree_entries)
        tree_sha = self._hash_object(tree_content, 'tree')
        
        # Create commit object
        parent = self._get_current_commit()
        timestamp = int(time.time())
        author = "User <user@example.com>"
        
        commit_lines = [
            f"tree {tree_sha}",
        ]
        if parent:
            commit_lines.append(f"parent {parent}")
        commit_lines.extend([
            f"author {author} {timestamp}",
            f"committer {author} {timestamp}",
            "",
            message,
        ])
        commit_content = '\n'.join(commit_lines)
        commit_sha = self._hash_object(commit_content, 'commit')
        
        # Update HEAD
        self._set_current_commit(commit_sha)
        
        # Clear index after commit (like git does)
        self._write_index({})
        
        print(f"[{commit_sha[:7]}] {message}")
    
    def log(self):
        """Show commit history."""
        if not self.minigit_dir.exists():
            print("Not a minigit repository. Run 'minigit init' first.")
            return
        
        commit_sha = self._get_current_commit()
        if not commit_sha:
            print("No commits yet")
            return
        
        while commit_sha:
            obj = self._read_object(commit_sha)
            if not obj or obj[0] != 'commit':
                break
            
            lines = obj[1].decode('utf-8').split('\n')
            
            tree = None
            parent = None
            author = None
            timestamp = None
            message_lines = []
            in_message = False
            
            for line in lines:
                if in_message:
                    message_lines.append(line)
                elif line.startswith('tree '):
                    tree = line[5:]
                elif line.startswith('parent '):
                    parent = line[7:]
                elif line.startswith('author '):
                    parts = line[7:].rsplit(' ', 1)
                    author = parts[0]
                    timestamp = int(parts[1]) if len(parts) > 1 else 0
                elif line == '':
                    in_message = True
            
            message = '\n'.join(message_lines).strip()
            date_str = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') if timestamp else 'Unknown'
            
            print(f"\033[33mcommit {commit_sha}\033[0m")
            if parent:
                print(f"Parent: {parent}")
            print(f"Author: {author}")
            print(f"Date:   {date_str}")
            print()
            print(f"    {message}")
            print()
            
            commit_sha = parent
    
    def status(self):
        """Show working tree status."""
        if not self.minigit_dir.exists():
            print("Not a minigit repository. Run 'minigit init' first.")
            return
        
        index = self._read_index()
        current_commit = self._get_current_commit()
        
        print(f"On branch master")
        if current_commit:
            print(f"Current commit: {current_commit[:7]}")
        else:
            print("No commits yet")
        print()
        
        if index:
            print("Changes to be committed:")
            print('  (use "minigit commit" to commit)')
            print()
            for filepath in sorted(index.keys()):
                print(f"\t\033[32mnew file:   {filepath}\033[0m")
            print()
        else:
            print("Nothing to commit, working tree clean")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Mini-Git: A simplified version control system")
        print()
        print("Usage: minigit <command> [<args>]")
        print()
        print("Commands:")
        print("  init              Initialize a new repository")
        print("  add <file>        Stage file for commit")
        print("  commit -m <msg>   Create a commit")
        print("  log               Show commit history")
        print("  status            Show repository status")
        print()
        print("Examples:")
        print("  minigit init")
        print("  minigit add README.md")
        print('  minigit commit -m "Initial commit"')
        print("  minigit log")
        sys.exit(1)
    
    command = sys.argv[1]
    args = sys.argv[2:]
    
    mg = MiniGit()
    
    if command == 'init':
        mg.init()
    
    elif command == 'add':
        if not args:
            print("Error: Nothing specified, nothing added.")
            sys.exit(1)
        mg.add(args[0])
    
    elif command == 'commit':
        message = None
        if len(args) >= 2 and args[0] == '-m':
            message = args[1]
        if not message:
            print("Error: Please provide a commit message with -m")
            sys.exit(1)
        mg.commit(message)
    
    elif command == 'log':
        mg.log()
    
    elif command == 'status':
        mg.status()
    
    else:
        print(f"Unknown command: {command}")
        print("Run 'minigit' for usage information.")
        sys.exit(1)


if __name__ == '__main__':
    main()

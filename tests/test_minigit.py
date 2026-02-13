#!/usr/bin/env python3
"""Unit tests for Mini-Git."""

import unittest
import sys
import tempfile
import os
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'mini-git'))

from minigit import MiniGit


class TestMiniGit(unittest.TestCase):
    """Test cases for MiniGit."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mg = MiniGit(self.temp_dir)
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_init_creates_structure(self):
        self.mg.init()
        self.assertTrue(self.mg.minigit_dir.exists())
        self.assertTrue(self.mg.objects_dir.exists())
        self.assertTrue((self.mg.minigit_dir / 'refs' / 'heads').exists())
        self.assertTrue(self.mg.head_file.exists())
        self.assertTrue(self.mg.index_file.exists())
    
    def test_head_points_to_master(self):
        self.mg.init()
        head_content = self.mg.head_file.read_text().strip()
        self.assertEqual(head_content, "ref: refs/heads/master")
    
    def test_index_starts_empty(self):
        self.mg.init()
        import json
        index = json.loads(self.mg.index_file.read_text())
        self.assertEqual(index, {})
    
    def test_hash_object_creates_file(self):
        self.mg.init()
        content = "Hello, World!"
        sha = self.mg._hash_object(content)
        
        # Check file was created
        obj_file = self.mg.objects_dir / sha[:2] / sha[2:]
        self.assertTrue(obj_file.exists())
        
        # Check content is retrievable
        obj_type, data = self.mg._read_object(sha)
        self.assertEqual(obj_type, "blob")
        self.assertEqual(data.decode('utf-8'), content)
    
    def test_add_stages_file(self):
        self.mg.init()
        
        # Create a test file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        
        # Add it
        self.mg.add("test.txt")
        
        # Check index
        index = self.mg._read_index()
        self.assertIn("test.txt", index)
        self.assertEqual(len(index["test.txt"]), 40)  # SHA-1 is 40 chars
    
    def test_add_nonexistent_file(self):
        self.mg.init()
        # Should not raise, just print message
        self.mg.add("nonexistent.txt")
        index = self.mg._read_index()
        self.assertNotIn("nonexistent.txt", index)
    
    def test_commit_creates_commit_object(self):
        self.mg.init()
        
        # Create and add a file
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        self.mg.add("test.txt")
        
        # Commit
        self.mg.commit("Test commit")
        
        # Check HEAD was updated
        commit_sha = self.mg._get_current_commit()
        self.assertIsNotNone(commit_sha)
        self.assertEqual(len(commit_sha), 40)
        
        # Check commit object exists
        obj_type, data = self.mg._read_object(commit_sha)
        self.assertEqual(obj_type, "commit")
        self.assertIn("Test commit", data.decode('utf-8'))
    
    def test_commit_clears_index(self):
        self.mg.init()
        
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("test content")
        self.mg.add("test.txt")
        
        self.mg.commit("Test commit")
        
        index = self.mg._read_index()
        self.assertEqual(index, {})
    
    def test_commit_with_parent(self):
        self.mg.init()
        
        # First commit
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("version 1")
        self.mg.add("test.txt")
        self.mg.commit("First commit")
        first_sha = self.mg._get_current_commit()
        
        # Second commit
        test_file.write_text("version 2")
        self.mg.add("test.txt")
        self.mg.commit("Second commit")
        second_sha = self.mg._get_current_commit()
        
        # Check second commit has parent
        obj_type, data = self.mg._read_object(second_sha)
        self.assertIn(f"parent {first_sha}", data.decode('utf-8'))
    
    def test_empty_commit_not_allowed(self):
        self.mg.init()
        # Should not create commit with empty index
        self.mg.commit("Empty commit")
        self.assertIsNone(self.mg._get_current_commit())


class TestHashing(unittest.TestCase):
    """Test content hashing."""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.mg = MiniGit(self.temp_dir)
        self.mg.init()
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_same_content_same_hash(self):
        content = "Hello, World!"
        sha1 = self.mg._hash_object(content)
        sha2 = self.mg._hash_object(content)
        self.assertEqual(sha1, sha2)
    
    def test_different_content_different_hash(self):
        sha1 = self.mg._hash_object("Content A")
        sha2 = self.mg._hash_object("Content B")
        self.assertNotEqual(sha1, sha2)


if __name__ == '__main__':
    unittest.main()

"""Tests for command history."""

import pytest
from gitwrapper.cli import InteractiveGitWrapper


class TestHistory:
    """Test command history functionality."""

    def test_add_to_history(self, tmp_path):
        """Test adding commands to history."""
        wrapper = InteractiveGitWrapper()
        wrapper.history_file = tmp_path / "test_history.json"
        wrapper.history = []
        
        wrapper.add_to_history("commit", "Test commit")
        assert len(wrapper.history) == 1
        assert wrapper.history[0]["command"] == "commit"
        assert wrapper.history[0]["description"] == "Test commit"
        assert "timestamp" in wrapper.history[0]

    def test_history_limit(self, tmp_path):
        """Test that history is limited to max_history."""
        wrapper = InteractiveGitWrapper()
        wrapper.history_file = tmp_path / "test_history.json"
        wrapper.config["max_history"] = 5
        wrapper.history = []
        
        # Add more than max_history items
        for i in range(10):
            wrapper.add_to_history(f"command{i}", f"Description {i}")
        
        # Should only keep last 5
        assert len(wrapper.history) == 5
        assert wrapper.history[0]["command"] == "command5"
        assert wrapper.history[-1]["command"] == "command9"

    def test_load_history(self, tmp_path):
        """Test loading history from file."""
        wrapper = InteractiveGitWrapper()
        wrapper.history_file = tmp_path / "test_history.json"
        wrapper.history = []
        
        # Add and save
        wrapper.add_to_history("test", "Test command")
        
        # Create new instance and load
        wrapper2 = InteractiveGitWrapper()
        wrapper2.history_file = tmp_path / "test_history.json"
        wrapper2.load_history()
        
        assert len(wrapper2.history) == 1
        assert wrapper2.history[0]["command"] == "test"

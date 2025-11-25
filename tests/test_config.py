"""Tests for configuration management."""

import json
import tempfile
from pathlib import Path
import pytest
from gitwrapper.cli import InteractiveGitWrapper


class TestConfiguration:
    """Test configuration loading and saving."""

    def test_default_config(self, tmp_path, monkeypatch):
        """Test that default configuration is loaded."""
        config_file = tmp_path / "test_config.json"
        monkeypatch.setattr(Path, "home", lambda: tmp_path)
        
        # Mock the config file path
        wrapper = InteractiveGitWrapper()
        wrapper.config_file = config_file
        wrapper.load_config()
        
        assert wrapper.config["default_branch"] == "main"
        assert wrapper.config["auto_push"] is True
        assert wrapper.config["show_emoji"] is True
        assert wrapper.config["default_remote"] == "origin"

    def test_save_and_load_config(self, tmp_path):
        """Test saving and loading configuration."""
        config_file = tmp_path / "test_config.json"
        
        wrapper = InteractiveGitWrapper()
        wrapper.config_file = config_file
        wrapper.config["name"] = "Test User"
        wrapper.config["email"] = "test@example.com"
        wrapper.save_config()
        
        # Create new instance and load
        wrapper2 = InteractiveGitWrapper()
        wrapper2.config_file = config_file
        wrapper2.load_config()
        
        assert wrapper2.config["name"] == "Test User"
        assert wrapper2.config["email"] == "test@example.com"

    def test_toggle_config(self, tmp_path):
        """Test toggling boolean configuration values."""
        wrapper = InteractiveGitWrapper()
        wrapper.config_file = tmp_path / "test_config.json"
        
        original_value = wrapper.config["auto_push"]
        wrapper.toggle_config("auto_push")
        assert wrapper.config["auto_push"] == (not original_value)
        
        wrapper.toggle_config("auto_push")
        assert wrapper.config["auto_push"] == original_value

    def test_update_config(self, tmp_path):
        """Test updating configuration values."""
        wrapper = InteractiveGitWrapper()
        wrapper.config_file = tmp_path / "test_config.json"
        
        wrapper.update_config("name", "New Name")
        assert wrapper.config["name"] == "New Name"
        
        wrapper.update_config("email", "new@example.com")
        assert wrapper.config["email"] == "new@example.com"

    def test_emoji_helper(self):
        """Test emoji helper method."""
        wrapper = InteractiveGitWrapper()
        
        wrapper.config["show_emoji"] = True
        assert wrapper.emoji("🚀") == "🚀"
        
        wrapper.config["show_emoji"] = False
        assert wrapper.emoji("🚀") == ""

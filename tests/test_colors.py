"""Tests for color output."""

import pytest
from gitwrapper.cli import InteractiveGitWrapper, Colors


class TestColors:
    """Test color functionality."""

    def test_colorize_enabled(self):
        """Test colorize when colors are enabled."""
        wrapper = InteractiveGitWrapper()
        wrapper.colors_enabled = True
        wrapper.config["use_colors"] = True
        
        result = wrapper.colorize("test", Colors.GREEN)
        assert Colors.GREEN in result
        assert Colors.RESET in result
        assert "test" in result

    def test_colorize_disabled(self):
        """Test colorize when colors are disabled."""
        wrapper = InteractiveGitWrapper()
        wrapper.colors_enabled = False
        
        result = wrapper.colorize("test", Colors.GREEN)
        assert result == "test"
        assert Colors.GREEN not in result

    def test_colorize_config_disabled(self):
        """Test colorize when config disables colors."""
        wrapper = InteractiveGitWrapper()
        wrapper.colors_enabled = True
        wrapper.config["use_colors"] = False
        
        result = wrapper.colorize("test", Colors.GREEN)
        assert result == "test"

    def test_print_methods(self, capsys):
        """Test print methods with colors."""
        wrapper = InteractiveGitWrapper()
        wrapper.colors_enabled = False  # Disable for testing
        wrapper.config["show_emoji"] = False
        
        wrapper.print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out
        
        wrapper.print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out
        
        wrapper.print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out
        
        wrapper.print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        
        wrapper.print_working("Working message")
        captured = capsys.readouterr()
        assert "Working message" in captured.out

    def test_print_methods_with_emoji(self, capsys):
        """Test print methods with emoji enabled."""
        wrapper = InteractiveGitWrapper()
        wrapper.colors_enabled = False
        wrapper.config["show_emoji"] = True
        
        wrapper.print_success("Success")
        captured = capsys.readouterr()
        assert "✅" in captured.out
        
        wrapper.print_error("Error")
        captured = capsys.readouterr()
        assert "❌" in captured.out

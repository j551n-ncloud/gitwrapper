"""Tests for utility functions."""

import pytest
from unittest.mock import Mock, patch
from gitwrapper.cli import InteractiveGitWrapper


class TestUtils:
    """Test utility methods."""

    def test_confirm_default_yes(self, monkeypatch):
        """Test confirm with default yes."""
        wrapper = InteractiveGitWrapper()
        
        # Simulate empty input (should use default)
        monkeypatch.setattr('builtins.input', lambda _: "")
        assert wrapper.confirm("Test?", default=True) is True
        
        # Simulate 'y' input
        monkeypatch.setattr('builtins.input', lambda _: "y")
        assert wrapper.confirm("Test?", default=True) is True
        
        # Simulate 'n' input
        monkeypatch.setattr('builtins.input', lambda _: "n")
        assert wrapper.confirm("Test?", default=True) is False

    def test_confirm_default_no(self, monkeypatch):
        """Test confirm with default no."""
        wrapper = InteractiveGitWrapper()
        
        # Simulate empty input (should use default)
        monkeypatch.setattr('builtins.input', lambda _: "")
        assert wrapper.confirm("Test?", default=False) is False
        
        # Simulate 'y' input
        monkeypatch.setattr('builtins.input', lambda _: "y")
        assert wrapper.confirm("Test?", default=False) is True

    def test_get_input_with_default(self, monkeypatch):
        """Test get_input with default value."""
        wrapper = InteractiveGitWrapper()
        
        # Empty input should return default
        monkeypatch.setattr('builtins.input', lambda _: "")
        result = wrapper.get_input("Test", default="default_value")
        assert result == "default_value"
        
        # Non-empty input should return input
        monkeypatch.setattr('builtins.input', lambda _: "user_input")
        result = wrapper.get_input("Test", default="default_value")
        assert result == "user_input"

    def test_get_input_without_default(self, monkeypatch):
        """Test get_input without default value."""
        wrapper = InteractiveGitWrapper()
        
        monkeypatch.setattr('builtins.input', lambda _: "user_input")
        result = wrapper.get_input("Test")
        assert result == "user_input"

    @patch('subprocess.run')
    def test_is_git_repo_true(self, mock_run):
        """Test is_git_repo when in a git repository."""
        mock_run.return_value = Mock(returncode=0)
        wrapper = InteractiveGitWrapper()
        
        assert wrapper.is_git_repo() is True

    @patch('subprocess.run')
    def test_is_git_repo_false(self, mock_run):
        """Test is_git_repo when not in a git repository."""
        from subprocess import CalledProcessError
        
        # First call succeeds (git --version check)
        # Second call fails (git rev-parse check)
        mock_run.side_effect = [
            Mock(returncode=0),  # git --version succeeds
            CalledProcessError(1, 'git')  # git rev-parse fails
        ]
        wrapper = InteractiveGitWrapper()
        
        assert wrapper.is_git_repo() is False

    @patch('subprocess.run')
    def test_get_remotes(self, mock_run):
        """Test getting list of remotes."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="origin\nupstream\n"
        )
        wrapper = InteractiveGitWrapper()
        
        remotes = wrapper.get_remotes()
        assert remotes == ["origin", "upstream"]

    @patch('subprocess.run')
    def test_get_remotes_empty(self, mock_run):
        """Test getting remotes when none exist."""
        mock_run.return_value = Mock(returncode=0, stdout="")
        wrapper = InteractiveGitWrapper()
        
        remotes = wrapper.get_remotes()
        assert remotes == []

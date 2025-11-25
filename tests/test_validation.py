"""Tests for input validation."""

import pytest
from gitwrapper.cli import InteractiveGitWrapper


class TestValidation:
    """Test input validation methods."""

    def test_validate_branch_name_valid(self):
        """Test validation of valid branch names."""
        wrapper = InteractiveGitWrapper()
        
        assert wrapper.validate_branch_name("main") is True
        assert wrapper.validate_branch_name("feature/new-feature") is True
        assert wrapper.validate_branch_name("bugfix-123") is True
        assert wrapper.validate_branch_name("release-v1.0.0") is True

    def test_validate_branch_name_invalid(self):
        """Test validation of invalid branch names."""
        wrapper = InteractiveGitWrapper()
        
        # Empty name
        assert wrapper.validate_branch_name("") is False
        
        # Contains spaces
        assert wrapper.validate_branch_name("feature branch") is False
        
        # Invalid characters
        assert wrapper.validate_branch_name("feature~123") is False
        assert wrapper.validate_branch_name("feature^123") is False
        assert wrapper.validate_branch_name("feature:123") is False
        assert wrapper.validate_branch_name("feature?123") is False
        assert wrapper.validate_branch_name("feature*123") is False
        assert wrapper.validate_branch_name("feature[123]") is False
        
        # Starts with dash
        assert wrapper.validate_branch_name("-feature") is False
        
        # Ends with dot
        assert wrapper.validate_branch_name("feature.") is False
        
        # Ends with .lock
        assert wrapper.validate_branch_name("feature.lock") is False
        
        # Contains ..
        assert wrapper.validate_branch_name("feature..branch") is False

    def test_validate_url_valid(self):
        """Test validation of valid URLs."""
        wrapper = InteractiveGitWrapper()
        
        # HTTPS URLs
        assert wrapper.validate_url("https://github.com/user/repo.git") is True
        assert wrapper.validate_url("http://gitlab.com/user/repo.git") is True
        
        # SSH URLs
        assert wrapper.validate_url("git@github.com:user/repo.git") is True
        assert wrapper.validate_url("ssh://git@github.com/user/repo.git") is True
        
        # File URLs
        assert wrapper.validate_url("file:///path/to/repo") is True
        
        # Absolute paths
        assert wrapper.validate_url("/path/to/repo") is True
        
        # Relative paths
        assert wrapper.validate_url("../repo") is True

    def test_validate_url_invalid(self):
        """Test validation of invalid URLs."""
        wrapper = InteractiveGitWrapper()
        
        # Empty URL
        assert wrapper.validate_url("") is False
        
        # Invalid format
        assert wrapper.validate_url("not-a-url") is False
        assert wrapper.validate_url("ftp://example.com") is False

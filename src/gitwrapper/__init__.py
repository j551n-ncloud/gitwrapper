"""
Interactive Git Wrapper - A user-friendly interface for Git operations.
"""

__version__ = "1.0.0"
__author__ = "Johannes Nguyen"

from .cli import InteractiveGitWrapper, main

__all__ = ["InteractiveGitWrapper", "main", "__version__"]

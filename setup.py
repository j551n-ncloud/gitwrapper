#!/usr/bin/env python3
"""Setup script for gitwrapper package."""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="gitwrapper",
    version="1.0.0",
    author="Johannes Nguyen",
    author_email="",
    description="Interactive Git Wrapper - A user-friendly interface for Git operations",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/gitwrapper",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.9",
    install_requires=[
        # No external dependencies - uses only stdlib
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "gw=gitwrapper.cli:main",
        ],
    },
    keywords="git wrapper interactive cli terminal",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/gitwrapper/issues",
        "Source": "https://github.com/yourusername/gitwrapper",
    },
)

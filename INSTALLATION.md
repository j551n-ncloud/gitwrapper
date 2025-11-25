# Installation Guide

## Quick Install

```bash
# Install the package
pip install -e .

# Verify installation
gw --help
```

## Step-by-Step Installation

### 1. Prerequisites

- Python 3.7 or higher
- Git installed and in PATH
- pip (Python package manager)

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/gitwrapper.git
cd gitwrapper
```

### 3. Install Package

**Option A: User Installation**
```bash
pip install -e .
```

**Option B: Development Installation**
```bash
pip install -e ".[dev]"
```

This installs:
- The `gitwrapper` package
- The `gw` command globally
- Development tools (pytest, black, flake8, mypy)

### 4. Verify Installation

```bash
# Check if gw command is available
which gw

# Run the application
gw

# Run tests
pytest
```

## Installation Locations

After installation:
- **Package**: `site-packages/gitwrapper/`
- **Command**: `bin/gw` (in your Python environment)
- **Config**: `~/.gitwrapper_config.json`
- **History**: `~/.gitwrapper_history.json`

## Troubleshooting

### Command not found: gw

If `gw` is not found after installation:

```bash
# Find where it was installed
python3 -m pip show gitwrapper

# Add to PATH (add to ~/.bashrc or ~/.zshrc)
export PATH="$HOME/.local/bin:$PATH"

# Or use full path
python3 -m gitwrapper.cli
```

### Import Error

If you get import errors:

```bash
# Reinstall in development mode
pip uninstall gitwrapper
pip install -e .
```

### Permission Denied

If you get permission errors:

```bash
# Install for current user only
pip install --user -e .
```

## Uninstallation

```bash
pip uninstall gitwrapper
```

This removes:
- The package
- The `gw` command
- Does NOT remove config files (~/.gitwrapper_*)

## Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install package
pip install -e ".[dev]"

# Use the tool
gw

# Deactivate when done
deactivate
```

## System-Wide Installation

```bash
# Install globally (requires sudo/admin)
sudo pip install -e .

# Now available to all users
gw
```

## Docker Installation (Optional)

```dockerfile
FROM python:3.10-slim

WORKDIR /app
COPY . .

RUN pip install -e .

ENTRYPOINT ["gw"]
```

Build and run:
```bash
docker build -t gitwrapper .
docker run -it -v $(pwd):/repo gitwrapper
```

## Updating

```bash
# Pull latest changes
git pull origin main

# Reinstall
pip install -e . --force-reinstall
```

## Platform-Specific Notes

### macOS
- Works out of the box
- Curses library included
- Terminal.app and iTerm2 supported

### Linux
- Works on all distributions
- Requires ncurses (usually pre-installed)

### Windows
- Requires Windows Terminal or WSL
- cmd.exe not fully supported (curses limitation)
- Git Bash recommended

## Next Steps

After installation:
1. Run `gw` to start interactive mode
2. Run `gw config` to set your preferences
3. Read `QUICKSTART.md` for usage examples
4. Check `README.md` for full documentation

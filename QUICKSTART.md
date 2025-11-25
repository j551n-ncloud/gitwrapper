# Quick Start Guide

## Installation

```bash
pip install -e .
```

## First Run

```bash
gw
```

You'll see the interactive menu. Navigate using numbers.

## Common Workflows

### 1. Quick Commit
```bash
gw commit
# or
gw
# Select "Quick Commit"
```

### 2. Add Specific Files
```bash
gw add
# Use arrow keys to select files
# Space to toggle, Enter to confirm
```

### 3. Push to Multiple Remotes
```bash
gw push
# Select "Push to all remotes"
# Parallel push for speed!
```

### 4. Stash Your Work
```bash
gw stash
# Save current changes
# Pop them later when ready
```

### 5. Create a Tag
```bash
gw tag
# Create new tag
# Enter: v1.0.0
```

## Configuration

```bash
gw config
```

Set your preferences:
- Name and email
- Default branch (main/master)
- Auto-push after commit
- Enable/disable emojis
- Enable/disable colors
- Parallel push

## Tips

1. **Use arrow keys** in file selector for quick selection
2. **Press 'a'** to select all files
3. **Press 'n'** to deselect all files
4. **Ctrl+C** exits at any time
5. **Empty input** uses default values (shown in [brackets])

## Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=src/gitwrapper

# Specific test
pytest tests/test_config.py
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Format code
black src/ tests/

# Lint
flake8 src/ tests/

# Type check
mypy src/
```

## Getting Help

```bash
gw
# Select "Help" from menu
```

Or check the full README.md for detailed documentation.

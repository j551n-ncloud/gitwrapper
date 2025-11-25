# Interactive Git Wrapper (gw)

A user-friendly, feature-rich interactive interface for Git operations with advanced multi-remote support.

## Features

### Core Operations
- **Interactive Status** - Enhanced status with ahead/behind tracking and stash count
- **Interactive File Selection** - Select files to add using arrow keys and spacebar
- **Quick Commit** - Fast commit workflow with auto-push option
- **Sync** - Pull and push in one operation with fetch support
- **Multi-Remote Push** - Push to single, multiple, or all remotes
- **Branch Management** - Create, switch, delete, rename branches with validation
- **Remote Management** - Add, remove, modify remotes with URL validation

### Advanced Features
- **Stash Operations** - Save, pop, apply, list, and manage stashes
- **Tag Management** - Create, list, delete, and push tags
- **Undo Operations** - Soft/hard reset, reflog navigation with safety warnings
- **Parallel Push** - Multi-threaded push to multiple remotes for speed
- **Dry Run Mode** - Preview push operations before executing
- **Command History** - Track and search recent operations
- **Colorized Output** - Color-coded messages for better readability
- **Input Validation** - Branch name and URL validation

## Installation

### From PyPI (when published)
```bash
pip install gitwrapper
```

### From Source
```bash
# Clone the repository
git clone https://github.com/yourusername/gitwrapper.git
cd gitwrapper

# Install in development mode
pip install -e .

# Or install with dev dependencies
pip install -e ".[dev]"
```

### Direct Script Usage
```bash
# Make executable
chmod +x src/gitwrapper/cli.py

# Create symlink
ln -s $(pwd)/src/gitwrapper/cli.py /usr/local/bin/gw
```

## Usage

### Interactive Mode
```bash
gw
```

### Quick Commands
```bash
gw status    # Show repository status
gw add       # Interactive file selection
gw commit    # Quick commit
gw sync      # Pull and push
gw push      # Push operations menu
gw stash     # Stash operations
gw tag       # Tag management
gw undo      # Undo operations
gw history   # View command history
gw config    # Configuration
```

## Configuration

Settings are stored in `~/.gitwrapper_config.json`:

- **name/email** - Git user configuration
- **default_branch** - Default branch name (main/master)
- **default_remote** - Default remote for operations
- **auto_push** - Auto-prompt to push after commit
- **show_emoji** - Display emoji in output
- **use_colors** - Colorized terminal output
- **parallel_push** - Enable parallel multi-remote push
- **max_history** - Number of commands to keep in history

## Key Improvements

### Type Hints
All functions now have proper type annotations for better IDE support and code clarity.

### Error Handling
- Robust validation for branch names and URLs
- Better error messages with context
- Safety confirmations for destructive operations

### Performance
- Parallel push using ThreadPoolExecutor for multi-remote operations
- Configurable thread pool size
- Progress feedback during operations

### User Experience
- Color-coded output (green=success, red=error, blue=info, yellow=warning)
- Ahead/behind commit tracking in status
- Stash count display
- Command history with timestamps
- Dry run mode for previewing operations

### Safety Features
- Double confirmation for destructive operations
- Input validation before execution
- Reflog access for recovery
- Soft/hard reset options with clear warnings

## Examples

### Interactive File Selection
```bash
gw add
# Use ↑↓ arrow keys to navigate
# Press Space to select/deselect files
# Press 'a' to select all, 'n' to select none
# Press Enter to confirm, 'q' to cancel
```

### Multi-Remote Push
```bash
gw push
# Select "Push to all remotes"
# Choose parallel or sequential
# Watch real-time progress
```

### Stash Workflow
```bash
gw stash
# Save current work
# Switch branches
# Pop stash when ready
```

### Undo Last Commit
```bash
gw undo
# Choose soft (keep changes) or hard (discard)
# Double confirmation for safety
```

## Requirements

- Python 3.9+
- Git installed and in PATH
- Terminal with ANSI color support (optional)

## License

MIT License - Feel free to modify and distribute

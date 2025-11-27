# Git Wrapper (gw) - Standalone Version

A user-friendly, interactive command-line interface for Git operations. This standalone version is a single Python file that you can drop into any project.

## Features

- 🎯 **Interactive Menu** - Easy-to-use interface for all Git operations
- 📤 **Multi-Remote Push** - Push to single, multiple, or all remotes (with parallel support)
- ➕ **Interactive File Selection** - Select files to add using arrow keys
- 📦 **Stash Management** - Save, pop, apply, and manage stashes
- 🏷️ **Tag Management** - Create, list, delete, and push tags
- 🌿 **Branch Operations** - Create, switch, delete, and rename branches
- ↩️ **Undo Operations** - Safely undo commits with soft/hard reset options
- 🔗 **Remote Management** - Add, remove, and configure multiple remotes
- 🎨 **Customizable** - Toggle emojis, colors, and configure defaults
- 📜 **Command History** - Track your recent Git operations

## Quick Start

### Installation

```bash
# Download the script
curl -O https://raw.githubusercontent.com/yourusername/gitwrapper/standalone/gw.py

# Make it executable
chmod +x gw.py

# Optional: Move to PATH
sudo mv gw.py /usr/local/bin/gw
```

Or simply copy `gw.py` to your project directory.

### Usage

```bash
# Interactive mode
./gw.py
# or if installed globally
gw

# Quick commands
./gw.py status
./gw.py add
./gw.py commit
./gw.py push
./gw.py stash
```

## Requirements

- Python 3.9 or higher
- Git installed and in PATH
- Terminal with ANSI color support (optional)

## Interactive File Selection

Select files to stage using arrow keys:

```
📁 Select Files to Add (Space=toggle, Enter=confirm, q=cancel)
================================================================
Use ↑↓ arrows to navigate, Space to select/deselect

>  [✓] src/main.py          ← Current position
   [✓] src/utils.py         ← Selected
   [ ] tests/test_main.py   ← Not selected
   [✓] README.md            ← Selected

Selected: 3/4 | Enter to confirm, q to cancel
```

**Controls:**
- `↑/↓` - Navigate
- `Space` - Toggle selection
- `Enter` - Confirm
- `q/ESC` - Cancel
- `a` - Select all
- `n` - Deselect all

## Multi-Remote Push

Push to multiple Git remotes simultaneously:

```bash
./gw.py push
# Select "Push to all remotes"
# Choose parallel or sequential
# Watch real-time progress
```

**Features:**
- Push to single remote
- Push to multiple selected remotes
- Push to all remotes at once
- Parallel push for speed
- Individual success/failure reporting

## Configuration

First run will create `~/.gitwrapper_config.json`:

```json
{
  "name": "Your Name",
  "email": "your@email.com",
  "default_branch": "main",
  "default_remote": "origin",
  "auto_push": true,
  "show_emoji": true,
  "use_colors": true,
  "parallel_push": true,
  "max_history": 20
}
```

Configure via the menu:
```bash
./gw.py config
```

## Main Menu Options

When you run `./gw.py`, you'll see:

```
🚀 Interactive Git Wrapper
==================================================
📁 Directory: my-project
📊 Status: 🟢 Git Repository
🌿 Current Branch: main
   ↑ 0 ahead, ↓ 0 behind
📝 Working Directory: Clean
==================================================

  1. 📊 Show Status
  2. ➕ Add Files
  3. 💾 Quick Commit
  4. 🔄 Sync (Pull & Push)
  5. 📤 Push Operations
  6. 🌿 Branch Operations
  7. 📋 View Changes
  8. 📜 View History
  9. 🔗 Remote Management
  10. 📦 Stash Operations
  11. 🏷️  Tag Management
  12. ↩️  Undo Operations
  13. 🔍 Search History
  14. ⚙️ Configuration
  15. ❓ Help
  16. 🚪 Exit
```

## Common Workflows

### Quick Commit
```bash
./gw.py commit
# Select files interactively
# Enter commit message
# Optionally push
```

### Stash and Switch Branch
```bash
./gw.py stash
# Save current work
# Switch to another branch
# Pop stash when ready
```

### Create and Push Tag
```bash
./gw.py
# Select "Tag Management"
# Create new tag (e.g., v1.0.0)
# Push to remote
```

### Undo Last Commit
```bash
./gw.py
# Select "Undo Operations"
# Choose soft (keep changes) or hard (discard)
# Confirm action
```

## Command Line Arguments

```bash
./gw.py status    # Show repository status
./gw.py add       # Interactive file selection
./gw.py commit    # Quick commit
./gw.py sync      # Pull and push
./gw.py push      # Push operations menu
./gw.py stash     # Stash operations
./gw.py tag       # Tag management
./gw.py undo      # Undo operations
./gw.py history   # View command history
./gw.py config    # Configuration menu
```

## Features in Detail

### Stash Operations
- Save current changes with optional message
- Pop latest stash
- Apply specific stash
- List all stashes
- Drop individual stashes
- Clear all stashes

### Tag Management
- Create lightweight or annotated tags
- List all tags with messages
- Delete tags locally and remotely
- Push tags to remotes
- Semantic versioning support

### Undo Operations
- Soft reset (keep changes staged)
- Hard reset (discard changes)
- Reset to specific commit
- View reflog for recovery
- Safety confirmations

### Branch Operations
- Create new branches
- Switch between branches
- List all branches (local and remote)
- Delete branches safely
- Rename branches
- Input validation

### Remote Management
- Add new remotes with URL validation
- Remove remotes
- Change remote URLs
- Set default remote
- List all remotes with details
- Fetch from remotes

## Customization

### Disable Emojis
```bash
./gw.py config
# Select "Toggle Emoji"
```

### Disable Colors
```bash
./gw.py config
# Select "Toggle Colors"
```

### Change Default Branch
```bash
./gw.py config
# Select "Set Default Branch"
# Enter: main (or master, develop, etc.)
```

### Enable/Disable Parallel Push
```bash
./gw.py config
# Select "Toggle Parallel Push"
```

## Tips

1. **Use arrow keys** in file selector for quick selection
2. **Press 'a'** to select all files at once
3. **Press 'n'** to deselect all files
4. **Ctrl+C** exits at any time
5. **Empty input** uses default values (shown in [brackets])
6. **Parallel push** speeds up multi-remote operations
7. **Command history** tracks your last 20 operations
8. **Dry run** previews push operations before executing

## Troubleshooting

### Git not found
```bash
# Install Git
sudo apt-get install git  # Ubuntu/Debian
brew install git          # macOS
```

### Permission denied
```bash
chmod +x gw.py
```

### Python version too old
```bash
# Check version
python3 --version

# Should be 3.9 or higher
```

### Curses not available (Windows)
Use Windows Terminal or WSL. The file selector requires curses support.

## Platform Support

- ✅ **Linux** - Full support
- ✅ **macOS** - Full support
- ⚠️ **Windows** - Requires Windows Terminal or WSL (cmd.exe not fully supported)

## File Locations

- **Config**: `~/.gitwrapper_config.json`
- **History**: `~/.gitwrapper_history.json`

## Examples

### Example 1: Quick Commit Workflow
```bash
./gw.py add
# Select files with arrow keys
# Press Enter

./gw.py commit
# Enter message: "Add new feature"
# Choose to push: Yes
```

### Example 2: Multi-Remote Setup
```bash
./gw.py
# Select "Remote Management"
# Add remote: github
# Add remote: gitlab
# Set default: github

# Later...
./gw.py push
# Select "Push to all remotes"
# Both remotes updated!
```

### Example 3: Stash Workflow
```bash
./gw.py stash
# Save: "WIP: new feature"

# Do other work...

./gw.py stash
# Pop latest stash
# Continue working
```

## Why Use This?

- **No installation required** - Single Python file
- **Beginner friendly** - Clear menus and prompts
- **Power user features** - Multi-remote, parallel push, history
- **Safe** - Confirmations for destructive operations
- **Portable** - Works on any system with Python 3.9+
- **Customizable** - Configure to your preferences
- **Fast** - Parallel operations for multi-remote workflows

## License

MIT License - Feel free to use, modify, and distribute.

## Contributing

This is the standalone version. For the full package version with tests and CI/CD, see the `main` branch.

## Author

Johannes Nguyen

## Version

1.0.0

---

**Happy Git-ing!** 🚀

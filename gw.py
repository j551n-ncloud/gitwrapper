#!/usr/bin/env python3
"""
Interactive Git Wrapper - A user-friendly interface for Git operations
Usage: gw [command] or just gw for interactive mode
"""

import subprocess
import sys
import os
import json
import time
import re
import curses
from pathlib import Path
from typing import Optional, List, Dict, Union
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
EMOJI_SUCCESS = "✅ "
EMOJI_ERROR = "❌ "
EMOJI_INFO = "ℹ️  "
EMOJI_WORKING = "🔄 "
EMOJI_WARNING = "⚠️  "

# ANSI Color codes
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    
    @staticmethod
    def enabled() -> bool:
        """Check if colors should be enabled"""
        return sys.stdout.isatty() and os.getenv('NO_COLOR') is None

class InteractiveGitWrapper:
    def __init__(self):
        self.config_file = Path.home() / '.gitwrapper_config.json'
        self.history_file = Path.home() / '.gitwrapper_history.json'
        self.load_config()
        self.load_history()
        self.check_git_available()
        self.colors_enabled = Colors.enabled()
    
    def load_config(self):
        """Load user configuration"""
        self.config = {
            'name': '', 'email': '', 'default_branch': 'main',
            'auto_push': True, 'show_emoji': True, 'default_remote': 'origin',
            'use_colors': True, 'parallel_push': True, 'max_history': 20
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config.update(json.load(f))
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_config(self):
        """Save user configuration"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError:
            self.print_error("Could not save configuration")
    
    def load_history(self):
        """Load command history"""
        self.history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    def save_history(self):
        """Save command history"""
        try:
            # Keep only last N commands
            max_history = self.config.get('max_history', 20)
            self.history = self.history[-max_history:]
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f, indent=2)
        except IOError:
            pass
    
    def add_to_history(self, command: str, description: str):
        """Add command to history"""
        self.history.append({
            'command': command,
            'description': description,
            'timestamp': time.time()
        })
        self.save_history()
    
    def colorize(self, text: str, color: str) -> str:
        """Add color to text if colors are enabled"""
        if self.colors_enabled and self.config.get('use_colors', True):
            return f"{color}{text}{Colors.RESET}"
        return text
    
    def print_success(self, message: str):
        emoji = EMOJI_SUCCESS if self.config['show_emoji'] else ""
        print(self.colorize(f"{emoji}{message}", Colors.GREEN))
    
    def print_error(self, message: str):
        emoji = EMOJI_ERROR if self.config['show_emoji'] else ""
        print(self.colorize(f"{emoji}{message}", Colors.RED))
    
    def print_info(self, message: str):
        emoji = EMOJI_INFO if self.config['show_emoji'] else ""
        print(self.colorize(f"{emoji}{message}", Colors.BLUE))
    
    def print_working(self, message: str):
        emoji = EMOJI_WORKING if self.config['show_emoji'] else ""
        print(self.colorize(f"{emoji}{message}", Colors.CYAN))
    
    def print_warning(self, message: str):
        emoji = EMOJI_WARNING if self.config['show_emoji'] else ""
        print(self.colorize(f"{emoji}{message}", Colors.YELLOW))
    
    def check_git_available(self):
        """Check if git is available"""
        try:
            subprocess.run(['git', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.print_error("Git is not installed or not available in PATH")
            sys.exit(1)
    
    def is_git_repo(self) -> bool:
        """Check if current directory is a git repository"""
        try:
            subprocess.run(['git', 'rev-parse', '--git-dir'], 
                         capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def run_git_command(self, cmd: List[str], capture_output: bool = False, 
                       show_output: bool = True) -> Union[bool, str]:
        """Run a git command and handle errors"""
        try:
            if capture_output:
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                return result.stdout.strip()
            else:
                if show_output:
                    subprocess.run(cmd, check=True)
                else:
                    subprocess.run(cmd, capture_output=True, check=True)
                return True
        except subprocess.CalledProcessError as e:
            self.print_error(f"Git command failed: {' '.join(cmd)}")
            if hasattr(e, 'stderr') and e.stderr:
                print(f"Details: {e.stderr}")
            return False
    
    def validate_branch_name(self, name: str) -> bool:
        """Validate branch name according to git rules"""
        if not name:
            return False
        # Basic validation - no spaces, no special chars that git doesn't allow
        invalid_chars = [' ', '~', '^', ':', '?', '*', '[', '\\', '..']
        if any(char in name for char in invalid_chars):
            return False
        if name.startswith('-') or name.endswith('.') or name.endswith('.lock'):
            return False
        return True
    
    def validate_url(self, url: str) -> bool:
        """Basic URL validation for git remotes"""
        if not url:
            return False
        # Check for common git URL patterns
        patterns = [
            r'^https?://',  # HTTP(S)
            r'^git@',  # SSH
            r'^ssh://',  # SSH
            r'^file://',  # Local
            r'^/',  # Absolute path
            r'^\.\.',  # Relative path
        ]
        return any(re.match(pattern, url) for pattern in patterns)
    
    def get_input(self, prompt: str, default: Optional[str] = None) -> str:
        """Get user input with optional default"""
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            return user_input if user_input else default
        return input(f"{prompt}: ").strip()
    
    def get_choice(self, prompt: str, choices: List[str], 
                   default: Optional[str] = None) -> str:
        """Get user choice from a list"""
        print(f"\n{prompt}")
        for i, choice in enumerate(choices, 1):
            marker = " (default)" if default and choice == default else ""
            print(f"  {i}. {choice}{marker}")
        
        while True:
            try:
                choice_input = input("\nEnter choice number: ").strip()
                if not choice_input and default:
                    return default
                choice_num = int(choice_input)
                if 1 <= choice_num <= len(choices):
                    return choices[choice_num - 1]
                print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
    
    def get_multiple_choice(self, prompt: str, choices: List[str]) -> List[str]:
        """Get multiple choices from a list"""
        print(f"\n{prompt}")
        print("(Enter comma-separated numbers, e.g., 1,3,4)")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                choice_input = input("\nEnter choice numbers: ").strip()
                if not choice_input:
                    return []
                
                choice_nums = [int(x.strip()) for x in choice_input.split(',')]
                selected = []
                for num in choice_nums:
                    if 1 <= num <= len(choices):
                        selected.append(choices[num - 1])
                    else:
                        print(f"Invalid choice: {num}")
                        return []
                return selected
            except ValueError:
                print("Please enter valid numbers separated by commas.")
    
    def confirm(self, message: str, default: bool = True) -> bool:
        """Ask for confirmation"""
        suffix = "[Y/n]" if default else "[y/N]"
        response = input(f"{message} {suffix}: ").strip().lower()
        return response in ['y', 'yes'] if response else default
    
    def get_remotes(self) -> List[str]:
        """Get list of remote repositories"""
        remotes_output = self.run_git_command(['git', 'remote'], capture_output=True)
        return remotes_output.split('\n') if remotes_output else []
    
    def get_branch_status(self) -> Dict[str, int]:
        """Get ahead/behind status for current branch"""
        try:
            result = subprocess.run(
                ['git', 'rev-list', '--left-right', '--count', 'HEAD...@{upstream}'],
                capture_output=True, text=True, check=True
            )
            ahead, behind = map(int, result.stdout.strip().split())
            return {'ahead': ahead, 'behind': behind}
        except (subprocess.CalledProcessError, ValueError):
            return {'ahead': 0, 'behind': 0}

    def show_main_menu(self):
        """Display the main interactive menu"""
        while True:
            self.clear_screen()
            repo_status = "🟢 Git Repository" if self.is_git_repo() else "🔴 Not a Git Repository"
            current_dir = os.path.basename(os.getcwd())
            
            print("=" * 50)
            print("🚀 Interactive Git Wrapper")
            print("=" * 50)
            print(f"📁 Directory: {current_dir}")
            print(f"📊 Status: {repo_status}")
            print("=" * 50)
            
            if self.is_git_repo():
                try:
                    branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
                    print(f"🌿 Current Branch: {branch}")
                    
                    # Show ahead/behind status
                    status_info = self.get_branch_status()
                    if status_info['ahead'] > 0 or status_info['behind'] > 0:
                        print(f"   ↑ {status_info['ahead']} ahead, ↓ {status_info['behind']} behind")
                    
                    status = self.run_git_command(['git', 'status', '--porcelain'], capture_output=True)
                    if status:
                        print(f"📝 Uncommitted Changes: {len(status.splitlines())} files")
                    else:
                        print("📝 Working Directory: Clean")
                    
                    # Show stash count
                    stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
                    if stash_list:
                        stash_count = len(stash_list.splitlines())
                        print(f"📦 Stashes: {stash_count}")
                    
                    print("-" * 50)
                except:
                    pass
            
            # Menu options
            options = []
            if self.is_git_repo():
                options.extend([
                    "📊 Show Status", "➕ Add Files", "💾 Quick Commit", "🔄 Sync (Pull & Push)",
                    "📤 Push Operations", "🌿 Branch Operations", "📋 View Changes", 
                    "📜 View History", "🔗 Remote Management", "📦 Stash Operations",
                    "🏷️  Tag Management", "↩️  Undo Operations", "🔍 Search History"
                ])
            else:
                options.extend(["🎯 Initialize Repository", "📥 Clone Repository"])
            
            options.extend(["⚙️ Configuration", "❓ Help", "🚪 Exit"])
            
            for i, option in enumerate(options, 1):
                print(f"  {i}. {option}")
            
            try:
                choice = int(input(f"\nEnter your choice (1-{len(options)}): "))
                if 1 <= choice <= len(options):
                    self.handle_menu_choice(options[choice-1])
                else:
                    self.print_error("Invalid choice!")
                    time.sleep(1)
            except ValueError:
                self.print_error("Please enter a valid number!")
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋")
                break
    
    def handle_menu_choice(self, choice: str):
        """Handle menu selection"""
        handlers = {
            "Show Status": self.interactive_status,
            "Add Files": self.interactive_add_files,
            "Quick Commit": self.interactive_commit,
            "Sync": self.interactive_sync,
            "Push Operations": self.interactive_push_menu,
            "Branch Operations": self.interactive_branch_menu,
            "View Changes": self.interactive_diff,
            "View History": self.interactive_log,
            "Remote Management": self.interactive_remote_menu,
            "Stash Operations": self.interactive_stash_menu,
            "Tag Management": self.interactive_tag_menu,
            "Undo Operations": self.interactive_undo_menu,
            "Search History": self.interactive_search_history,
            "Initialize Repository": self.interactive_init,
            "Clone Repository": self.interactive_clone,
            "Configuration": self.interactive_config_menu,
            "Help": self.show_help,
            "Exit": lambda: (print("\nGoodbye! 👋"), sys.exit(0))
        }
        
        for key, handler in handlers.items():
            if key in choice:
                handler()
                break
    
    def interactive_status(self):
        """Interactive status display"""
        self.clear_screen()
        print("📊 Repository Status\n" + "=" * 30)
        
        branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        if branch:
            print(f"🌿 Current branch: {branch}")
            
            # Show ahead/behind
            status_info = self.get_branch_status()
            if status_info['ahead'] > 0 or status_info['behind'] > 0:
                print(f"   ↑ {status_info['ahead']} commits ahead")
                print(f"   ↓ {status_info['behind']} commits behind")
        
        print("\n📝 Working Directory Status:")
        self.run_git_command(['git', 'status'])
        
        # Show stash list
        stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
        if stash_list:
            print(f"\n📦 Stashes ({len(stash_list.splitlines())}):")
            for line in stash_list.splitlines()[:5]:
                print(f"   {line}")
        
        print(f"\n📜 Recent commits:")
        self.run_git_command(['git', 'log', '--oneline', '--graph', '-5'])
        
        input("\nPress Enter to continue...")
    
    def interactive_add_files(self):
        """Interactive file adding"""
        self.clear_screen()
        print("➕ Add Files\n" + "=" * 20)
        
        status = self.run_git_command(['git', 'status', '--porcelain'], capture_output=True)
        if not status:
            self.print_info("No changes to add!")
            input("Press Enter to continue...")
            return
        
        # Parse files from status
        files = []
        for line in status.splitlines():
            if line.strip():
                file_path = line[3:].strip()
                files.append(file_path)
        
        print(f"Found {len(files)} changed file(s)\n")
        
        # Ask user preference
        choice = self.get_choice(
            "How do you want to add files?",
            ["Add all files", "Select files interactively", "Cancel"]
        )
        
        if "Cancel" in choice:
            return
        
        files_to_add = []
        
        if "Add all" in choice:
            files_to_add = ['.']
            self.print_working("Adding all files...")
        else:
            # Interactive selection
            selected_files = self.select_files_interactive(files)
            if not selected_files:
                self.print_info("No files selected. Cancelled.")
                input("Press Enter to continue...")
                return
            files_to_add = selected_files
            self.print_working(f"Adding {len(files_to_add)} file(s)...")
        
        # Add selected files
        success_count = 0
        for file in files_to_add:
            if self.run_git_command(['git', 'add', file], show_output=False):
                success_count += 1
            else:
                self.print_error(f"Failed to add {file}")
        
        if success_count > 0:
            self.print_success(f"Successfully added {success_count} file(s)!")
            self.add_to_history('add', f"Added {success_count} file(s)")
        
        input("Press Enter to continue...")
    
    def select_files_interactive(self, files: List[str]) -> List[str]:
        """Interactive file selection using arrow keys and space/enter"""
        def draw_menu(stdscr, selected_indices: set, current_pos: int):
            stdscr.clear()
            h, w = stdscr.getmaxyx()
            
            # Header
            header = "📁 Select Files to Add (Space=toggle, Enter=confirm, q=cancel)"
            stdscr.addstr(0, 0, header[:w-1], curses.A_BOLD)
            stdscr.addstr(1, 0, "=" * min(len(header), w-1))
            stdscr.addstr(2, 0, "Use ↑↓ arrows to navigate, Space to select/deselect")
            
            # Calculate visible range
            max_visible = h - 6
            start_idx = max(0, current_pos - max_visible + 1) if current_pos >= max_visible else 0
            end_idx = min(len(files), start_idx + max_visible)
            
            # Display files
            for idx in range(start_idx, end_idx):
                file = files[idx]
                y_pos = 4 + (idx - start_idx)
                
                if y_pos >= h - 2:
                    break
                
                # Checkbox
                checkbox = "[✓]" if idx in selected_indices else "[ ]"
                
                # Highlight current line
                if idx == current_pos:
                    stdscr.addstr(y_pos, 0, "> ", curses.A_BOLD)
                    stdscr.addstr(y_pos, 2, f"{checkbox} {file}"[:w-3], curses.A_REVERSE)
                else:
                    stdscr.addstr(y_pos, 0, "  ")
                    stdscr.addstr(y_pos, 2, f"{checkbox} {file}"[:w-3])
            
            # Footer
            footer_y = h - 1
            selected_count = len(selected_indices)
            footer = f"Selected: {selected_count}/{len(files)} | Enter to confirm, q to cancel"
            stdscr.addstr(footer_y, 0, footer[:w-1], curses.A_BOLD)
            
            stdscr.refresh()
        
        def file_selector(stdscr):
            curses.curs_set(0)  # Hide cursor
            current_pos = 0
            selected_indices = set(range(len(files)))  # Select all by default
            
            while True:
                draw_menu(stdscr, selected_indices, current_pos)
                
                try:
                    key = stdscr.getch()
                    
                    if key == curses.KEY_UP and current_pos > 0:
                        current_pos -= 1
                    elif key == curses.KEY_DOWN and current_pos < len(files) - 1:
                        current_pos += 1
                    elif key == ord(' '):  # Space to toggle
                        if current_pos in selected_indices:
                            selected_indices.remove(current_pos)
                        else:
                            selected_indices.add(current_pos)
                    elif key == ord('\n') or key == curses.KEY_ENTER or key == 10:  # Enter to confirm
                        return [files[i] for i in sorted(selected_indices)]
                    elif key == ord('q') or key == ord('Q') or key == 27:  # q or ESC to cancel
                        return []
                    elif key == ord('a') or key == ord('A'):  # 'a' to select all
                        selected_indices = set(range(len(files)))
                    elif key == ord('n') or key == ord('N'):  # 'n' to select none
                        selected_indices = set()
                except KeyboardInterrupt:
                    return []
        
        try:
            return curses.wrapper(file_selector)
        except Exception as e:
            # Fallback to simple selection if curses fails
            self.print_error(f"Interactive selection failed: {e}")
            return files

    def interactive_commit(self):
        """Interactive commit process"""
        self.clear_screen()
        print("💾 Quick Commit\n" + "=" * 20)
        
        status = self.run_git_command(['git', 'status', '--porcelain'], capture_output=True)
        if not status:
            self.print_info("No changes to commit!")
            input("Press Enter to continue...")
            return
        
        # Parse files from status
        files = []
        for line in status.splitlines():
            if line.strip():
                # Extract filename (handle spaces in filenames)
                file_path = line[3:].strip()
                files.append(file_path)
        
        print(f"Found {len(files)} changed file(s)")
        
        # Ask user preference
        choice = self.get_choice(
            "How do you want to add files?",
            ["Add all files", "Select files interactively", "Cancel"]
        )
        
        if "Cancel" in choice:
            return
        
        files_to_add = []
        
        if "Add all" in choice:
            files_to_add = ['.']
        else:
            # Interactive selection
            selected_files = self.select_files_interactive(files)
            if not selected_files:
                self.print_info("No files selected. Cancelled.")
                input("Press Enter to continue...")
                return
            files_to_add = selected_files
        
        message = self.get_input("\nEnter commit message")
        if not message:
            self.print_error("Commit message required!")
            input("Press Enter to continue...")
            return
        
        # Add selected files
        self.print_working(f"Adding {len(files_to_add)} file(s)...")
        for file in files_to_add:
            if not self.run_git_command(['git', 'add', file], show_output=False):
                self.print_error(f"Failed to add {file}")
                input("Press Enter to continue...")
                return
        
        self.print_working(f"Committing with message: '{message}'")
        if self.run_git_command(['git', 'commit', '-m', message]):
            self.print_success("Commit successful!")
            self.add_to_history('commit', f"Committed: {message}")
            
            if self.config['auto_push'] and self.confirm("Push to remote(s)?", True):
                self.interactive_push_menu()
        
        input("Press Enter to continue...")
    
    def _execute_push(self, remote: str, branch: str, show_output: bool = True) -> bool:
        """Execute push to a single remote"""
        return self.run_git_command(['git', 'push', remote, branch], show_output=show_output)
    
    def _push_to_remotes(self, remotes: List[str], branch: str, parallel: bool = False):
        """Push to multiple remotes with summary"""
        if parallel and self.config.get('parallel_push', True) and len(remotes) > 1:
            self._push_parallel(remotes, branch)
        else:
            self._push_sequential(remotes, branch)
    
    def _push_sequential(self, remotes: List[str], branch: str):
        """Push to remotes sequentially"""
        success_count = 0
        failed_remotes = []
        
        for remote in remotes:
            self.print_working(f"Pushing to {remote}...")
            if self._execute_push(remote, branch, show_output=False):
                self.print_success(f"✓ Pushed to {remote}")
                success_count += 1
            else:
                self.print_error(f"✗ Failed to push to {remote}")
                failed_remotes.append(remote)
        
        self._print_push_summary(success_count, len(remotes), failed_remotes)
    
    def _push_parallel(self, remotes: List[str], branch: str):
        """Push to remotes in parallel using threads"""
        self.print_info(f"Pushing to {len(remotes)} remotes in parallel...")
        success_count = 0
        failed_remotes = []
        
        with ThreadPoolExecutor(max_workers=min(len(remotes), 5)) as executor:
            future_to_remote = {
                executor.submit(self._execute_push, remote, branch, False): remote 
                for remote in remotes
            }
            
            for future in as_completed(future_to_remote):
                remote = future_to_remote[future]
                try:
                    if future.result():
                        self.print_success(f"✓ Pushed to {remote}")
                        success_count += 1
                    else:
                        self.print_error(f"✗ Failed to push to {remote}")
                        failed_remotes.append(remote)
                except Exception as e:
                    self.print_error(f"✗ Error pushing to {remote}: {e}")
                    failed_remotes.append(remote)
        
        self._print_push_summary(success_count, len(remotes), failed_remotes)
    
    def _print_push_summary(self, success: int, total: int, failed: List[str]):
        """Print push operation summary"""
        print(f"\nSummary: {success}/{total} remotes successful")
        if failed:
            print(f"Failed remotes: {', '.join(failed)}")

    def interactive_push_menu(self):
        """Interactive push operations menu"""
        self.clear_screen()
        print("📤 Push Operations\n" + "=" * 20)
        
        remotes = self.get_remotes()
        if not remotes:
            self.print_error("No remotes configured!")
            input("Press Enter to continue...")
            return
        
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        print(f"Current branch: {current_branch or 'unknown'}")
        print(f"Available remotes: {', '.join(remotes)}")
        print("-" * 30)
        
        options = [
            "Push to single remote",
            "Push to multiple remotes",
            "Push to all remotes",
            "Dry run (preview)",
            "Back to main menu"
        ]
        
        choice = self.get_choice("Push Options:", options)
        
        if "single remote" in choice:
            self.interactive_push_single()
        elif "multiple remotes" in choice:
            self.interactive_push_multiple()
        elif "all remotes" in choice:
            self.interactive_push_all()
        elif "Dry run" in choice:
            self.interactive_push_dry_run()
        elif "Back to main menu" in choice:
            return
    
    def interactive_push_single(self):
        """Push to a single selected remote"""
        remotes = self.get_remotes()
        if not remotes:
            return
        
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        branch = self.get_input("Branch to push", current_branch or self.config['default_branch'])
        
        default_remote = self.config.get('default_remote', 'origin')
        if default_remote not in remotes:
            default_remote = remotes[0]
        
        remote = self.get_choice("Select remote to push to:", remotes, default_remote)
        
        self.print_working(f"Pushing {branch} to {remote}...")
        if self.run_git_command(['git', 'push', remote, branch]):
            self.print_success(f"Successfully pushed to {remote}/{branch}!")
            self.add_to_history('push', f"Pushed {branch} to {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_push_multiple(self):
        """Push to multiple selected remotes"""
        remotes = self.get_remotes()
        if not remotes:
            return
        
        if len(remotes) == 1:
            self.print_info("Only one remote available. Use single remote push instead.")
            input("Press Enter to continue...")
            return
        
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        branch = self.get_input("Branch to push", current_branch or self.config['default_branch'])
        
        selected_remotes = self.get_multiple_choice("Select remotes to push to:", remotes)
        
        if not selected_remotes:
            self.print_info("No remotes selected.")
            input("Press Enter to continue...")
            return
        
        use_parallel = self.config.get('parallel_push', True) and len(selected_remotes) > 1
        if use_parallel:
            self.print_info("Using parallel push for faster operation")
        
        self._push_to_remotes(selected_remotes, branch, parallel=use_parallel)
        self.add_to_history('push', f"Pushed {branch} to {len(selected_remotes)} remotes")
        
        input("Press Enter to continue...")
    
    def interactive_push_all(self):
        """Push to all configured remotes"""
        remotes = self.get_remotes()
        if not remotes:
            return
        
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        branch = self.get_input("Branch to push", current_branch or self.config['default_branch'])
        
        if not self.confirm(f"Push {branch} to ALL {len(remotes)} remotes?", False):
            return
        
        use_parallel = self.config.get('parallel_push', True) and len(remotes) > 1
        if use_parallel:
            self.print_info("Using parallel push for faster operation")
        
        self._push_to_remotes(remotes, branch, parallel=use_parallel)
        self.add_to_history('push', f"Pushed {branch} to all remotes")
        
        input("Press Enter to continue...")
    
    def interactive_push_dry_run(self):
        """Preview what would be pushed"""
        self.clear_screen()
        print("🔍 Push Dry Run\n" + "=" * 20)
        
        remotes = self.get_remotes()
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        branch = self.get_input("Branch to check", current_branch or self.config['default_branch'])
        
        for remote in remotes:
            print(f"\n{remote}:")
            result = self.run_git_command(
                ['git', 'push', '--dry-run', remote, branch],
                capture_output=False
            )
        
        input("\nPress Enter to continue...")
    
    def interactive_sync(self):
        """Interactive sync process"""
        self.clear_screen()
        print("🔄 Sync Repository\n" + "=" * 20)
        
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        branch = self.get_input("Branch to sync", current_branch or self.config['default_branch'])
        
        # Select remote for sync
        remotes = self.get_remotes()
        if not remotes:
            self.print_error("No remotes configured!")
            input("Press Enter to continue...")
            return
        
        default_remote = self.config.get('default_remote', 'origin')
        if default_remote not in remotes:
            default_remote = remotes[0]
        
        remote = self.get_choice("Select remote for sync:", remotes, default_remote)
        
        self.print_working(f"Syncing with {remote}/{branch}")
        
        # Fetch first
        self.print_working("Fetching latest changes...")
        if not self.run_git_command(['git', 'fetch', remote]):
            input("Press Enter to continue...")
            return
        
        # Pull
        self.print_working("Pulling latest changes...")
        if not self.run_git_command(['git', 'pull', remote, branch]):
            input("Press Enter to continue...")
            return
        
        # Push
        self.print_working("Pushing local commits...")
        if self.run_git_command(['git', 'push', remote, branch]):
            self.print_success("Sync completed successfully!")
            self.add_to_history('sync', f"Synced {branch} with {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_stash_menu(self):
        """Interactive stash operations menu"""
        while True:
            self.clear_screen()
            print("📦 Stash Operations\n" + "=" * 25)
            
            stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
            if stash_list:
                print("Current stashes:")
                for line in stash_list.splitlines()[:10]:
                    print(f"  {line}")
                print()
            else:
                print("No stashes found\n")
            
            options = [
                "Save current changes", "Pop latest stash", "Apply stash",
                "List all stashes", "Drop stash", "Clear all stashes", "Back to main menu"
            ]
            
            choice = self.get_choice("Stash Operations:", options)
            
            if "Save current" in choice:
                self.interactive_stash_save()
            elif "Pop latest" in choice:
                self.interactive_stash_pop()
            elif "Apply stash" in choice:
                self.interactive_stash_apply()
            elif "List all" in choice:
                self.interactive_stash_list()
            elif "Drop stash" in choice:
                self.interactive_stash_drop()
            elif "Clear all" in choice:
                self.interactive_stash_clear()
            elif "Back to main menu" in choice:
                break
    
    def interactive_stash_save(self):
        """Save current changes to stash"""
        message = self.get_input("Stash message (optional)")
        
        cmd = ['git', 'stash', 'push']
        if message:
            cmd.extend(['-m', message])
        
        self.print_working("Saving changes to stash...")
        if self.run_git_command(cmd):
            self.print_success("Changes stashed successfully!")
            self.add_to_history('stash', f"Stashed: {message or 'unnamed'}")
        
        input("Press Enter to continue...")
    
    def interactive_stash_pop(self):
        """Pop the latest stash"""
        stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
        if not stash_list:
            self.print_info("No stashes to pop")
            input("Press Enter to continue...")
            return
        
        if self.confirm("Pop the latest stash?", True):
            self.print_working("Popping stash...")
            if self.run_git_command(['git', 'stash', 'pop']):
                self.print_success("Stash popped successfully!")
                self.add_to_history('stash', "Popped latest stash")
        
        input("Press Enter to continue...")
    
    def interactive_stash_apply(self):
        """Apply a specific stash"""
        stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
        if not stash_list:
            self.print_info("No stashes available")
            input("Press Enter to continue...")
            return
        
        stashes = stash_list.splitlines()
        stash = self.get_choice("Select stash to apply:", stashes)
        stash_id = stash.split(':')[0]
        
        self.print_working(f"Applying {stash_id}...")
        if self.run_git_command(['git', 'stash', 'apply', stash_id]):
            self.print_success("Stash applied successfully!")
            self.add_to_history('stash', f"Applied {stash_id}")
        
        input("Press Enter to continue...")
    
    def interactive_stash_list(self):
        """List all stashes"""
        self.clear_screen()
        print("📦 All Stashes\n" + "=" * 15)
        self.run_git_command(['git', 'stash', 'list'])
        input("\nPress Enter to continue...")
    
    def interactive_stash_drop(self):
        """Drop a specific stash"""
        stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
        if not stash_list:
            self.print_info("No stashes to drop")
            input("Press Enter to continue...")
            return
        
        stashes = stash_list.splitlines()
        stash = self.get_choice("Select stash to drop:", stashes)
        stash_id = stash.split(':')[0]
        
        if self.confirm(f"Drop {stash_id}?", False):
            if self.run_git_command(['git', 'stash', 'drop', stash_id]):
                self.print_success("Stash dropped successfully!")
        
        input("Press Enter to continue...")
    
    def interactive_stash_clear(self):
        """Clear all stashes"""
        stash_list = self.run_git_command(['git', 'stash', 'list'], capture_output=True)
        if not stash_list:
            self.print_info("No stashes to clear")
            input("Press Enter to continue...")
            return
        
        stash_count = len(stash_list.splitlines())
        if self.confirm(f"Clear ALL {stash_count} stashes? This cannot be undone!", False):
            if self.run_git_command(['git', 'stash', 'clear']):
                self.print_success("All stashes cleared!")
        
        input("Press Enter to continue...")

    def interactive_tag_menu(self):
        """Interactive tag management menu"""
        while True:
            self.clear_screen()
            print("🏷️  Tag Management\n" + "=" * 25)
            
            tags = self.run_git_command(['git', 'tag'], capture_output=True)
            if tags:
                tag_list = tags.splitlines()
                print(f"Current tags ({len(tag_list)}):")
                for tag in tag_list[-10:]:
                    print(f"  {tag}")
                print()
            else:
                print("No tags found\n")
            
            options = [
                "Create new tag", "List all tags", "Delete tag",
                "Push tags to remote", "Back to main menu"
            ]
            
            choice = self.get_choice("Tag Operations:", options)
            
            if "Create new" in choice:
                self.interactive_tag_create()
            elif "List all" in choice:
                self.interactive_tag_list()
            elif "Delete tag" in choice:
                self.interactive_tag_delete()
            elif "Push tags" in choice:
                self.interactive_tag_push()
            elif "Back to main menu" in choice:
                break
    
    def interactive_tag_create(self):
        """Create a new tag"""
        tag_name = self.get_input("Tag name (e.g., v1.0.0)")
        if not tag_name:
            return
        
        message = self.get_input("Tag message (optional)")
        
        cmd = ['git', 'tag']
        if message:
            cmd.extend(['-a', tag_name, '-m', message])
        else:
            cmd.append(tag_name)
        
        self.print_working(f"Creating tag: {tag_name}")
        if self.run_git_command(cmd):
            self.print_success(f"Tag '{tag_name}' created successfully!")
            self.add_to_history('tag', f"Created tag {tag_name}")
            
            if self.confirm("Push tag to remote?", False):
                remotes = self.get_remotes()
                if remotes:
                    remote = self.get_choice("Select remote:", remotes, self.config.get('default_remote', 'origin'))
                    if self.run_git_command(['git', 'push', remote, tag_name]):
                        self.print_success(f"Tag pushed to {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_tag_list(self):
        """List all tags with details"""
        self.clear_screen()
        print("🏷️  All Tags\n" + "=" * 15)
        self.run_git_command(['git', 'tag', '-n'])
        input("\nPress Enter to continue...")
    
    def interactive_tag_delete(self):
        """Delete a tag"""
        tags = self.run_git_command(['git', 'tag'], capture_output=True)
        if not tags:
            self.print_info("No tags to delete")
            input("Press Enter to continue...")
            return
        
        tag_list = tags.splitlines()
        tag = self.get_choice("Select tag to delete:", tag_list)
        
        if self.confirm(f"Delete tag '{tag}'?", False):
            if self.run_git_command(['git', 'tag', '-d', tag]):
                self.print_success(f"Tag '{tag}' deleted locally!")
                
                if self.confirm("Delete from remote as well?", False):
                    remotes = self.get_remotes()
                    if remotes:
                        remote = self.get_choice("Select remote:", remotes, self.config.get('default_remote', 'origin'))
                        if self.run_git_command(['git', 'push', remote, '--delete', tag]):
                            self.print_success(f"Tag deleted from {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_tag_push(self):
        """Push tags to remote"""
        remotes = self.get_remotes()
        if not remotes:
            self.print_error("No remotes configured!")
            input("Press Enter to continue...")
            return
        
        remote = self.get_choice("Select remote:", remotes, self.config.get('default_remote', 'origin'))
        
        if self.confirm("Push all tags?", True):
            self.print_working(f"Pushing all tags to {remote}...")
            if self.run_git_command(['git', 'push', remote, '--tags']):
                self.print_success("All tags pushed successfully!")
        
        input("Press Enter to continue...")
    
    def interactive_undo_menu(self):
        """Interactive undo operations menu"""
        while True:
            self.clear_screen()
            print("↩️  Undo Operations\n" + "=" * 25)
            self.print_warning("Use these operations carefully!")
            print()
            
            options = [
                "Undo last commit (keep changes)", "Undo last commit (discard changes)",
                "Reset to specific commit", "View reflog", "Back to main menu"
            ]
            
            choice = self.get_choice("Undo Operations:", options)
            
            if "keep changes" in choice:
                self.interactive_undo_commit_soft()
            elif "discard changes" in choice:
                self.interactive_undo_commit_hard()
            elif "Reset to specific" in choice:
                self.interactive_reset_to_commit()
            elif "View reflog" in choice:
                self.interactive_reflog()
            elif "Back to main menu" in choice:
                break
    
    def interactive_undo_commit_soft(self):
        """Undo last commit but keep changes"""
        self.print_warning("This will undo the last commit but keep your changes staged")
        
        if self.confirm("Proceed with soft reset?", False):
            self.print_working("Undoing last commit...")
            if self.run_git_command(['git', 'reset', '--soft', 'HEAD~1']):
                self.print_success("Last commit undone! Changes are still staged.")
                self.add_to_history('undo', "Soft reset last commit")
        
        input("Press Enter to continue...")
    
    def interactive_undo_commit_hard(self):
        """Undo last commit and discard changes"""
        self.print_warning("⚠️  This will PERMANENTLY discard the last commit and all changes!")
        
        if self.confirm("Are you ABSOLUTELY sure?", False):
            if self.confirm("Last chance - this cannot be undone!", False):
                self.print_working("Undoing last commit and discarding changes...")
                if self.run_git_command(['git', 'reset', '--hard', 'HEAD~1']):
                    self.print_success("Last commit undone and changes discarded.")
                    self.add_to_history('undo', "Hard reset last commit")
        
        input("Press Enter to continue...")
    
    def interactive_reset_to_commit(self):
        """Reset to a specific commit"""
        self.clear_screen()
        print("Recent commits:")
        self.run_git_command(['git', 'log', '--oneline', '-10'])
        
        commit_hash = self.get_input("\nEnter commit hash to reset to")
        if not commit_hash:
            return
        
        reset_type = self.get_choice(
            "Reset type:",
            ["Soft (keep changes staged)", "Mixed (keep changes unstaged)", "Hard (discard all changes)"]
        )
        
        flag = '--soft' if 'Soft' in reset_type else '--mixed' if 'Mixed' in reset_type else '--hard'
        
        self.print_warning(f"This will reset to {commit_hash} using {flag}")
        if self.confirm("Proceed?", False):
            if self.run_git_command(['git', 'reset', flag, commit_hash]):
                self.print_success(f"Reset to {commit_hash} successfully!")
                self.add_to_history('undo', f"Reset to {commit_hash}")
        
        input("Press Enter to continue...")
    
    def interactive_reflog(self):
        """View reflog"""
        self.clear_screen()
        print("📜 Reflog (Recent HEAD movements)\n" + "=" * 35)
        self.run_git_command(['git', 'reflog', '-20'])
        input("\nPress Enter to continue...")
    
    def interactive_search_history(self):
        """Search command history"""
        self.clear_screen()
        print("🔍 Command History\n" + "=" * 20)
        
        if not self.history:
            self.print_info("No command history available")
            input("Press Enter to continue...")
            return
        
        print("Recent commands:")
        for i, entry in enumerate(reversed(self.history[-20:]), 1):
            timestamp = time.strftime('%Y-%m-%d %H:%M', time.localtime(entry['timestamp']))
            print(f"  {i}. [{timestamp}] {entry['command']}: {entry['description']}")
        
        input("\nPress Enter to continue...")
    
    def interactive_remote_menu(self):
        """Interactive remote management menu"""
        while True:
            self.clear_screen()
            print("🔗 Remote Management\n" + "=" * 25)
            
            remotes = self.get_remotes()
            if remotes:
                print("Current remotes:")
                for remote in remotes:
                    url = self.run_git_command(['git', 'remote', 'get-url', remote], capture_output=True)
                    default_marker = f" (default)" if remote == self.config.get('default_remote') else ""
                    print(f"  {remote}: {url}{default_marker}")
                print()
            else:
                print("No remotes configured\n")
            
            options = [
                "Add remote", "Remove remote", "List remotes", 
                "Change remote URL", "Set default remote", "Fetch from remote", "Back to main menu"
            ]
            
            choice = self.get_choice("Remote Operations:", options)
            
            if "Add remote" in choice:
                self.interactive_add_remote()
            elif "Remove remote" in choice:
                self.interactive_remove_remote()
            elif "List remotes" in choice:
                self.interactive_list_remotes()
            elif "Change remote URL" in choice:
                self.interactive_change_remote_url()
            elif "Set default remote" in choice:
                self.interactive_set_default_remote()
            elif "Fetch from remote" in choice:
                self.interactive_fetch()
            elif "Back to main menu" in choice:
                break
    
    def interactive_fetch(self):
        """Fetch from remote without merging"""
        remotes = self.get_remotes()
        if not remotes:
            self.print_error("No remotes configured!")
            input("Press Enter to continue...")
            return
        
        remote = self.get_choice("Select remote to fetch from:", remotes, self.config.get('default_remote', 'origin'))
        
        self.print_working(f"Fetching from {remote}...")
        if self.run_git_command(['git', 'fetch', remote]):
            self.print_success(f"Fetched from {remote} successfully!")
            self.add_to_history('fetch', f"Fetched from {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_set_default_remote(self):
        """Set default remote for operations"""
        remotes = self.get_remotes()
        if not remotes:
            self.print_info("No remotes configured")
            input("Press Enter to continue...")
            return
        
        current_default = self.config.get('default_remote', 'origin')
        remote = self.get_choice("Select default remote:", remotes, current_default)
        
        self.config['default_remote'] = remote
        self.save_config()
        self.print_success(f"Default remote set to: {remote}")
        
        input("Press Enter to continue...")
    
    def interactive_add_remote(self):
        """Add a new remote"""
        name = self.get_input("Remote name", "origin")
        if not name:
            return
    
        url = self.get_input("Remote URL")
        if not url:
            return
        
        if not self.validate_url(url):
            self.print_error("Invalid URL format!")
            input("Press Enter to continue...")
            return
    
        self.print_working(f"Adding remote '{name}'...")
        if not self.run_git_command(['git', 'remote', 'add', name, url]):
            input("Press Enter to continue...")
            return
    
        self.print_success(f"Remote '{name}' added successfully!")
        self.add_to_history('remote', f"Added remote {name}")
    
        # If this is the first remote, make it default
        remotes = self.get_remotes()
        if len(remotes) == 1:
            self.config['default_remote'] = name
            self.save_config()
            self.print_info(f"Set as default remote: {name}")
    
        input("Press Enter to continue...")

    def interactive_remove_remote(self):
        """Remove an existing remote"""
        remotes = self.get_remotes()
        if not remotes:
            self.print_info("No remotes to remove")
            input("Press Enter to continue...")
            return
        
        remote = self.get_choice("Select remote to remove:", remotes)
        
        if self.confirm(f"Are you sure you want to remove remote '{remote}'?", False):
            if self.run_git_command(['git', 'remote', 'remove', remote]):
                self.print_success(f"Remote '{remote}' removed successfully!")
                
                # Update default remote if removed
                if self.config.get('default_remote') == remote:
                    remaining_remotes = self.get_remotes()
                    if remaining_remotes:
                        self.config['default_remote'] = remaining_remotes[0]
                        self.save_config()
                        self.print_info(f"Default remote changed to: {remaining_remotes[0]}")
                    else:
                        self.config['default_remote'] = 'origin'
                        self.save_config()
        
        input("Press Enter to continue...")
    
    def interactive_list_remotes(self):
        """List all remotes with details"""
        self.clear_screen()
        print("🔗 All Remotes\n" + "=" * 15)
        self.run_git_command(['git', 'remote', '-v'])
        input("\nPress Enter to continue...")
    
    def interactive_change_remote_url(self):
        """Change URL of existing remote"""
        remotes = self.get_remotes()
        if not remotes:
            self.print_info("No remotes configured")
            input("Press Enter to continue...")
            return
        
        remote = self.get_choice("Select remote to modify:", remotes)
        current_url = self.run_git_command(['git', 'remote', 'get-url', remote], capture_output=True)
        
        print(f"Current URL: {current_url}")
        new_url = self.get_input("New URL")
        if not new_url:
            return
        
        if not self.validate_url(new_url):
            self.print_error("Invalid URL format!")
            input("Press Enter to continue...")
            return
        
        if self.run_git_command(['git', 'remote', 'set-url', remote, new_url]):
            self.print_success(f"URL for '{remote}' updated successfully!")
        
        input("Press Enter to continue...")
    
    def interactive_branch_menu(self):
        """Interactive branch operations menu"""
        while True:
            self.clear_screen()
            print("🌿 Branch Operations\n" + "=" * 25)
            
            current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
            if current_branch:
                print(f"Current branch: {current_branch}\n")
            
            options = [
                "Create new branch", "Switch to existing branch", "List all branches",
                "Delete branch", "Rename branch", "Back to main menu"
            ]
            
            choice = self.get_choice("Branch Operations:", options)
            
            handlers = {
                "Create new branch": self.interactive_create_branch,
                "Switch to existing branch": self.interactive_switch_branch,
                "List all branches": self.interactive_list_branches,
                "Delete branch": self.interactive_delete_branch,
                "Rename branch": self.interactive_rename_branch,
                "Back to main menu": lambda: None
            }
            
            for key, handler in handlers.items():
                if key in choice:
                    result = handler()
                    if key == "Back to main menu":
                        return
                    break
    
    def interactive_create_branch(self):
        """Interactive branch creation"""
        branch_name = self.get_input("Enter new branch name")
        if not branch_name:
            return
        
        if not self.validate_branch_name(branch_name):
            self.print_error("Invalid branch name! Avoid spaces and special characters.")
            input("Press Enter to continue...")
            return
        
        self.print_working(f"Creating new branch: {branch_name}")
        if self.run_git_command(['git', 'checkout', '-b', branch_name]):
            self.print_success(f"Created and switched to branch: {branch_name}")
            self.add_to_history('branch', f"Created branch {branch_name}")
        
        input("Press Enter to continue...")
    
    def interactive_switch_branch(self):
        """Interactive branch switching"""
        branches_output = self.run_git_command(['git', 'branch'], capture_output=True)
        if not branches_output:
            return
        
        branches = [b.strip().replace('* ', '') for b in branches_output.split('\n') if b.strip()]
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        
        if len(branches) > 1:
            branches = [b for b in branches if b != current_branch]
        
        if not branches:
            self.print_info("No other branches available")
            input("Press Enter to continue...")
            return
        
        branch = self.get_choice("Select branch to switch to:", branches)
        
        self.print_working(f"Switching to branch: {branch}")
        if self.run_git_command(['git', 'checkout', branch]):
            self.print_success(f"Switched to branch: {branch}")
            self.add_to_history('branch', f"Switched to {branch}")
        
        input("Press Enter to continue...")
    
    def interactive_list_branches(self):
        """Interactive branch listing"""
        self.clear_screen()
        print("🌿 All Branches\n" + "=" * 15)
        self.run_git_command(['git', 'branch', '-a'])
        input("\nPress Enter to continue...")
    
    def interactive_delete_branch(self):
        """Interactive branch deletion"""
        branches_output = self.run_git_command(['git', 'branch'], capture_output=True)
        if not branches_output:
            return
        
        branches = [b.strip().replace('* ', '') for b in branches_output.split('\n') if b.strip()]
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        
        if len(branches) > 1:
            branches = [b for b in branches if b != current_branch]
        
        if not branches:
            self.print_info("No branches available to delete")
            input("Press Enter to continue...")
            return
        
        branch = self.get_choice("Select branch to delete:", branches)
        
        if self.confirm(f"Are you sure you want to delete branch '{branch}'?", False):
            if self.run_git_command(['git', 'branch', '-d', branch]):
                self.print_success(f"Deleted branch: {branch}")
                self.add_to_history('branch', f"Deleted branch {branch}")
        
        input("Press Enter to continue...")
    
    def interactive_rename_branch(self):
        """Rename current or selected branch"""
        current_branch = self.run_git_command(['git', 'branch', '--show-current'], capture_output=True)
        
        if self.confirm(f"Rename current branch '{current_branch}'?", True):
            branch_to_rename = current_branch
        else:
            branches_output = self.run_git_command(['git', 'branch'], capture_output=True)
            branches = [b.strip().replace('* ', '') for b in branches_output.split('\n') if b.strip()]
            branch_to_rename = self.get_choice("Select branch to rename:", branches)
        
        new_name = self.get_input("Enter new branch name")
        if not new_name:
            return
        
        if not self.validate_branch_name(new_name):
            self.print_error("Invalid branch name!")
            input("Press Enter to continue...")
            return
        
        if self.run_git_command(['git', 'branch', '-m', branch_to_rename, new_name]):
            self.print_success(f"Branch renamed to: {new_name}")
            self.add_to_history('branch', f"Renamed {branch_to_rename} to {new_name}")
        
        input("Press Enter to continue...")
    
    def interactive_diff(self):
        """Interactive diff viewing"""
        self.clear_screen()
        
        diff_type = self.get_choice("What changes to view?", 
                                  ["Unstaged changes", "Staged changes", "Last commit"])
        
        if "Staged" in diff_type:
            print("📋 Staged changes:")
            self.run_git_command(['git', 'diff', '--cached'])
        elif "Last commit" in diff_type:
            print("📋 Last commit changes:")
            self.run_git_command(['git', 'show', 'HEAD'])
        else:
            print("📋 Unstaged changes:")
            self.run_git_command(['git', 'diff'])
        
        input("\nPress Enter to continue...")
    
    def interactive_log(self):
        """Interactive log viewing"""
        self.clear_screen()
        
        try:
            count = int(self.get_input("Number of commits to show", "10"))
        except ValueError:
            count = 10
        
        log_format = self.get_choice(
            "Log format:",
            ["Oneline", "Detailed", "Graph"]
        )
        
        print(f"📜 Last {count} commits:")
        
        if "Oneline" in log_format:
            self.run_git_command(['git', 'log', '--oneline', f'-{count}'])
        elif "Graph" in log_format:
            self.run_git_command(['git', 'log', '--oneline', '--graph', '--all', f'-{count}'])
        else:
            self.run_git_command(['git', 'log', f'-{count}'])
        
        input("\nPress Enter to continue...")
    
    def interactive_init(self):
        """Interactive repository initialization"""
        self.clear_screen()
        print("🎯 Initialize Repository\n" + "=" * 25)
        
        if self.confirm("Initialize git repository in current directory?", True):
            self.print_working("Initializing repository...")
            if not self.run_git_command(['git', 'init']):
                input("Press Enter to continue...")
                return
            
            if self.config['name'] and self.config['email']:
                self.run_git_command(['git', 'config', 'user.name', self.config['name']], show_output=False)
                self.run_git_command(['git', 'config', 'user.email', self.config['email']], show_output=False)
                self.print_info("Applied your saved configuration")
            
            if self.confirm("Add remote origin?", False):
                remote_url = self.get_input("Remote URL")
                if remote_url and self.validate_url(remote_url):
                    if self.run_git_command(['git', 'remote', 'add', 'origin', remote_url]):
                        self.print_success("Remote origin added")
                        self.config['default_remote'] = 'origin'
                        self.save_config()
            
            self.print_success("Repository initialized successfully!")
            self.add_to_history('init', "Initialized repository")
        
        input("Press Enter to continue...")
    
    def interactive_clone(self):
        """Interactive repository cloning"""
        self.clear_screen()
        print("📥 Clone Repository\n" + "=" * 20)
        
        url = self.get_input("Repository URL")
        if not url:
            return
        
        if not self.validate_url(url):
            self.print_error("Invalid URL format!")
            input("Press Enter to continue...")
            return
        
        directory = self.get_input("Directory name (optional)")
        
        cmd = ['git', 'clone', url]
        if directory:
            cmd.append(directory)
        
        self.print_working(f"Cloning repository: {url}")
        if self.run_git_command(cmd):
            self.print_success("Repository cloned successfully!")
            self.add_to_history('clone', f"Cloned {url}")
            
            if directory and self.confirm("Change to cloned directory?", True):
                try:
                    os.chdir(directory)
                    self.print_success(f"Changed to directory: {directory}")
                except FileNotFoundError:
                    self.print_error("Could not change directory")
        
        input("Press Enter to continue...")
    
    def interactive_config_menu(self):
        """Interactive configuration menu"""
        while True:
            self.clear_screen()
            print("⚙️ Configuration\n" + "=" * 20)
            print(f"Name: {self.config['name'] or 'Not set'}")
            print(f"Email: {self.config['email'] or 'Not set'}")
            print(f"Default Branch: {self.config['default_branch']}")
            print(f"Default Remote: {self.config['default_remote']}")
            print(f"Auto Push: {self.config['auto_push']}")
            print(f"Show Emoji: {self.config['show_emoji']}")
            print(f"Use Colors: {self.config.get('use_colors', True)}")
            print(f"Parallel Push: {self.config.get('parallel_push', True)}")
            print("-" * 30)
            
            options = [
                "Set Name", "Set Email", "Set Default Branch", "Set Default Remote",
                "Toggle Auto Push", "Toggle Emoji", "Toggle Colors", "Toggle Parallel Push",
                "Back to main menu"
            ]
            
            choice = self.get_choice("Configuration Options:", options)
            
            config_handlers = {
                "Set Name": lambda: self.update_config('name', self.get_input("Enter your name", self.config['name'])),
                "Set Email": lambda: self.update_config('email', self.get_input("Enter your email", self.config['email'])),
                "Set Default Branch": lambda: self.update_config('default_branch', self.get_input("Enter default branch", self.config['default_branch'])),
                "Set Default Remote": self.interactive_set_default_remote_config,
                "Toggle Auto Push": lambda: self.toggle_config('auto_push'),
                "Toggle Emoji": lambda: self.toggle_config('show_emoji'),
                "Toggle Colors": lambda: self.toggle_config('use_colors'),
                "Toggle Parallel Push": lambda: self.toggle_config('parallel_push'),
                "Back to main menu": lambda: None
            }
            
            for key, handler in config_handlers.items():
                if key in choice:
                    result = handler()
                    if key == "Back to main menu":
                        return
                    break
            
            if "Back to main menu" not in choice:
                time.sleep(1)
    
    def interactive_set_default_remote_config(self):
        """Set default remote from config menu"""
        if not self.is_git_repo():
            self.print_error("Not in a git repository")
            return
        
        remotes = self.get_remotes()
        if not remotes:
            self.print_info("No remotes configured in current repository")
            return
        
        current_default = self.config.get('default_remote', 'origin')
        remote = self.get_choice("Select default remote:", remotes, current_default)
        
        self.config['default_remote'] = remote
        self.save_config()
        self.print_success(f"Default remote set to: {remote}")
    
    def update_config(self, key: str, value: str):
        """Update configuration value"""
        if value:
            self.config[key] = value
            self.save_config()
            self.print_success(f"{key.replace('_', ' ').title()} updated!")
    
    def toggle_config(self, key: str):
        """Toggle boolean configuration value"""
        self.config[key] = not self.config[key]
        self.save_config()
        status = 'enabled' if self.config[key] else 'disabled'
        self.print_success(f"{key.replace('_', ' ').title()} {status}!")
    
    def show_help(self):
        """Show help information"""
        self.clear_screen()
        print("❓ Git Wrapper Help\n" + "=" * 25)
        print("""
🚀 Main Features:
• Interactive menus for all operations
• Multi-remote push support (single/multiple/all)
• Parallel push for faster multi-remote operations
• Remote management with default remote setting
• Branch operations and configuration management
• Stash operations for temporary changes
• Tag management for versioning
• Undo operations with safety warnings
• Command history tracking
• Colorized output for better readability

📤 Push Operations:
• Push to single remote (with remote selection)
• Push to multiple selected remotes
• Push to all configured remotes at once
• Parallel push option for speed
• Dry run mode to preview changes
• Visual feedback for multi-remote operations

📦 Stash Operations:
• Save current changes temporarily
• Pop/apply stashes when needed
• List and manage all stashes
• Clear stashes safely

🏷️  Tag Management:
• Create annotated or lightweight tags
• List all tags with messages
• Delete tags locally and remotely
• Push tags to remotes

↩️  Undo Operations:
• Undo last commit (soft/hard)
• Reset to specific commit
• View reflog for recovery
• Safety confirmations for destructive operations

⚡ Quick Commands:
• gw status    - Show repository status
• gw add       - Interactive file selection
• gw commit    - Quick commit with message
• gw sync      - Pull and push changes
• gw config    - Open configuration menu
• gw push      - Open push operations menu

🔗 Remote Management:
• Add/remove remotes with URL validation
• Set default remote for operations
• Change remote URLs
• Fetch from remotes
• Multi-remote push capabilities

💡 Tips:
• Use Ctrl+C to exit at any time
• Default values are shown in [brackets]
• All destructive operations ask for confirmation
• Multi-remote operations show individual results
• Set a default remote to speed up operations
• Enable parallel push for faster multi-remote operations
• Command history is saved automatically
• Colors can be toggled in configuration

Created by Johannes Nguyen
Enhanced with advanced features and safety improvements
        """)
        input("\nPress Enter to continue...")
    
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')

def main():
    """Main entry point"""
    git = InteractiveGitWrapper()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        handlers = {
            'status': git.interactive_status,
            'add': git.interactive_add_files,
            'commit': git.interactive_commit,
            'sync': git.interactive_sync,
            'push': git.interactive_push_menu,
            'config': git.interactive_config_menu,
            'stash': git.interactive_stash_menu,
            'tag': git.interactive_tag_menu,
            'undo': git.interactive_undo_menu,
            'history': git.interactive_search_history
        }
        
        if command in handlers:
            handlers[command]()
        else:
            print(f"Unknown command: {command}")
            print("Available commands: status, add, commit, sync, push, config, stash, tag, undo, history")
            print("Or run 'gw' without arguments for interactive mode")
    else:
        try:
            git.show_main_menu()
        except KeyboardInterrupt:
            print("\n\nGoodbye! 👋")

if __name__ == '__main__':
    main()

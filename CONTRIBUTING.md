# Contributing to GitWrapper

Thank you for your interest in contributing to GitWrapper!

## Development Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/gitwrapper.git
   cd gitwrapper
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install in development mode**
   ```bash
   pip install -e ".[dev]"
   ```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/gitwrapper --cov-report=html

# Run specific test file
pytest tests/test_config.py

# Run specific test
pytest tests/test_config.py::TestConfiguration::test_default_config
```

## Code Style

We use:
- **Black** for code formatting
- **Flake8** for linting
- **MyPy** for type checking

```bash
# Format code
black src/ tests/

# Check formatting
black --check src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=100

# Type check
mypy src/ --ignore-missing-imports
```

## Project Structure

```
gitwrapper/
├── src/
│   └── gitwrapper/
│       ├── __init__.py
│       └── cli.py          # Main application code
├── tests/
│   ├── __init__.py
│   ├── test_config.py      # Configuration tests
│   ├── test_validation.py  # Input validation tests
│   ├── test_colors.py      # Color output tests
│   ├── test_history.py     # Command history tests
│   └── test_utils.py       # Utility function tests
├── setup.py
├── pyproject.toml
└── README.md
```

## Adding New Features

1. Create a new branch
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Write tests first (TDD approach)
   ```bash
   # Add tests in tests/test_*.py
   pytest tests/test_your_feature.py
   ```

3. Implement the feature

4. Ensure all tests pass
   ```bash
   pytest
   ```

5. Format and lint your code
   ```bash
   black src/ tests/
   flake8 src/ tests/
   ```

6. Commit and push
   ```bash
   git add .
   git commit -m "Add: your feature description"
   git push origin feature/your-feature-name
   ```

7. Create a Pull Request

## Testing Guidelines

- Write tests for all new features
- Maintain or improve code coverage
- Use descriptive test names
- Test both success and failure cases
- Mock external dependencies (git commands, file I/O)

## Commit Message Format

```
Type: Brief description

Detailed description if needed

Types:
- Add: New feature
- Fix: Bug fix
- Update: Changes to existing features
- Refactor: Code restructuring
- Docs: Documentation changes
- Test: Test additions or changes
```

## Questions?

Feel free to open an issue for any questions or concerns!

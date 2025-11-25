# CI/CD Setup

## GitHub Actions Workflows

### 1. test.yml - Basic Testing
**Purpose**: Fast, simple test execution  
**Triggers**: Push to main/develop, Pull Requests  
**Matrix**: 
- OS: Ubuntu, macOS
- Python: 3.9, 3.10, 3.11, 3.12
- Total: 8 configurations

**Steps**:
1. Checkout code
2. Set up Python
3. Install package (`pip install -e .`)
4. Install pytest
5. Run tests (`pytest tests/ -v`)

**No coverage** - Runs faster, simpler setup

### 2. ci.yml - Complete CI Pipeline
**Purpose**: Comprehensive testing with coverage and linting  
**Triggers**: Push to main/develop, Pull Requests

**Jobs**:

#### Test Job
- Matrix: Ubuntu + macOS × Python 3.9-3.12
- Runs all tests
- No coverage (for speed)

#### Coverage Job
- Single run on Ubuntu + Python 3.11
- Generates coverage report
- Uploads to Codecov
- Includes `pytest-cov`

#### Lint Job
- Code formatting check (Black)
- Linting (Flake8)
- Type checking (MyPy)
- Non-blocking (uses `|| true`)

## Local Testing

### Basic Tests
```bash
# Install package
pip install -e .

# Install pytest
pip install pytest

# Run tests
pytest tests/ -v
```

### With Coverage
```bash
# Install with coverage
pip install pytest pytest-cov

# Run with coverage
pytest tests/ -v --cov=src/gitwrapper --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Code Quality
```bash
# Install tools
pip install black flake8 mypy

# Format code
black src/ tests/

# Lint
flake8 src/ tests/ --max-line-length=100 --ignore=E203,W503

# Type check
mypy src/ --ignore-missing-imports
```

## Configuration Files

### pyproject.toml
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v"  # No coverage by default
```

### requirements.txt
- Empty (no runtime dependencies)

### requirements-dev.txt
```
pytest>=7.0.0
pytest-cov>=4.0.0
black>=22.0.0
flake8>=5.0.0
mypy>=0.990
```

## Troubleshooting

### Error: unrecognized arguments: --cov
**Problem**: pytest-cov not installed  
**Solution**: 
```bash
pip install pytest-cov
```

Or run without coverage:
```bash
pytest tests/ -v
```

### Error: No module named 'gitwrapper'
**Problem**: Package not installed  
**Solution**:
```bash
pip install -e .
```

### Error: Git not available
**Problem**: Git not in PATH  
**Solution**: Install Git or skip git-dependent tests

## CI/CD Best Practices

### Fast Feedback
- Basic tests run without coverage (faster)
- Coverage only on one configuration
- Linting is non-blocking

### Matrix Strategy
- Test on multiple OS (Ubuntu, macOS)
- Test on multiple Python versions (3.9-3.12)
- Use `fail-fast: false` to see all failures

### Dependencies
- Install package first: `pip install -e .`
- Install test tools separately
- Keep requirements minimal

## Workflow Status

Check workflow status:
- GitHub Actions tab in repository
- Badge in README (optional)

## Adding Badges

Add to README.md:
```markdown
![Tests](https://github.com/username/gitwrapper/workflows/Tests/badge.svg)
![CI](https://github.com/username/gitwrapper/workflows/CI/badge.svg)
```

## Future Improvements

1. **Add Windows testing** (requires WSL setup)
2. **Add integration tests** (test with real git repos)
3. **Add performance tests** (benchmark operations)
4. **Add security scanning** (bandit, safety)
5. **Add dependency updates** (dependabot)
6. **Add release automation** (publish to PyPI on tag)

## Running Specific Workflows

### Locally
```bash
# All tests
pytest

# Specific test file
pytest tests/test_config.py

# Specific test
pytest tests/test_config.py::TestConfiguration::test_default_config

# With coverage
pytest --cov=src/gitwrapper --cov-report=html
```

### On GitHub
- Push to main/develop branch
- Create pull request
- Manually trigger from Actions tab

## Summary

✅ **test.yml**: Fast, simple testing (8 configurations)  
✅ **ci.yml**: Complete pipeline with coverage and linting  
✅ **Local testing**: Works without coverage tools  
✅ **No runtime dependencies**: Only stdlib  
✅ **Dev dependencies**: Optional, in requirements-dev.txt  

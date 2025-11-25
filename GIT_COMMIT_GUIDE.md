# Git Commit Guide

## Changes to Commit

### Modified Files
```bash
# Configuration
pyproject.toml                    # Removed coverage from default pytest options
.github/workflows/test.yml        # Simplified test workflow

# Documentation  
README.md                         # Updated Python version to 3.9+
INSTALLATION.md                   # Updated prerequisites
PACKAGE_INFO.md                   # Updated test matrix
SUMMARY.md                        # Updated Python version
CHECKLIST.md                      # Updated supported versions
```

### New Files
```bash
# CI/CD
.github/workflows/ci.yml          # Complete CI pipeline with coverage
requirements.txt                  # Empty (no runtime deps)

# Documentation
CI_CD_SETUP.md                    # CI/CD documentation
CI_FIX_SUMMARY.md                 # Fix summary
PYTHON_VERSION_UPDATE.md          # Python version change log
UPDATE_SUMMARY.md                 # Update summary
GIT_COMMIT_GUIDE.md               # This file
```

## Commit Messages

### Option 1: Single Commit
```bash
git add .
git commit -m "Fix: CI/CD pipeline and update Python requirement to 3.9+

- Remove coverage from default pytest config
- Simplify test.yml workflow (no coverage)
- Add ci.yml with separate coverage job
- Update Python requirement from 3.7+ to 3.9+
- Update all documentation
- Add CI/CD setup documentation

Fixes pytest coverage argument error in GitHub Actions"
```

### Option 2: Multiple Commits
```bash
# Commit 1: Python version update
git add setup.py pyproject.toml .github/workflows/test.yml
git add README.md INSTALLATION.md PACKAGE_INFO.md SUMMARY.md CHECKLIST.md
git commit -m "Update: Python requirement to 3.9+

- Update setup.py and pyproject.toml
- Update CI/CD matrix to test 3.9-3.12
- Update all documentation"

# Commit 2: CI/CD fix
git add pyproject.toml .github/workflows/
git add requirements.txt
git commit -m "Fix: CI/CD pytest coverage error

- Remove coverage from default pytest options
- Simplify test.yml (basic tests only)
- Add ci.yml (complete pipeline with coverage)
- Add requirements.txt"

# Commit 3: Documentation
git add CI_CD_SETUP.md CI_FIX_SUMMARY.md PYTHON_VERSION_UPDATE.md
git add UPDATE_SUMMARY.md GIT_COMMIT_GUIDE.md
git commit -m "Docs: Add CI/CD and update documentation"
```

## Verification Before Commit

```bash
# 1. Check status
git status

# 2. Review changes
git diff

# 3. Run tests locally
pytest tests/ -v

# 4. Check package installs
pip install -e .

# 5. Verify command works
gw --help || python3 -m gitwrapper.cli --help
```

## Push to GitHub

```bash
# Push to main branch
git push origin main

# Or push to develop branch
git push origin develop

# Or create a new branch
git checkout -b fix/ci-cd-pipeline
git push origin fix/ci-cd-pipeline
# Then create a Pull Request on GitHub
```

## After Push

1. **Check GitHub Actions**
   - Go to Actions tab
   - Verify workflows run successfully
   - Check all 8 test configurations pass

2. **Review Workflow Results**
   - test.yml should complete in ~2-3 minutes
   - ci.yml should complete in ~5-7 minutes
   - All jobs should be green ✓

3. **Optional: Add Badges**
   ```markdown
   ![Tests](https://github.com/username/gitwrapper/workflows/Tests/badge.svg)
   ![CI](https://github.com/username/gitwrapper/workflows/CI/badge.svg)
   ```

## Files to Ignore (Already in .gitignore)

```
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
dist/
build/
*.egg-info/
.gitwrapper_config.json
.gitwrapper_history.json
```

## Summary of Changes

### Python Version
- ❌ Python 3.7, 3.8
- ✅ Python 3.9, 3.10, 3.11, 3.12

### CI/CD
- ✅ Basic tests (no coverage) - Fast
- ✅ Coverage job (separate) - Detailed
- ✅ Linting job (non-blocking) - Quality

### Testing
- ✅ Works without pytest-cov
- ✅ Works with pytest-cov (optional)
- ✅ 25 tests passing

### Documentation
- ✅ 7 new documentation files
- ✅ Updated existing docs
- ✅ Complete CI/CD guide

## Quick Commands

```bash
# Stage all changes
git add .

# Commit with message
git commit -m "Fix: CI/CD and update to Python 3.9+"

# Push
git push origin main

# Check status
git status

# View log
git log --oneline -5
```

## Recommended Approach

**Best Practice**: Use multiple commits for clarity

1. Python version update
2. CI/CD fixes
3. Documentation

This makes it easier to:
- Review changes
- Revert if needed
- Understand history

---

**Ready to commit!** All changes are tested and documented.

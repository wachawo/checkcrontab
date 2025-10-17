# Checkcrontab - Crontab Syntax Checker

**Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.**

Checkcrontab is a Python package for validating crontab file syntax. It provides cross-platform support (Linux, macOS, Windows) with comprehensive validation of time fields, user existence, dangerous commands, and special keywords.

## Working Effectively

### Bootstrap and Setup
```bash
# Install development dependencies - takes 1 second if already cached
pip install pytest flake8 mypy ruff

# Install the package in development mode - takes 5 seconds
# NOTE: May fail due to network limitations with "Read timed out" error
pip install -e .

# If pip install -e . fails due to network issues, the package may still be usable
# Verify with: python -c "import checkcrontab; print(checkcrontab.__version__)"

# Optional: Install pre-commit (may fail due to network limitations)
pip install pre-commit
pre-commit install
```

### Build and Test
```bash
# Run linting - takes 0.01 seconds, NEVER CANCEL
ruff check . --output-format=github

# Run type checking - takes 0.1-1.5 seconds, NEVER CANCEL
mypy .

# Check code formatting - takes 0.01 seconds, NEVER CANCEL
ruff format --check .

# Run all tests - takes 0.4-0.6 seconds, NEVER CANCEL
pytest

# Test CLI functionality - takes 0.05-0.08 seconds each
python -m checkcrontab examples/system_valid.txt
python -m checkcrontab examples/user_valid.txt
checkcrontab --help
checkcrontab --version
```

### Network Limitations
⚠️ **IMPORTANT**: Some operations fail due to network timeouts to PyPI:
- `pip install -e .` - may fail with "Read timed out" error after 16 seconds
- `pre-commit run --all-files` - fails due to PyPI timeout after 18 seconds
- `python -m build` - fails due to PyPI timeout after 16 seconds
- **Workaround**: If previously installed, packages remain usable despite install failures
- **Always document**: "fails due to network limitations" if encountered

## Validation

### Always validate changes with these scenarios:
1. **Basic CLI functionality:**
   ```bash
   python -m checkcrontab examples/system_valid.txt  # Should exit 0
   python -m checkcrontab examples/system_incorrect.txt  # Should exit 1 with errors
   python -m checkcrontab examples/user_valid.txt  # Should exit 0
   python -m checkcrontab examples/user_incorrect.txt  # Should exit 1 with errors
   ```

2. **Debug output validation:**
   ```bash
   python -m checkcrontab --debug examples/user_valid.txt
   # Should show detailed line-by-line validation info
   ```

3. **Error handling validation:**
   ```bash
   python -m checkcrontab examples/system_incorrect.txt
   # Should show specific error messages for each invalid line
   ```

4. **Module import validation:**
   ```bash
   python -c "import checkcrontab; print(checkcrontab.__version__)"
   # Should print version number (currently 0.0.5)
   ```

### Always run before committing:
```bash
ruff check .
mypy .
pytest
```

## Common Tasks

### Repository Structure
```
checkcrontab/
├── checkcrontab/           # Main package
│   ├── __init__.py        # Package initialization and version
│   ├── __main__.py        # CLI entry point
│   ├── main.py           # Main application logic
│   ├── checker.py        # Core validation logic
│   └── logging_config.py # Colored logging configuration
├── examples/             # Test crontab files
│   ├── system_valid.txt   # Valid system crontab examples
│   ├── system_incorrect.txt  # Invalid system crontab examples
│   ├── user_valid.txt     # Valid user crontab examples
│   └── user_incorrect.txt    # Invalid user crontab examples
├── test_main.py          # Test suite (35 tests)
├── pyproject.toml        # Package configuration
├── .pre-commit-config.yaml  # Pre-commit hooks
└── README.md             # Documentation
```

### Key Files to Monitor
- **checkcrontab/checker.py** - Core validation logic, check after making validation changes
- **checkcrontab/main.py** - CLI interface and file processing
- **test_main.py** - Comprehensive test suite covering all validation scenarios
- **examples/** - Test files used in CI and manual validation

### Development Workflow
1. Make changes to code
2. Run `ruff check . && mypy . && pytest` to validate
3. Test with example files: `python -m checkcrontab examples/system_valid.txt`
4. For new features, add tests to `test_main.py`
5. Update version in `checkcrontab/__init__.py` if needed

### CI Information
- **GitHub Actions**: `.github/workflows/ci.yml`
- **Platforms tested**: Ubuntu, Windows, macOS
- **Python versions**: 3.8, 3.9, 3.10, 3.11, 3.12, 3.13
- **CI steps**: Install deps, lint (ruff), type-check (mypy), test (pytest), CLI validation

### Common Commands Reference
```bash
# Help and version
checkcrontab --help
checkcrontab --version

# Basic usage
checkcrontab                        # Check system crontab (Linux only)
checkcrontab /path/to/crontab      # Check specific file
checkcrontab username              # Check user's crontab

# Advanced usage
checkcrontab -S system.cron -U user.cron  # Explicit file types
checkcrontab -u user1 -u user2            # Multiple users
checkcrontab --debug file.cron             # Debug output
checkcrontab --no-colors file.cron         # Disable colors

# Development
python -m checkcrontab file.cron    # Run from source
```

### Package Information
- **Entry point**: `checkcrontab.main:main`
- **Current version**: 0.0.5 (in `checkcrontab/__init__.py`)
- **Dependencies**: None (runtime), pytest/ruff/mypy/flake8 (development)
- **Build system**: setuptools + pyproject.toml
- **License**: MIT

### Features Validated
✅ Cross-platform support (Linux, macOS, Windows)
✅ System and user crontab validation
✅ Time field validation (minutes, hours, days, months, weekdays)
✅ User existence validation (Linux/macOS)
✅ Dangerous command detection
✅ Special keyword support (@reboot, @daily, etc.)
✅ Multi-line command support
✅ Environment variable handling
✅ Colored output with Windows ANSI support

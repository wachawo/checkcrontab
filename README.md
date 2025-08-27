## Checkcrontab - check syntax in crontab files

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

A Python script for checking syntax of crontab files. Cross-platform support for Linux, macOS, and Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requirements

- **Python 3.7 or higher**
- **Linux**: Linux system with systemctl (for daemon checks), read access to `/etc/crontab`
- **macOS**: Unix system with read access to `/etc/crontab` (systemctl not available)
- **Windows**: No additional requirements (file-based validation only)

### Platform Support

**Linux (Full Support):**
- ✅ System crontab validation (`/etc/crontab`)
- ✅ User crontab validation (via `crontab -l -u username`)
- ✅ User existence validation
- ✅ Daemon/service checks via systemctl
- ✅ All crontab syntax features
- ✅ File permissions validation
- ✅ Cron daemon status checks

**macOS (Partial Support):**
- ✅ System crontab validation (`/etc/crontab`)
- ✅ User crontab validation (via `crontab -l -u username`)
- ✅ User existence validation
- ❌ Daemon/service checks (systemctl not available)
- ✅ All crontab syntax features
- ✅ File permissions validation
- ❌ Cron daemon status checks

**Windows (Limited Support):**
- ✅ File-based crontab syntax validation
- ❌ User existence checks (no user management integration)
- ❌ System crontab access (no `/etc/crontab`)
- ❌ Daemon/service checks (no systemctl)
- ✅ All crontab syntax features supported
- ❌ File permissions validation (no Unix permissions)
- ❌ Cron daemon status checks (no cron daemon)

### Installation

```bash
pip3 install checkcrontab
```

Or from GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Usage

```bash
# Check system crontab (Linux/macOS only)
checkcrontab

# Check crontab file
checkcrontab /etc/crontab

# Check user crontab (Linux/macOS only)
checkcrontab username

# Check with explicit type flags
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Show help
checkcrontab --help

# Show version
checkcrontab --version
```

**Platform-specific behavior:**
- **Linux**: Full functionality including daemon checks and user validation
- **macOS**: Full functionality except daemon checks (systemctl not available)
- **Windows**: File-based validation only, no system integration

### JSON Output
For machine-readable output, use the `--format json` flag:

```bash
checkcrontab --format json examples/user_valid.txt
```

#### SARIF Output
For SARIF output, use the `--format sarif` flag:

```bash
checkcrontab --format sarif examples/user_valid.txt
```

Example JSON output:

```json
{
  "success": true,
  "total_files": 2,
  "total_rows": 27,
  "total_rows_errors": 0,
  "total_errors": 0,
  "files": [
    {
      "file": "/etc/crontab",
      "is_system_crontab": true,
      "rows": 5,
      "rows_errors": 0,
      "errors_count": 0,
      "errors": [],
      "success": true
    },
    {
      "file": "examples/user_valid.txt",
      "is_system_crontab": false,
      "rows": 22,
      "rows_errors": 0,
      "errors_count": 0,
      "errors": [],
      "success": true
    }
  ]
}
```

### Exit codes

| Code | Meaning |
|------|---------|
| 0    | No errors (warnings allowed). With `--exit-zero` always 0. |
| 1    | Findings present: any error, or any warning when `--strict` is set. |
| 2    | Runtime/usage error (unexpected failure, bad CLI args, etc.). |

### Command Line Options

- `-S, --system` - System crontab files
- `-U, --user` - User crontab files
- `-u, --username` - Usernames to check
- `-v, --version` - Show version
- `-d, --debug` - Debug output
- `-n, --no-colors` - Disable colored output
- `--format {text,json,sarif}` - Output results in JSON format
- `--strict` - Treat warnings as errors
- `--exit-zero` - Always return exit code 0

### Features

- **Cross-platform syntax validation** (Linux, macOS, Windows)
- **Platform-specific features:**
  - **Linux/macOS**: System and user crontab validation, user existence checks, daemon validation
  - **Windows**: File-based validation only
- **Time field validation** (minutes, hours, days, months, weekdays)
- **Dangerous command detection**
- **Special keyword support** (@reboot, @daily, etc.)
- **Multi-line command support**

**[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Comprehensive guide to supported syntax, valid values, examples, and error messages.

### Development Tools

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Usage with pre-commit

You can use checkcrontab as a pre-commit hook in your projects:

1. Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Use the latest version
    hooks:
      - id: checkcrontab
        files: \.(cron|crontab|tab|conf)$
        exclude: (\.git|node_modules|__pycache__)/
        args: [--format, json, --strict]
```

2. Install pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. The hook will automatically check all `.cron`, `.crontab`, and `.tab` files in your repository.

### License

MIT License

## Checkcrontab - check syntax in crontab files

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

A Python script for checking syntax of crontab files. Cross-platform support for Linux, macOS, and Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requirements

- **Python 3.7 or higher**
- Linux/Unix system with systemctl (for daemon checks)
- Read access to `/etc/crontab` (on Linux)

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
# Check system crontab (Linux only)
checkcrontab

# Check crontab file
checkcrontab /etc/crontab

# Check user crontab
checkcrontab username

# Check with explicit type flags
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Show help
checkcrontab --help

# Show version
checkcrontab --version
```

### Command Line Options

- `-S, --system` - System crontab files
- `-U, --user` - User crontab files
- `-u, --username` - Usernames to check
- `-v, --version` - Show version
- `-d, --debug` - Debug output
- `-n, --no-colors` - Disable colored output

### Features

- **Cross-platform support** (Linux, macOS, Windows)
- **System and user crontab validation**
- **Time field validation** (minutes, hours, days, months, weekdays)
- **User existence validation** (Linux/macOS)
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

### License

MIT License

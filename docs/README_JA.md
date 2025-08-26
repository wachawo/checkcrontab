## Checkcrontab - check syntax in crontab files

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

A Python script for checking syntax of crontab files. Cross-platform support for Linux, macOS, and Windows.

[English](../README.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [Русский](README_RU.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

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
# Check system crontab
checkcrontab

# Check crontab file
checkcrontab /etc/crontab

# Check user crontab
checkcrontab username

# Show help
checkcrontab --help
```

### Development Tools

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### License

MIT License

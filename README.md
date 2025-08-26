## Checkcrontab - check syntax in crontab files

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

A Python script for checking syntax of crontab files in Linux.

[English](README.md) | [Español](docs/README_ES.md) | [Português](docs/README_PT.md) | [Français](docs/README_FR.md) | [Deutsch](docs/README_DE.md) | [Italiano](docs/README_IT.md) | [Русский](docs/README_RU.md) | [中文](docs/README_ZH.md) | [日本語](docs/README_JA.md) | [हिन्दी](docs/README_HI.md)

### Requirements

- **Python 3.7 or higher**
- Linux/Unix system with systemctl
- Read access to `/etc/crontab`

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
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### License

MIT License

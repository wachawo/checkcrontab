## Checkcrontab - Crontab-Datei-Validator
[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Python-Skript zur Überprüfung der Syntax und Korrektheit von Crontab-Dateien in Linux/Unix-Systemen.

**Übersetzungen:** [English](../README.md) | [Русский](README_RU.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

### Anforderungen

- **Python 3.8 oder höher**
- Linux/Unix-System mit systemctl
- Lesezugriff auf `/etc/crontab`

### Installation

```bash
pip3 install checkcrontab
```

Oder von GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Verwendung

```bash
# System-Crontab überprüfen
checkcrontab

# Crontab-Datei überprüfen
checkcrontab /etc/crontab

# Benutzer-Crontab überprüfen
checkcrontab username

# Hilfe anzeigen
checkcrontab --help
```

### Entwicklungswerkzeuge

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Lizenz

MIT License

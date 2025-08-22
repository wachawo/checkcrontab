## Checkcrontab - Crontab-Datei-Validator
[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Python-Skript zur Überprüfung der Syntax und Korrektheit von Crontab-Dateien in Linux/Unix-Systemen.

**Übersetzungen:** [English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

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

## Checkcrontab - Syntax in crontab-Dateien prüfen

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Ein Python-Skript zur Überprüfung der Syntax von crontab-Dateien. Plattformübergreifende Unterstützung für Linux, macOS und Windows.

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | **[Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md)** | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Anforderungen

- **Python 3.7 oder höher**
- Linux/Unix-System mit systemctl (für Daemon-Prüfungen)
- Lesezugriff auf `/etc/crontab` (unter Linux)

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
# System-crontab prüfen (nur Linux)
checkcrontab

# crontab-Datei prüfen
checkcrontab /etc/crontab

# Benutzer-crontab prüfen
checkcrontab username

# Mit expliziten Typ-Flags prüfen
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Hilfe anzeigen
checkcrontab --help

# Version anzeigen
checkcrontab --version
```

### Kommandozeilen-Optionen

- `-S, --system` - System-crontab-Dateien
- `-U, --user` - Benutzer-crontab-Dateien
- `-u, --username` - Zu prüfende Benutzernamen
- `-v, --version` - Version anzeigen
- `-d, --debug` - Debug-Ausgabe
- `-n, --no-colors` - Farbige Ausgabe deaktivieren

### Funktionen

- **Plattformübergreifende Unterstützung** (Linux, macOS, Windows)
- **System- und Benutzer-crontab-Validierung**
- **Zeitfeld-Validierung** (Minuten, Stunden, Tage, Monate, Wochentage)
- **Benutzer-Existenz-Validierung** (Linux/macOS)
- **Gefährliche Befehle erkennen**
- **Spezielle Schlüsselwort-Unterstützung** (@reboot, @daily, usw.)
- **Mehrzeilen-Befehl-Unterstützung**

**[Funktions-Dokumentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Umfassender Leitfaden zu unterstützter Syntax, gültigen Werten, Beispielen und Fehlermeldungen.

### Entwicklungstools

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Lizenz

MIT-Lizenz

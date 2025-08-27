## Checkcrontab - Syntax in crontab-Dateien überprüfen

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

Ein Python-Skript zur Überprüfung der Syntax von crontab-Dateien. Plattformübergreifende Unterstützung für Linux, macOS und Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | **[Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md)** | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Anforderungen

- **Python 3.7 oder höher**
- **Linux/macOS**: Linux/Unix-System mit systemctl (für Daemon-Prüfungen), Lesezugriff auf `/etc/crontab`
- **Windows**: Keine zusätzlichen Anforderungen (nur dateibasierte Validierung)

### Plattformunterstützung

**Linux/macOS (Vollständige Unterstützung):**
- System-crontab-Validierung (`/etc/crontab`)
- Benutzer-crontab-Validierung (über `crontab -l -u username`)
- Benutzerexistenz-Validierung
- Daemon/Service-Prüfungen über systemctl
- Alle crontab-Syntax-Funktionen

**Windows (Eingeschränkte Unterstützung):**
- Dateibasierte crontab-Syntax-Validierung
- Keine Benutzerexistenz-Prüfungen
- Kein Zugriff auf System-crontab
- Keine Daemon/Service-Prüfungen
- Alle crontab-Syntax-Funktionen unterstützt

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

# Crontab-Datei prüfen
checkcrontab /etc/crontab

# Benutzer-crontab prüfen
checkcrontab username
# Strenger Modus (Warnungen als Fehler behandeln)
checkcrontab --strict examples/user_valid.txt

# Immer mit Erfolgscode beenden
checkcrontab --exit-zero examples/user_valid.txt

# Strenger Modus (Warnungen als Fehler behandeln)
checkcrontab --strict examples/user_valid.txt

# Immer mit Erfolgscode beenden
checkcrontab --exit-zero examples/user_valid.txt


# Mit expliziten Typ-Flags prüfen
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Hilfe anzeigen
checkcrontab --help

# Version anzeigen
checkcrontab --version
# Strenger Modus (Warnungen als Fehler behandeln)
checkcrontab --strict examples/user_valid.txt

# Immer mit Erfolgscode beenden
checkcrontab --exit-zero examples/user_valid.txt

# Strenger Modus (Warnungen als Fehler behandeln)
checkcrontab --strict examples/user_valid.txt

# Immer mit Erfolgscode beenden
checkcrontab --exit-zero examples/user_valid.txt

```

### JSON-Ausgabe

Für maschinenlesbare Ausgabe verwenden Sie das `--format json`-Flag:

```bash
checkcrontab --format json examples/user_valid.txt
```

Beispiel JSON-Ausgabe:

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

### Kommandozeilenoptionen

- `-S, --system` - System-crontab-Dateien
- `-U, --user` - Benutzer-crontab-Dateien
- `-u, --username` - Zu prüfende Benutzernamen
- `-v, --version` - Version anzeigen
- `-d, --debug` - Debug-Ausgabe
- `-n, --no-colors` - Farbige Ausgabe deaktivieren
- `--format {text,json,sarif}` - Ausgabeformat (Standard: text)
- `--strict` - Warnungen als Fehler behandeln
- `--exit-zero` - Immer mit Code 0 beenden

### Funktionen

- **Plattformübergreifende Syntax-Validierung** (Linux, macOS, Windows)
- **Plattformspezifische Funktionen:**
  - **Linux/macOS**: System- und Benutzer-crontab-Validierung, Benutzerexistenz-Prüfung, Daemon-Validierung
  - **Windows**: Nur dateibasierte Validierung
- **Zeitfeld-Validierung** (Minuten, Stunden, Tage, Monate, Wochentage)
- **Gefährliche Befehle erkennen**
- **Unterstützung für spezielle Schlüsselwörter** (@reboot, @daily, etc.)
- **Unterstützung für mehrzeilige Befehle**

### Dokumentation

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Detaillierte Dokumentation der Funktionen und Fähigkeiten

### Entwicklungstools

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Verwendung mit pre-commit

Sie können checkcrontab als pre-commit-Hook in Ihren Projekten verwenden:

1. Fügen Sie zu Ihrer `.pre-commit-config.yaml` hinzu:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Verwenden Sie die neueste Version
    hooks:
      - id: checkcrontab
```

2. Installieren Sie pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. Der Hook überprüft automatisch alle `.cron`, `.crontab` und `.tab` Dateien in Ihrem Repository.

### Lizenz

MIT License

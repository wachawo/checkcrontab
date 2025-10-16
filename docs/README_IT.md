## Checkcrontab - verifica la sintassi nei file crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/main/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Uno script Python per controllare la sintassi dei file crontab. Supporto multipiattaforma per Linux, macOS e Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | **[Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md)** | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisiti

- **Python 3.7 o superiore**
- **Linux/macOS**: Sistema Linux/Unix con systemctl (per controlli daemon), accesso in lettura a `/etc/crontab`
- **Windows**: Nessun requisito aggiuntivo (solo validazione basata su file)

### Supporto piattaforme

**Linux/macOS (Supporto completo):**
- Validazione crontab di sistema (`/etc/crontab`)
- Validazione crontab utente (via `crontab -l -u username`)
- Validazione esistenza utente
- Controlli daemon/servizi via systemctl
- Tutte le funzionalità di sintassi crontab

**Windows (Supporto limitato):**
- Validazione sintassi crontab basata su file
- Nessun controllo esistenza utente
- Nessun accesso al crontab di sistema
- Nessun controllo daemon/servizi
- Tutte le funzionalità di sintassi crontab supportate

### Installazione

```bash
pip3 install checkcrontab
```

O da GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Utilizzo

```bash
# Controlla il crontab di sistema (solo Linux/macOS)
checkcrontab

# Controlla un file crontab
checkcrontab /etc/crontab

# Controlla il crontab di un utente (solo Linux/macOS)
checkcrontab username

# Controlla con flag di tipo espliciti
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Controlla tutti i crontab di una directory
checkcrontab /etc/cron.d

# Mostra l'aiuto
checkcrontab --help

# Mostra la versione
checkcrontab --version
```

### Output JSON

Per output leggibile da macchina, usa il flag `--format json`:

```bash
checkcrontab --format json examples/user_valid.txt
```

Esempio output JSON:

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

### Opzioni riga di comando

- `-S, --system` - File crontab di sistema
- `-U, --user` - File crontab utente
- `-u, --username` - Nomi utente da controllare
- `-v, --version` - Mostra versione
- `-d, --debug` - Output debug
- `-n, --no-colors` - Disabilita output colorato
- `--format {text,json,sarif}` - Formato di output (predefinito: text)
- `--strict` - Tratta gli avvisi come errori
- `--exit-zero` - Esci sempre con codice 0

### Funzionalità

- **Validazione sintassi multipiattaforma** (Linux, macOS, Windows)
- **Funzionalità specifiche per piattaforma:**
  - **Linux/macOS**: Validazione crontab di sistema e utente, verifica esistenza utente, validazione daemon
  - **Windows**: Solo validazione basata su file
- **Validazione campi temporali** (minuti, ore, giorni, mesi, giorni della settimana)
- **Rilevamento comandi pericolosi**
- **Supporto parole chiave speciali** (@reboot, @daily, ecc.)
- **Supporto comandi multi-riga**

### Documentazione

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Documentazione dettagliata delle funzionalità e capacità

### Strumenti di sviluppo

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Utilizzo con pre-commit

Puoi usare checkcrontab come hook pre-commit nei tuoi progetti:

1. Aggiungi al tuo `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Usa l'ultima versione
    hooks:
      - id: checkcrontab
```

2. Installa pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. L'hook controllerà automaticamente tutti i file `.cron`, `.crontab` e `.tab` nel tuo repository.

### Licenza

MIT License

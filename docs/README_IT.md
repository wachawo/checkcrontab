## Checkcrontab - controlla la sintassi nei file crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Uno script Python per controllare la sintassi dei file crontab. Supporto multipiattaforma per Linux, macOS e Windows.

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisiti

- **Python 3.7 o superiore**
- Sistema Linux/Unix con systemctl (per controlli daemon)
- Accesso in lettura a `/etc/crontab` (su Linux)

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
# Controlla crontab di sistema (solo Linux)
checkcrontab

# Controlla file crontab
checkcrontab /etc/crontab

# Controlla crontab utente
checkcrontab username

# Controlla con flag di tipo espliciti
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Mostra aiuto
checkcrontab --help

# Mostra versione
checkcrontab --version
```

### Opzioni da riga di comando

- `-S, --system` - File crontab di sistema
- `-U, --user` - File crontab utente
- `-u, --username` - Nomi utente da controllare
- `-v, --version` - Mostra versione
- `-d, --debug` - Output di debug
- `-n, --no-colors` - Disabilita output colorato

### Funzionalità

- **Supporto multipiattaforma** (Linux, macOS, Windows)
- **Validazione crontab di sistema e utente**
- **Validazione campi temporali** (minuti, ore, giorni, mesi, giorni della settimana)
- **Validazione esistenza utente** (Linux/macOS)
- **Rilevamento comandi pericolosi**
- **Supporto parole chiave speciali** (@reboot, @daily, ecc.)
- **Supporto comandi multi-riga**

**[Documentazione funzionalità](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Guida completa alla sintassi supportata, valori validi, esempi e messaggi di errore.

### Strumenti di sviluppo

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Licenza

Licenza MIT

### Checkcrontab - Validatore di file crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Script Python per verificare la sintassi e la correttezza dei file crontab nei sistemi Linux/Unix.

**Traduzioni:** [English](../README.md) | [Русский](README_RU.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

#### Requisiti

- **Python 3.8 o superiore**
- Sistema Linux/Unix con systemctl
- Accesso in lettura a `/etc/crontab`

#### Installazione

```bash
pip3 install checkcrontab
```

O da GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### Utilizzo

```bash
# Verificare il crontab di sistema
checkcrontab

# Verificare il file crontab
checkcrontab /etc/crontab

# Verificare il crontab utente
checkcrontab username

# Mostrare aiuto
checkcrontab --help
```

#### Strumenti di sviluppo

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### Licenza

MIT License

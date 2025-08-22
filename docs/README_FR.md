### Checkcrontab - Validateur de fichiers crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Script Python pour vérifier la syntaxe et la correction des fichiers crontab dans les systèmes Linux/Unix.

**Traductions:** [English](../README.md) | [Русский](README_RU.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

#### Exigences

- **Python 3.8 ou supérieur**
- Système Linux/Unix avec systemctl
- Accès en lecture à `/etc/crontab`

#### Installation

```bash
pip3 install checkcrontab
```

Ou depuis GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### Utilisation

```bash
# Vérifier le crontab système
checkcrontab

# Vérifier le fichier crontab
checkcrontab /etc/crontab

# Vérifier le crontab utilisateur
checkcrontab username

# Afficher l'aide
checkcrontab --help
```

#### Outils de développement

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### Licence

MIT License

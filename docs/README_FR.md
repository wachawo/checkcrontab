## Checkcrontab - vérifier la syntaxe des fichiers crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Un script Python pour vérifier la syntaxe des fichiers crontab. Support multiplateforme pour Linux, macOS et Windows.

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Exigences

- **Python 3.7 ou supérieur**
- Système Linux/Unix avec systemctl (pour les vérifications de démon)
- Accès en lecture à `/etc/crontab` (sur Linux)

### Installation

```bash
pip3 install checkcrontab
```

Ou depuis GitHub :

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Utilisation

```bash
# Vérifier le crontab système (Linux uniquement)
checkcrontab

# Vérifier un fichier crontab
checkcrontab /etc/crontab

# Vérifier le crontab utilisateur
checkcrontab username

# Vérifier avec des drapeaux de type explicites
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Afficher l'aide
checkcrontab --help

# Afficher la version
checkcrontab --version
```

### Options de ligne de commande

- `-S, --system` - Fichiers crontab système
- `-U, --user` - Fichiers crontab utilisateur
- `-u, --username` - Noms d'utilisateur à vérifier
- `-v, --version` - Afficher la version
- `-d, --debug` - Sortie de débogage
- `-n, --no-colors` - Désactiver la sortie colorée

### Fonctionnalités

- **Support multiplateforme** (Linux, macOS, Windows)
- **Validation des crontab système et utilisateur**
- **Validation des champs temporels** (minutes, heures, jours, mois, jours de la semaine)
- **Validation de l'existence des utilisateurs** (Linux/macOS)
- **Détection des commandes dangereuses**
- **Support des mots-clés spéciaux** (@reboot, @daily, etc.)
- **Support des commandes multi-lignes**

**[Documentation des fonctionnalités](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Guide complet de la syntaxe prise en charge, des valeurs valides, des exemples et des messages d'erreur.

### Outils de développement

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Licence

Licence MIT

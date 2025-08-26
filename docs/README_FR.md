## Checkcrontab - vérifier la syntaxe des fichiers crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

Un script Python pour vérifier la syntaxe des fichiers crontab. Support multiplateforme pour Linux, macOS et Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | **[Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md)** | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Exigences

- **Python 3.7 ou supérieur**
- **Linux/macOS**: Système Linux/Unix avec systemctl (pour les vérifications de démons), accès en lecture à `/etc/crontab`
- **Windows**: Aucune exigence supplémentaire (validation basée sur les fichiers uniquement)

### Support des plateformes

**Linux/macOS (Support complet):**
- Validation du crontab système (`/etc/crontab`)
- Validation du crontab utilisateur (via `crontab -l -u username`)
- Validation de l'existence de l'utilisateur
- Vérifications de démons/services via systemctl
- Toutes les fonctionnalités de syntaxe crontab

**Windows (Support limité):**
- Validation de syntaxe crontab basée sur les fichiers
- Aucune vérification d'existence d'utilisateur
- Aucun accès au crontab système
- Aucune vérification de démons/services
- Toutes les fonctionnalités de syntaxe crontab prises en charge

### Installation

```bash
pip3 install checkcrontab
```

Ou depuis GitHub:

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

### Sortie JSON

Pour une sortie lisible par machine, utilisez le drapeau `--json`:

```bash
checkcrontab --json examples/user_valid.txt
```

Exemple de sortie JSON:

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

### Options de ligne de commande

- `-S, --system` - Fichiers crontab système
- `-U, --user` - Fichiers crontab utilisateur
- `-u, --username` - Noms d'utilisateur à vérifier
- `-v, --version` - Afficher la version
- `-d, --debug` - Sortie de débogage
- `-n, --no-colors` - Désactiver la sortie colorée
- `-j, --json` - Sortie des résultats au format JSON

### Fonctionnalités

- **Validation de syntaxe multiplateforme** (Linux, macOS, Windows)
- **Fonctionnalités spécifiques à la plateforme:**
  - **Linux/macOS**: Validation du crontab système et utilisateur, vérification de l'existence de l'utilisateur, validation des démons
  - **Windows**: Validation basée sur les fichiers uniquement
- **Validation des champs temporels** (minutes, heures, jours, mois, jours de la semaine)
- **Détection de commandes dangereuses**
- **Support de mots-clés spéciaux** (@reboot, @daily, etc.)
- **Support de commandes multi-lignes**

### Documentation

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Documentation détaillée des fonctionnalités et capacités

### Outils de développement

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Utilisation avec pre-commit

Vous pouvez utiliser checkcrontab comme un hook pre-commit dans vos projets:

1. Ajoutez à votre `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: v1.0.0  # Utilisez la dernière version
    hooks:
      - id: checkcrontab
```

2. Installez pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. Le hook vérifiera automatiquement tous les fichiers `.cron`, `.crontab` et `.tab` dans votre dépôt.

### Licence

MIT License

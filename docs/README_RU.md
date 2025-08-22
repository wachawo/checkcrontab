### Checkcrontab - Валидатор файлов crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Python скрипт для проверки синтаксиса и корректности файлов crontab в системах Linux/Unix.

**Переводы:** [English](../README.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

#### Требования

- **Python 3.8 или выше**
- Система Linux/Unix с systemctl
- Доступ на чтение к `/etc/crontab`

### Установка

```bash
pip3 install checkcrontab
```

Или с GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Использование

```bash
# Проверить системный crontab
checkcrontab

# Проверить файл crontab
checkcrontab /etc/crontab

# Проверить crontab пользователя
checkcrontab username

# Показать справку
checkcrontab --help
```

### Инструменты разработки

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### Лицензия

MIT License

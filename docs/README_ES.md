### Checkcrontab - Validador de archivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Script de Python para verificar la sintaxis y corrección de archivos crontab en sistemas Linux/Unix.

**Traducciones:** [English](../README.md) | [Русский](README_RU.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

#### Requisitos

- **Python 3.8 o superior**
- Sistema Linux/Unix con systemctl
- Acceso de lectura a `/etc/crontab`

#### Instalación

```bash
pip3 install checkcrontab
```

O desde GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### Uso

```bash
# Verificar crontab del sistema
checkcrontab

# Verificar archivo crontab
checkcrontab /etc/crontab

# Verificar crontab de usuario
checkcrontab username

# Mostrar ayuda
checkcrontab --help
```

#### Herramientas de desarrollo

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### Licencia

MIT License

### Checkcrontab - Validador de arquivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Script Python para verificar a sintaxe e correção de arquivos crontab em sistemas Linux/Unix.

**Traduções:** [English](../README.md) | [Русский](README_RU.md) | [Español](README_ES.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [日本語](README_JA.md) | [हिन्दी](README_HI.md)

#### Requisitos

- **Python 3.8 ou superior**
- Sistema Linux/Unix com systemctl
- Acesso de leitura a `/etc/crontab`

#### Instalação

```bash
pip3 install checkcrontab
```

Ou do GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### Uso

```bash
# Verificar crontab do sistema
checkcrontab

# Verificar arquivo crontab
checkcrontab /etc/crontab

# Verificar crontab do usuário
checkcrontab username

# Mostrar ajuda
checkcrontab --help
```

#### Ferramentas de desenvolvimento

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### Licença

MIT License

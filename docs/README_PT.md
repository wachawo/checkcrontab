## Checkcrontab - verificar sintaxe em arquivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Um script Python para verificar a sintaxe de arquivos crontab. Suporte multiplataforma para Linux, macOS e Windows.

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisitos

- **Python 3.7 ou superior**
- Sistema Linux/Unix com systemctl (para verificações de daemon)
- Acesso de leitura a `/etc/crontab` (no Linux)

### Instalação

```bash
pip3 install checkcrontab
```

Ou do GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Uso

```bash
# Verificar crontab do sistema (apenas Linux)
checkcrontab

# Verificar arquivo crontab
checkcrontab /etc/crontab

# Verificar crontab do usuário
checkcrontab username

# Verificar com flags de tipo explícitos
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Mostrar ajuda
checkcrontab --help

# Mostrar versão
checkcrontab --version
```

### Opções da linha de comando

- `-S, --system` - Arquivos crontab do sistema
- `-U, --user` - Arquivos crontab do usuário
- `-u, --username` - Nomes de usuário para verificar
- `-v, --version` - Mostrar versão
- `-d, --debug` - Saída de debug
- `-n, --no-colors` - Desabilitar saída colorida

### Recursos

- **Suporte multiplataforma** (Linux, macOS, Windows)
- **Validação de crontab do sistema e usuário**
- **Validação de campos de tempo** (minutos, horas, dias, meses, dias da semana)
- **Validação de existência do usuário** (Linux/macOS)
- **Detecção de comandos perigosos**
- **Suporte a palavras-chave especiais** (@reboot, @daily, etc.)
- **Suporte a comandos multi-linha**

**[Documentação de recursos](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Guia abrangente da sintaxe suportada, valores válidos, exemplos e mensagens de erro.

### Ferramentas de desenvolvimento

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Licença

Licença MIT

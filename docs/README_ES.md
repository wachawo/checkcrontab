## Checkcrontab - verificar sintaxis en archivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Un script de Python para verificar la sintaxis de archivos crontab. Soporte multiplataforma para Linux, macOS y Windows.

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | **[Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md)** | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisitos

- **Python 3.7 o superior**
- Sistema Linux/Unix con systemctl (para verificaciones de daemon)
- Acceso de lectura a `/etc/crontab` (en Linux)

### Instalación

```bash
pip3 install checkcrontab
```

O desde GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Uso

```bash
# Verificar crontab del sistema (solo Linux)
checkcrontab

# Verificar archivo crontab
checkcrontab /etc/crontab

# Verificar crontab de usuario
checkcrontab username

# Verificar con flags de tipo explícitos
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Mostrar ayuda
checkcrontab --help

# Mostrar versión
checkcrontab --version
```

### Opciones de línea de comandos

- `-S, --system` - Archivos crontab del sistema
- `-U, --user` - Archivos crontab de usuario
- `-u, --username` - Nombres de usuario a verificar
- `-v, --version` - Mostrar versión
- `-d, --debug` - Salida de debug
- `-n, --no-colors` - Deshabilitar salida colorida

### Características

- **Soporte multiplataforma** (Linux, macOS, Windows)
- **Validación de crontab del sistema y usuario**
- **Validación de campos de tiempo** (minutos, horas, días, meses, días de la semana)
- **Validación de existencia de usuario** (Linux/macOS)
- **Detección de comandos peligrosos**
- **Soporte de palabras clave especiales** (@reboot, @daily, etc.)
- **Soporte de comandos multi-línea**

**[Documentación de características](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Guía completa de la sintaxis soportada, valores válidos, ejemplos y mensajes de error.

### Herramientas de desarrollo

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Licencia

Licencia MIT

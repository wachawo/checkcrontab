## Checkcrontab - verificar sintaxis en archivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

Un script de Python para verificar la sintaxis de archivos crontab. Soporte multiplataforma para Linux, macOS y Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | **[Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md)** | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisitos

- **Python 3.7 o superior**
- **Linux/macOS**: Sistema Linux/Unix con systemctl (para verificaciones de demonios), acceso de lectura a `/etc/crontab`
- **Windows**: Sin requisitos adicionales (solo validación basada en archivos)

### Soporte de plataformas

**Linux/macOS (Soporte completo):**
- Validación de crontab del sistema (`/etc/crontab`)
- Validación de crontab de usuario (vía `crontab -l -u username`)
- Validación de existencia de usuario
- Verificaciones de demonios/servicios vía systemctl
- Todas las características de sintaxis crontab

**Windows (Soporte limitado):**
- Validación de sintaxis crontab basada en archivos
- Sin verificaciones de existencia de usuario
- Sin acceso a crontab del sistema
- Sin verificaciones de demonios/servicios
- Todas las características de sintaxis crontab soportadas

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

# Verificar con banderas de tipo explícitas
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Mostrar ayuda
checkcrontab --help

# Mostrar versión
checkcrontab --version
```

### Salida JSON

Para salida legible por máquina, use la bandera `--json`:

```bash
checkcrontab --json examples/user_valid.txt
```

Ejemplo de salida JSON:

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

### Opciones de línea de comandos

- `-S, --system` - Archivos crontab del sistema
- `-U, --user` - Archivos crontab de usuario
- `-u, --username` - Nombres de usuario a verificar
- `-v, --version` - Mostrar versión
- `-d, --debug` - Salida de depuración
- `-n, --no-colors` - Deshabilitar salida coloreada
- `-j, --json` - Salida de resultados en formato JSON

### Características

- **Validación de sintaxis multiplataforma** (Linux, macOS, Windows)
- **Características específicas de plataforma:**
  - **Linux/macOS**: Validación de crontab del sistema y usuario, verificación de existencia de usuario, validación de demonios
  - **Windows**: Solo validación basada en archivos
- **Validación de campos de tiempo** (minutos, horas, días, meses, días de la semana)
- **Detección de comandos peligrosos**
- **Soporte de palabras clave especiales** (@reboot, @daily, etc.)
- **Soporte de comandos multilínea**

### Documentación

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Documentación detallada de funciones y capacidades

### Herramientas de desarrollo

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Uso con pre-commit

Puede usar checkcrontab como un hook de pre-commit en sus proyectos:

1. Agregue a su `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: v1.0.0  # Use la última versión
    hooks:
      - id: checkcrontab
```

2. Instale pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. El hook verificará automáticamente todos los archivos `.cron`, `.crontab` y `.tab` en su repositorio.

### Licencia

MIT License

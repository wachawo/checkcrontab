## Checkcrontab - verificar sintaxis en archivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/main/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Un script de Python para verificar la sintaxis de archivos crontab. Soporte multiplataforma para Linux, macOS y Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | **[Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md)** | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md) | [한국어](https://github.com/wachawo/checkcrontab/blob/main/README_KR.md)

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
# Verificar el crontab del sistema (solo Linux/macOS)
checkcrontab

# Verificar un archivo crontab
checkcrontab /etc/crontab

# Verificar el crontab de un usuario (solo Linux/macOS)
checkcrontab username

# Verificar con banderas de tipo explícitas
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Verificar todos los crontab de un directorio
checkcrontab /etc/cron.d

# Mostrar ayuda
checkcrontab --help

# Mostrar versión
checkcrontab --version
```

### Formatos de Salida

#### Salida de Texto (Predeterminado)
Salida de registro estándar a stderr (comportamiento predeterminado):

```bash
checkcrontab examples/user_valid.txt
```
#### Salida de Texto a stdout
Para enviar el registro a stdout en lugar de stderr, use `--format text`:

```bash
checkcrontab --format text examples/user_valid.txt
```

#### Salida SARIF
Para salida SARIF (Static Analysis Results Interchange Format), use la bandera `--format sarif`:

```bash
checkcrontab --format sarif examples/user_valid.txt
```

#### Salida JSON
Para salida legible por máquina, use la bandera `--format json`:

```bash
checkcrontab --format json examples/user_valid.txt
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

### Códigos de Salida

| Código | Significado |
|--------|-------------|
| 0      | Sin errores (advertencias permitidas). Con `--exit-zero` siempre 0. |
| 1      | Problemas encontrados: cualquier error o cualquier advertencia cuando `--strict` está configurado. |
| 2      | Error de ejecución/uso (fallo inesperado, argumentos CLI incorrectos, etc.). |

### Opciones de línea de comandos

- `-S, --system` - Archivos crontab del sistema
- `-U, --user` - Archivos crontab de usuario
- `-u, --username` - Nombres de usuario a verificar
- `-v, --version` - Mostrar versión
- `-d, --debug` - Salida de depuración
- `-n, --no-colors` - Deshabilitar salida coloreada
- `--format {text,json,sarif}` - Formato de salida (predeterminado: text)
- `--strict` - Tratar advertencias como errores
- `--exit-zero` - Siempre salir con código 0

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
    rev: 0.0.8  # Use la última versión
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

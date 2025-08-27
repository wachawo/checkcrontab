## Checkcrontab - проверка синтаксиса в crontab файлах

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

Python скрипт для проверки синтаксиса crontab файлов. Кроссплатформенная поддержка для Linux, macOS и Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | **[Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md)** | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Требования

- **Python 3.7 или выше**
- **Linux/macOS**: Linux/Unix система с systemctl (для проверки демонов), доступ на чтение к `/etc/crontab`
- **Windows**: Дополнительных требований нет (только файловая валидация)

### Поддержка платформ

**Linux/macOS (Полная поддержка):**
- Валидация системного crontab (`/etc/crontab`)
- Валидация пользовательского crontab (через `crontab -l -u username`)
- Проверка существования пользователей
- Проверка демонов/сервисов через systemctl
- Все функции синтаксиса crontab

**Windows (Ограниченная поддержка):**
- Файловая валидация синтаксиса crontab
- Без проверки существования пользователей
- Без доступа к системному crontab
- Без проверки демонов/сервисов
- Все функции синтаксиса crontab поддерживаются

### Установка

```bash
pip3 install checkcrontab
```

Или из GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Использование

```bash
# Проверить системный crontab (только Linux)
checkcrontab

# Проверить crontab файл
checkcrontab /etc/crontab

# Проверить пользовательский crontab
checkcrontab username

# Проверить с явными флагами типа
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Строгий режим (обрабатывать предупреждения как ошибки)
checkcrontab --strict examples/user_valid.txt

# Всегда возвращать код успеха
checkcrontab --exit-zero examples/user_valid.txt

# Показать справку
checkcrontab --help

# Показать версию
checkcrontab --version
```

### Форматы вывода

#### Текстовый вывод (по умолчанию)
Стандартный вывод логирования в stderr (поведение по умолчанию):

```bash
checkcrontab examples/user_valid.txt
```

#### JSON вывод
Для машиночитаемого вывода используйте флаг `--format json`:

```bash
checkcrontab --format json examples/user_valid.txt
```

#### SARIF вывод
Для SARIF (Static Analysis Results Interchange Format) вывода используйте флаг `--format sarif`:

```bash
checkcrontab --format sarif examples/user_valid.txt
```

#### Текстовый вывод в stdout
Для вывода логирования в stdout вместо stderr используйте `--format text`:

```bash
checkcrontab --format text examples/user_valid.txt
```

Пример JSON вывода:

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

### Коды возврата

| Код | Значение |
|-----|----------|
| 0   | Нет ошибок (предупреждения разрешены). С `--exit-zero` всегда 0. |
| 1   | Найдены проблемы: любая ошибка или любое предупреждение при установке `--strict`. |
| 2   | Ошибка выполнения/использования (неожиданный сбой, плохие аргументы CLI и т.д.). |

### Параметры командной строки

- `-S, --system` - Системные crontab файлы
- `-U, --user` - Пользовательские crontab файлы
- `-u, --username` - Имена пользователей для проверки
- `-v, --version` - Показать версию
- `-d, --debug` - Отладочный вывод
- `-n, --no-colors` - Отключить цветной вывод
- `--format {text,json,sarif}` - Формат вывода (по умолчанию: text)
- `--strict` - Обрабатывать предупреждения как ошибки
- `--exit-zero` - Всегда возвращать код 0

### Возможности

- **Кроссплатформенная валидация синтаксиса** (Linux, macOS, Windows)
- **Платформо-специфичные функции:**
  - **Linux/macOS**: Валидация системного и пользовательского crontab, проверка существования пользователей, валидация демонов
  - **Windows**: Только файловая валидация
- **Валидация временных полей** (минуты, часы, дни, месяцы, дни недели)
- **Обнаружение опасных команд**
- **Поддержка специальных ключевых слов** (@reboot, @daily, и т.д.)
- **Поддержка многострочных команд**

### Документация

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Подробная документация функций и возможностей

### Инструменты разработки

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Использование с pre-commit

Вы можете использовать checkcrontab как pre-commit хук в своих проектах:

1. Добавьте в ваш `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Используйте последнюю версию
    hooks:
      - id: checkcrontab
```

2. Установите pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. Хук автоматически проверит все файлы `.cron`, `.crontab` и `.tab` в вашем репозитории.

### Лицензия

MIT License

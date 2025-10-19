## Checkcrontab - validar sintaxe em ficheiros crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/main/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Um script em Python para validar a sintaxe de ficheiros crontab. Suporte multiplataforma para Linux, macOS e Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | **[Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md)** | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisitos

* **Python 3.7 ou superior**
* **Linux**: Sistema Linux com systemctl (para verificações de daemon) e acesso de leitura a `/etc/crontab`
* **macOS**: Sistema Unix com acesso de leitura a `/etc/crontab` (systemctl não disponível)
* **Windows**: Sem requisitos adicionais (validação baseada em ficheiro apenas)

### Suporte de Plataformas

**Linux (Suporte Completo):**

* ✅ Validação do crontab do sistema (`/etc/crontab`)
* ✅ Validação do crontab do utilizador (via `crontab -l -u username`)
* ✅ Validação da existência de utilizadores
* ✅ Verificação de serviços/daemons via systemctl
* ✅ Todas as funcionalidades de sintaxe do crontab
* ✅ Validação de permissões de ficheiros
* ✅ Verificação do estado do daemon do cron

**macOS (Suporte Parcial):**

* ✅ Validação do crontab do sistema (`/etc/crontab`)
* ✅ Validação do crontab do utilizador (via `crontab -l -u username`)
* ✅ Validação da existência de utilizadores
* ❌ Verificação de serviços/daemons (systemctl não disponível)
* ✅ Todas as funcionalidades de sintaxe do crontab
* ✅ Validação de permissões de ficheiros
* ❌ Verificação do estado do daemon do cron

**Windows (Suporte Limitado):**

* ✅ Validação de sintaxe baseada em ficheiros
* ❌ Validação de utilizadores (sem integração com gestão de utilizadores)
* ❌ Acesso ao crontab do sistema (sem `/etc/crontab`)
* ❌ Verificação de serviços/daemons (sem systemctl)
* ✅ Todas as funcionalidades de sintaxe do crontab suportadas
* ❌ Validação de permissões de ficheiros
* ❌ Verificação do estado do daemon do cron

### Instalação

```bash
pip3 install checkcrontab
```

Ou a partir do GitHub:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### Utilização

```bash
# Validar o crontab do sistema (apenas Linux/macOS)
checkcrontab

# Validar um ficheiro crontab
checkcrontab /etc/crontab

# Validar o crontab de um utilizador (apenas Linux/macOS)
checkcrontab username

# Validar com parâmetros explícitos
gheckcrontab -S system.cron -U user.cron -u username1 -u username2

# Validar todos os crontabs de um diretório
checkcrontab /etc/cron.d

# Mostrar ajuda
checkcrontab --help

# Mostrar versão
checkcrontab --version
```

**Comportamento específico da plataforma:**

* **Linux**: Funcionalidade completa, incluindo verificações de daemon e de utilizadores.
* **macOS**: Funcionalidade completa, exceto verificações de daemon (systemctl não disponível).
* **Windows**: Apenas validação baseada em ficheiros, sem integração com o sistema.

### Saídas de Texto

Para redirecionar a saída de STDERR para STDOUT (por exemplo, em CI), use `--format text`:

```bash
checkcrontab --format text examples/user_valid.txt
```

#### Saída SARIF

Para saída no formato SARIF (Static Analysis Results Interchange Format), use a flag `--format sarif`:

```bash
checkcrontab --format sarif examples/user_valid.txt
```

#### Saída JSON

Para saída legível por máquina, use a flag `--format json`:

```bash
checkcrontab --format json examples/user_valid.txt
```

Exemplo de saída JSON:

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

### Códigos de Saída

| Código | Significado                                                                          |
| ------ | ------------------------------------------------------------------------------------ |
| 0      | Sem erros (avisos permitidos). Com `--exit-zero`, o código será sempre 0.            |
| 1      | Problemas encontrados: qualquer erro ou qualquer aviso quando `--strict` está ativo. |
| 2      | Erro de execução/uso (falha inesperada, argumentos incorretos, etc.).                |

### Opções de Linha de Comando

* `-S, --system` - Ficheiros crontab do sistema
* `-U, --user` - Ficheiros crontab do utilizador
* `-u, --username` - Nomes de utilizador a validar
* `-v, --version` - Mostrar versão
* `-d, --debug` - Saída de depuração
* `-n, --no-colors` - Desativar cores na saída
* `--format {text,json,sarif}` - Formato de saída (padrão: text)
* `--strict` - Tratar avisos como erros
* `--exit-zero` - Forçar saída com código 0

### Funcionalidades

* **Validação de sintaxe multiplataforma** (Linux, macOS, Windows)
* **Funcionalidades específicas por plataforma:**

  * **Linux/macOS**: Validação de crontabs do sistema e do utilizador, verificação de existência de utilizadores, validação de daemons
  * **Windows**: Apenas validação baseada em ficheiros
* **Validação de campos de tempo** (minutos, horas, dias, meses, dias da semana)
* **Deteção de comandos perigosos**
* **Suporte a palavras-chave especiais** (@reboot, @daily, etc.)
* **Suporte a comandos em múltiplas linhas**
* **Validação de permissões de ficheiros**
* **Verificação do estado do daemon do cron**

**[Documentação de Funcionalidades](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** — Guia detalhado com sintaxe suportada, valores válidos, exemplos e mensagens de erro.

### Ferramentas de Desenvolvimento

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Testes

```bash
pytest --cov=checkcrontab --cov-report=term-missing
coverage html  # relatório HTML local opcional em htmlcov/index.html
# CI faz o upload automático do coverage.xml para o Codecov
# python -m coverage_badge -o docs/coverage.svg
```

### Uso com pre-commit

Pode utilizar o checkcrontab como hook pre-commit nos seus projetos:

1. Adicione ao seu `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Use a versão mais recente
    hooks:
      - id: checkcrontab
        files: \.(cron|crontab|tab|conf)$
        exclude: (\.git|node_modules|__pycache__)/
        args: [--format, json, --strict]
```

2. Instale o pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. O hook verificará automaticamente todos os ficheiros `.cron`, `.crontab` e `.tab` no seu repositório.

### Licença

Licença MIT

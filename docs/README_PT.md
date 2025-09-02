## Checkcrontab - verificar sintaxe em arquivos crontab

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)

Um script Python para verificar a sintaxe de arquivos crontab. Suporte multiplataforma para Linux, macOS e Windows.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | **[Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md)** | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### Requisitos

- **Python 3.7 ou superior**
- **Linux/macOS**: Sistema Linux/Unix com systemctl (para verificações de daemon), acesso de leitura a `/etc/crontab`
- **Windows**: Sem requisitos adicionais (apenas validação baseada em arquivos)

### Suporte de plataformas

**Linux/macOS (Suporte completo):**
- Validação de crontab do sistema (`/etc/crontab`)
- Validação de crontab do usuário (via `crontab -l -u username`)
- Validação de existência do usuário
- Verificações de daemon/serviços via systemctl
- Todas as funcionalidades de sintaxe crontab

**Windows (Suporte limitado):**
- Validação de sintaxe crontab baseada em arquivos
- Sem verificações de existência do usuário
- Sem acesso ao crontab do sistema
- Sem verificações de daemon/serviços
- Todas as funcionalidades de sintaxe crontab suportadas

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

# Verificar com flags de tipo explícitas
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# Mostrar ajuda
checkcrontab --help

# Mostrar versão
checkcrontab --version
```

### Formatos de Saída

#### Saída de Texto (Padrão)
Saída de registro padrão para stderr (comportamento padrão):

```bash
checkcrontab examples/user_valid.txt
```

#### Saída de Texto para stdout
Para enviar o registro para stdout em vez de stderr, use `--format text`:

```bash
checkcrontab --format text examples/user_valid.txt
```

#### Saída SARIF
Para saída SARIF (Static Analysis Results Interchange Format), use a flag `--format sarif`:

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

| Código | Significado |
|--------|-------------|
| 0      | Sem erros (avisos permitidos). Com `--exit-zero` sempre 0. |
| 1      | Problemas encontrados: qualquer erro ou qualquer aviso quando `--strict` está configurado. |
| 2      | Erro de execução/uso (falha inesperada, argumentos CLI incorretos, etc.). |



### Códigos de Saída

| Código | Significado |
|--------|-------------|
| 0      | Sem erros (avisos permitidos). Com `--exit-zero` sempre 0. |
| 1      | Problemas encontrados: qualquer erro ou qualquer aviso quando `--strict` está configurado. |
| 2      | Erro de execução/uso (falha inesperada, argumentos CLI incorretos, etc.). |

### Opções de linha de comando

- `-S, --system` - Arquivos crontab do sistema
- `-U, --user` - Arquivos crontab do usuário
- `-u, --username` - Nomes de usuário para verificar
- `-v, --version` - Mostrar versão
- `-d, --debug` - Saída de debug
- `-n, --no-colors` - Desabilitar saída colorida
- `--format {text,json,sarif}` - Formato de saída (padrão: text)
- `--strict` - Tratar avisos como erros
- `--exit-zero` - Sempre sair com código 0

### Exemplos de uso

```bash
# Verificar arquivo crontab
checkcrontab examples/user_valid.txt

# Verificar com saída JSON
checkcrontab --format json examples/user_valid.txt

# Modo estrito (tratar avisos como erros)
checkcrontab --strict examples/user_valid.txt

# Sempre sair com código de sucesso
checkcrontab --exit-zero examples/user_valid.txt
```

### Funcionalidades

- **Validação de sintaxe multiplataforma** (Linux, macOS, Windows)
- **Funcionalidades específicas da plataforma:**
  - **Linux/macOS**: Validação de crontab do sistema e usuário, verificação de existência do usuário, validação de daemon
  - **Windows**: Apenas validação baseada em arquivos
- **Validação de campos de tempo** (minutos, horas, dias, meses, dias da semana)
- **Detecção de comandos perigosos**
- **Suporte a palavras-chave especiais** (@reboot, @daily, etc.)
- **Suporte a comandos multi-linha**

### Documentação

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - Documentação detalhada de funcionalidades e capacidades

### Ferramentas de desenvolvimento

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### Uso com pre-commit

Você pode usar checkcrontab como um hook pre-commit em seus projetos:

1. Adicione ao seu `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # Use a versão mais recente
    hooks:
      - id: checkcrontab
```

2. Instale pre-commit:

```bash
pip install pre-commit
pre-commit install
```

3. O hook verificará automaticamente todos os arquivos `.cron`, `.crontab` e `.tab` no seu repositório.

### Licença

MIT License

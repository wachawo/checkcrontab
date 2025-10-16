## Checkcrontab - 检查 crontab 文件语法

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/0.0.11/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

用于检查 crontab 文件语法的 Python 脚本。支持 Linux、macOS 和 Windows 的跨平台。

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | **[中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md)** | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### 要求

- **Python 3.7 或更高版本**
- **Linux/macOS**: 带有 systemctl 的 Linux/Unix 系统（用于守护进程检查），对 `/etc/crontab` 的读取权限
- **Windows**: 无额外要求（仅基于文件的验证）

### 平台支持

**Linux/macOS（完整支持）：**
- 系统 crontab 验证（`/etc/crontab`）
- 用户 crontab 验证（通过 `crontab -l -u username`）
- 用户存在性验证
- 通过 systemctl 进行守护进程/服务检查
- 所有 crontab 语法功能

**Windows（有限支持）：**
- 基于文件的 crontab 语法验证
- 无用户存在性检查
- 无系统 crontab 访问
- 无守护进程/服务检查
- 支持所有 crontab 语法功能

### 安装

```bash
pip3 install checkcrontab
```

或从 GitHub：

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### 使用方法

```bash
# 检查系统 crontab（仅 Linux）
checkcrontab

# 检查 crontab 文件
checkcrontab /etc/crontab

# 检查用户 crontab
checkcrontab username
# 严格模式（将警告视为错误）
checkcrontab --strict examples/user_valid.txt

# 始终以成功代码退出
checkcrontab --exit-zero examples/user_valid.txt

# 严格模式（将警告视为错误）
checkcrontab --strict examples/user_valid.txt

# 始终以成功代码退出
checkcrontab --exit-zero examples/user_valid.txt


# 使用显式类型标志检查
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# 显示帮助
checkcrontab --help

# 显示版本
checkcrontab --version
# 严格模式（将警告视为错误）
checkcrontab --strict examples/user_valid.txt

# 始终以成功代码退出
checkcrontab --exit-zero examples/user_valid.txt

# 严格模式（将警告视为错误）
checkcrontab --strict examples/user_valid.txt

# 始终以成功代码退出
checkcrontab --exit-zero examples/user_valid.txt

```

### JSON 输出

对于机器可读的输出，使用 `--format json` 标志：

```bash
checkcrontab --format json examples/user_valid.txt
```

JSON 输出示例：

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

### 命令行选项

- `-S, --system` - 系统 crontab 文件
- `-U, --user` - 用户 crontab 文件
- `-u, --username` - 要检查的用户名
- `-v, --version` - 显示版本
- `-d, --debug` - 调试输出
- `-n, --no-colors` - 禁用彩色输出
- `--format {text,json,sarif}` - 输出格式（默认：text）
- `--strict` - 将警告视为错误
- `--exit-zero` - 始终以代码 0 退出

### 功能

- **跨平台语法验证**（Linux、macOS、Windows）
- **平台特定功能：**
  - **Linux/macOS**: 系统和用户 crontab 验证、用户存在性检查、守护进程验证
  - **Windows**: 仅基于文件的验证
- **时间字段验证**（分钟、小时、天、月、星期几）
- **危险命令检测**
- **特殊关键字支持**（@reboot、@daily 等）
- **多行命令支持**

### 文档

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - 详细的功能和功能文档

### 开发工具

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### 与 pre-commit 一起使用

您可以在项目中将 checkcrontab 用作 pre-commit 钩子：

1. 添加到您的 `.pre-commit-config.yaml`：

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # 使用最新版本
    hooks:
      - id: checkcrontab
```

2. 安装 pre-commit：

```bash
pip install pre-commit
pre-commit install
```

3. 钩子将自动检查您存储库中的所有 `.cron`、`.crontab` 和 `.tab` 文件。

### 许可证

MIT License

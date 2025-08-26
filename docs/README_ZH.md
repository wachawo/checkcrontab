## Checkcrontab - 检查 crontab 文件语法

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

一个用于检查 crontab 文件语法的 Python 脚本。支持 Linux、macOS 和 Windows 跨平台。

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### 系统要求

- **Python 3.7 或更高版本**
- 带有 systemctl 的 Linux/Unix 系统（用于守护进程检查）
- 对 `/etc/crontab` 的读取权限（在 Linux 上）

### 安装

```bash
pip3 install checkcrontab
```

或从 GitHub 安装：

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### 使用方法

```bash
# 检查系统 crontab（仅限 Linux）
checkcrontab

# 检查 crontab 文件
checkcrontab /etc/crontab

# 检查用户 crontab
checkcrontab username

# 使用显式类型标志检查
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# 显示帮助
checkcrontab --help

# 显示版本
checkcrontab --version
```

### 命令行选项

- `-S, --system` - 系统 crontab 文件
- `-U, --user` - 用户 crontab 文件
- `-u, --username` - 要检查的用户名
- `-v, --version` - 显示版本
- `-d, --debug` - 调试输出
- `-n, --no-colors` - 禁用彩色输出

### 功能特性

- **跨平台支持** (Linux, macOS, Windows)
- **系统和用户 crontab 验证**
- **时间字段验证** (分钟、小时、日期、月份、星期)
- **用户存在性验证** (Linux/macOS)
- **危险命令检测**
- **特殊关键字支持** (@reboot, @daily, 等)
- **多行命令支持**

**[功能文档](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - 支持的语法、有效值、示例和错误消息的综合指南。

### 开发工具

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### 许可证

MIT 许可证

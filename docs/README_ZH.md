### Checkcrontab - Crontab 文件验证器

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

用于检查 Linux/Unix 系统中 crontab 文件语法和正确性的 Python 脚本。

**翻译:** [English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

#### 要求

- **Python 3.8 或更高版本**
- 带有 systemctl 的 Linux/Unix 系统
- 对 `/etc/crontab` 的读取权限

#### 安装

```bash
pip3 install checkcrontab
```

或从 GitHub 安装:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### 使用方法

```bash
# 检查系统 crontab
checkcrontab

# 检查 crontab 文件
checkcrontab /etc/crontab

# 检查用户 crontab
checkcrontab username

# 显示帮助
checkcrontab --help
```

#### 开发工具

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### 许可证

MIT License

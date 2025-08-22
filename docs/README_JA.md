### Checkcrontab - Crontab ファイル検証ツール

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Linux/Unix システムで crontab ファイルの構文と正確性をチェックする Python スクリプト。

**翻訳:** [English](../README.md) | [Русский](README_RU.md) | [Español](README_ES.md) | [Português](README_PT.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Italiano](README_IT.md) | [中文](README_ZH.md) | [हिन्दी](README_HI.md)

#### 要件

- **Python 3.8 以上**
- systemctl を持つ Linux/Unix システム
- `/etc/crontab` への読み取りアクセス

#### インストール

```bash
pip3 install checkcrontab
```

または GitHub から:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### 使用方法

```bash
# システム crontab をチェック
checkcrontab
# crontab ファイルをチェック
checkcrontab /etc/crontab

# ユーザー crontab をチェック
checkcrontab username

# ヘルプを表示
checkcrontab --help
```

#### 開発ツール

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### ライセンス

MIT License

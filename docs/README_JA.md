### Checkcrontab - Crontab ファイル検証ツール

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Linux/Unix システムで crontab ファイルの構文と正確性をチェックする Python スクリプト。

**翻訳:** [English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

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

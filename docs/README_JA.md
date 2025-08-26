## Checkcrontab - crontab ファイルの構文チェック

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

crontab ファイルの構文をチェックする Python スクリプト。Linux、macOS、Windows のクロスプラットフォーム対応。

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | **[日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md)** | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)

### 要件

- **Python 3.7 以上**
- systemctl を備えた Linux/Unix システム（デーモンチェック用）
- `/etc/crontab` への読み取りアクセス（Linux の場合）

### インストール

```bash
pip3 install checkcrontab
```

または GitHub から：

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### 使用方法

```bash
# システム crontab をチェック（Linux のみ）
checkcrontab

# crontab ファイルをチェック
checkcrontab /etc/crontab

# ユーザー crontab をチェック
checkcrontab username

# 明示的なタイプフラグでチェック
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# ヘルプを表示
checkcrontab --help

# バージョンを表示
checkcrontab --version
```

### コマンドラインオプション

- `-S, --system` - システム crontab ファイル
- `-U, --user` - ユーザー crontab ファイル
- `-u, --username` - チェックするユーザー名
- `-v, --version` - バージョンを表示
- `-d, --debug` - デバッグ出力
- `-n, --no-colors` - カラー出力を無効化

### 機能

- **クロスプラットフォーム対応** (Linux, macOS, Windows)
- **システムおよびユーザー crontab 検証**
- **時間フィールド検証** (分、時、日、月、曜日)
- **ユーザー存在性検証** (Linux/macOS)
- **危険なコマンド検出**
- **特殊キーワード対応** (@reboot, @daily, など)
- **複数行コマンド対応**

**[機能ドキュメント](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - サポートされる構文、有効な値、例、エラーメッセージの包括的なガイド。

### 開発ツール

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### ライセンス

MIT ライセンス

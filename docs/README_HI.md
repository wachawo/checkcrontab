### Checkcrontab - Crontab फ़ाइल वैलिडेटर

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

Linux/Unix सिस्टम में crontab फ़ाइलों की सिंटैक्स और सटीकता की जांच के लिए Python स्क्रिप्ट।

**अनुवाद:** [English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md)

#### आवश्यकताएं

- **Python 3.8 या उससे ऊपर**
- systemctl के साथ Linux/Unix सिस्टम
- `/etc/crontab` तक पढ़ने का अधिकार

#### इंस्टॉलेशन

```bash
pip3 install checkcrontab
```

या GitHub से:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

#### उपयोग

```bash
# सिस्टम crontab की जांच करें
checkcrontab

# crontab फ़ाइल की जांच करें
checkcrontab /etc/crontab

# उपयोगकर्ता crontab की जांच करें
checkcrontab username

# सहायता दिखाएं
checkcrontab --help
```

#### विकास उपकरण

```bash
pip3 install pre-commit flake8 pytest
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

#### लाइसेंस

MIT License

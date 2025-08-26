## Checkcrontab - crontab फ़ाइलों में सिंटैक्स की जांच

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

crontab फ़ाइलों के सिंटैक्स की जांच के लिए एक Python स्क्रिप्ट।Linux, macOS, और Windows के लिए क्रॉस-प्लेटफ़ॉर्म समर्थन।

[English](https://github.com/wachawo/checkcrontab/blob/main/README.md) | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | **[हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)**

### आवश्यकताएं

- **Python 3.7 या उससे ऊपर**
- systemctl के साथ Linux/Unix सिस्टम (डेमन चेक के लिए)
- `/etc/crontab` तक पढ़ने का अधिकार (Linux पर)

### इंस्टॉलेशन

```bash
pip3 install checkcrontab
```

या GitHub से:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### उपयोग

```bash
# सिस्टम crontab की जांच करें (केवल Linux)
checkcrontab

# crontab फ़ाइल की जांच करें
checkcrontab /etc/crontab

# उपयोगकर्ता crontab की जांच करें
checkcrontab username

# स्पष्ट प्रकार के फ्लैग के साथ जांच करें
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# सहायता दिखाएं
checkcrontab --help

# संस्करण दिखाएं
checkcrontab --version
```

### कमांड लाइन विकल्प

- `-S, --system` - सिस्टम crontab फ़ाइलें
- `-U, --user` - उपयोगकर्ता crontab फ़ाइलें
- `-u, --username` - जांच करने के लिए उपयोगकर्ता नाम
- `-v, --version` - संस्करण दिखाएं
- `-d, --debug` - डीबग आउटपुट
- `-n, --no-colors` - रंगीन आउटपुट अक्षम करें

### सुविधाएं

- **क्रॉस-प्लेटफ़ॉर्म समर्थन** (Linux, macOS, Windows)
- **सिस्टम और उपयोगकर्ता crontab सत्यापन**
- **समय फ़ील्ड सत्यापन** (मिनट, घंटे, दिन, महीने, सप्ताह के दिन)
- **उपयोगकर्ता अस्तित्व सत्यापन** (Linux/macOS)
- **खतरनाक कमांड का पता लगाना**
- **विशेष कीवर्ड समर्थन** (@reboot, @daily, आदि)
- **बहु-पंक्ति कमांड समर्थन**

**[सुविधा दस्तावेज़](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - समर्थित सिंटैक्स, मान्य मान, उदाहरण और त्रुटि संदेशों का व्यापक गाइड।

### विकास उपकरण

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### लाइसेंस

MIT लाइसेंस

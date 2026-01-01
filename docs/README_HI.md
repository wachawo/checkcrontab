## Checkcrontab - crontab फ़ाइलों में सिंटैक्स की जांच करें

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/main/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

crontab फ़ाइलों के सिंटैक्स की जांच के लिए Python स्क्रिप्ट। Linux, macOS और Windows के लिए क्रॉस-प्लेटफ़ॉर्म समर्थन।

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | **[हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md)** | [한국어](https://github.com/wachawo/checkcrontab/blob/main/docs/README_KR.md)

### आवश्यकताएं

- **Python 3.7 या उससे ऊपर**
- **Linux/macOS**: systemctl के साथ Linux/Unix सिस्टम (डेमन चेक के लिए), `/etc/crontab` तक पढ़ने का अधिकार
- **Windows**: कोई अतिरिक्त आवश्यकता नहीं (केवल फ़ाइल-आधारित सत्यापन)

### प्लेटफ़ॉर्म समर्थन

**Linux/macOS (पूर्ण समर्थन):**
- सिस्टम crontab सत्यापन (`/etc/crontab`)
- उपयोगकर्ता crontab सत्यापन (`crontab -l -u username` के माध्यम से)
- उपयोगकर्ता अस्तित्व सत्यापन
- systemctl के माध्यम से डेमन/सेवा चेक
- सभी crontab सिंटैक्स सुविधाएं

**Windows (सीमित समर्थन):**
- फ़ाइल-आधारित crontab सिंटैक्स सत्यापन
- कोई उपयोगकर्ता अस्तित्व चेक नहीं
- सिस्टम crontab तक कोई पहुंच नहीं
- कोई डेमन/सेवा चेक नहीं
- सभी crontab सिंटैक्स सुविधाएं समर्थित

### स्थापना

```bash
pip3 install checkcrontab
```

या GitHub से:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### उपयोग

```bash
# सिस्टम crontab की जांच करें (केवल Linux/macOS)
checkcrontab

# crontab फ़ाइल की जांच करें
checkcrontab /etc/crontab

# उपयोगकर्ता crontab की जांच करें (केवल Linux/macOS)
checkcrontab username

# स्पष्ट प्रकार फ़्लैग के साथ जांच करें
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# किसी निर्देशिका के सभी crontab की जांच करें
checkcrontab /etc/cron.d

# सहायता दिखाएं
checkcrontab --help

# संस्करण दिखाएं
checkcrontab --version
```

### JSON आउटपुट

मशीन-पठनीय आउटपुट के लिए `---format json` फ़्लैग का उपयोग करें:

```bash
checkcrontab --format json examples/user_valid.txt
```

JSON आउटपुट उदाहरण:

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

### कमांड लाइन विकल्प

- `-S, --system` - सिस्टम crontab फ़ाइलें
- `-U, --user` - उपयोगकर्ता crontab फ़ाइलें
- `-u, --username` - जांच करने के लिए उपयोगकर्ता नाम
- `-v, --version` - संस्करण दिखाएं
- `-d, --debug` - डीबग आउटपुट
- `-n, --no-colors` - रंगीन आउटपुट अक्षम करें
- `--format {text,json,sarif}` - आउटपुट प्रारूप (डिफ़ॉल्ट: text)
- `--strict` - चेतावनियों को त्रुटियों के रूप में मानें
- `--exit-zero` - हमेशा कोड 0 के साथ बाहर निकलें

### सुविधाएं

- **क्रॉस-प्लेटफ़ॉर्म सिंटैक्स सत्यापन** (Linux, macOS, Windows)
- **प्लेटफ़ॉर्म-विशिष्ट सुविधाएं:**
  - **Linux/macOS**: सिस्टम और उपयोगकर्ता crontab सत्यापन, उपयोगकर्ता अस्तित्व जांच, डेमन सत्यापन
  - **Windows**: केवल फ़ाइल-आधारित सत्यापन
- **समय फ़ील्ड सत्यापन** (मिनट, घंटे, दिन, महीने, सप्ताह के दिन)
- **खतरनाक कमांड का पता लगाना**
- **विशेष कीवर्ड समर्थन** (@reboot, @daily, आदि)
- **बहु-पंक्ति कमांड समर्थन**

### दस्तावेज़ीकरण

- **[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - सुविधाओं और क्षमताओं का विस्तृत दस्तावेज़ीकरण

### विकास उपकरण

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### pre-commit के साथ उपयोग

आप अपने प्रोजेक्ट्स में checkcrontab को pre-commit हुक के रूप में उपयोग कर सकते हैं:

1. अपने `.pre-commit-config.yaml` में जोड़ें:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.8  # नवीनतम संस्करण का उपयोग करें
    hooks:
      - id: checkcrontab
```

2. pre-commit इंस्टॉल करें:

```bash
pip install pre-commit
pre-commit install
```

3. हुक स्वचालित रूप से आपके रिपॉजिटरी में सभी `.cron`, `.crontab` और `.tab` फ़ाइलों की जांच करेगा।

### लाइसेंस

MIT License

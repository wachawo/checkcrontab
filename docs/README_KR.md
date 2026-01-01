## Checkcrontab - 크론탭(crontab) 파일 구문 검사 도구

[![CI](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml/badge.svg)](https://github.com/wachawo/checkcrontab/actions/workflows/ci.yml)
[![Coverage](https://codecov.io/gh/wachawo/checkcrontab/branch/main/graph/badge.svg)](https://codecov.io/gh/wachawo/checkcrontab?branch=main)
[![PyPI](https://img.shields.io/pypi/v/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![Downloads](https://img.shields.io/pypi/dm/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/wachawo/checkcrontab/blob/main/LICENSE)
[![Python](https://img.shields.io/pypi/pyversions/checkcrontab.svg)](https://pypi.org/project/checkcrontab/)

크론탭(crontab) 파일의 구문을 검사하기 위한 Python 스크립트입니다. Linux, macOS 및 Windows를 지원하는 크로스 플랫폼 도구입니다.

**[English](https://github.com/wachawo/checkcrontab/blob/main/README.md)** | [Español](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ES.md) | [Português](https://github.com/wachawo/checkcrontab/blob/main/docs/README_PT.md) | [Français](https://github.com/wachawo/checkcrontab/blob/main/docs/README_FR.md) | [Deutsch](https://github.com/wachawo/checkcrontab/blob/main/docs/README_DE.md) | [Italiano](https://github.com/wachawo/checkcrontab/blob/main/docs/README_IT.md) | [Русский](https://github.com/wachawo/checkcrontab/blob/main/docs/README_RU.md) | [中文](https://github.com/wachawo/checkcrontab/blob/main/docs/README_ZH.md) | [日本語](https://github.com/wachawo/checkcrontab/blob/main/docs/README_JA.md) | [हिन्दी](https://github.com/wachawo/checkcrontab/blob/main/docs/README_HI.md) | **[한국어](https://github.com/wachawo/checkcrontab/blob/main/docs/README_KR.md)**

<img width="1108" height="257" alt="image" src="https://github.com/user-attachments/assets/9ad75b94-3a72-4d0f-b9f4-9e1b22ac475d" />

### 요구 사항

- **Python 3.7 이상**
- **Linux**: `/etc/crontab` 파일 읽기 권한 및 systemctl이 설치된 Linux 시스템 (데몬 검사용)
- **macOS**: `/etc/crontab` 파일 읽기 권한이 있는 Unix 시스템 (systemctl 미지원)
- **Windows**: 추가 요구 사항 없음 (파일 기반 구문 검사만 지원)

### 지원 플랫폼

**Linux (전체 지원):**
- ✅ 시스템 크론탭 검사 (`/etc/crontab`)
- ✅ 사용자 크론탭 검사 (`crontab -l -u username` 사용)
- ✅ 사용자 존재 검사
- ✅ systemctl을 통한 데몬/서비스 상태 검사
- ✅ 모든 크론탭 구문 기능 지원
- ✅ 파일 권한 검사
- ✅ 크론 데몬 상태 검사

**macOS (부분 지원):**
- ✅ 시스템 크론탭 검사 (`/etc/crontab`)
- ✅ 사용자 크론탭 검사 (`crontab -l -u username` 사용)
- ✅ 사용자 존재 검사
- ❌ 데몬/서비스 상태 검사 (systemctl 미지원)
- ✅ 모든 크론탭 구문 기능 지원
- ✅ 파일 권한 검사
- ❌ 크론 데몬 상태 검사

**Windows (제한 지원):**
- ✅ 파일 기반 크론탭 구문 검사
- ❌ 사용자 존재 검사 (사용자 관리 연동 미지원)
- ❌ 시스템 크론탭 접근 (`/etc/crontab` 없음)
- ❌ 데몬/서비스 상태 검사 (systemctl 미지원)
- ✅ 모든 크론탭 구문 기능 지원
- ❌ 파일 권한 검사 (Unix 권한 체계 미지원)
- ❌ 크론 데몬 상태 검사 (크론 데몬 없음)

### 설치 방법

```bash
pip3 install checkcrontab
```

또는 GitHub에서 설치:

```bash
pip3 install git+https://github.com/wachawo/checkcrontab.git
```

### 사용 방법

```bash
# 시스템 크론탭 검사 (Linux/macOS 전용)
checkcrontab

# 크론탭 파일 검사
checkcrontab /etc/crontab

# 사용자 크론탭 검사 (Linux/macOS 전용)
checkcrontab username

# 타입 플래그를 지정해 검사
checkcrontab -S system.cron -U user.cron -u username1 -u username2

# 크론탭 디렉토리 검사
checkcrontab /etc/cron.d

# 도움말 표시
checkcrontab --help

# 버전 표시
checkcrontab --version
```

**플랫폼별 동작:**
- **Linux**: 데몬 및 사용자 검사를 포함한 모든 기능 지원
- **macOS**: 데몬 검사(systemctl 미지원)를 제외한 모든 기능 지원
- **Windows**: 파일 기반 검사만 지원, 시스템 연동 기능 미지원

### TEXT 출력
CI 환경 등에서 `STDERR` 출력을 `STDOUT`으로 리디렉션하려면 `--format text` 플래그를 사용하세요:

```bash
checkcrontab --format text examples/user_valid.txt
```

#### SARIF 출력
SARIF 형식으로 출력하려면 `--format sarif` 플래그를 사용하세요:

```bash
checkcrontab --format sarif examples/user_valid.txt
```

### JSON 출력
기계가독형(machine-readable)으로 출력하려면 `--format json` 플래그를 사용하세요:

```bash
checkcrontab --format json examples/user_valid.txt
```

JSON 출력 예시:

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

### 종료 코드

| 코드 | 의미 |
|------|---------|
| 0    | 오류 없음 (경고 허용): `--exit-zero` 사용 시 항상 0 반환. |
| 1    | 문제 발견: 오류가 있거나 `--strict` 설정 시 경고가 있는 경우. |
| 2    | 런타임/사용 오류: 예기치 않은 실패, 잘못된 명령줄 인자(CLI args) 등. |

### 명령줄 옵션

- `-S, --system` - 시스템 크론탭 파일
- `-U, --user` - 사용자 크론탭 파일
- `-u, --username` - 검사할 사용자 이름
- `-v, --version` - 버전 표시
- `-d, --debug` - 디버그 출력
- `-n, --no-colors` - 색상 출력 비활성화
- `--format {text,json,sarif}` - 출력 형식
- `--strict` - 경고를 오류로 처리
- `--exit-zero` - 항상 종료 코드 0 반환

### 주요 기능

- **크로스 플랫폼 구문 검사** (Linux, macOS, Windows)
- **플랫폼별 특화 기능:**
  - **Linux/macOS**: 시스템 및 사용자 크론탭 검사, 사용자 존재 검사, 데몬 검사
  - **Windows**: 파일 기반 검사만 지원
- **시간 필드 검사** (분, 시, 일, 월, 요일)
- **위험 명령어 탐지**
- **특수 키워드 지원** (@reboot, @daily, 등)
- **다중 행 명령어 지원**

**[Features Documentation](https://github.com/wachawo/checkcrontab/blob/main/docs/FEATURES.md)** - 지원 구문, 유효한 값, 예제 및 오류 메시지에 대한 종합 가이드입니다.

### 개발 도구

```bash
pip3 install pre-commit flake8 pytest mypy ruff
pre-commit install
pre-commit run --all-files
pre-commit autoupdate
```

### 테스트

```bash
pytest --cov=checkcrontab --cov-report=term-missing --cov-report=xml
coverage report
# CI에서 자동으로 coverage.xml을 Codecov에 업로드합니다.
# python -m coverage_badge -o docs/coverage.svg
```

### pre-commit과 함께 사용하기

프로젝트에서 `checkcrontab`을 pre-commit 훅(hook)으로 사용할 수 있습니다.

1. `.pre-commit-config.yaml` 파일에 다음 내용을 추가하세요:

```yaml
repos:
  - repo: https://github.com/wachawo/checkcrontab
    rev: 0.0.12  # 최신 버전을 사용하세요
    hooks:
      - id: checkcrontab
        files: \.(cron|crontab|tab|conf)$
        exclude: (\.git|node_modules|__pycache__)/
        args: [--format, json, --strict]
```

2. pre-commit 설치:

```bash
pip install pre-commit
pre-commit install
```

3. 이제 훅(hook)이 저장소 내의 모든 `.cron`, `.crontab`, `.tab` 파일을 자동으로 검사합니다.

### 라이선스

MIT License

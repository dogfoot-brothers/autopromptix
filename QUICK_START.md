# 🚀 AutoPromptix Quick Start Guide

AutoPromptix를 빠르게 시작하는 방법을 안내합니다.

## 📋 요구사항

- Python 3.8 이상
- pip (Python 패키지 관리자)

## 🎯 빠른 시작

### Windows 사용자

1. **실행 스크립트 사용** (권장)
   ```bash
   start.bat
   ```

2. **직접 실행**
   ```bash
   # Enhanced 서버 (권장)
   python enhanced_main.py
   
   # 기본 서버
   python main.py
   ```

### Linux/Mac 사용자

1. **실행 스크립트 사용** (권장)
   ```bash
   chmod +x start.sh
   ./start.sh
   ```

2. **직접 실행**
   ```bash
   # Enhanced 서버 (권장)
   python enhanced_main.py
   
   # 기본 서버
   python main.py
   ```

## 🌐 접속 방법

실행 후 웹 브라우저에서 다음 주소로 접속:

- **Enhanced 서버**: http://127.0.0.1:8001
- **기본 서버**: http://127.0.0.1:8000

## 📦 의존성 설치

처음 실행 시 의존성을 설치해야 합니다:

```bash
pip install -r requirements.txt
```

## 🐳 Docker 사용자

Docker가 설치되어 있다면:

```bash
# Windows
run-docker.bat enhanced

# Linux/Mac
./docker-run.sh enhanced
```

## 🔧 문제 해결

### 포트 충돌
다른 포트를 사용하거나 기존 프로세스를 종료하세요:
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f python
```

### 의존성 오류
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 권한 오류 (Linux/Mac)
```bash
chmod +x start.sh
chmod +x setup-permissions.sh
```

## 📚 추가 정보

- [전체 문서](../README.md)
- [Docker 가이드](../DOCKER_README.md)
- [테스트 가이드](../TESTING_GUIDE.md) 
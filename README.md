# AutoPromptix

AutoPromptix는 AI 함수의 자동 테스트 및 개선을 위한 프레임워크입니다.

## 🚀 빠른 시작

### Docker 기반 실행 (권장)

```bash
# Windows
cd docker
.\quick-start.bat

# Linux/Mac
cd docker
docker build -f Dockerfile.simple -t autopromptix ..
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix
```

### Python 직접 실행

Docker가 없는 경우 Python으로 직접 실행:

```bash
# Enhanced 서버 (권장)
python enhanced_main.py
```

## 🌐 접속

실행 후 웹 브라우저에서 다음 URL로 접속:
**http://127.0.0.1:8001**

## 🏗️ 아키텍처

AutoPromptix는 단순화된 아키텍처를 사용합니다:

```
dashboard/
├── backend/                    # Flask API 서버
│   └── server.py              # API 엔드포인트 + HTML 대시보드
└── run_dashboard.py           # 개발용 실행 스크립트
```

## 🐳 Docker 설정

Docker 관련 파일들은 `docker/` 디렉토리에서 관리됩니다:

```bash
docker/
├── README.md                    # Docker 설정 가이드
├── Dockerfile.simple           # 단순화된 Dockerfile (권장)
├── quick-start.bat             # Windows용 빠른 시작 스크립트
├── docker-compose.yml          # Docker Compose 설정
└── ...
```

### Docker 실행 방법

```bash
# Windows
cd docker
.\quick-start.bat

# Linux/Mac
cd docker
docker build -f Dockerfile.simple -t autopromptix ..
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix

# Docker Compose 사용
cd docker
docker-compose up -d
```

## 📚 자세한 가이드

- [Docker 설정 가이드](docker/README.md)
- [Docker 빠른 시작](docker/quick-start.bat)

## 🌐 접속 방법

실행 후 웹 브라우저에서 접속:
- **Enhanced 서버**: http://127.0.0.1:8001
- **기본 서버**: http://127.0.0.1:8000

## 📦 설치

### 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)
- Docker (권장)

### 의존성 설치
```bash
pip install -r requirements.txt
```

## 🔧 문제 해결

### Docker 설치
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (Windows/Mac)
- [Docker Engine](https://docs.docker.com/engine/install/) (Linux)

### Docker 문제 해결
자세한 문제 해결 가이드는 [docker/README.md](docker/README.md)를 참조하세요.

### 포트 충돌
```bash
# Windows
taskkill /f /im python.exe

# Linux/Mac
pkill -f python

# Docker 컨테이너 정리
docker stop autopromptix-enhanced
docker rm autopromptix-enhanced
```

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다. 
# Docker Setup for AutoPromptix

이 디렉토리는 AutoPromptix의 Docker 관련 파일들을 관리합니다.

## 파일 구조

```
docker/
├── README.md                    # 이 파일
├── Dockerfile                   # 원본 Dockerfile (멀티스테이지 빌드)
├── Dockerfile.simple           # 단순화된 Dockerfile (권장)
├── docker-compose.yml          # Docker Compose 설정
├── .dockerignore               # Docker 빌드 시 제외할 파일들
├── quick-start.bat             # 빠른 시작 스크립트 (Windows)
├── run-docker-simple.bat       # Windows용 Docker 실행 스크립트
├── run-docker.bat              # Windows용 Docker 실행 스크립트 (원본)
├── docker-run.sh               # Linux용 Docker 실행 스크립트
├── docker-build.sh             # Linux용 Docker 빌드 스크립트
├── docker-entrypoint.sh        # 컨테이너 진입점 스크립트
├── docker-dashboard-entrypoint.sh # 대시보드 전용 진입점
└── setup-docker.bat            # Windows용 Docker 설정 스크립트
```

## 🚀 빠른 시작

### Windows에서 실행 (가장 간단)
```powershell
# 빠른 시작 (권장)
cd docker
.\quick-start.bat

# 또는 옵션 선택
cd docker
.\run-docker-simple.bat enhanced
```

### Linux/Mac에서 실행
```bash
# 빌드 및 실행
cd docker
./docker-build.sh
./docker-run.sh

# 또는 직접 실행
docker build -f docker/Dockerfile.simple -t autopromptix ..
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix
```

### Docker Compose 사용
```bash
# Enhanced 서버 실행
cd docker
docker-compose --profile enhanced up -d

# Basic 서버 실행
docker-compose --profile basic up -d

# 개발 환경 실행
docker-compose --profile development up -d
```

## Dockerfile 비교

### Dockerfile.simple (권장)
- ✅ 단순한 구조
- ✅ 빠른 빌드
- ✅ 안정적인 실행
- ✅ 문제 해결됨

### Dockerfile (원본)
- ⚠️ 멀티스테이지 빌드
- ⚠️ 복잡한 구조
- ❌ README.md 의존성 문제

## 포트 설정

- **Enhanced 서버**: 8001
- **Basic 서버**: 8000
- **개발 환경**: 8003

## 접속 URL

- **로컬**: http://127.0.0.1:8001
- **네트워크**: http://[IP]:8001

## 문제 해결

자세한 문제 해결 가이드는 상위 디렉토리의 `DOCKER_TROUBLESHOOTING_GUIDE.md`를 참조하세요.

## 유용한 명령어

```powershell
# 컨테이너 상태 확인
docker ps

# 로그 확인
docker logs autopromptix-enhanced

# 컨테이너 중지
docker stop autopromptix-enhanced

# 컨테이너 제거
docker rm autopromptix-enhanced

# 이미지 제거
docker rmi autopromptix

# 모든 컨테이너 정리
docker system prune -f
```

## 환경 변수

```bash
# OpenAI API 키 설정 (선택사항)
export OPENAI_API_KEY=your_api_key_here

# 또는 .env 파일 생성
echo OPENAI_API_KEY=your_api_key_here > .env
``` 
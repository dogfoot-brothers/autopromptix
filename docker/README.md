# Docker Setup for AutoPromptix

이 디렉토리는 AutoPromptix의 Docker 관련 파일들을 관리합니다.

## 파일 구조

```
docker/
├── README.md                    # 이 파일
├── Dockerfile.simple           # 단순화된 Dockerfile (권장)
├── docker-compose.yml          # Docker Compose 설정
├── .dockerignore               # Docker 빌드 시 제외할 파일들
└── quick-start.bat             # 빠른 시작 스크립트 (Windows)
```

## 🚀 빠른 시작

### Windows에서 실행 (가장 간단)
```powershell
# 빠른 시작 (권장)
cd docker
.\quick-start.bat

# 또는 직접 실행
cd docker
docker build -f Dockerfile.simple -t autopromptix ..
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix
```

### Linux/Mac에서 실행
```bash
# 직접 실행
cd docker
docker build -f Dockerfile.simple -t autopromptix ..
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix

# 또는 Docker Compose 사용
cd docker
docker-compose up -d
```

### Docker Compose 사용
```bash
# 기본 실행
cd docker
docker-compose up -d

# 백그라운드 실행
cd docker
docker-compose up -d
```



## Dockerfile 비교

### Dockerfile.simple (권장)
- ✅ 단순한 구조
- ✅ 빠른 빌드
- ✅ 안정적인 실행
- ✅ 문제 해결됨



## 포트 설정

- **AutoPromptix 서버**: 8001

## 접속 URL

- **로컬**: http://127.0.0.1:8001
- **네트워크**: http://[IP]:8001

## 문제 해결

Docker 관련 문제는 다음을 확인하세요:

### 일반적인 문제들
1. **Docker Desktop이 실행되지 않는 경우**
   - Windows 기능에서 "Virtual Machine Platform" 활성화
   - BIOS에서 가상화 기능 활성화
   - Docker Desktop 재시작

2. **포트 충돌**
   ```bash
   # 기존 컨테이너 정리
   docker stop autopromptix-enhanced
   docker rm autopromptix-enhanced
   ```

3. **빌드 실패**
   - Docker Desktop이 실행 중인지 확인
   - 충분한 디스크 공간 확보
   - 네트워크 연결 확인

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
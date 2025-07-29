# Docker Troubleshooting Guide for AutoPromptix

## 개요
이 가이드는 AutoPromptix를 Docker로 실행하는 과정에서 발생한 문제들과 해결 방법을 정리한 문서입니다.

## 문제 해결 과정

### 1. 초기 Docker 환경 문제

#### 문제: Docker Desktop 연결 오류
```
ERROR: request returned 500 Internal Server Error for API route and version 
http://%2F%2F.%2Fpipe%2FdockerDesktopLinuxEngine/_ping
```

#### 해결 방법:
1. **WSL2 재시작**
   ```powershell
   wsl --shutdown
   ```
2. **Docker Desktop 재시작**
   ```powershell
   taskkill /f /im "Docker Desktop.exe"
   Start-Process "C:\Program Files\Docker\Docker\Docker Desktop.exe"
   ```

### 2. 가상화 지원 문제

#### 문제: Virtualization support not detected
```
Virtualization support not detected Docker Desktop couldn't start as virtualization 
support is not enabled on your machine.
```

#### 해결 방법:
1. **Windows 기능 활성화**
   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
   ```
2. **BIOS에서 가상화 활성화** (VT-x/AMD-V)
3. **시스템 재부팅**

### 3. Docker 빌드 오류

#### 문제: README.md 파일 누락
```
FileNotFoundError: [Errno 2] No such file or directory: 'README.md'
```

#### 원인: 
`setup.py`에서 `README.md`를 참조하지만 Docker 빌드 시 파일이 없음

#### 해결 방법:
1. **Dockerfile.simple 생성** - 복잡한 멀티스테이지 빌드 제거
2. **`pip install -e .` 단계 제거** - 패키지 설치 대신 직접 실행

### 4. 컨테이너 포트 바인딩 문제

#### 문제: 컨테이너가 시작되지만 웹 접근 불가
```
ERR_EMPTY_RESPONSE
```

#### 원인: 
서버가 `127.0.0.1`에만 바인딩되어 컨테이너 외부에서 접근 불가

#### 해결 방법:
1. **호스트 바인딩 변경**
   ```python
   # enhanced_main.py 수정
   dashboard = GoogleStyleDashboardServer(
       host='0.0.0.0',  # 127.0.0.1에서 변경
       port=8001
   )
   ```

### 5. 포트 충돌 문제

#### 문제: 포트가 이미 사용 중
```
Bind for 0.0.0.0:8001 failed: port is already allocated
```

#### 해결 방법:
1. **기존 컨테이너 제거**
   ```powershell
   docker rm -f autopromptix-enhanced
   ```
2. **다른 포트 사용**
   ```powershell
   docker run -d --name autopromptix-enhanced -p 8002:8001 autopromptix
   ```

## 최종 성공 설정

### Dockerfile.simple
```dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd --create-home --shell /bin/bash autopromptix && \
    chown -R autopromptix:autopromptix /app
USER autopromptix

EXPOSE 8000 8001

CMD ["python", "enhanced_main.py"]
```

### 실행 명령어
```powershell
# 이미지 빌드
docker build -f Dockerfile.simple -t autopromptix .

# 컨테이너 실행
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix

# 접속 확인
curl http://127.0.0.1:8001
```

## 문제 해결 체크리스트

- [ ] Docker Desktop이 실행 중인가?
- [ ] WSL2가 정상 작동하는가?
- [ ] 가상화가 BIOS에서 활성화되었는가?
- [ ] Windows 기능이 활성화되었는가?
- [ ] 포트 8001이 사용 가능한가?
- [ ] 컨테이너가 정상 실행되는가?
- [ ] 웹 서버가 0.0.0.0에 바인딩되었는가?

## 유용한 명령어

```powershell
# Docker 상태 확인
docker --version
docker ps
docker ps -a

# 컨테이너 로그 확인
docker logs autopromptix-enhanced

# 컨테이너 내부 접속
docker exec -it autopromptix-enhanced bash

# 포트 사용 확인
netstat -ano | findstr :8001

# 컨테이너 정리
docker stop autopromptix-enhanced
docker rm autopromptix-enhanced
```

## 주의사항

1. **Docker Desktop 필수**: Windows에서는 Docker Desktop이 필요
2. **가상화 활성화**: BIOS와 Windows 기능 모두 활성화 필요
3. **포트 관리**: 호스트 포트와 컨테이너 포트 매핑 주의
4. **권한 문제**: 컨테이너 내부에서 non-root 사용자 사용
5. **네트워크 바인딩**: `0.0.0.0`으로 바인딩하여 외부 접근 허용

## 성공 지표

- ✅ Docker 이미지 빌드 성공
- ✅ 컨테이너 실행 및 유지
- ✅ 웹 브라우저에서 http://127.0.0.1:8001 접속 가능
- ✅ HTTP 200 응답 확인
- ✅ AutoPromptix 대시보드 표시 
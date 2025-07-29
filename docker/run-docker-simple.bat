@echo off
echo AutoPromptix Docker Runner for Windows
echo ======================================

if "%1"=="" (
    echo Usage: %0 [OPTION]
    echo.
    echo Options:
    echo   enhanced    - Run enhanced AutoPromptix server (port 8001)
    echo   basic       - Run basic AutoPromptix server (port 8000)
    echo   stop        - Stop all AutoPromptix containers
    echo.
    echo Examples:
    echo   %0 enhanced
    echo   %0 stop
    exit /b 1
)

REM Check Docker availability
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is not installed or not running
    echo Falling back to Python version...
    python enhanced_main.py
    exit /b 0
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo Docker is installed but daemon is not running
    echo Falling back to Python version...
    python enhanced_main.py
    exit /b 0
)

if "%1"=="enhanced" (
    echo Starting enhanced AutoPromptix server...
    
    REM Check if Docker image exists
    docker images autopromptix >nul 2>&1
    if %errorlevel% neq 0 (
        echo Docker image not found. Building image...
        docker build -f Dockerfile.simple -t autopromptix ..
        if %errorlevel% neq 0 (
            echo Failed to build Docker image
            echo Falling back to Python version...
            python enhanced_main.py
            exit /b 0
        )
    )
    
    docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix
    echo Enhanced server started at http://localhost:8001
    goto :show_containers
)

if "%1"=="basic" (
    echo Starting basic AutoPromptix server...
    
    REM Check if Docker image exists
    docker images autopromptix >nul 2>&1
    if %errorlevel% neq 0 (
        echo Docker image not found. Building image...
        docker build -f Dockerfile.simple -t autopromptix ..
        if %errorlevel% neq 0 (
            echo Failed to build Docker image
            echo Falling back to Python version...
            python main.py
            exit /b 0
        )
    )
    
    docker run -d --name autopromptix-basic -p 8000:8000 autopromptix
    echo Basic server started at http://localhost:8000
    goto :show_containers
)

if "%1"=="stop" (
    echo Stopping AutoPromptix containers...
    docker stop autopromptix-enhanced autopromptix-basic 2>nul
    docker rm autopromptix-enhanced autopromptix-basic 2>nul
    echo Containers stopped and removed
    exit /b 0
)

:show_containers
echo.
echo Running containers:
docker ps --filter "name=autopromptix"
echo.
echo To stop containers: %0 stop
exit /b 0 
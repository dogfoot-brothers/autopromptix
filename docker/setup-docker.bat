@echo off
echo 🐳 AutoPromptix Docker Setup for Windows
echo ==========================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo ✅ Docker is available

REM Build Docker images
echo 🔨 Building Docker images...
docker build --target production -t autopromptix:prod .
if %errorlevel% neq 0 (
    echo ❌ Failed to build production image
    pause
    exit /b 1
)

docker build --target dashboard -t autopromptix:dashboard .
if %errorlevel% neq 0 (
    echo ❌ Failed to build dashboard image
    pause
    exit /b 1
)

echo ✅ All images built successfully

echo.
echo 🚀 Available commands:
echo   docker run -p 8001:8001 autopromptix:prod
echo   docker run -p 8002:8001 autopromptix:dashboard
echo   docker-compose --profile enhanced up -d
echo.
echo 📖 For more information, see DOCKER_README.md
pause 
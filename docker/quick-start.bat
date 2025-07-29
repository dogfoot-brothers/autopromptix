@echo off
echo AutoPromptix Quick Start
echo =======================

echo Building and running AutoPromptix with Docker...
echo.

REM Build the image
echo Building Docker image...
docker build -f Dockerfile.simple -t autopromptix ..

if %errorlevel% neq 0 (
    echo Failed to build Docker image
    echo Please check Docker is running and try again
    pause
    exit /b 1
)

REM Stop existing containers
echo Stopping existing containers...
docker stop autopromptix-enhanced 2>nul
docker rm autopromptix-enhanced 2>nul

REM Run the container
echo Starting AutoPromptix...
docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix

if %errorlevel% neq 0 (
    echo Failed to start container
    pause
    exit /b 1
)

echo.
echo ✅ AutoPromptix is now running!
echo 🌐 Open your browser and go to: http://127.0.0.1:8001
echo.
echo To stop the server: docker stop autopromptix-enhanced
echo To view logs: docker logs autopromptix-enhanced
echo.
pause 
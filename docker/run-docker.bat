@echo off
echo 🚀 AutoPromptix Docker Runner for Windows
echo ==========================================

if "%1"=="" (
    echo Usage: %0 [OPTION]
    echo.
    echo Options:
    echo   enhanced    - Run enhanced AutoPromptix server ^(port 8001^)
    echo   dashboard   - Run dashboard with frontend ^(port 8002^)
    echo   basic       - Run basic AutoPromptix server ^(port 8000^)
    echo   dev         - Run development environment ^(port 8003^)
    echo   stop        - Stop all AutoPromptix containers
    echo   logs        - Show logs for running containers
    echo   clean       - Remove all AutoPromptix containers and images
    echo.
    echo Examples:
    echo   %0 enhanced
    echo   %0 dashboard
    echo   %0 stop
    exit /b 1
)

REM Function to check Docker availability
:check_docker
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running
    echo.
    echo 💡 To use Docker version, please install Docker Desktop:
    echo    https://www.docker.com/products/docker-desktop/
    echo.
    exit /b 1
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is installed but daemon is not running
    echo.
    echo 💡 Please start Docker Desktop and try again
    echo.
    exit /b 1
)
exit /b 0

if "%1"=="enhanced" (
    echo 📡 Starting enhanced AutoPromptix server...
    
    call :check_docker
    if %errorlevel% neq 0 (
        echo 🔄 Falling back to Python version...
        echo 🐍 Starting Python Enhanced Server...
        echo 🌐 Server will be available at: http://127.0.0.1:8001
        echo ⏹️  Press Ctrl+C to stop the server
        echo.
        python enhanced_main.py
        exit /b 0
    )
    
    REM Check if Docker image exists
    docker images autopromptix:prod >nul 2>&1
    if %errorlevel% neq 0 (
        echo ⚠️  Docker image not found. Building image...
        docker build --target production -t autopromptix:prod .
        if %errorlevel% neq 0 (
            echo ❌ Failed to build Docker image
            echo 🔄 Falling back to Python version...
            python enhanced_main.py
            exit /b 0
        )
    )
    
    docker run -d --name autopromptix-enhanced -p 8001:8001 autopromptix:prod
    echo ✅ Enhanced server started at http://localhost:8001
    goto :show_containers
)

if "%1"=="dashboard" (
    echo 📡 Starting dashboard with frontend...
    
    call :check_docker
    if %errorlevel% neq 0 (
        echo 🔄 Falling back to Python version...
        echo 🐍 Starting Python Dashboard...
        echo 🌐 Dashboard will be available at: http://127.0.0.1:8001
        echo ⏹️  Press Ctrl+C to stop the server
        echo.
        python dashboard/run_dashboard.py
        exit /b 0
    )
    
    docker run -d --name autopromptix-dashboard -p 8002:8001 autopromptix:dashboard
    echo ✅ Dashboard started at http://localhost:8002
    goto :show_containers
)

if "%1"=="basic" (
    echo 📡 Starting basic AutoPromptix server...
    
    call :check_docker
    if %errorlevel% neq 0 (
        echo 🔄 Falling back to Python version...
        echo 🐍 Starting Python Basic Server...
        echo 🌐 Server will be available at: http://127.0.0.1:8000
        echo ⏹️  Press Ctrl+C to stop the server
        echo.
        python main.py
        exit /b 0
    )
    
    docker run -d --name autopromptix-basic -p 8000:8000 -e AUTOPROMPTIX_MODE=basic autopromptix:prod
    echo ✅ Basic server started at http://localhost:8000
    goto :show_containers
)

if "%1"=="dev" (
    echo 📡 Starting development environment...
    
    call :check_docker
    if %errorlevel% neq 0 (
        echo 🔄 Falling back to Python version...
        echo 🐍 Starting Python Enhanced Server...
        echo 🌐 Server will be available at: http://127.0.0.1:8001
        echo ⏹️  Press Ctrl+C to stop the server
        echo.
        python enhanced_main.py
        exit /b 0
    )
    
    docker run -d --name autopromptix-dev -p 8003:8001 -p 8004:8000 -v "%cd%:/app" autopromptix:dev
    echo ✅ Development environment started
    echo ✅ Enhanced server: http://localhost:8003
    echo ✅ Basic server: http://localhost:8004
    goto :show_containers
)

if "%1"=="stop" (
    echo 🛑 Stopping AutoPromptix containers...
    call :check_docker
    if %errorlevel% neq 0 (
        echo ❌ Docker not available
        exit /b 1
    )
    
    for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}" ^| findstr autopromptix') do (
        echo Stopping %%i...
        docker stop %%i
    )
    echo ✅ All AutoPromptix containers stopped
    exit /b 0
)

if "%1"=="logs" (
    echo 📋 Showing logs for AutoPromptix containers...
    call :check_docker
    if %errorlevel% neq 0 (
        echo ❌ Docker not available
        exit /b 1
    )
    
    for /f "tokens=*" %%i in ('docker ps --format "{{.Names}}" ^| findstr autopromptix') do (
        echo.
        echo Logs for %%i:
        docker logs --tail=20 %%i
    )
    exit /b 0
)

if "%1"=="clean" (
    echo ⚠️  This will remove all AutoPromptix containers and images!
    set /p confirm="Are you sure? (y/N): "
    if /i "%confirm%"=="y" (
        call :check_docker
        if %errorlevel% neq 0 (
            echo ❌ Docker not available
            exit /b 1
        )
        
        echo 🗑️  Removing AutoPromptix containers...
        for /f "tokens=*" %%i in ('docker ps -a --format "{{.Names}}" ^| findstr autopromptix') do (
            docker rm -f %%i
        )
        echo 🗑️  Removing AutoPromptix images...
        for /f "tokens=*" %%i in ('docker images --format "{{.Repository}}:{{.Tag}}" ^| findstr autopromptix') do (
            docker rmi %%i
        )
        echo ✅ Cleanup completed
    ) else (
        echo ❌ Cleanup cancelled
    )
    exit /b 0
)

echo ❌ Unknown option: %1
echo Use '%0' without arguments to see available options
exit /b 1

:show_containers
echo.
echo 📋 Running AutoPromptix containers:
docker ps --format "table {{.Names}}\t{{.Ports}}\t{{.Status}}" | findstr autopromptix 2>nul
if %errorlevel% neq 0 (
    echo No containers running
) 
@echo off
REM AgentDaf1 Development Startup Script for Windows
REM Quick start for development environment

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=agentdaf1
set ENV_FILE=.env
set LOG_FILE=./logs/startup.log

REM Create necessary directories
if not exist "./logs" mkdir "./logs"
if not exist "./uploads" mkdir "./uploads"
if not exist "./data" mkdir "./data"
if not exist "./backups" mkdir "./backups"

REM Colors for output (Windows 10+)
set "RED=[91m"
set "GREEN=[92m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "NC=[0m"

REM Logging function
:log
echo %GREEN%[%date% %time%] %~1%NC%
echo [%date% %time%] %~1 >> "%LOG_FILE%"
goto :eof

:error
echo %RED%[%date% %time%] ERROR: %~1%NC%
echo [%date% %time%] ERROR: %~1 >> "%LOG_FILE%"
goto :eof

:warning
echo %YELLOW%[%date% %time%] WARNING: %~1%NC%
echo [%date% %time%] WARNING: %~1 >> "%LOG_FILE%"
goto :eof

:info
echo %BLUE%[%date% %time%] INFO: %~1%NC%
echo [%date% %time%] INFO: %~1 >> "%LOG_FILE%"
goto :eof

REM Check if Docker is running
:check_docker
docker info >nul 2>&1
if errorlevel 1 (
    call :error "Docker is not running. Please start Docker first."
    exit /b 1
)
call :log "Docker is running"
goto :eof

REM Check if docker-compose is available
:check_docker_compose
docker-compose --version >nul 2>&1
if errorlevel 1 (
    call :error "docker-compose is not installed or not in PATH"
    exit /b 1
)
call :log "docker-compose is available"
goto :eof

REM Setup environment
:setup_environment
call :log "Setting up development environment..."

REM Copy .env file if it doesn't exist
if not exist "%ENV_FILE%" (
    if exist ".env.example" (
        copy .env.example %ENV_FILE% >nul
        call :log "Created .env file from .env.example"
        call :warning "Please update %ENV_FILE% with your configuration"
    ) else (
        call :warning ".env.example not found. Creating basic .env file"
        (
            echo # Development Environment
            echo DEBUG=true
            echo ENVIRONMENT=development
            echo DB_PASSWORD=dev_password
            echo JWT_SECRET=dev_jwt_secret_change_me
            echo GRAFANA_PASSWORD=admin
        ) > %ENV_FILE%
    )
)

REM Create Python virtual environment if it doesn't exist
if not exist "venv" (
    call :log "Creating Python virtual environment..."
    python -m venv venv
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    call :log "Virtual environment created and dependencies installed"
)

REM Install Node.js dependencies if they exist
if exist "enterprise\web\package.json" (
    call :log "Installing Node.js dependencies..."
    cd enterprise\web
    npm install
    cd ..\..
    call :log "Node.js dependencies installed"
)
goto :eof

REM Start development services
:start_dev_services
call :log "Starting development services..."

REM Start core services
docker-compose -f docker-compose.yml up -d postgres redis rabbitmq

REM Wait for services to be ready
call :log "Waiting for core services to be ready..."
timeout /t 15 /nobreak >nul

REM Start application services
docker-compose -f docker-compose.yml up -d agentdaf1-app gateway data-service analytics-service websocket-service

REM Wait for application services
timeout /t 10 /nobreak >nul

REM Start web services
docker-compose -f docker-compose.yml up -d web-server web-app

call :log "All development services started"
goto :eof

REM Start local development servers
:start_local_servers
call :log "Starting local development servers..."

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Start Flask API in background
call :info "Starting Flask API server on port 8080..."
start /B python app.py > .\logs\flask.log 2>&1

REM Start FastAPI server in background
call :info "Starting FastAPI server on port 8000..."
start /B python src\main.py > .\logs\fastapi.log 2>&1

REM Start WebSocket server in background
call :info "Starting WebSocket server on port 8004..."
start /B python services\websocket_service.py > .\logs\websocket.log 2>&1

REM Start static file server for website
call :info "Starting static file server on port 8082..."
cd gitsitestylewebseite
start /B python -m http.server 8082 > ..\logs\website.log 2>&1
cd ..

call :log "All local servers started"
goto :eof

REM Check service health
:check_services
call :log "Checking service health..."

REM Check Docker services
docker ps | findstr "agentdaf1-postgres" >nul && call :log "✓ agentdaf1-postgres is running" || call :warning "agentdaf1-postgres is not running"
docker ps | findstr "agentdaf1-redis" >nul && call :log "✓ agentdaf1-redis is running" || call :warning "agentdaf1-redis is not running"
docker ps | findstr "agentdaf1-rabbitmq" >nul && call :log "✓ agentdaf1-rabbitmq is running" || call :warning "agentdaf1-rabbitmq is not running"
docker ps | findstr "agentdaf1-app" >nul && call :log "✓ agentdaf1-app is running" || call :warning "agentdaf1-app is not running"
docker ps | findstr "agentdaf1-gateway" >nul && call :log "✓ agentdaf1-gateway is running" || call :warning "agentdaf1-gateway is not running"

REM Check local servers
tasklist | findstr "python.exe" >nul && call :log "✓ Python servers are running" || call :warning "Python servers may not be running"
goto :eof

REM Show access URLs
:show_urls
call :log "Development environment is ready!"
echo.
echo Access URLs:
echo   Main Application:    http://localhost:8080
echo   API Gateway:         http://localhost:8000
echo   Enhanced Dashboard:   http://localhost:8082/enhanced-dashboard.html
echo   Static Website:      http://localhost:8082
echo   WebSocket:           ws://localhost:8004
echo   RabbitMQ Management: http://localhost:15672 ^(admin/admin123^)
echo   Grafana:            http://localhost:3001 ^(admin/admin^)
echo   Prometheus:         http://localhost:9090
echo.
echo Logs:
echo   Flask:    ./logs/flask.log
echo   FastAPI:  ./logs/fastapi.log
echo   WebSocket: ./logs/websocket.log
echo   Website:  ./logs/website.log
echo.
echo To stop all services, run: scripts\stop-dev.bat
goto :eof

REM Stop development services
:stop_services
call :log "Stopping development services..."

REM Stop local servers
taskkill /f /im python.exe >nul 2>&1

REM Stop Docker services
docker-compose -f docker-compose.yml down

call :log "All development services stopped"
goto :eof

REM Show help
:show_help
echo AgentDaf1 Development Startup Script
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   start     Start development environment ^(default^)
echo   stop      Stop development environment
echo   restart   Restart development environment
echo   status    Check service status
echo   logs      Show service logs
echo   setup     Setup development environment only
echo   help      Show this help message
echo.
echo Examples:
echo   %~nx0 start
echo   %~nx0 stop
echo   %~nx0 status
goto :eof

REM Main script logic
if "%1"=="start" (
    call :check_docker
    call :check_docker_compose
    call :setup_environment
    call :start_dev_services
    call :start_local_servers
    timeout /t 5 /nobreak >nul
    call :check_services
    call :show_urls
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="restart" (
    call :stop_services
    timeout /t 2 /nobreak >nul
    call :check_docker
    call :check_docker_compose
    call :start_dev_services
    call :start_local_servers
    timeout /t 5 /nobreak >nul
    call :check_services
    call :show_urls
) else if "%1"=="status" (
    call :check_services
) else if "%1"=="logs" (
    call :log "Showing logs..."
    if exist "./logs" (
        for %%f in (logs\*.log) do (
            echo === %%f ===
            type "%%f"
            echo.
        )
    )
) else if "%1"=="setup" (
    call :check_docker
    call :check_docker_compose
    call :setup_environment
    call :log "Development environment setup completed"
) else if "%1"=="help" (
    call :show_help
) else if "%1"=="--help" (
    call :show_help
) else if "%1"=="-h" (
    call :show_help
) else if "%1"=="" (
    call :check_docker
    call :check_docker_compose
    call :setup_environment
    call :start_dev_services
    call :start_local_servers
    timeout /t 5 /nobreak >nul
    call :check_services
    call :show_urls
) else (
    call :error "Unknown command: %1"
    call :show_help
    exit /b 1
)

call :log "Script completed successfully"
goto :eof
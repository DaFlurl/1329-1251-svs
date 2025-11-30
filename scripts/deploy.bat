@echo off
REM AgentDaf1 Deployment Script for Windows
REM Automated deployment and container management

setlocal enabledelayedexpansion

REM Configuration
set PROJECT_NAME=agentdaf1
set DOCKER_COMPOSE_FILE=docker-compose.yml
set ENV_FILE=.env
set BACKUP_DIR=./backups
set LOG_FILE=./logs/deployment.log

REM Create necessary directories
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
if not exist "./logs" mkdir "./logs"

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

REM Backup current data
:backup_data
call :log "Creating backup of current data..."
for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "BACKUP_NAME=backup_%dt:~0,8%_%dt:~8,6%"
set "BACKUP_PATH=%BACKUP_DIR%\%BACKUP_NAME%"

mkdir "%BACKUP_PATH%"

REM Backup database
docker ps | findstr "postgres" >nul
if not errorlevel 1 (
    docker exec agentdaf1-postgres pg_dump -U agentdaf1 agentdaf1 > "%BACKUP_PATH%\database.sql" 2>nul || call :warning "Could not backup database"
)

REM Backup important directories
if exist "data" xcopy /E /I "data" "%BACKUP_PATH%\data" >nul 2>&1 || call :warning "Could not backup data directory"
if exist "uploads" xcopy /E /I "uploads" "%BACKUP_PATH%\uploads" >nul 2>&1 || call :warning "Could not backup uploads directory"
if exist "gitsitestylewebseite" xcopy /E /I "gitsitestylewebseite" "%BACKUP_PATH%\gitsitestylewebseite" >nul 2>&1 || call :warning "Could not backup website directory"

call :log "Backup created: %BACKUP_PATH%"
goto :eof

REM Build Docker images
:build_images
call :log "Building Docker images..."
docker-compose build --no-cache
if errorlevel 1 (
    call :error "Failed to build Docker images"
    exit /b 1
)
call :log "Docker images built successfully"
goto :eof

REM Start services
:start_services
call :log "Starting services..."
docker-compose up -d
if errorlevel 1 (
    call :error "Failed to start services"
    exit /b 1
)

REM Wait for services to be ready
call :log "Waiting for services to be ready..."
timeout /t 30 /nobreak >nul

REM Check service health
call :check_service_health
goto :eof

REM Check service health
:check_service_health
call :log "Checking service health..."

REM Check main services
docker ps | findstr "agentdaf1-app" >nul && call :log "✓ agentdaf1-app is running" || call :warning "agentdaf1-app is not running"
docker ps | findstr "agentdaf1-redis" >nul && call :log "✓ agentdaf1-redis is running" || call :warning "agentdaf1-redis is not running"
docker ps | findstr "agentdaf1-postgres" >nul && call :log "✓ agentdaf1-postgres is running" || call :warning "agentdaf1-postgres is not running"
docker ps | findstr "agentdaf1-nginx" >nul && call :log "✓ agentdaf1-nginx is running" || call :warning "agentdaf1-nginx is not running"
goto :eof

REM Stop services
:stop_services
call :log "Stopping services..."
docker-compose down
call :log "Services stopped"
goto :eof

REM Clean up Docker resources
:cleanup_docker
call :log "Cleaning up Docker resources..."
docker system prune -f
docker volume prune -f
call :log "Docker cleanup completed"
goto :eof

REM Deploy to production
:deploy_production
call :log "Starting production deployment..."

call :check_docker
call :check_docker_compose
call :backup_data

REM Stop existing services
call :stop_services

REM Build and start new services
call :build_images
call :start_services

call :log "Production deployment completed successfully"
goto :eof

REM Deploy to development
:deploy_development
call :log "Starting development deployment..."

call :check_docker
call :check_docker_compose

REM Start services in development mode
docker-compose -f docker-compose.yml up -d

call :log "Development deployment completed"
goto :eof

REM Update services only
:update_services
call :log "Updating services..."

call :check_docker
call :check_docker_compose

REM Pull latest images
docker-compose pull

REM Restart services
docker-compose up -d --force-recreate

call :log "Services updated successfully"
goto :eof

REM Show logs
:show_logs
call :log "Showing logs..."
docker-compose logs -f --tail=100
goto :eof

REM Show status
:show_status
call :log "Service status:"
docker-compose ps

call :log "Resource usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\t{{.BlockIO}}"
goto :eof

REM Show help
:show_help
echo AgentDaf1 Deployment Script
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   production     Deploy to production environment
echo   development    Deploy to development environment
echo   update         Update existing services
echo   stop           Stop all services
echo   start          Start all services
echo   restart        Restart all services
echo   logs           Show service logs
echo   status         Show service status
echo   cleanup        Clean up Docker resources
echo   backup         Create backup
echo   health         Check service health
echo   help           Show this help message
echo.
echo Examples:
echo   %~nx0 production
echo   %~nx0 logs
echo   %~nx0 status
goto :eof

REM Main script logic
if "%1"=="production" (
    call :deploy_production
) else if "%1"=="development" (
    call :deploy_development
) else if "%1"=="update" (
    call :update_services
) else if "%1"=="stop" (
    call :stop_services
) else if "%1"=="start" (
    call :start_services
) else if "%1"=="restart" (
    call :stop_services
    call :start_services
) else if "%1"=="logs" (
    call :show_logs
) else if "%1"=="status" (
    call :show_status
) else if "%1"=="cleanup" (
    call :cleanup_docker
) else if "%1"=="backup" (
    call :backup_data
) else if "%1"=="health" (
    call :check_service_health
) else if "%1"=="help" (
    call :show_help
) else if "%1"=="--help" (
    call :show_help
) else if "%1"=="-h" (
    call :show_help
) else (
    call :error "Unknown command: %1"
    call :show_help
    exit /b 1
)

call :log "Script completed successfully"
goto :eof
@echo off
setlocal enabledelayedexpansion

:: ========================================
:: AgentDaf1.1 Deployment Script
:: ========================================
:: Simple deployment for AgentDaf1.1 application
:: Uses simplified Docker setup with app and Redis services

echo Starting AgentDaf1.1 deployment...
echo.

:: Check if Docker is running
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not running
    echo Please install Docker Desktop and ensure it's running
    pause
    exit /b 1
)

:: Check if docker-compose file exists
if not exist "docker-compose.simple.yml" (
    echo ERROR: docker-compose.simple.yml not found
    echo Please ensure the Docker Compose file exists in the current directory
    pause
    exit /b 1
)

:: Stop existing containers
echo Stopping existing containers...
docker-compose -f docker-compose.simple.yml down

:: Start services
echo Starting services with simplified configuration...
docker-compose -f docker-compose.simple.yml up -d

:: Wait for services to be ready
echo Waiting for services to start...
timeout /t 30 /nobreak >nul
set /p "count=0"
:wait_loop
if "%count%" lss "30" (
    set /a count+=1
    echo Checking service readiness... %%count%%/30
    timeout /t 1 /nobreak >nul
    goto wait_loop
)

:: Check service health
echo Checking service health...
timeout /t 10 curl -f http://localhost:8080/api/health >nul 2>&1
if errorlevel 1 (
    echo WARNING: Health check failed, but continuing...
) else (
    echo ✓ Services are running and accessible
)

echo.
echo Deployment completed!
echo Application should be available at: http://localhost:8080
echo.
echo Redis is available at: localhost:6379
echo.
echo To check logs: docker-compose -f docker-compose.simple.yml logs -f
echo.
echo To stop services: docker-compose -f docker-compose.simple.yml down
echo.

pause
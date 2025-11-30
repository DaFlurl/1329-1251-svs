@echo off
REM AgentDaf1.1 Enterprise Deployment Script for Windows
REM This script deploys the complete enterprise microservices system

setlocal enabledelayedexpansion

echo ==================================
echo AgentDaf1.1 Enterprise Deployment
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Check if docker-compose file exists
if not exist "docker-compose.enterprise.yml" (
    echo ERROR: Docker Compose file not found: docker-compose.enterprise.yml
    pause
    exit /b 1
)

REM Create necessary directories
echo Creating necessary directories...
if not exist "enterprise\monitoring\prometheus" mkdir "enterprise\monitoring\prometheus"
if not exist "enterprise\monitoring\grafana\dashboards" mkdir "enterprise\monitoring\grafana\dashboards"
if not exist "enterprise\monitoring\grafana\datasources" mkdir "enterprise\monitoring\grafana\datasources"
if not exist "enterprise\nginx\ssl" mkdir "enterprise\nginx\ssl"
if not exist "enterprise\database\init" mkdir "enterprise\database\init"

REM Create environment file if it doesn't exist
if not exist ".env" (
    echo Creating .env file with default values...
    (
        echo # Database Configuration
        echo DB_PASSWORD=your_secure_password_here
        echo.
        echo # JWT Configuration
        echo JWT_SECRET=your-super-secret-jwt-key-change-in-production
        echo.
        echo # Grafana Configuration
        echo GRAFANA_PASSWORD=admin
        echo.
        echo # Environment
        echo ENVIRONMENT=production
    ) > .env
    echo WARNING: Please edit .env file with your secure passwords before proceeding!
    pause
)

REM Build and start services
echo Building Docker images...
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise build

echo Starting services...
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise up -d

REM Wait for services to be ready
echo Waiting for services to be ready...
timeout /t 30 /nobreak >nul

REM Check service health
echo Checking service health...
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise ps

REM Display access information
echo.
echo Access Information:
echo ==================================
echo Main Dashboard:     http://localhost:3000
echo API Gateway:        http://localhost:8000
echo Analytics Service:   http://localhost:8002
echo WebSocket Service:  http://localhost:8004
echo Prometheus:         http://localhost:9090
echo Grafana:            http://localhost:3001 ^(admin/admin^)
echo Database:           localhost:5432
echo Redis:              localhost:6379

echo.
echo API Documentation:
echo ==================================
echo Gateway Docs:        http://localhost:8000/docs
echo Data Service Docs:   http://localhost:8001/docs
echo Analytics Docs:     http://localhost:8002/docs

echo.
echo Management Commands:
echo ==================================
echo View logs:        docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise logs -f [service-name]
echo Stop services:    docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise down
echo Restart services: docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise restart [service-name]
echo Update services:  docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise pull ^&^& docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise up -d

echo.
echo AgentDaf1.1 Enterprise deployment completed successfully!
echo WARNING: Remember to change default passwords in production!
pause
@echo off
REM AgentDaf1.1 Dual System Deployment Script
REM Deploys both Basic and Enterprise systems simultaneously

setlocal enabledelayedexpansion

echo ==========================================
echo 🚀 AgentDaf1.1 Dual System Deployment
echo ==========================================
echo.
echo This will deploy BOTH systems:
echo 📊 Basic System (Ports 80, 8080, 6379)
echo 🏢 Enterprise System (Ports 3000, 8000-8004, 3001, 9090, 5432)
echo.

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Create necessary directories
echo 📁 Creating necessary directories...
if not exist "uploads" mkdir "uploads"
if not exist "logs" mkdir "logs"
if not exist "data" mkdir "data"
if not exist "ssl" mkdir "ssl"
if not exist "enterprise\monitoring\prometheus" mkdir "enterprise\monitoring\prometheus"
if not exist "enterprise\monitoring\grafana\dashboards" mkdir "enterprise\monitoring\grafana\dashboards"
if not exist "enterprise\monitoring\grafana\datasources" mkdir "enterprise\monitoring\grafana\datasources"
if not exist "enterprise\nginx\ssl" mkdir "enterprise\nginx\ssl"
if not exist "enterprise\database\init" mkdir "enterprise\database\init"

REM Create environment file if it doesn't exist
if not exist ".env" (
    echo 📝 Creating .env file with default values...
    (
        echo # Basic System Configuration
        echo GITHUB_TOKEN=
        echo GITHUB_REPO_OWNER=
        echo GITHUB_REPO_NAME=
        echo.
        echo # Enterprise System Configuration
        echo DB_PASSWORD=your_secure_password_here
        echo JWT_SECRET=your-super-secret-jwt-key-change-in-production
        echo GRAFANA_PASSWORD=admin
        echo ENVIRONMENT=production
    ) > .env
    echo ⚠️  Please edit .env file with your configuration before proceeding!
    pause
)

echo.
echo 🔨 Building and Starting Basic System...
docker-compose up -d --build

echo.
echo 🏢 Building and Starting Enterprise System...
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise up -d --build

REM Wait for services to be ready
echo.
echo ⏳ Waiting for services to be ready...
timeout /t 45 /nobreak >nul

echo.
echo 🏥 Checking Service Health...
echo ==========================================
echo.
echo 📊 BASIC SYSTEM:
docker-compose ps

echo.
echo 🏢 ENTERPRISE SYSTEM:
docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise ps

echo.
echo 🌐 ACCESS INFORMATION:
echo ==========================================
echo.
echo 📊 BASIC SYSTEM:
echo    Main App:        http://localhost:8080
echo    Nginx Proxy:     http://localhost:80
echo    Redis:           localhost:6379
echo.
echo 🏢 ENTERPRISE SYSTEM:
echo    Premium Dashboard: http://localhost:3000
echo    API Gateway:      http://localhost:8000
echo    Data Service:     http://localhost:8001
echo    Analytics:        http://localhost:8002
echo    WebSocket:        http://localhost:8004
echo    Prometheus:       http://localhost:9090
echo    Grafana:          http://localhost:3001 (admin/admin)
echo    PostgreSQL:       localhost:5432
echo    Redis (Enterprise): localhost:6379
echo.
echo 📚 API DOCUMENTATION:
echo    Gateway Docs:     http://localhost:8000/docs
echo    Data Service:     http://localhost:8001/docs
echo    Analytics:        http://localhost:8002/docs
echo.
echo 🔧 MANAGEMENT COMMANDS:
echo ==========================================
echo.
echo 📊 Basic System:
echo    View logs:        docker-compose logs -f [service-name]
echo    Stop basic:       docker-compose down
echo    Restart basic:     docker-compose restart [service-name]
echo.
echo 🏢 Enterprise System:
echo    View logs:        docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise logs -f [service-name]
echo    Stop enterprise:  docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise down
echo    Restart enterprise: docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise restart [service-name]
echo.
echo 🔄 BOTH SYSTEMS:
echo    Stop all:         docker-compose down ^&^& docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise down
echo    Restart all:      docker-compose restart ^&^& docker-compose -f docker-compose.enterprise.yml -p agentdaf1-enterprise restart
echo.
echo 📈 SYSTEM COMPARISON:
echo ==========================================
echo 📊 Basic System:    Simple, lightweight, good for development
echo 🏢 Enterprise:       Full-featured, production-ready, AI-powered
echo.
echo 💡 TIP: Use Basic System for quick testing, Enterprise System for full features!
echo.
echo 🎉 Both AgentDaf1.1 systems deployed successfully!
echo ⚠️  Remember to change default passwords in production!
pause
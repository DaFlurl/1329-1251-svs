@echo off
echo 🚀 Starting AgentDaf1.1 Deployment...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Stop existing containers
echo 🛑 Stopping existing containers...
docker-compose down --remove-orphans

REM Build and start containers
echo 🔨 Building AgentDaf1.1 container...
docker-compose build --no-cache

echo 🚀 Starting containers...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check container status
echo 📊 Checking container status...
docker-compose ps

REM Health check
echo 🏥 Performing health check...
curl -f http://localhost/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ AgentDaf1.1 is running successfully!
    echo 🌐 Access application at: http://localhost
    echo 🔍 Health check: http://localhost/health
    echo 📊 API: http://localhost/api/
) else (
    echo ❌ Health check failed. Checking logs...
    docker-compose logs agentdaf1-app
)

echo 🎉 Deployment complete!
pause
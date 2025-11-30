@echo off
REM AgentDaf1.1 MCP Sequential Thinking Setup Script for Windows

echo 🚀 Setting up MCP Sequential Thinking with Docker...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker Desktop first.
    pause
    exit /b 1
)

REM Pull latest Sequential Thinking image
echo 📦 Pulling Sequential Thinking MCP image...
docker pull mcp/sequentialthinking

REM Build and start all services
echo 🔧 Building and starting services...
docker-compose up -d --build

REM Wait for services to be ready
echo ⏳ Waiting for services to start...
timeout /t 10 /nobreak >nul

REM Check service status
echo 📊 Checking service status...
docker-compose ps

REM Test MCP Sequential Thinking
echo 🧪 Testing MCP Sequential Thinking...
python mcp_sequential_integration.py

echo ✅ Setup complete!
echo.
echo 🌐 Access Points:
echo    - Main App: http://localhost:8080
echo    - Grafana: http://localhost:3000 (admin/admin123)
echo    - Prometheus: http://localhost:9090
echo    - MCP Sequential Thinking: http://localhost:3010
echo.
echo 🧠 MCP Commands:
echo    - Test integration: python mcp_sequential_integration.py
echo    - View logs: docker-compose logs -f sequential-thinking
echo    - Stop services: docker-compose down
echo    - Restart MCP: docker-compose restart sequential-thinking
echo.
pause
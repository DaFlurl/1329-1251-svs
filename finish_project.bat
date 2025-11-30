@echo off
REM AgentDaf1.1 Enterprise System Repair & Completion Tool
REM Automatically repairs, configures, and finalizes complete enterprise system

setlocal enabledelayedexpansion

echo ==========================================
echo 🔧 AgentDaf1.1 System Repair & Completion
echo ==========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Run the repair tool
echo 🚀 Running system repair and completion...
python finish_project.py

if errorlevel 1 (
    echo ❌ System repair encountered errors!
    pause
    exit /b 1
) else (
    echo.
    echo ✅ System repair completed successfully!
    echo.
    echo 📋 Check SYSTEM_COMPLETION_REPORT.json for full details
    echo.
    echo 🚀 Your AgentDaf1.1 Enterprise system is COMPLETE!
    echo.
    echo 🌐 Quick Access:
    echo    Basic System:     http://localhost:8080
    echo    Enterprise:        http://localhost:3000
    echo    Monitoring:        http://localhost:3001
    echo.
    echo 🎯 Next Steps:
    echo    1. Run: deploy-enterprise.bat (Enterprise only)
    echo    2. Run: deploy-both-systems.bat (Both systems)
    echo    3. Configure environment variables
    echo    4. Access your dashboards!
    echo.
    pause
)
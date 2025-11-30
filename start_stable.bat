@echo off
echo ========================================
echo   AgentDaf1.1 - Stable Base Launcher
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting Stable Base System...
echo Version: 1.1.0
echo Mode: Production Ready
echo.

python stable_base.py

pause
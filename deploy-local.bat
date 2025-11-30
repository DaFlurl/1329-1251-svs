@echo off
REM AgentDaf1.1 Local Development Deployment (Docker Fallback)
REM This script sets up local development without Docker

echo ==================================
echo AgentDaf1.1 Local Development Setup
echo ==================================

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed. Please install Python 3.8+ first.
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install enterprise dependencies
if exist "enterprise\requirements.txt" (
    pip install -r enterprise\requirements.txt
)

REM Start basic application
echo Starting basic application...
python src\main.py

pause

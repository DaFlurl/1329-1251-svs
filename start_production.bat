@echo off
echo Starting AgentDaf1.1 Production Server...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install Gunicorn if not available
python -c "import gunicorn" >nul 2>&1
if errorlevel 1 (
    echo Installing Gunicorn for production server...
    pip install gunicorn
)

REM Start with Gunicorn production server
echo.
echo ========================================
echo   AgentDaf1.1 Production Server
echo ========================================
echo.
echo Starting Gunicorn WSGI server...
echo Access at: http://localhost:8080
echo Press CTRL+C to stop
echo.

python -m gunicorn --config gunicorn.conf.py wsgi:app

pause
@echo off
echo Starting AgentDaf1.1 Production System...
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Check if required files exist
if not exist "app.py" (
    echo Error: app.py not found
    echo Creating simple app.py...
    echo from flask import Flask, render_template > app.py
    echo app = Flask(__name__) >> app.py
    echo. >> app.py
    echo @app.route('/') >> app.py
    echo def home(): >> app.py
    echo     return '''<h1>AgentDaf1.1 Dashboard</h1> >> app.py
    echo     <p>System Status: Running</p> >> app.py
    echo     <p><a href="/monitoring">Monitoring</a></p> >> app.py
    echo     <p><a href="/database">Database</a></p> >> app.py
    echo     <p><a href="/auth">Authentication</a></p> >> app.py
    echo     <p><a href="/backup">Backup System</a></p> >> app.py
    echo     ''' >> app.py
    echo. >> app.py
    echo if __name__ == '__main__': >> app.py
    echo     app.run(host='0.0.0.0', port=8080, debug=True) >> app.py
)

REM Start the application
echo Starting Flask application on port 8080...
python app.py

pause
@echo off
echo Setting up GitHub synchronization...
echo.

REM Check if GITHUB_TOKEN is set
if "%GITHUB_TOKEN%"=="" (
    echo Please set GITHUB_TOKEN environment variable
    echo Example: set GITHUB_TOKEN=your_token_here
    pause
    exit /b 1
)

echo Creating GitHub repository...
python tools/github_manager.py sync

if %ERRORLEVEL% EQU 0 (
    echo.
    echo Success! Repository synchronized to GitHub
    echo.
    echo Repository URL: https://github.com/FlorinStrobel/AgentDaf1.1
    echo Branch: feature/user-profile-enhancement-2
) else (
    echo.
    echo Failed to synchronize to GitHub
    echo Please check your token and network connection
)

pause
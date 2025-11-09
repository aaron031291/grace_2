@echo off
echo ========================================
echo   GRACE Auto-Refresh Log Viewer
echo   Updates every 5 minutes
echo ========================================
echo.

cd /d "%~dp0"

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scripts\watch_all_logs.py

pause

@echo off
echo ========================================
echo   GRACE Autonomous Healing Monitor
echo   Real-time healing activity display
echo ========================================
echo.

cd /d "%~dp0"

if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)

python scripts\watch_healing.py

pause

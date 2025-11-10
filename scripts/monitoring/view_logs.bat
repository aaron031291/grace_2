@echo off
echo ========================================
echo   GRACE System Logs Viewer
echo   Last 50 Entries from All Systems
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

echo Running log viewer...
python scripts\view_all_logs.py

pause

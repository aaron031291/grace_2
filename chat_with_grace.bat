@echo off
echo ========================================
echo   Starting Grace Terminal Chat
echo ========================================
echo.
echo Make sure backend is running first!
echo Backend should be at: http://localhost:8000
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo Warning: Virtual environment not found
    echo Using system Python...
)

echo.
echo Starting Grace chat interface...
echo.

REM Run terminal chat
python backend\terminal_chat.py

if errorlevel 1 (
    echo.
    echo ❌ Error starting Grace chat
    echo Make sure:
    echo   1. Backend is running (start_both.bat)
    echo   2. Virtual environment is set up
    echo.
)

pause

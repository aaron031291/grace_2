@echo off
echo ========================================
echo   Starting Grace Terminal Chat
echo ========================================
echo.

cd /d "%~dp0"

REM Activate virtual environment
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
    echo Using system Python...
)

REM Run terminal chat
python backend\terminal_chat.py

pause

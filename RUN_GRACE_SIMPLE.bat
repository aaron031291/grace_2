@echo off
cls
echo.
echo ========================================
echo Starting Grace Backend (Simple)
echo ========================================
echo.
echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Starting Grace on http://localhost:8000
echo Press Ctrl+C to stop
echo.
echo ========================================
echo.

REM Start Grace backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

pause

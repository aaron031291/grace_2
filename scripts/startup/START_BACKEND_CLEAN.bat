@echo off
echo Stopping any running backend...
taskkill /F /FI "WINDOWTITLE eq *Grace API*" 2>nul
timeout /t 2 /nobreak >nul

echo Starting Grace Backend...
cd /d "%~dp0"
python -m uvicorn backend.main:app --reload --port 8000

pause

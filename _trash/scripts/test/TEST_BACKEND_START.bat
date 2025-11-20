@echo off
echo Testing backend startup...
echo.

cd /d C:\Users\aaron\grace_2

REM Start backend and capture output
timeout /t 3 >nul
start "GRACE Backend Test" cmd /k "python serve.py"

echo Backend starting in separate window...
echo.
echo Wait 20 seconds then check:
echo   http://localhost:8000/api/health
echo.
echo Or run: python test_multi_os_fabric_e2e.py
echo.
pause

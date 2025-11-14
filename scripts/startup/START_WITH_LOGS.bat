@echo off
cls
echo ========================================
echo GRACE - Starting with Live Log View
echo ========================================
echo.

cd /d C:\Users\aaron\grace_2

REM Kill old processes
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Start backend and capture output to file
echo [1/3] Starting backend...
start "GRACE Backend" cmd /c "python serve.py 2>&1 | tee backend_live.log"

REM Wait a bit
timeout /t 5 >nul

REM Show live logs
echo [2/3] Showing backend startup logs...
echo ========================================
echo.

REM Tail the log file as it's being written
powershell -Command "Get-Content backend_live.log -Wait -Tail 50"

pause

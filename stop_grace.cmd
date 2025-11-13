@echo off
REM Grace Server Shutdown Script

echo ============================================================
echo Grace AI System - Server Shutdown
echo ============================================================
echo.

echo Finding Grace processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
    set PID=%%a
    echo Found process: %%a
    taskkill /F /PID %%a
    echo Process terminated
)

echo.
echo Checking for Python processes...
tasklist | findstr python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Python processes still running
    tasklist | findstr python.exe
) else (
    echo No Python processes found
)

echo.
echo Grace shutdown complete
pause

@echo off
REM Grace Server Startup Script
REM Handles port conflicts and clean startup

echo ============================================================
echo Grace AI System - Server Startup
echo ============================================================
echo.

REM Check if port 8000 is in use
echo Checking port 8000...
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1

if %ERRORLEVEL% EQU 0 (
    echo WARNING: Port 8000 is already in use
    echo.
    echo Finding process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do (
        set PID=%%a
        echo Process ID: %%a
    )
    
    echo.
    set /p KILL="Kill existing process? (Y/N): "
    if /i "%KILL%"=="Y" (
        taskkill /F /PID %PID%
        echo Process killed
        timeout /t 2 /nobreak >nul
    ) else (
        echo.
        echo Cannot start - port 8000 is occupied
        pause
        exit /b 1
    )
)

echo Port 8000 is available
echo.

echo Starting Grace backend...
echo ============================================================
python serve.py

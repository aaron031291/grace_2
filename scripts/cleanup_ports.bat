@echo off
REM Cleanup script to kill processes on Grace ports before starting
REM Run this if you get "address already in use" errors

echo.
echo ========================================
echo Grace Port Cleanup
echo ========================================
echo.

echo Checking for processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8000.*LISTENING"') do (
    echo Found process PID %%a on port 8000
    taskkill /PID %%a /F >nul 2>&1
    if !errorlevel! == 0 (
        echo   [OK] Killed PID %%a
    ) else (
        echo   [WARN] Could not kill PID %%a - may need admin
    )
)

echo.
echo Waiting 2 seconds for cleanup...
timeout /t 2 /nobreak >nul

echo.
echo Verifying port 8000 is free...
netstat -ano | findstr ":8000.*LISTENING" >nul 2>&1
if %errorlevel% == 0 (
    echo   [WARN] Port 8000 still in use!
    echo   You may need to run this script as Administrator
    netstat -ano | findstr ":8000.*LISTENING"
) else (
    echo   [OK] Port 8000 is free
)

echo.
echo ========================================
echo Cleanup Complete
echo ========================================
echo.
pause

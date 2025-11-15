@echo off
cls
echo.
echo ====================================================================
echo GRACE - CLEAN START
echo ====================================================================
echo.
echo Step 1: Killing ALL Python processes...
echo.

taskkill /F /IM python.exe /T >nul 2>&1

timeout /t 2 >nul

echo Step 2: Verifying ports are free...
echo.

netstat -ano | findstr :800 | findstr LISTENING

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ⚠️ Some ports still in use. Waiting 5 seconds...
    timeout /t 5 >nul
) else (
    echo ✓ All ports free!
)

echo.
echo Step 3: Starting Grace...
echo.
echo ====================================================================
echo.

python serve.py

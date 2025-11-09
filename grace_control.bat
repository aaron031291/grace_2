@echo off
REM Grace Master Control Script
REM Single script to control all Grace systems

:menu
cls
echo ========================================
echo      GRACE MASTER CONTROL CENTER
echo ========================================
echo.
echo 1. Start Grace (Backend + Frontend)
echo 2. Start Backend Only
echo 3. Chat with Grace (Terminal)
echo 4. View Logs (One-time)
echo 5. Watch Logs (Auto-refresh 5min)
echo 6. Watch Healing (Real-time)
echo 7. Check Health
echo 8. Enable Autonomy
echo 9. Exit
echo.
set /p choice="Select option (1-9): "

if "%choice%"=="1" goto start_all
if "%choice%"=="2" goto start_backend
if "%choice%"=="3" goto chat
if "%choice%"=="4" goto view_logs
if "%choice%"=="5" goto watch_logs
if "%choice%"=="6" goto watch_healing
if "%choice%"=="7" goto health_check
if "%choice%"=="8" goto enable_autonomy
if "%choice%"=="9" goto end

goto menu

:start_all
echo.
echo Starting Grace (Backend + Frontend)...
start "Grace Backend" start_both.bat
timeout /t 3
goto menu

:start_backend
echo.
echo Starting Backend...
start "Grace Backend" restart_backend.bat
timeout /t 3
goto menu

:chat
echo.
echo Opening chat with Grace...
call chat_with_grace.bat
goto menu

:view_logs
echo.
echo Viewing logs...
call view_logs.bat
goto menu

:watch_logs
echo.
echo Starting auto-refresh log viewer (5 min intervals)...
call watch_all_logs.bat
goto menu

:watch_healing
echo.
echo Starting real-time healing monitor...
call watch_healing.bat
goto menu

:health_check
echo.
echo Checking Grace health...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
curl http://localhost:8000/health 2>nul
if errorlevel 1 (
    echo.
    echo Backend not running. Start it first ^(option 1 or 2^)
)
echo.
pause
goto menu

:enable_autonomy
echo.
echo Enabling autonomy...
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
curl -X POST http://localhost:8000/api/healing/autonomy/enable -H "Content-Type: application/json" -d "{\"tier\": 2}" 2>nul
if errorlevel 1 (
    echo.
    echo Backend not running. Start it first.
) else (
    echo.
    echo ✅ Autonomy enabled at Tier 2
)
echo.
pause
goto menu

:end
echo.
echo Goodbye!
echo.
exit

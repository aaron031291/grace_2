@echo off
REM Grace Control Script - Start/Stop/Status

setlocal
set GRACE_DIR=%~dp0
cd /d "%GRACE_DIR%"

if "%1"=="start" goto START
if "%1"=="stop" goto STOP
if "%1"=="restart" goto RESTART
if "%1"=="status" goto STATUS
if "%1"=="watch" goto WATCH
if "%1"=="logs" goto LOGS

:HELP
echo.
echo Grace Control Script
echo ====================
echo.
echo Usage: grace.cmd [command]
echo.
echo Commands:
echo   start    - Start Grace with watchdog
echo   stop     - Stop Grace (kill switch - won't auto-restart)
echo   restart  - Restart Grace
echo   status   - Show Grace status
echo   watch    - Run with watchdog supervisor
echo   logs     - View recent logs
echo.
goto END

:START
echo Starting Grace...
python serve.py
goto END

:STOP
echo.
echo ================================
echo GRACE KILL SWITCH - Manual Stop
echo ================================
echo.
echo Setting manual shutdown flag...
echo {"manual_shutdown": true, "timestamp": "%date% %time%"} > grace_state.json

echo Stopping Grace process...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq GRACE*" 2>nul
taskkill /F /IM python.exe /FI "COMMANDLINE eq *serve.py*" 2>nul

echo.
echo ✅ Grace stopped (manual shutdown)
echo    Watchdog will NOT auto-restart
echo.
goto END

:RESTART
echo Restarting Grace...
call :STOP
timeout /t 3 >nul
echo {"manual_shutdown": false} > grace_state.json
call :START
goto END

:STATUS
echo.
echo Grace Status
echo ============
powershell -Command "if (Test-Path grace_state.json) { $state = Get-Content grace_state.json | ConvertFrom-Json; Write-Host 'State file:' $state.manual_shutdown; if ($state.manual_shutdown -eq $true) { Write-Host 'Status: STOPPED (manual)' -ForegroundColor Yellow } else { Write-Host 'Status: Should be running' -ForegroundColor Green } } else { Write-Host 'No state file' }"

echo.
echo Checking if backend is running...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 2 -UseBasicParsing; Write-Host '✅ Backend ALIVE on port 8000' -ForegroundColor Green } catch { Write-Host '❌ Backend not responding' -ForegroundColor Red }"
echo.
goto END

:WATCH
echo.
echo Starting Grace with Watchdog Supervisor
echo ========================================
echo.
echo The watchdog will:
echo  - Keep Grace running
echo  - Auto-restart on crashes
echo  - Respect kill switch (manual stops)
echo  - Log all restart events
echo.
echo Press Ctrl+C to stop both Grace and watchdog
echo.
python grace_watchdog.py
goto END

:LOGS
echo.
echo Recent Watchdog Logs:
echo =====================
if exist watchdog.log (
    powershell -Command "Get-Content watchdog.log -Tail 50"
) else (
    echo No watchdog.log found
)
echo.
goto END

:END
endlocal

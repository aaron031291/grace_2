@echo off
REM Start Grace with Auto-Restart

echo.
echo ================================
echo Starting GRACE with Watchdog
echo ================================
echo.

cd /d %~dp0

REM Clear manual shutdown flag
echo {"manual_shutdown": false, "timestamp": "%date% %time%", "started_by": "start_script"} > grace_state.json

echo Launching Grace with supervisor...
echo.
echo The watchdog will:
echo  ✅ Keep Grace running
echo  ✅ Auto-restart on crashes
echo  ✅ Log all events
echo  ✅ Alert on failures
echo.
echo Press Ctrl+C to stop
echo.

python grace_watchdog.py

pause

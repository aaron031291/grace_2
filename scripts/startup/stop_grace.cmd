@echo off
REM Kill Switch - Manual Stop (Won't Auto-Restart)

echo.
echo ================================
echo GRACE KILL SWITCH
echo ================================
echo.
echo This will STOP Grace and prevent auto-restart
echo.
pause

cd /d %~dp0

echo Setting manual shutdown flag...
echo {"manual_shutdown": true, "timestamp": "%date% %time%", "stopped_by": "kill_switch"} > grace_state.json

echo.
echo Stopping all Grace processes...
taskkill /F /IM python.exe 2>nul

echo.
echo ✅ Grace stopped
echo.
echo Manual shutdown flag set - watchdog will NOT restart
echo.
echo To start Grace again:
echo   grace.cmd start
echo   OR
echo   grace.cmd watch  (with supervisor)
echo.
pause

@echo off
cls
echo.
echo ========================================
echo GRACE - Auto-Restart System
echo ========================================
echo.
echo Starting Grace with full resilience:
echo.
echo  Layer 1: Internal Kernel Supervision
echo    - Monitors kernel heartbeats
echo    - Auto-restarts failed kernels
echo    - Max 3 attempts per kernel
echo.
echo  Layer 2: External Process Watchdog
echo    - Monitors serve.py process
echo    - Auto-restarts on crash
echo    - Respects kill switch
echo    - Logs all events
echo.
echo ========================================
echo.

cd /d %~dp0

REM Clear manual shutdown flag
echo {"manual_shutdown": false, "timestamp": "%date% %time%"} > grace_state.json

echo Starting watchdog supervisor...
echo.
echo Press Ctrl+C to stop Grace
echo.

python grace_watchdog.py

echo.
echo Watchdog stopped.
pause

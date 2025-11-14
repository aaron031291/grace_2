@echo off
REM Complete Grace Demo with Live Activity Monitor

echo ================================================================================
echo GRACE COMPLETE SYSTEM DEMO - WITH LIVE MONITORING
echo ================================================================================
echo.
echo This will run the complete demo and show you Grace's activities in real-time
echo.
echo ================================================================================
echo.

REM Enable PC and Firefox access for demo
set ENABLE_PC_ACCESS=true
set ENABLE_FIREFOX_ACCESS=true

echo [INFO] PC Access: ENABLED
echo [INFO] Firefox Access: ENABLED
echo.

REM Run demo
python DEMO_GRACE_COMPLETE.py

echo.
echo ================================================================================
echo Demo complete!
echo.
echo To watch Grace work continuously in background:
echo   START_GRACE_AND_WATCH.bat
echo.
echo ================================================================================
pause

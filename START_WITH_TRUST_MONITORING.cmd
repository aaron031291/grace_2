@echo off
REM Start Grace with TRUST Framework Monitoring

echo ============================================================
echo GRACE WITH TRUST FRAMEWORK
echo ============================================================
echo.
echo Starting Grace in Terminal 1...
echo Will open TRUST monitoring in Terminal 2...
echo.

REM Start Grace in new window
start "Grace Server" cmd /k "python serve.py"

REM Wait for Grace to boot
echo Waiting for Grace to boot (30 seconds)...
timeout /t 30 /nobreak

REM Start TRUST monitor in new window
start "TRUST Monitor" cmd /k "python scripts/utilities/trust_monitor_live.py"

echo.
echo ============================================================
echo GRACE + TRUST FRAMEWORK STARTED
echo ============================================================
echo.
echo Terminal 1: Grace Server (main API)
echo Terminal 2: TRUST Framework Monitor (real-time)
echo.
echo API: http://localhost:8000
echo Dashboard: http://localhost:8000/api/trust/dashboard
echo.
echo Press any key to stop both...
pause

REM Kill Grace
python kill_grace.py

echo.
echo Stopped.

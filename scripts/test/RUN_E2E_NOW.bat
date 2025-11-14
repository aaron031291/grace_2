@echo off
echo Starting backend and running E2E test...
cd /d C:\Users\aaron\grace_2

REM Start backend in background, redirect output
start /MIN "GRACE Backend" cmd /c "python serve.py > backend_e2e.log 2>&1"

echo Waiting 35 seconds for backend to fully start...
ping 127.0.0.1 -n 36 > nul

echo.
echo Running E2E tests...
echo.
python test_multi_os_fabric_e2e.py

echo.
echo ========================================
echo Last 50 lines of backend log:
echo ========================================
powershell -Command "if (Test-Path backend_e2e.log) { Get-Content backend_e2e.log -Tail 50 } else { Write-Host 'No log file created yet' }"

pause

@echo off
cls
echo ========================================
echo GRACE - Simple Start and Test
echo ========================================
echo.

cd /d C:\Users\aaron\grace_2

REM Kill old processes
echo Cleaning up old processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Start backend and save output
echo.
echo Starting backend (output will be saved to backend_output.log)...
echo ========================================
echo.

start /B cmd /c "python serve.py > backend_output.log 2>&1"

REM Wait and show progress
echo Waiting for backend to start...
echo [==          ] 10 seconds...
timeout /t 10 >nul

echo [=====       ] 20 seconds...
timeout /t 10 >nul

echo [========    ] 30 seconds...
timeout /t 10 >nul

echo [===========] 40 seconds...
timeout /t 10 >nul

echo.
echo ========================================
echo Backend should be ready now!
echo ========================================
echo.

REM Show last 50 lines of backend log
echo Last 50 lines of backend output:
echo ----------------------------------------
powershell -Command "if (Test-Path backend_output.log) { Get-Content backend_output.log -Tail 50 } else { Write-Host 'No log file yet' }"
echo ----------------------------------------
echo.

REM Check if backend is responding
echo Checking if backend is responding...
powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -TimeoutSec 5 -UseBasicParsing; Write-Host '[OK] Backend is ALIVE on port 8000' -ForegroundColor Green; Write-Host 'Response:' $r.Content } catch { Write-Host '[FAIL] Backend not responding yet' -ForegroundColor Red; Write-Host 'Error:' $_.Exception.Message }"

echo.
echo.
echo ========================================
echo Run Tests Now? (Y/N)
echo ========================================
set /p runtests=

if /i "%runtests%"=="Y" (
    echo.
    echo Running E2E tests...
    echo ========================================
    python test_multi_os_fabric_e2e.py
    echo.
    echo ========================================
    echo Test complete!
)

echo.
echo To view full backend log, run: VIEW_LOGS_NOW.bat
echo To stop backend: taskkill /F /IM python.exe
echo.
pause

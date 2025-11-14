@echo off
echo Starting backend and running tests...
cd /d C:\Users\aaron\grace_2

REM Start backend in background
start /MIN "GRACE Backend" cmd /c "python serve.py > backend_run.log 2>&1"

echo Waiting 25 seconds for backend to start...
timeout /t 25 >nul

echo.
echo Running tests...
python test_multi_os_fabric_e2e.py

echo.
echo Done! Check backend_run.log for backend output.
pause

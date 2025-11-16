@echo off
echo ========================================
echo GRACE - Clean Start
echo ========================================
echo.

echo Step 1: Killing any running Grace processes...
python kill_grace.py >nul 2>&1
timeout /t 2 /nobreak >nul

echo Step 2: Cleaning up stale port allocations...
python cleanup_stale_ports.py --yes

echo Step 3: Starting Grace with complete infrastructure...
echo.
echo Starting in 3 seconds...
timeout /t 3 /nobreak >nul

python serve.py

pause

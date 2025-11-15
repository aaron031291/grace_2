@echo off
echo ==========================================
echo GRACE - Restarting Backend
echo ==========================================
echo.

echo Stopping any running Python processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting backend with all 19 kernels...
echo.

cd /d C:\Users\aaron\grace_2
python serve.py

echo.
echo Backend stopped
pause

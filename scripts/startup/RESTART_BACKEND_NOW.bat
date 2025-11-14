@echo off
echo.
echo ========================================
echo  Restarting Backend with Fixed Routes
echo ========================================
echo.

echo Stopping any running Python processes...
taskkill /F /IM python.exe >nul 2>&1

timeout /t 2 /nobreak >nul

echo.
echo Starting backend with stub routes (prevents JSON errors)...
echo.

python serve.py

pause

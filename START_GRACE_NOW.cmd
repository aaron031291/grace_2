@echo off
echo ==========================================
echo GRACE - STARTING ALL 20 KERNELS
echo ==========================================
echo.

echo Cleaning up any old processes...
taskkill /F /IM python.exe 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting backend with:
echo   - 20 kernels
echo   - 31 API endpoints
echo   - Voice conversation system
echo   - Full NLP integration
echo.

cd /d C:\Users\aaron\grace_2
python serve.py

pause

@echo off
echo.
echo Finding process using port 8001...
echo.

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8001') do (
    echo Found PID: %%a
    taskkill /PID %%a /F
)

echo.
echo Port 8001 should now be free!
echo.
pause

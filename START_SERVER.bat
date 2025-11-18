@echo off
REM Start Grace Server
REM This is a simple wrapper around server.py

echo ========================================
echo Starting GRACE Server
echo ========================================
echo.
echo Port: 8000 (or GRACE_PORT if set)
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

python server.py

pause

@echo off
echo.
echo ========================================
echo Starting Grace Terminal Control
echo ========================================
echo.
echo Controls:
echo   - Type to chat with Grace
echo   - Ctrl+S to stop remote access
echo   - Ctrl+C to exit
echo.
echo Press any key to start...
pause >nul

python grace_terminal_control.py

pause

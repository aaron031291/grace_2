@echo off
echo.
echo ========================================
echo GRACE REMOTE ACCESS - LIVE SYSTEM
echo ========================================
echo.
echo Starting backend with remote access enabled...
echo.
echo Once running, you can:
echo   - Register your device
echo   - Get session token
echo   - Execute commands remotely
echo   - Access via WebSocket shell
echo.
echo API Documentation: http://localhost:8000/docs
echo.
echo ========================================
echo.

python serve.py

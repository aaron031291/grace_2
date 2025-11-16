@echo off
echo ========================================
echo GRACE - Complete System Startup
echo ========================================
echo.

echo Cleaning up old processes...
python kill_grace.py >nul 2>&1

echo.
echo Starting Grace with complete infrastructure...
echo - Domain System
echo - Infrastructure Layer (Service Mesh, Gateway, Discovery)
echo - Network Healing
echo - Kernel Port Manager
echo.

python serve.py

pause

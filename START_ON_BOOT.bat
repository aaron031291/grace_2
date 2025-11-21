@echo off
title Grace System - AutoBoot
echo ===================================================
echo GRACE SYSTEM - AUTONOMOUS BOOT SEQUENCE
echo ===================================================
echo.

REM 1. Start Backend (The Brain)
echo [BOOT] Starting Grace Backend (server.py)...
cd /d "%~dp0"
start "Grace Backend" cmd /k "python server.py"

REM 2. Wait for Backend to initialize
echo [BOOT] Waiting for brain to wake up...
timeout /t 5 /nobreak >nul

REM 3. Start Frontend (The Face)
echo [BOOT] Starting Grace Frontend (Vite)...
cd /d "%~dp0frontend"
start "Grace Frontend" cmd /k "npm run dev"

echo.
echo [BOOT] System Fully Operational.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo.
echo You can close this window, but keep the other two open.
timeout /t 10
exit

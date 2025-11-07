@echo off
echo Restarting Grace Backend...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
cd /d %~dp0
title Grace Backend
.venv\Scripts\activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000

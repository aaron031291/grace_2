@echo off
echo Starting Grace Backend (Simple Mode)...
cd /d %~dp0
.venv\Scripts\activate
uvicorn backend.main:app --host 127.0.0.1 --port 8000

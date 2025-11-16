@echo off
echo Starting Grace Chat Bridge (Port 8001)...
cd /d %~dp0
title Grace Chat Bridge
.venv\Scripts\activate
python chat_bridge\main.py

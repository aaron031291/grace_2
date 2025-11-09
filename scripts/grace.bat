@echo off
cd /d "C:\Users\aaron\grace_2"
if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate.bat
)
python backend\terminal_chat.py
